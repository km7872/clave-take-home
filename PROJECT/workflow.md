## Project Workflow & Architecture (Candidate Implementation)

This document describes **what was built**, **how it works end‑to‑end**, and the **key decisions** made while implementing the Clave take‑home.

---

## 1. Goals & Scope

- Normalize multiple restaurant data sources (Square POS, DoorDash, Toast export) into a **unified Supabase schema**.
- Expose that normalized data via a **FastAPI backend** and a **React dashboard** that supports:
  - Standard analytics (revenue, top items, locations, time‑of‑day).
  - **Natural‑language queries** that map to SQL and visualizations.
- Keep the implementation **pragmatic**: fully implement Square + DoorDash, and document Toast mapping without over‑engineering.

---

## 2. Data Model Design

I started by designing a **source‑agnostic schema**, then made each source conform to it.

**Core entities (mirrored as Python dataclasses in `src/dataclasses/`):**

- **Locations / Addresses**
  - `Location(id, name, timezone, status, type, merchant_id)`
  - `Address(location_id, address_line_1, locality, administrative_district_level_1, postal_code, country)`
  - One row per physical store; separate address table for flexibility.

- **Menu hierarchy**
  - `Category(id, name, display_name)`
  - `Item(id, name, description, category_id, display_name)`
  - `ItemVariation(id, item_id, name, price_currency, price, display_name)`
  - `ItemLocMapping(item_id, location_id)`
  - Supports “category → item → variation” plus “which items exist at which locations”.

- **Orders & line items**
  - `Order(id, location_id, ref_id, source, created_at, updated_at, closed_at, tip_amount, tip_amount_currency, tax_amount, tax_currency, total_money, total_money_currency)`
  - `OrderDetail(id, order_id, itemvar_id, qty, gross_amount_currency, gross_amount, total_amount_currency, total_amount)`
  - `Fulfillment(order_id, uid, type, state)`

- **Payments**
  - `Payment(id, order_id, location_id, amount_currency, tip_amount_currency, total_money_currency, created_at, updated_at, amount, tip_amount, total_money, source_type, status)`
  - `CardDetails(payment_id, status, card_brand, last_4, exp_month, exp_year, entry_method)`
  - `CashDetails(payment_id, buyer_supplied_currency, change_back_currency, buyer_supplied_money, change_back_money)`

**Key decisions:**

- **Unified schema first**: no source‑specific tables; every source must be mapped into these entities.
- **Money as cents in JSON, dollars in DB**: all parsers convert integer cents to float dollars.
- **Raw vs cleaned names**: `name` is the exact upstream value; `display_name` is reserved for cleaned, canonical naming.

---

## 3. Parsing Workflow per Source

### 3.1 Square (`src/parser/square_parser.py`)

**Input:**

- `data/sources/square/catalog.json`
- `data/sources/square/orders.json`
- `data/sources/square/payments.json`
- `data/sources/square/locations.json`

**Process:**

1. **Catalog**
   - Parse `CATEGORY`, `ITEM`, and `ITEM_VARIATION` objects into `Category`, `Item`, `ItemVariation`.
   - Strip emojis from names for easier downstream use.
   - Build `ItemLocMapping` from `present_at_location_ids`.

2. **Locations & addresses**
   - `Location` and `Address` from `locations.json`.

3. **Orders & line items**
   - `Order` from `orders.json` (timestamps, source, tip, tax, totals).
   - `OrderDetail` from `line_items` (each line gets a UUID for `id`).
   - `Fulfillment` from `order.fulfillments`.

4. **Payments**
   - `Payment`, `CardDetails`, `CashDetails` from `payments.json`.

5. **Return shape**
   - `parse_all()` returns a dict with keys:
     - `categories`, `items`, `item_variations`, `locations`, `address`,
       `item_loc_mapping`, `orders`, `order_details`, `fulfillments`,
       `payments`, `card_details`, `cash_details`.

**Decision:** treat Square as the “reference” implementation that defines what other sources must output.

---

### 3.2 DoorDash (`src/parser/doordash_parser.py`)

**Input:**

- `data/sources/doordash_orders.json` (merchant, stores, orders).

**Process:**

1. **Locations & addresses**
   - Each `store` becomes a `Location` + `Address`.
   - `Location.id` = `store_id`, `type` = `"DOORDASH_STORE"`, `merchant_id` from top‑level `merchant`.

2. **Catalog reconstruction**
   - No separate catalog file; reconstruct from `orders[*].order_items[*]`:
     - `Category` from unique `category` strings.
     - `Item` from unique `item_id` with `category_id`.
     - `ItemVariation`: simple one‑per‑item variation (`id = item_id`, price from `unit_price`).

3. **Item‑location mapping**
   - `ItemLocMapping(item_id, location_id)` derived from `(item_id, store_id)` pairs seen in orders.

4. **Orders & line items**
   - One `Order` per DoorDash order:
     - `id`/`ref_id` = `external_delivery_id`, `location_id` = `store_id`, `source` = `"DoorDash"`.
     - `created_at`, `closed_at`, `updated_at` from `created_at`, `delivery_time`, `pickup_time`.
     - `tip_amount` from `dasher_tip`, `tax_amount` from `tax_amount`.
     - `total_money` = `total_charged_to_consumer`.
   - `OrderDetail` per `order_items` entry:
     - `itemvar_id` = `item_id`.
     - `qty` from `quantity`.
     - `gross_amount` from `unit_price`, `total_amount` from `total_price` (cents→dollars).

5. **Fulfillment & payments**
   - `Fulfillment` from `order_fulfillment_method` + `order_status`.
   - `Payment` per order:
     - `amount` = `merchant_payout` (merchant net).
     - `total_money` = `total_charged_to_consumer` (customer total).
     - `tip_amount` = `dasher_tip`.
     - `source_type` = `"DOORDASH_PAYOUT"`, `status` = `order_status`.
   - `card_details`, `cash_details` = empty lists (not available from DoorDash).

6. **Return shape**
   - `parse_all()` returns the same keys as `SquareParser.parse_all()`.

**Decisions:**

- **Do not change schema for DoorDash‑specific fees** (delivery_fee, service_fee, commission) to keep the core model simple.
- Use a **minimal variation model** (one variation per item) for DoorDash.
- Treat `total_charged_to_consumer` as the `Order.total_money` to align “total” semantics with Square (customer perspective), while putting `merchant_payout` on the `Payment` record.

---

### 3.3 Toast (`data/sources/toast_pos_export.json`)

Toast mapping was **designed but not implemented**, to avoid scope creep.

Key points considered:

- Toast has `orders → checks → selections → payments`.
- There is a design choice whether:
  - `Order` in our schema should represent a **Toast order** (parent of many checks) or
  - a **Toast check** (more aligned to payment units).
- Also needs careful handling of:
  - `businessDate` vs real timestamps.
  - Voided/deleted checks and selections.
  - Revenue centers and servers.

I stopped at the design stage and documented the mapping (in the main README/workflow notes) rather than half‑implementing something ambiguous.

---

## 4. Database Ingestion Workflow

### 4.1 Insert layer (`src/db/insert.py`)

- Each function takes a `List[Dataclass]`, converts to dicts, strips `None`, serializes datetimes, and calls Supabase:
  - `insert_locations`, `insert_addresses`, `insert_categories`, `insert_items`,
    `insert_item_variations`, `insert_item_location_mapping`,
    `insert_orders`, `insert_order_details`, `insert_fulfillments`,
    `insert_payments`, `insert_card_details`, `insert_cash_details`.

### 4.2 Transaction runner (`src/db/test.py`)

This script is used to load either Square or DoorDash into Supabase.

- Source toggle:

  ```python
  LOAD_SQUARE = False  # True => Square, False => DoorDash
  ```

- Workflow:
  1. Instantiate the appropriate parser (`SquareParser` or `DoorDashParser`).
  2. Run `data = parser.parse_all()`.
  3. Start a transaction via `begin_transaction()`.
  4. Insert in FK‑safe order:
     - locations → addresses → categories → items → item_variations →
       item_location_mapping → orders → order_details → fulfillments →
       payments → card_details → cash_details.
  5. On any non‑200 status, raise and rollback; otherwise commit.
  6. Optionally read back counts per table for sanity.

**Decision:** the transaction and insert pipeline are **source‑agnostic**. As long as a parser returns the same keys from `parse_all()`, the ingestion flow doesn’t need to change.

---

## 5. Name Cleaning Workflow

Location: `src/cleaner/clean_names.py`

**Goal:** Normalize `display_name` for items and item variations across messy sources.

Steps:

1. Fetch all `items` and `item_variations` where `display_name` is null/empty.
2. Group:
   - Items by `category_id`.
   - Variations by `item_id`.
3. Within each group, **fuzzy‑cluster** similar names (e.g., typos, different casing).
4. Use `GPTCleaner` to propose a canonical `display_name` for each cluster.
5. Show a **preview** of changes (category or item name + original → cleaned mapping).
6. On user confirmation, update the DB via `db_updater.py`, with rollback on failure.

**Decisions:**

- Keep `name` as the source‑of‑truth; only write to `display_name`.
- Require **human confirmation** before updating DB to avoid GPT silently making bad decisions.

---

## 6. API & Frontend Workflow (Brief)

- **Backend API**
  - FastAPI app at `src/api/main.py`, run via `python run_api.py`.
  - Routes under `src/api/routes/`, using services in `src/api/services/`.
  - Exposes:
    - Location metrics, product performance, orders, payments.
    - Time‑based analytics endpoints.
    - NLP endpoints (via `src/query/`) that convert NL queries to structured queries/SQL.

- **Frontend**
  - Vite + React + TypeScript in `frontend/`.
  - Dashboard components under `frontend/src/components/dashboard/`.
  - Uses:
    - A date‑range context so charts stay in sync.
    - Chart components for revenue by location, trends, peak hours, top sellers, etc.
    - A natural‑language query dialog that calls the backend NLP API and renders returned charts/tables.

---

## 7. How to Run (Quick Reference)

From project root:

1. **Install Python deps**

   ```bash
   pip install -r requirements.txt
   ```

   Configure Supabase env variables for `src/db/dbConnect.py` and (optionally) `OPENAI_API_KEY`.

2. **Load data into Supabase**

   - For **Square**:

     ```python
     # in src/db/test.py
     LOAD_SQUARE = True
     ```

     ```bash
     python -m src.db.test
     ```

   - For **DoorDash**:

     ```python
     # in src/db/test.py
     LOAD_SQUARE = False
     ```

     ```bash
     python -m src.db.test
     ```

3. **Run API**

   ```bash
   python run_api.py
   ```

4. **Run frontend**

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

---

## 8. What I’d Do Next With More Time

- Implement the **Toast parser** on top of the same schema, making a clear call on “order vs check” representation.
- Extend the schema (or add auxiliary tables) for:
  - Detailed DoorDash fee breakdown.
  - Toast revenue centers, servers, and business dates.
- Add tests around each parser to validate row counts and key metrics vs known expectations.


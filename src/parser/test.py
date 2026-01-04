import json
from datetime import datetime
from typing import List, Dict, Optional
from src.dataclasses.category import Category
from src.dataclasses.item import Item
from src.dataclasses.item_variation import ItemVariation
from src.dataclasses.location import Location
from src.dataclasses.address import Address
from src.dataclasses.order import Order
from src.dataclasses.order_detail import OrderDetail
from src.dataclasses.fulfillment import Fulfillment
from src.dataclasses.payment import Payment
from src.dataclasses.card_details import CardDetails
from src.dataclasses.cash_details import CashDetails
from src.parser.square_parser import SquareParser

parser = SquareParser(
        catalog_path='data/sources/square/catalog.json',
        orders_path='data/sources/square/orders.json',
        payments_path='data/sources/square/payments.json',
        locations_path='data/sources/square/locations.json'
    )
    

data = parser.parse_all()


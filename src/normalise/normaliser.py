# take json data, put it in panda dataframe and normalise it

import pandas as pd
import json

class Normaliser:
    def __init__(self, data: dict):
        self.data = data
        self.df = pd.DataFrame(data)

    def analyse_data(self):
        print(self.df.info())
        print(self.df.isnull().sum())
        print(self.df.shape)

        string_cols = self.df.select_dtypes(include="object").columns

        for col in string_cols:
            print(f"\nColumn: {col}")
            print(self.df[col].value_counts().head(10))


def main():
    data = json.load(open('data/sources/square/locations.json'))
    normaliser = Normaliser(data)
    normaliser.analyse_data()

if __name__ == "__main__":
    main()

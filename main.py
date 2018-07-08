# -*- coding: utf-8 -*-
import pandas as pd
import matplotlib.pyplot as plt

# pip install python-Levenshtein
import Levenshtein as Levenshtein

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

INPUT_FILE_MAPS = "./data/maps_datos_spain_mod.csv"
INPUT_FILE_CITY_NAMES = "./data/cities_final.xlsx"
OUTPUT_FILE_CITY_NAMES = "./data/cities_final_processed.xlsx"
DEBUG = False


def sanitize_name(serie):
    serie = serie.str.strip()
    return serie


def process_name(serie):
    serie = serie.str.lower()
    serie = serie.str.replace(r"\b( )?de(l)? \b", " ")
    serie = serie.str.replace(r"\b( )?l[ao](s)? \b", " ")
    serie = serie.str.replace(r"\s+", " ")
    serie = serie.str.replace(r"[\(\)_\\/]", "-")
    serie = serie.str.replace("[áà]", "a")
    serie = serie.str.replace("[éè]", "e")
    serie = serie.str.replace("[íì]", "i")
    serie = serie.str.replace("[óò]", "o")
    serie = serie.str.replace("[úù]", "u")
    serie = serie.str.strip()
    return serie


# %%
if __name__ == '__main__':
    print("Procesing file {:s}".format(INPUT_FILE_CITY_NAMES))
    # Load data
    df_cities = pd.read_excel(INPUT_FILE_CITY_NAMES)
    df_maps = pd.read_csv(INPUT_FILE_MAPS, header=0, encoding="utf-8")

    # Sanitize data
    df_cities = df_cities.drop_duplicates()
    df_cities.loc[:, "localidad"] = sanitize_name(df_cities.localidad)
    df_maps = df_maps.drop("municipio", axis=1)
    df_maps = df_maps.rename(columns={"cp5": "cp"})
    df_maps = df_maps.drop_duplicates()
    df_maps.loc[:, "municipio_consolidado"] = sanitize_name(df_maps.municipio_consolidado)
    df_maps.loc[:, "provincia_consolidada"] = sanitize_name(df_maps.provincia_consolidada)

    # Normalize data
    df_cities.loc[:, "localidad_proc"] = process_name(df_cities.localidad)
    df_maps.loc[:, "municipio_proc"] = process_name(df_maps.municipio_consolidado)

    # Join
    df_maps = df_maps.set_index("cp")
    df_cities = df_cities.set_index("cp")
    df = df_cities.join(df_maps, how="left")
    df.loc[:, "manual_check"] = pd.isna(df.municipio_proc)
    df = df.fillna("")

    # Distance
    df.loc[:, "distance"] = df.apply(lambda x: (Levenshtein.distance(x.localidad_proc, x.municipio_proc) /
                                                len(x.localidad_proc)), axis=1)
    df.loc[:, "diff_long"] = df.apply(lambda x: (len(x.municipio_proc) - len(x.localidad_proc)) / len(x.localidad_proc),
                                      axis=1)

    if DEBUG:
        df.distance.hist(bins=100)
        # plt.yscale("log")
        plt.show()
        df.diff_long.hist(bins=100)
        plt.show()
    df.loc[df.distance > 0.5, "manual_check"] = 1
    df.loc[(abs(df.diff_long) < 0.2) & (df.distance > 0.2), "manual_check"] = 1
    df[df.manual_check == 1].to_excel(OUTPUT_FILE_CITY_NAMES)
    print("File created: {:s}".format(OUTPUT_FILE_CITY_NAMES))

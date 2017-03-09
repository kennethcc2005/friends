from bs4 import BeautifulSoup as BS
from googleplaces import GooglePlaces, types, lang
import requests
from geopy.geocoders import Nominatim
import json
import pandas as pd
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, CollectionInvalid
import datetime as dt
import time
# Define the MongoDB database and table

def read_df(data_path,data_path2):
    df = pd.read_csv(data_path,index_col = 0)
    df2 = pd.read_csv(data_path2,index_col = 0)
    ta_rating = np.zeros(df2.shape[0])
    reviews = np.zeros(df2.shape[0])
    city_rank = np.zeros(df2.shape[0])
    fee = np.chararray(df2.shape[0],itemsize=20)
    visit_length = np.chararray(df2.shape[0],itemsize=20)
    tag = np.chararray(df2.shape[0],itemsize=40)
    for idx in xrange(df2.shape[0]):
        current_df = df[(df.city == df2.loc[idx]['city']) & (df.state == df2.loc[idx]['state'])]
        cdf = current_df[[df2.loc[idx]['name'] in i for i in current_df.name.values]]
        if cdf.shape[0] == 1:
            ta_rating[idx] = cdf['rating'].values[0]
            reviews[idx] = cdf['reviews'].values[0]
            city_rank[idx] = cdf['city_rank'].values[0]
            fee[idx] = cdf['fee'].values[0]
            visit_length[idx] = cdf['visit_length'].values[0]
            tag[idx] = cdf['tag'].values[0]

        elif cdf.shape[0] == 0:
            ta_rating[idx] = None
            reviews[idx] = None
            city_rank[idx] = None
            fee[idx] = None
            visit_length[idx] = None
            tag[idx] = None
        else:
            if df2.loc[idx]['name'] in cdf.name.values:
                for j in range(cdf.shape[0]):
                    if cdf.name.values[j] == df2.loc[idx]['name']:
                        ta_rating[idx] = cdf.rating.values[j]
                        reviews[idx] = cdf.reviews.values[j]
                        city_rank[idx] = cdf.city_rank.values[j]
                        fee[idx] = cdf.fee.values[j]
                        visit_length[idx] = cdf.visit_length.values[j]
                        tag[idx] = cdf.tag.values[j]
                        break
            else:
                ta_rating[idx] = -999
                reviews[idx] = -999
                city_rank[idx] = -999
                fee[idx] = -999
                visit_length[idx] = -999
                tag[idx] = -999
            
    return 
if __name__ == '__main__':
    data_path='/Users/zoesh/Desktop/travel_with_friends/poi_places.csv'
    data_path2='/Users/zoesh/Desktop/travel_with_friends/poi_process.csv'

    df = top_1000_cities(data_path)
    top_1000_cities_poi(df)


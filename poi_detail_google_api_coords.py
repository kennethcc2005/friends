import pandas as pd
import time
import numpy as np
import json
import simplejson
import urllib
import config
import ast
import bs4
import geocoder
import us_state_abbrevation as abb
from bs4 import BeautifulSoup as BS
from pymongo import MongoClient
import re
client = MongoClient()
db = client.zoeshrm
db.TripAdvisor

## import progressbar 

abb2state_dict = abb.abb2state
with open('api_key_list.config') as api_key_list_file:
    api_key_list = json.load(api_key_list_file)
api_key = api_key_list['api_key_list']
def poi_detail_web():    
    poi_detail_df = pd.read_csv('poi_detail_df.csv', index_col = 0)
    poi_detail_df.geo_content = poi_detail_df.geo_content.astype(str)
    print 'round1'
    cnt = 0
    i = 0
    for index in poi_detail_df.index:
        full_address = poi_detail_df.loc[index].address
        name = poi_detail_df.loc[index]['name']
        try:

            result_longlat = find_latlng(full_address, name, api_key[i])
            while result_longlat == False:
                i+=1
                print i, api_key[i]
                result_longlat = find_latlng(full_address, name, api_i)
        except:
            geo_error =1
            latitude, longitude, geo_content = None, None, None
        [latitude, longitude, geo_content] = result_longlat 
        poi_detail_df.set_value(index, 'coord_long', longitude)
        poi_detail_df.set_value(index, 'coord_lat', latitude)
        poi_detail_df.set_value(index, 'geo_content', geo_content)
        
        if cnt % 10 == 0:
            print cnt, name
        if cnt % 1000 == 0:
            poi_detail_df.to_csv('poi_detail_coords_%s.csv' %(cnt), index_col = None, encoding=('utf-8'))
        cnt+=1

    poi_detail_df.to_csv('poi_detail_df_coords.csv',encoding=('utf-8'))
    return poi_detail_df

def find_latlng(full_address, name, key):
    g_address = geocoder.google(full_address, key = key)
    if g_address.content['status'] == 'OVER_QUERY_LIMIT':
        return False
    if g_address.ok:
        latitude= g_address.lat
        longitude = g_address.lng
        return [latitude, longitude, g_address.content]
    
    g_name = geocoder.google(name, key = key)
    if g_name.content['status'] == 'OVER_QUERY_LIMIT':
        return False
    if g_name.ok:
        latitude= g_name.lat
        longitude = g_name.lng
        return [latitude, longitude, g_name.content]
    else:
        latitude = None
        longitude = None
        return [latitude, longitude, None]

if __name__ == '__main__':
    poi_pages = db.TripAdvisor.find()
    poi_detail_web()

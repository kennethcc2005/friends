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

def state_park_web(db_html):    

    poi_detail_state_park_df=pd.DataFrame(columns=['index','name','street_address','city','state_abb','state','postal_code','country','address','coord_lat','coord_long','num_reviews','review_score','ranking','tag','raw_visit_length','fee','description','url',"geo_content"])
    error_message_df = pd.DataFrame(columns=['index','name','url','state_abb_error', 'state_error','address_error','geo_error','review_error','score_error','ranking_error','tag_error']) 
    search_visit_length = re.compile('Recommended length of visit:')
    search_fee = re.compile('Fee:')
    cnt = 0
    name_lst = []
    full_address_lst = []
    api_i = 0
    for page in db_html[len(poi_detail_state_park_df):]:
        s = BS(page['html'], "html.parser")
        #index
        #name
        input_list, error_message = [],[]
        state_abb_error, state_error, address_error, geo_error, review_error, score_error, ranking_error, tag_error = 0,0,0,0,0,0,0,0
        latitude, longitude, geo_content = None, None, None
        #     print name
        url = page['url']
        name = s.find('h1', attrs = {'class':'heading_name'}).text.strip()

        #street_address
        street_address = s.find('span', attrs = {'class':'street-address'}).text.strip()
        #city
        city = s.find('span', attrs = {'property':'addressLocality'}).text.strip()
        #state
        state_abb = s.find('span', attrs = {'property':'addressRegion'}).text.strip()
        if state_abb:
            try:
                # state = state_abb_dict.keys()[state_abb_dict.values().index(state_abb)]
                state = abb2state_dict[state_abb]
            except:
                state_abb_error = 1
                state = state_abb
        else:
            state_error =1
            state_abb = None
            state = None
        #postal_code
        postal_code = s.find('span', attrs = {'property':'postalCode'}).text.strip()
        #country
        if s.find('span', attrs = {'property':'addressCountry'}).get('content'):
            country = s.find('span',{'property':'addressCountry'}).get('content')
        elif s.find('span',{'property':'addressCountry'}).get('content') == None:
            country = s.find('span',{'property':'addressCountry'}).text.strip()
        else:
            country = 'United States'
        #address
        if state:
            full_address = street_address+', '+city+', '+state+', '+postal_code[:5]+', '+country
        else:
            address_error =1
            full_address = street_address+', '+city+', '+postal_code[:5]+', '+country
        if (name in name_lst) and (full_address in full_address_lst):
            continue
        else:
            name_lst.append(name)
            full_address_lst.append(full_address)
        coord
        try:
            # latitude, longitude, geo_content = find_latlng(full_address, name, api_key)
            result_longlat = find_latlng(full_address, name, api_i)
            while result_longlat == False:
                api_i+=1
                result_longlat = find_latlng(full_address, name, api_i)
        except:
            geo_error =1
            latitude, longitude, geo_content = None, None, None
            
        [latitude, longitude, geo_content] = result_longlat
        #num_reviews
        try:
            num_reviews = s.find('div', attrs = {'class': 'rs rating'}).find('a').get('content')
            if num_reviews == None:
                num_reviews = s.find('a', {'property': "reviewCount"}).get('content')    
        except:
            num_reviews = 0
            review_error=1    
        #review_score
        try:
            review_score = s.find('div', attrs = {'class': 'heading_rating separator'}).find('img').get('content')
            if review_score == None:
                review_score = s.find('a', {'property': "ratingValue"}).get('content')
        except:
            review_score = 0 
            score_error =1
        #ranking
        try:
            ranking = s.find('b', attrs = {'class':'rank_text wrap'}).text.strip().replace('#',"")
        except:
            ranking = 999
            ranking_error=1
        #tag
        try:
            tags = ", ".join(label.text.strip() for label in s.select('div.detail > a') + s.select('span.collapse.hidden > a'))
        except:
            tags = None
            tag_error =1
        #visit_length
        if s.find('b', text =search_visit_length):
            raw_visit_length = s.find('b', text =search_visit_length).next_sibling.strip()
        else:
            raw_visit_length = None
        #fee
        if s.find('b', text= search_fee):
            fee = s.find('b',text= search_fee).next_sibling.strip()
        else:
            fee = 'Unknown'
        #description
        if s.find('div', attrs = {'class': "listing_details"}):
            description = s.find('div', attrs = {'class': "listing_details"}).text.strip()
        else:
            description = None
        error_message = [len(poi_detail_state_park_df), name, url,state_abb_error, state_error, address_error, geo_error, review_error, score_error, ranking_error, tag_error]
        error_message_df.loc[len(poi_detail_state_park_df)] =error_message


        input_list = [len(poi_detail_state_park_df), name, street_address, city, state_abb, state, postal_code, country, full_address, latitude, longitude, num_reviews, review_score, ranking, tags, raw_visit_length, fee, description, url, geo_content]
        poi_detail_state_park_df.loc[len(poi_detail_state_park_df)] = input_list
        
        print cnt, name
        cnt+=1
        if cnt % 100 == 0:
            poi_detail_state_park_df.to_csv('test_poi_detail_no_coords_%s.csv' %(cnt), index_col = None, encoding=('utf-8'))
            error_message_df.to_csv('test_poi_error_message_no_coords_%s.csv' %(cnt), index_col = None, encoding=('utf-8'))
        # time.sleep(1)
    poi_detail_state_park_df.to_csv('test_poi_detail_df.csv',encoding=('utf-8'))
    error_message_df.to_csv('test_poi_error_message_df.csv',encoding=('utf-8'))
    return poi_detail_state_park_df, error_message_df

def find_latlng(full_address, name, i):
    
    # api_key1 = 'AIzaSyCrgwS_L75NfO9qzIKG8L0ox7zGw81BpRU' #geocoder.google API only
    # api_key2 = 'AIzaSyBwh4WqOIVJGJuKkmzpQxlkjahgx6qzimk'
    # api_key3 = 'AIzaSyA25LW2CRcD9mSmiAWBYSPOSoiKP_m2plQ'
    # api_key4 = ''


    
    g_address = geocoder.google(full_address, key = api_key[i])
    if g_address.content['status'] == 'OVER_QUERY_LIMIT':
        return False
    if g_address.ok:
        latitude= g_address.lat
        longitude = g_address.lng
        return [latitude, longitude, g_address.content]
    
    g_name = geocoder.google(name, key = api_key[i])
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

    #error_message
    #state_abb_error : state_abb can not change to state name/ either state_abb is already state name or state_abb is not in United States
    #state_error : no state can be found
    #address_error : address that do not have state(not USA) or address is not complete
    #geo_error : geocoder api error, mainly due to over limit
    #review_error and score_error  ranking_error : can not get review/ score. either no one review or new style of website. 
    #tag_error : can not get tags. maybe different style of website or no tags on that location. (plz report error)
    #


    # save into cvs
    #
    # error_message_df.to_csv('error_message.csv', encoding=('utf-8'))
    # poi_detail_state_park.to_csv("poi_detail_state_park.csv", encoding=('utf-8'))
    # 
    # remove geo_content before input to sql, normal sql cannot handle geo_content (we take out and put into mongodb)
    # 
    # poi_additional_detail = poi_detail_state_park[['index','name','url','address','geo_content']]
    # geo_content_detail=poi_detail_state_park.pop('geo_content')
    # 
    # save into mongodb and sql
    # 
    # db.geo_content.insert_many(poi_additional_detail.to_dict('records'))
    # poi_detail_state_park.to_sql('poi_detail_state_park_table',engine, if_exists = "replace")


# def __init__ (self):
#     self.state_park_web = state_park_web()
if __name__ == '__main__':
    poi_pages = db.TripAdvisor.find()
    state_park_web(poi_pages)

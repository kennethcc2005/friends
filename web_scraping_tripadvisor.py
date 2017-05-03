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
from helpers import *
from math import cos, radians
import us_state_abbrevation as abb
from bs4 import BeautifulSoup as BS
from pymongo import MongoClient

import re
client = MongoClient()
db = client.zoeshrm
db.TripAdvisor

## import progressbar 

abb2state_dict = abb.abb2state
with open('api_key_list.config') as key_file:
    api_key_list = json.load(key_file)
api_key_list["goecoder_api_key_list"]


def state_park_web(db_html):    
    poi_detail_state_park_df=pd.DataFrame(columns=['index','name','street_address','city', 'county','state_abb','state','postal_code','country','address','coord_lat','coord_long','num_reviews','review_score','ranking','tag','raw_visit_length','fee','description','url',"geo_content", "adjusted_visit_length", "area"])
    error_message_df = pd.DataFrame(columns=['index','name','url','state_abb_error', 'state_error','address_error','geo_error','review_error','score_error','ranking_error','tag_error','county_error']) 
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
        state_abb_error, state_error, address_error, geo_error, review_error, score_error, ranking_error, tag_error, county_error = 0,0,0,0,0,0,0,0,0
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
        # if (name in name_lst) and (full_address in full_address_lst):
        #     continue
        # else:
        #     name_lst.append(name)
        #     full_address_lst.append(full_address)

        #geo 
        
        try:
            # latitude, longitude, geo_content = find_latlng(full_address, name, api_key)
            result_longlat = find_latlng(full_address, name, api_i)
            while result_longlat == False:
                api_i+=1
                result_longlat = find_latlng(full_address, name, api_i)
        except:
            geo_error =1
            latitude, longitude, county, geo_content = None, None, None, None
            
        [latitude, longitude, county ,bbox, geo_content] = result_longlat


        # county
        if county == None:
            try:
                county = find_county(state, city)
            except:
                county_error =1

        #num_reviews
        try:
            num_reviews = s.find('div', attrs = {'class': 'rs rating'}).find('a').get('content')
            if not num_reviews:
                num_reviews = 0
        except:
            try:
                num_reviews = s.find('a', {'property': "reviewCount"}).get('content')
                if not num_reviews:
                    num_reviews = 0
            except:
                num_reviews = 0
                review_error=1 
        #review_score
        try:
            review_score = s.find('div', attrs = {'class': 'heading_rating separator'}).find('img').get('content')
            if not review_score:
                review_score =0
        except:
            try:
                review_score = s.find('span', {'property': "ratingValue"}).get('content')
                if not review_score:
                    review_score =0
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
            adjusted_time = raw_to_adjust_time(raw_visit_length)
        else:
            raw_visit_length = None
            adjusted_time = None


        #area to determine the time spent on poi
        if bbox !=None:
            area = find_area(bbox)
            if adjusted_time ==None:
                adjusted_time == area_to_adjust_time(area)


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
        adjusted_time = raw_to_adjust_time(raw_visit_length)

        error_message = [len(poi_detail_state_park_df), name, url,state_abb_error, state_error, address_error, geo_error, review_error, score_error, ranking_error, tag_error, county_error]
        error_message_df.loc[len(poi_detail_state_park_df)] =error_message

        input_list = [len(poi_detail_state_park_df), name, street_address, city, county, state_abb, state, postal_code, country, full_address, latitude, longitude, num_reviews, review_score, ranking, tags, raw_visit_length, fee, description, url, geo_content, adjusted_time, area]
        poi_detail_state_park_df.loc[len(poi_detail_state_park_df)] = input_list
        
    #     print cnt, name
    #     if cnt % 1000 == 0:
    #         poi_detail_state_park_df.to_csv('poi_detail_no_coords_%s.csv' %(cnt), index_col = None, encoding=('utf-8'))
    #         error_message_df.to_csv('poi_error_message_no_coords_%s.csv' %(cnt), index_col = None, encoding=('utf-8'))
    #     # time.sleep(1)
    #     cnt+=1

    # poi_detail_state_park_df.to_csv('poi_detail_state_park_df3.csv',encoding=('utf-8'))
    # error_message_df.to_csv('poi_error_message__state_park_df3.csv',encoding=('utf-8'))
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
        county= g_address.county.replace("County","").upper().encode('utf-8').strip()
        return [g_address.lat, g_address.lng, county ,g_address.bbox ,g_address.content]
    
    g_name = geocoder.google(name, key = api_key[i])
    if g_name.content['status'] == 'OVER_QUERY_LIMIT':
        return False
    if g_name.ok:
        county= g_name.county.replace("County","").upper().encode('utf-8').strip()
        return [g_name.lat, g_name.lng, county, g_name.bbox, g_name.content]
    else:
        return [None, None, None, None]


def find_area(box):
#     to make thing simple, we use 111.111 
#     we assume the distance:
#     Latitude: 1 deg = 110.574 km
#     Longitude: 1 deg = 111.320*cos(latitude) km
#     if we need more accuracy number, we need to use different approach.
#     ex. using Shapely to calculate polygon/ WGS84 formula
    lat = (box["southwest"][0]-box["northeast"][0])*110.574
    lng = 111.320*cos(radians(box["southwest"][1]-box["northeast"][1]))
    return abs(lat*lng)

def request_s(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    r=requests.get(url,headers=headers)
    s = BS(r.text, 'html.parser')
    return s
def thing_to_do_in_national_park(s):
    thing_to_do = pd.DataFrame(columns=["national_park_name","activate_name","url","num_reviews","score","ranking","tags"])
    national_park_name = s.find('h1', {"id": "HEADING"}).text.strip('\n').replace("Things to Do in ","")
    print "park name: ",national_park_name
    for activate in s.findAll('div', {"class":"listing_title"}):
        activate_name = activate.text.strip()
        url ="https://www.tripadvisor.com"+ activate.find('a').get("href")
        if activate.find_next('div', {"class":"rs rating"}) ==None:
            score, num_reviews = 0, 0
        else:
            score = activate.find_next('div', {"class":"rs rating"}).find('span').get('alt').replace(" of 5 bubbles","")
            num_reviews = activate.find_next('div', {"class":"rs rating"}).find('span', {'class': "more"}).text.strip().replace("reviews","")
        ranking = activate.find_next('div', {'class':"popRanking wrap"}).text.strip().replace("#","")[0]
        if activate.find_next('div',{'class':"tag_line"}).find('span') == None:
            tags = None
        else:
            tags = activate.find_next('div',{'class':"tag_line"}).find('span').text
        list_thing = [national_park_name, activate_name, url, num_reviews, score, ranking, tags]
        thing_to_do.loc[len(thing_to_do)] = list_thing
    return thing_to_do


def wiki_table(s):
    #s is webpage in html
    name, state =None, None
    table =  s.find('table', {"class" : "wikitable"})
    # col_name =  [x.text for x in table.findAll("th",{"scope":"col"})]
    # num_col = len(col_name)

    # wiki_table= pd.DataFrame(columns=col_name)
    df = pd.DataFrame(columns = ["name","state","description"])
    for row in table.findAll("tr")[1:]:
        if row.find('th', {'scope':"row"}) != None:
            name = row.find('th', {'scope':"row"}).next_element.get('title')
        cells = row.findAll("td")
        #For each "tr", assign each "td" to a variable.
        #have 6 columns, we only need 1,5 (state, description)
        if len(cells) == 6:
            state = cells[1].find(text=True)

            des = str("".join(cells[5].findAll(text=True)).encode('utf8'))
            description = re.sub(r"\[\d+\]","",des)

    df.loc[len(df)] = [name, state, description]
    return df

def raw_to_adjust_time(raw):
    adjusted_time =0
    if raw == "1-2 hours":
        adjusted_time = 120
    if raw == "2-3 hours":
        adjusted_time = 180
    if raw == "More than 3 hours":
        adjusted_time = 360
    if raw == "<1 hour":
        adjusted_time = 60
    return adjusted_time

def area_to_adjust_time(area):

    if area<34:
        adjusted_time =  60
    elif area<500:
        adjusted_time = 120
    elif area<2000:
        adjusted_time = 180
    else:
        adjusted_time = 240
    return adjusted_time


    #error_message
    #state_abb_error : state_abb can not change to state name/ either state_abb is already state name or state_abb is not in United States
    #state_error : no state can be found
    #address_error : address that do not have state(not USA) or address is not complete
    #geo_error : geocoder api error, mainly due to over limit
    #review_error and score_error  ranking_error : can not get review/ score. either no one review or new style of website. 
    #tag_error : can not get tags. maybe different style of website or no tags on that location. (plz report error)
    # save into cvs
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

if __name__ == '__main__':
    poi_pages = db.TripAdvisor.find()
    state_park_web(poi_pages)

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


## import progressbar 

state_abb_dict = abb.state2abb

def state_park_web(db_html):    
    poi_detail_state_park_df=pd.DataFrame(columns=['index','name','street_address','city','state_abb','state','postal_code','country','address','coord_lat','coord_long','num_reviews','review_score','ranking','tag','visit_length','fee','description','url',"geo_content"])
    error_message_df = pd.DataFrame(columns=['index','name','url','state_abb_error','address_error','geo_error','review_error','score_error','ranking_error','tag_error']) 

    for page in db_html[len(poi_detail_state_park_df):]:
        s = BS(page['html'], "html.parser")
        #index
        #name
        error_message = []
        state_abb_error, address_error, geo_error, review_error, score_error, ranking_error, tag_error = 0,0,0,0,0,0,0
        input_list = []
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
                state = state_abb_dict.keys()[state_abb_dict.values().index(state_abb)]
            except:
                state_abb_error = 1
                state = state_abb
        else:
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
        if state_abb:
            full_address = street_address+', '+city+', '+state_abb+', '+postal_code[:5]+', '+country
        else:
            address_error =1
            full_address = street_address+', '+city+', '+postal_code[:5]+', '+country

        #coord
        try:
            latitude, longitude, geo_content = find_latlng(full_address, name)
        except:
            geo_error =1
            latitude, longitude, geo_content = None, None, None
            break
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
        if s.find(text ="Recommended length of visit:"):
            visit_length = s.find(text ="Recommended length of visit:").parent.next_sibling
        else:
            visit_length = None
        #fee
        if s.find(text= "Fee:"):
            fee = s.find(text= "Fee:").parent.next_sibling.upper()
        else:
            fee = 'NO'
        #description
        if s.find('div', attrs = {'class': "listing_details"}):
            description = s.find('div', attrs = {'class': "listing_details"}).text.strip()
        else:
            description = None

        input_list = [len(poi_detail_state_park_df), name, street_address, city, state_abb, state, postal_code, country, full_address, latitude, longitude, num_reviews, review_score, ranking, tags, visit_length, fee, description, url, geo_content]
        poi_detail_state_park_df.loc[len(poi_detail_state_park_df)] = input_list
        
        error_message = [len(poi_detail_state_park_df), name, url,state_abb_error, address_error, geo_error, review_error, score_error, ranking_error, tag_error]
        error_message_df.loc[len(poi_detail_state_park_df)] =error_message
        time.sleep(1)
    return poi_detail_state_park, error_message_df 



    #error_message
    #state_abb_error : state_abb can not change to state name/ either state_abb is already state name or state_abb is not in United States
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






import pandas as pd
import re
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
db_cilent = MongoClient()
db = db_cilent['zoeshrm']
table2 = db['Places']

old_df = pd.read_csv('poi_process.csv')
df = pd.DataFrame(columns=['name','city','state','rating', 'reviews', 'city_rank','fee','visit_length', 'tag'])
city = "Chicago, Illinois"
counter = 0
for city in cities['city_state']:
    for doc in db.TripAdvisor.find({"city": city}):
        city_poi = BS(doc['html'], 'html.parser')
        head_name = city_poi.find('h1', attrs = {'class':'heading_name'}).text.strip()
        if head_name not in old_df.name:
            city_rank = city_poi.find('b', attrs = {'class':'rank_text wrap'}).text.strip().replace('#',"")
            if None == city_poi.find('div', attrs = {'class': 'heading_rating separator'}).find('img'):
                continue
            rating = city_poi.find('div', attrs = {'class': 'heading_rating separator'}).find('img').get('content')
            reviews = city_poi.find('div', attrs = {'class': 'rs rating'}).find('a').get('content')
            neighborhood = city_poi.find('div', attrs = {'class': 'heading_details'})\
                            .find_all('div', attrs = {'class':'detail'})
            neighborhood_0 = neighborhood[0].text.split(',')[0].strip()
            if not len(neighborhood) > 2:
                tag = neighborhood_0
            else:
                tag = neighborhood[2].text.split(',')[0].strip()
            try:
                fee = city_poi.find('div', attrs = {'class': 'detail_section details'})\
                    .find_all('div', attrs ={'class':'detail'} )[-1].text.strip().split('\n')[-1].strip()
                if not "Yes" in fee and not "No" in fee:
                    fee = "No"
                visit_length = city_poi.find_all('div', attrs = {'class':'detail_section details'})[0]\
                            .find('div', attrs = {'class':'detail'})\
                            .text.strip().split('\n')[-1].strip()
            except:
                fee = 'No'
                visit_length = '15 min'
            df = df.append({'name': re.sub(u"(\u2018|\u2019)", "'", head_name), 'city': re.sub(u"(\u2018|\u2019)", "'", city.split(', ')[0]), \
                            'state': re.sub(u"(\u2018|\u2019)", "'", city.split(', ')[1]), 'rating': re.sub(u"(\u2018|\u2019)", "'", rating),\
                           'reviews': re.sub(u"(\u2018|\u2019)", "'", reviews), 'city_rank': re.sub(u"(\u2018|\u2019)", "'", city_rank), \
                            'fee': re.sub(u"(\u2018|\u2019)", "'", fee), \
                            'visit_length': re.sub(u"(\u2018|\u2019)", "'", visit_length), 'tag':re.sub(u"(\u2018|\u2019)", "'", tag)}, ignore_index=True)
    print df.shape, city
    counter+=1
    if counter % 20 == 0:
        df.to_csv('poi_process.csv')

df = df.drop_duplicates()

df2 =  pd.DataFrame(list(table2.find()))
df2['Name'] = [i['title'] for i in df2.properties]
df2['City'] = [i.split(', ')[0] for i in df2.city]
df2['State'] = [i.split(', ')[1] for i in df2.city]
df2['Coord0'] = [i['coordinates'][0] for i in df2.geometry]
df2['Coord1'] = [i['coordinates'][1] for i in df2.geometry]
df2['POI_rank'] = [i['rank'] for i in df2.properties]
df2['img_url'] = [i['thumbnail_url'] for i in df2.properties]
df2 = df2.drop(['_id','city','geometry','properties'],axis=1)
df2.columns = [i.lower() for i in df2.columns.values]
df2.to_csv('poi_places.csv')

idx = 0
ta_rating = np.zeros(df2.shape[0])
reviews = np.zeros(df2.shape[0])
city_rank = np.zeros(df2.shape[0])
fee = np.chararray(df2.shape[0],itemsize=20)
visit_length = np.chararray(df2.shape[0],itemsize=20)
tag = np.chararray(df2.shape[0],itemsize=40)
for idx in range(df2.shape[0]):
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

df3 = df2.copy()
df3['rating'] = ta_rating
df3['reviews'] = reviews
df3['city_rank'] = city_rank
df3['fee'] = fee
df3['visit_length'] = visit_length
df3['tag'] = tag
df3 = df3.drop_duplicates()
df3.to_csv('step2_poi.csv')

normal_trip_min = np.chararray(df3.shape[0],itemsize=20)
fast_trip_min = np.chararray(df3.shape[0],itemsize=20)
for i,v in enumerate(df3.google_time_spent_txt.values):
    if v:
        if ('hour' in v):
            normal_trip_min[i] = v.split(' ')[-2]
            if '-' in normal_trip_min[i]:
                fast_trip_min[i] = float(normal_trip_min[i].split('-')[0])*60
                normal_trip_min[i] = float(normal_trip_min[i].split('-')[-1])*60
            else:
                fast_trip_min[i] = float(normal_trip_min[i])*60/2
                normal_trip_min[i] = float(normal_trip_min[i])*60
        elif 'hr' in v:
            
            normal_trip_min[i] = float(v.split(' ')[-2])*60
            if 'min' not in v:
                fast_trip_min[i] = float(v.split(' ')[0])*60
            else:
                fast_trip_min[i] = float(v.split(' ')[0])
        else:
            normal_trip_min[i] = v.split(' ')[-2]
            
            if '-' in v:
                normal_trip_min[i] = float(normal_trip_min[i].split('-')[-1])
                fast_trip_min[i] = float(normal_trip_min[i].split('-')[-1])
            else:
                fast_trip_min[i] = float(v.split(' ')[-2])/2
        if float(normal_trip_min[i]) < 15:
            normal_trip_min[i] = 15
        elif float(normal_trip_min[i]) < 30:
            normal_trip_min[i] = 30
        if float(fast_trip_min[i]) < 15:
            fast_trip_min[i] = 15
        elif float(fast_trip_min[i]) < 30:
            fast_trip_min[i] = 30
    else:
        fast_trip_min[i] = v
        normal_trip_min[i] = v
    
    
df3['google_normal_min'] = normal_trip_min
df3['google_fast_min'] = fast_trip_min

tripadvisor_normal_min = np.chararray(df3.shape[0],itemsize=20)
tripadvisor_fast_min =  np.chararray(df3.shape[0],itemsize=20)
for i,v in enumerate(df3.visit_length.values):
    if v != 'None':
        if v == 'More than 3 hours':
            tripadvisor_normal_min[i] = 5*60
            tripadvisor_fast_min[i] = 3*60
        elif 'hour' in v:
            if '-' in v:
                tripadvisor_normal_min[i] = float(v.split(' ')[-2].split('-')[-1])*60
                tripadvisor_fast_min[i] = float(v.split(' ')[-2].split('-')[-2])*60
            else:
                tripadvisor_normal_min[i] = 60
                tripadvisor_fast_min[i] = 30
        else:
            tripadvisor_normal_min[i] = 15
            tripadvisor_fast_min[i] = 15
    else:
        tripadvisor_normal_min[i] = None
        tripadvisor_fast_min[i] = None
        
df3['tripadvisor_fast_min'] = tripadvisor_fast_min
df3['tripadvisor_normal_min'] = tripadvisor_normal_min
df3.to_csv('step3_poi.csv')


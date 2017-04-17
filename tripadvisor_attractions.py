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
import pickle

db_cilent = MongoClient()
db = db_cilent['zoeshrm']
# table = db['TripAdvisor']
table = db['TripAdvisor_state_park']

us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY',
    'District of Columbia':'DC',
}

def createKey(city, state):
    return city.upper() + ":" + state.upper()

def city_poi(city,state):
    urlCity = city.replace(' ','+')
    urlState = us_state_abbrev[state]
    key = createKey(urlCity, urlState)
    baseUrl = "http://www.tripadvisor.com"
    citySearchUrl = baseUrl+"/Search?q="+urlCity+"%2C+"+urlState+"&sub-search=SEARCH&geo=&returnTo=__2F__#&ssrc=g&o=0"
    r = requests.get(citySearchUrl)
    if r.status_code != 200:
        print 'WARNING: ', city, ', ',state, r.status_code
    else:
        s = BS(r.text, 'html.parser')
        # print citySearchUrl, s
        for item in s.find('div',attrs = {'class':'info geo-info'}):
            if 'Things to do' in item.text:
                attrsUrl = item.find('a').attrs['href']
                fullUrl = baseUrl + attrsUrl
        responses = requests.get(fullUrl)
        if responses.status_code != 200:
            print 'WARNING: ', city, ', ',state, r.status_code
        else:
            soup = BS(responses.text, 'html.parser')
            property_titles = soup.find_all('div', attrs = {'class':'property_title'})
            url_list = []
            for property_url in property_titles: 
                poi_url = baseUrl + property_url.find('a').attrs['href']
                # print poi_url
                url_list.append(poi_url)
                # poi_details(poi_url)
            return url_list
        

def poi_details(poi_url,city):
    try:
        r = requests.get(poi_url)
    except:
        print 'too fast, take 5 min break'
        time.sleep(5*60)
        r = requests.get(poi_url)
    if r.status_code != 200:
        print 'WARNING: ', poi_url, r.status_code
    else:
        s = BS(r.text, 'html.parser')
        try:
            table.insert({'url':poi_url,
                        'city': city,
                        'html': s.decode('utf8')
                })
        except DuplicateKeyError:
            print 'DUPS!'
   
def state_park_details(poi_url):
    try:
        r = requests.get(poi_url)
    except:
        print 'too fast, take 5 min break'
        time.sleep(5*60)
        r = requests.get(poi_url)
    if r.status_code != 200:
        print 'WARNING: ', poi_url, r.status_code
    else:
        s = BS(r.text, 'html.parser')
        try:
            table.insert({'url':poi_url,
                        'html': s.decode('utf8')
                })
        except DuplicateKeyError:
            print 'DUPS!'


def top_1000_cities(data_path):
    df = pd.read_csv(data_path)
    return df

def top_1000_cities_poi(df):
    df['search_city'] = df.city + ', ' + df.state
    my_list = []
    for city in df.search_city:
        print city.split(', ')[0],city.split(', ')[1]
        time.sleep(10)
        try:
            for poi_url in city_poi(city.split(', ')[0],city.split(', ')[1]):
                time.sleep(10)
                if 'http://www.tripadvisor.com/Attraction_Review' in poi_url:
                    poi_details(poi_url,city)
                    my_list.append(poi_url)
                
            print city, ' DONE!'
        except: 
            print 'WARNING: ', city, 'No Attractions Return'
    with open('outfile', 'wb') as fp:
        pickle.dump(my_list, fp)

if __name__ == '__main__':
    # data_path='/Users/zoesh/Desktop/travel_with_friends/top_1000_us_cities.csv'
    # df = top_1000_cities(data_path)
    # top_1000_cities_poi(df)
    for poi_url in url_list:
        state_park_details(poi_url)

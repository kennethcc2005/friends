my_key = 'AIzaSyDMbpmHBLl7dTOXUOMZP7Vi3zbMJlByEKM'
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
table = db['Places']

def city_poi(city):
    geolocator = Nominatim()
    try:
        location = geolocator.geocode(city)
    except:
        print 'too fast, take 5 min break'
        time.sleep(5*60)
        location = geolocator.geocode(city)
    x1,x2,y1,y2 = location.raw['boundingbox']
    base_url = 'http://www.pointsonamap.com/search?bounds=%s,%s,%s,%s' %(str(x1),str(y1),str(x2),str(y2))
    r = requests.get(base_url)
    if r.status_code != 200:
        print 'WARNING: ', city, r.status_code
    else:
        data = json.loads(r.text)
        return data['features']

def top_1000_cities(data_path):
    df = pd.read_csv(data_path)
    return df

def time_spent_txt(poi):
    poi_name = poi['properties']['title']
    poi_name = poi_name.replace(' ', '+')
    baseurl = 'https://www.google.com/search?q=%s' %(poi_name)
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    r = requests.get(baseurl,headers=headers)
    if r.status_code != 200:
        print 'WARNING: ', poi_name, r.status_code
    else:
        s = BS(r.text, 'html.parser')
        try:
            time_spent=  s.find("div", attrs={"class": "_OKe"}).find('div',attrs={'class':'_B1k'}).find('b').text
            return time_spent
        except:
            return None

def top_1000_cities_poi(df):
    df['search_city'] = df.city + ', ' + df.state
    for city in df.search_city:
        for data in city_poi(city):
            data['city'] = city
            data['google_time_spent_txt'] = time_spent_txt(data)
            try:
                table.insert(data)
            except DuplicateKeyError:
                print 'DUPS!'
        print city, ' DONE!'

if __name__ == '__main__':
    data_path='/Users/zoesh/Desktop/travel_with_friends/top_1000_us_cities.csv'
    df = top_1000_cities(data_path)
    top_1000_cities_poi(df)
# baseurl = 'https://www.google.com/search?q=ice+bar+stockholm'
# headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
# r = requests.get(baseurl,headers=headers)
# s = BS(r.text, 'html.parser')
# # soup_class ="_kLl _R1o"
# stay_length =  s.find("div", attrs={"class": "_OKe"}).find('div',attrs={'class':'_B1k'}).find('b')
# print stay_length.text


# YOUR_API_KEY = 'AIzaSyDMbpmHBLl7dTOXUOMZP7Vi3zbMJlByEKM'

# google_places = GooglePlaces(YOUR_API_KEY)

# # You may prefer to use the text_search API, instead.
# query_result = google_places.nearby_search(
#         location='New York, United States', keyword='New York Public Library',
#         radius=20000)
# If types param contains only 1 item the request to Google Places API
# will be send as type param to fullfil:
# http://googlegeodevelopers.blogspot.com.au/2016/02/changes-and-quality-improvements-in_16.html

# if query_result.has_attributions:
#     print query_result.html_attributions


# for place in query_result.places:
#     # Returned places from a query are place summaries.
#     print place.name
#     print place.geo_location
#     print place.place_id

#     # The following method has to make a further API call.
#     place.get_details()
#     # Referencing any of the attributes below, prior to making a call to
#     # get_details() will raise a googleplaces.GooglePlacesAttributeError.
#     print place.details # A dict matching the JSON response from Google.
# #     print place.local_phone_number
# #     print place.international_phone_number
# #     print place.website
# #     print place.url

#     # Getting place photos

# #     for photo in place.photos:
# #         # 'maxheight' or 'maxwidth' is required
# #         photo.get(maxheight=500, maxwidth=500)
# #         # MIME-type, e.g. 'image/jpeg'
# #         photo.mimetype
# #         # Image URL
# #         photo.url
# #         # Original filename (optional)
# #         photo.filename
# #         # Raw image data
# #         photo.data


# # Are there any additional pages of results?
# if query_result.has_next_page_token:
#     query_result_next_page = google_places.nearby_search(
#             pagetoken=query_result.next_page_token)


# # Adding and deleting a place
# try:
#     added_place = google_places.add_place(name='Mom and Pop local store',
#             lat_lng={'lat': 51.501984, 'lng': -0.141792},
#             accuracy=100,
#             types=types.TYPE_HOME_GOODS_STORE,
#             language=lang.ENGLISH_GREAT_BRITAIN)
#     print added_place.place_id # The Google Places identifier - Important!
#     print added_place.id

#     # Delete the place that you've just added.
#     google_places.delete_place(added_place.place_id)
# except GooglePlacesError as error_detail:
#     # You've passed in parameter values that the Places API doesn't like..
#     print error_detail


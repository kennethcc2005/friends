from restaurant_db import Restaurant
import argparse
import pprint
import requests
import sys
import urllib
import json
from urllib2 import HTTPError
from urllib import quote
from urllib import urlencode
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, CollectionInvalid
import datetime

# Define the MongoDB database and table
db_cilent = MongoClient()
db = db_cilent['zoeshrm']
table = db['Restaurant']
Base = declarative_base()
# OAuth credential placeholders that must be filled in by users.
# You can find them on
# https://www.yelp.com/developers/v3/manage_app
CLIENT_ID = 'ikQEq0n6teM1C3uBtScgmw'
CLIENT_SECRET = 'y8O5CIwHYUsxBLMuj6GpWGGfTd3oh17z8DNcmdhHTUCZ4tidOIgJOfmKj5bbDP48'


# API constants, you shouldn't have to change these.
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.
TOKEN_PATH = '/oauth2/token'
GRANT_TYPE = 'client_credentials'


# Defaults for our simple example.
DEFAULT_TERM = 'yolk'
DEFAULT_LOCATION = 'chicago, il'
SEARCH_LIMIT = 3


def obtain_bearer_token(host, path):
    """Given a bearer token, send a GET request to the API.
    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        url_params (dict): An optional set of query parameters in the request.
    Returns:
        str: OAuth bearer token, obtained using client_id and client_secret.
    Raises:
        HTTPError: An error occurs from the HTTP request.
    """
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    data = urlencode({
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': GRANT_TYPE,
    })
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
    }
    response = requests.request('POST', url, data=data, headers=headers)
    bearer_token = response.json()['access_token']
    return bearer_token


def request(host, path, bearer_token, url_params=None):
    """Given a bearer token, send a GET request to the API.
    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        bearer_token (str): OAuth bearer token, obtained using client_id and client_secret.
        url_params (dict): An optional set of query parameters in the request.
    Returns:
        dict: The JSON response from the request.
    Raises:
        HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % bearer_token,
    }

    print(u'Querying {0} ...'.format(url))

    response = requests.request('GET', url, headers=headers, params=url_params)

    return response.json()


def search(bearer_token, term, location, offset = None, SEARCH_LIMIT = 3):
    """Query the Search API by a search term and location.
    Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.
    Returns:
        dict: The JSON response from the request.
    """
    #'limit': SEARCH_LIMIT,
    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
        'limit': None,
        'offset':offset
    }
    return request(API_HOST, SEARCH_PATH, bearer_token, url_params=url_params)


def get_business(bearer_token, business_id):
    """Query the Business API by a business ID.
    Args:
        business_id (str): The ID of the business to query.
    Returns:
        dict: The JSON response from the request.
    """
    business_path = BUSINESS_PATH + business_id

    return request(API_HOST, business_path, bearer_token)


def query_api(term, location):
    """Queries the API by the input values from the user.
    Args:
        term (str): The search term to query.
        location (str): The location of the business to query.
    """
    bearer_token = obtain_bearer_token(API_HOST, TOKEN_PATH)

    response = search(bearer_token, term, location)

    businesses = response.get('businesses')

    if not businesses:
        print(u'No businesses for {0} in {1} found.'.format(term, location))
        return

    business_id = businesses[0]['id']

    print(u'{0} businesses found, querying business info ' \
        'for the top result "{1}" ...'.format(
            len(businesses), business_id))
    response = get_business(bearer_token, business_id)

    print(u'Result for business "{0}" found:'.format(business_id))
    pprint.pprint(response, indent=2)
    dict_list = []
    for i in response:
        dict_list.append(i)
    print dict_list

def connect_db():
    engine = create_engine("postgres://localhost/zoeshrm")
    if not database_exists(engine.url):
        create_database(engine.url)
    print(database_exists(engine.url))
    Base.metadata.create_all(engine)

    Base.metadata.bind = engine
 
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    return session

def load_restaurants(city):
    """Get all restaurants for a city from Yelp and load restaurants into database."""
    session = connect_db()
    # Start offset at 0 to return the first 20 results from Yelp API request
    offset = 0

    # Get total number of restaurants for this city
    bearer_token = obtain_bearer_token(API_HOST, TOKEN_PATH)
    result_len = 20
    
    # Get all restaurants for a city and load each restaurant into the database
    # Note: Yelp has a limitation of 1000 for accessible results, so get total results
    # if less than 1000 or get only 1000 results back even if there should be more
    while (1000 > offset) and (result_len==20):
        results = search(bearer_token, 'restaurant', city, offset)
        result_len = len(results['businesses'])

        # API response returns a SearchResponse object with accessible attributes
        # response.businesses returns a list of business objects with further attributes
        for business in results['businesses']:
            biz = get_business(bearer_token, business['id'])
            try:
                table.insert(biz)
            except DuplicateKeyError:
                print 'DUPS!'

            hour_start_monday = None
            hour_end_monday = None           
            hour_start_tuesday = None
            hour_end_tuesday = None
            hour_start_wednesday = None
            hour_end_wednesday = None 
            hour_start_thursday = None
            hour_end_thursday = None            
            hour_start_friday = None
            hour_end_friday = None            
            hour_start_saturday = None
            hour_end_saturday = None            
            hour_start_sunday = None
            hour_end_sunday = None
            try:
                yelp_price_level = biz['price']
            except:
                yelp_price_level = None
            try:
                hours_type = biz['hours'][0]['hours_type']
                is_open_now = biz['hours'][0]['is_open_now']
                for item in biz['hours'][0]['open']:
                    if item['day'] == 1:
                        hour_start_tuesday = item['start']
                        hour_end_tuesday = item['end']
                    elif item['day'] == 0:
                        hour_start_monday = item['start']
                        hour_end_monday = item['end']
                    elif item['day'] == 2:
                        hour_start_wednesday = item['start']
                        hour_end_wednesday = item['end']
                    elif item['day'] == 3:
                        hour_start_thursday = item['start']
                        hour_end_thursday = item['end']
                    elif item['day'] == 4:
                        hour_start_friday = item['start']
                        hour_end_friday = item['end']
                    elif item['day'] == 5:
                        hour_start_saturday = item['start']
                        hour_end_saturday = item['end']
                    elif item['day'] == 6:
                        hour_start_sunday = item['start']
                        hour_end_sunday = item['end']
            except:
                hours_type = None
                is_open_now = None
                hour_start_monday = None
                hour_end_monday = None           
                hour_start_tuesday = None
                hour_end_tuesday = None
                hour_start_wednesday = None
                hour_end_wednesday = None 
                hour_start_thursday = None
                hour_end_thursday = None            
                hour_start_friday = None
                hour_end_friday = None            
                hour_start_saturday = None
                hour_end_saturday = None            
                hour_start_sunday = None
                hour_end_sunday = None
            restaurant = Restaurant(
                                    yelp_id = business['id'],
                                    yelp_rating = biz['rating'],
                                    yelp_review_count = biz['review_count'],
                                    name =  biz['name'],
                                    phone = biz['phone'],
                                    yelp_url = biz['url'],
                                    yelp_price_level = yelp_price_level,
                                    latitude = biz['coordinates']['latitude'],
                                    longitude = biz['coordinates']['longitude'],
                                    hours_type = hours_type,
                                    is_open_now = is_open_now,
                                    hour_start_monday = hour_start_monday,
                                    hour_end_monday = hour_end_monday,
                                    hour_start_tuesday = hour_start_tuesday,
                                    hour_end_tuesday = hour_end_tuesday,
                                    hour_start_wednesday = hour_start_wednesday,
                                    hour_end_wednesday = hour_end_wednesday, 
                                    hour_start_thursday = hour_start_thursday,
                                    hour_end_thursday = hour_end_thursday,            
                                    hour_start_friday = hour_start_friday,
                                    hour_end_friday = hour_end_friday,            
                                    hour_start_saturday = hour_start_saturday,
                                    hour_end_saturday = hour_end_saturday,            
                                    hour_start_sunday = hour_start_sunday,
                                    hour_end_sunday = hour_end_sunday, 
                                    is_closed = biz['is_closed'],
                                    categories = biz['categories'][0]['alias'],
                                    display_phone = biz['display_phone'],
                                    location = ' '.join(biz['location']['display_address']),
                                    location_city = biz['location']['city'],
                                    location_state = biz['location']['state'],
                                    location_zip_code = biz['location']['zip_code'],
                                    location_city_id = biz['location']['city'] + ', ' + biz['location']['state'])
            session.merge(restaurant)
        # Yelp returns only 20 results each time, so need to offset by 20 while iterating
        offset += 20
        print('current offset: ', offset)
        session.commit()

def main():

    try:
        # query_api(input_values.term, input_values.location)
        # query_api(DEFAULT_TERM,DEFAULT_LOCATION)
        bearer_token = obtain_bearer_token(API_HOST, TOKEN_PATH)
        # test_search = search(bearer_token, 'restaurant', 'chicago')
        # print test_search['businesses'][0]
        # pprint.pprint(test_search['businesses'][0], indent=2)
        # business = test_search['businesses'][0]
        # biz_term = business['id']
        # pprint.pprint(get_business(bearer_token, biz_term),indent=2)
        load_restaurants('chicago')
    except HTTPError as error:
        sys.exit(
            'Encountered HTTP error {0} on {1}:\n {2}\nAbort program.'.format(
                error.code,
                error.url,
                error.read(),
            )
        )


if __name__ == '__main__':
    main()
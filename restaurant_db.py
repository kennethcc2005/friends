"""Models and database functions."""
import datetime

# from sqlalchemy_searchable import make_searchable
# from sqlalchemy_utils.types import TSVectorType

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)
# db = SQLAlchemy()

from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

Base = declarative_base()
 
##############################################################################
# Model definitions
class Restaurant(Base):
    """Restaurant on website."""

    __tablename__ = "restaurants"

    [u'is_claimed', u'rating', u'review_count', u'name', u'phone', u'url', 
     u'price', u'coordinates', u'hours', u'photos', u'image_url', u'categories', 
     u'display_phone', u'id', u'is_closed', u'location']
    
    restaurant_id = Column(Integer, autoincrement=True, primary_key = True)
    yelp_id = Column(String(150), primary_key = True, nullable=False)
    yelp_rating = Column(Numeric, nullable=True)
    yelp_review_count = Column(Integer, nullable=True)
    name = Column(String(150), nullable=False)
    phone = Column(String(20), nullable=True)
    yelp_url = Column(String(400), nullable=True)
    yelp_price_level = Column(String(10), nullable=True)
    latitude = Column(Numeric, nullable=True)
    longitude = Column(Numeric, nullable=True)
    hours_type = Column(String(20), nullable=True)
    is_open_now = Column(Boolean(), nullable=True) 
    hour_start_monday = Column(String(20), nullable=True)
    hour_end_monday = Column(String(20), nullable=True)
    hour_start_tuesday = Column(String(20), nullable=True)
    hour_end_tuesday = Column(String(20), nullable=True)    
    hour_start_wednesday = Column(String(20), nullable=True)
    hour_end_wednesday = Column(String(20), nullable=True)    
    hour_start_thursday = Column(String(20), nullable=True)
    hour_end_thursday = Column(String(20), nullable=True)    
    hour_start_friday = Column(String(20), nullable=True)
    hour_end_friday = Column(String(20), nullable=True)    
    hour_start_saturday = Column(String(20), nullable=True)
    hour_end_saturday = Column(String(20), nullable=True)    
    hour_start_sunday = Column(String(20), nullable=True)
    hour_end_sunday = Column(String(20), nullable=True)    
    is_closed = Column(Boolean(), nullable=True) 
    categories = Column(String(200), nullable=True)
    display_phone = Column(String(50), nullable=True)
    location = Column(String(400), nullable=True)
    location_city = Column(String(50), nullable=True)
    location_state = Column(String(50), nullable=True)
    location_zip_code = Column(String(50), nullable=True)
    location_city_id = Column(String(100), nullable=True)
    # Latitude and Longitude need to be Numeric, not Integer to have decimal places
    # Put restaurant name and address inside definition of TSVectorType to be fulltext-indexed (searchable)
#     city = relationship("City", backref=backref("restaurants"))
#     categories = relationship("Category", secondary="restaurantcategories", backref="restaurants")
#     users = relationship("User", secondary="visits", backref="restaurants")

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Restaurant restaurant_id=%s name=%s>" % (self.restaurant_id,
                                                          self.name)

def example_data():
    """Create some sample data for testing."""

#     van = City(name="Vancouver")

    chambar = Restaurant(name="Chambar",
                         location="568 Beatty St, Vancouver, BC V6B 2L3",
                         phone="(604) 879-7119",
                         latitude=49.2810018,
                         longitude=-123.1109668)

    miku = Restaurant(name="Miku",
                      address="200 Granville St #70, Vancouver, BC V6C 1S4",
                      phone="(604) 568-3900",
                      latitude=49.2868017,
                      longitude=-123.1131884)

    fable = Restaurant(name="Fable",
                       address="1944 W 4th Ave, Vancouver, BC V6J 1M7",
                       phone="(604) 732-1322",
                       latitude=49.2679389,
                       longitude=-123.2190482)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

#     from server import app
#     connect_to_db(app)
    engine = create_engine("postgres://localhost/zoeshrm")
    if not database_exists(engine.url):
        create_database(engine.url)

    print(database_exists(engine.url))
    Base.metadata.create_all(engine)

    from sqlalchemy.orm import sessionmaker
    Base.metadata.bind = engine
 
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    # chambar = Restaurant(name="Chambar",
    #                  location="568 Beatty St, Vancouver, BC V6B 2L3",
    #                  phone="(604) 879-7119",
    #                  latitude=49.2810018,
    #                  longitude=-123.1109668)
    # session.add(chambar)
    session.commit()
    print "Connected to db"
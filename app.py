from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
load_dotenv()
import os
import requests

app = Flask(__name__)
CORS(app)

user = os.environ.get("postgreUser")
password = os.environ.get("postgrePassword")
host = os.environ.get("postgreHost")
database = os.environ.get("postreDb")

# use the below conf for connecting to mysql @ localhost
# conf = "mysql+pymysql://john:applesauce@localhost:3306/flickr"

# use the belo conf for connecting to postgresql with credentials from environment file
conf = "postgresql://" + user + ":" + password + "@" + host + "/" + database

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = conf
db = SQLAlchemy(app)
flickrUrl = os.environ.get("flickrUrl")

# Model for Cities table
class Cities(db.Model):
    __tablename__ = "cities"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __init__(self, name, lat, lon):
        self.name = name
        self.lat = lat
        self.lon = lon

    def __repr__(self):
        return f"{self.id}"

# Model for favourites table
class Favourites(db.Model):
    __tablename__ = "favourites"
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(256))

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __init__(self, url):
        self.url = url

    def __repr__(self):
        return f"{self.url}"

db.create_all()

# routes for managing the backend
@app.route("/api/v1/cities", methods=["POST"]) # provide pictures for given place name or coordinates
def city_details():
    data = request.get_json()
    image_list = []
    search = Cities.query.filter_by(name=data["city"]).all()
    if search: # if present in db
        lat = data["lat"]
        lon = data["lon"]
        params = {
            "method": "flickr.photos.search",
            "api_key": "64a43c7d7ffb9625314393941ea01e45",
            "lat": lat,
            "lon": lon,
            "format": "json",
            "nojsoncallback": "?",
            "page": 1,
            "per_page": 10,
        }
        response = requests.get(flickrUrl, params=params).json()
        for photo in response["photos"]["photo"]:
            img_dict = {}
            img_dict["url"] = (
                "https://live.staticflickr.com/"
                + photo["server"]
                + "/"
                + photo["id"]
                + "_"
                + photo["secret"]
                + ".jpg"
            )
            image_list.append(img_dict)

        response_object = {"page": response["photos"]["page"], "pictures": image_list}

    else:
        # save city details to db
        new_city = Cities(name=data["city"], lat=data["lat"], lon=data["lon"])
        db.session.add(new_city)
        db.session.commit()
        db.session.close()

        # fetch pictures
        lat = data["lat"]
        lon = data["lon"]
        params = {
            "method": "flickr.photos.search",
            "api_key": "64a43c7d7ffb9625314393941ea01e45",
            "lat": lat,
            "lon": lon,
            "format": "json",
            "nojsoncallback": "?",
            "page": 1,
            "per_page": 10,
        }
        response = requests.get(flickrUrl, params=params).json()
        for photo in response["photos"]["photo"]:
            img_dict = {}
            img_dict["url"] = (
                "https://live.staticflickr.com/"
                + photo["server"]
                + "/"
                + photo["id"]
                + "_"
                + photo["secret"]
                + ".jpg"
            )
            image_list.append(img_dict)

        response_object = {"page": response["photos"]["page"], "pictures": image_list}

    return response_object


@app.route("/api/v1/getCities", methods=["GET"]) # get all preset cities' names
def getCitiesNames():
    response_list = []
    citiesList = db.session.query(Cities.name).all()
    for cities in citiesList:
        response_list.append(cities[0])
    response = {"cities": response_list}
    return response


@app.route("/api/v1/addtoFavourites", methods=["POST"]) # add pictures to favourites
def addtoFav():
    data = request.get_json()
    check = db.session.query(Favourites).filter_by(url=data["url"]).first()
    if check is not None:
        response = {"present": "true", "message": "Already present in favourites!"}
    else:
        new_url = Favourites(url=data["url"])
        db.session.add(new_url)
        db.session.commit()
        db.session.close()
        response = {"present": "false", "message": "Successfully added to favourites!"}
    return response


@app.route("/api/v1/getAllFavourites", methods=["GET"]) # get all favourites pictures
def getFavourites():
    favourites_list = []
    result = db.session.query(Favourites.url).all()
    for items in result:
        favourites_list.append(items[0])
    response = {"data": favourites_list}
    return response


@app.route("/api/v1/presetCitiesData", methods=["POST"]) # get pictures as per place name from preset list
def presetCities():
    data = request.get_json()
    image_list = []
    place = data["place"]
    lat = db.session.query(Cities.lat).filter_by(name=place).first()[0]
    lon = db.session.query(Cities.lon).filter_by(name=place).first()[0]
    params = {
        "method": "flickr.photos.search",
        "api_key": "64a43c7d7ffb9625314393941ea01e45",
        "lat": lat,
        "lon": lon,
        "format": "json",
        "nojsoncallback": "?",
        "page": 1,
        "per_page": 10,
    }
    response = requests.get(flickrUrl, params=params).json()
    for photo in response["photos"]["photo"]:
        img_dict = {}
        img_dict["url"] = (
            "https://live.staticflickr.com/"
            + photo["server"]
            + "/"
            + photo["id"]
            + "_"
            + photo["secret"]
            + ".jpg"
        )
        image_list.append(img_dict)

    response_object = {"page": response["photos"]["page"], "pictures": image_list}

    return response_object

@app.route("/api/v1/nextPage", methods=['POST']) # pictures' details from next page
def nextPage():
    image_list = []
    data = request.get_json()
    page = data['page']
    place = data['place']
    lat = db.session.query(Cities.lat).filter_by(name=place).first()[0]
    lon = db.session.query(Cities.lon).filter_by(name=place).first()[0]
    params = {
        "method": "flickr.photos.search",
        "api_key": "64a43c7d7ffb9625314393941ea01e45",
        "lat": lat,
        "lon": lon,
        "format": "json",
        "nojsoncallback": "?",
        "page": page,
        "per_page": 10,
    }
    response = requests.get(flickrUrl, params=params).json()
    for photo in response["photos"]["photo"]:
        img_dict = {}
        img_dict["url"] = (
            "https://live.staticflickr.com/"
            + photo["server"]
            + "/"
            + photo["id"]
            + "_"
            + photo["secret"]
            + ".jpg"
        )
        image_list.append(img_dict)

    response_object = {"page": response["photos"]["page"], "pictures": image_list}

    return response_object

@app.route("/api/v1/prevPage", methods=['POST']) # pictures' details from previous page
def prevPage():
    image_list = []
    data = request.get_json()
    page = data['page']
    place = data['place']
    lat = db.session.query(Cities.lat).filter_by(name=place).first()[0]
    lon = db.session.query(Cities.lon).filter_by(name=place).first()[0]
    params = {
        "method": "flickr.photos.search",
        "api_key": "64a43c7d7ffb9625314393941ea01e45",
        "lat": lat,
        "lon": lon,
        "format": "json",
        "nojsoncallback": "?",
        "page": page,
        "per_page": 10,
    }
    response = requests.get(flickrUrl, params=params).json()
    for photo in response["photos"]["photo"]:
        img_dict = {}
        img_dict["url"] = (
            "https://live.staticflickr.com/"
            + photo["server"]
            + "/"
            + photo["id"]
            + "_"
            + photo["secret"]
            + ".jpg"
        )
        image_list.append(img_dict)

    response_object = {"page": response["photos"]["page"], "pictures": image_list}

    return response_object
import requests
import os

from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask import Flask, request
from sqlalchemy import ForeignKey

load_dotenv()

app = Flask(__name__)
CORS(app)

user = os.environ.get("postgreUser")
password = os.environ.get("postgrePassword")
host = os.environ.get("postgreHost")
database = os.environ.get("postreDb")
url = os.environ.get("url")
api_key = os.environ.get("api_key")
img_url = os.environ.get("img_url")

# below conf is for connecting to the database
conf = url.format(user=user, password=password, host=host, database=database)

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = conf
db = SQLAlchemy(app)
flickrUrl = os.environ.get("flickrUrl")


class Cities(db.Model):

    # Model for Cities table
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


class User(db.Model):

    # Model for user table
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256))
    password = db.Column(db.String(256))

    def __repr__(self):
        return f"{self.id}"


class Favourites(db.Model):

    # Model for favourites table
    __tablename__ = "favourites"
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(256))
    user_id = db.Column(db.Integer, ForeignKey(
        'user.id', ondelete='CASCADE'
    ))

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __init__(self, url, user_id):
        self.url = url
        self.user_id = user_id

    def __repr__(self):
        return f"{self.url}"


db.create_all()


@app.before_first_request
def before_first_request():

    # add data to Cities table
    check_city = Cities.query.all()

    if not check_city:
        city = Cities(name='Paris', lat=48.8589, lon=2.32004)
        db.session.add(city)
        db.session.commit()
        db.session.close()

    # add data to User table
    check_user = User.query.all()

    if not check_user:
        user = User(username='John', password='john@123')
        db.session.add(user)
        db.session.commit()
        db.session.close()


@app.route("/api/v1/login", methods=["POST"])
def getuser():

    # route for user login
    data = request.get_json()
    username = data['username']
    password = data['password']
    result = db.session.query(User.id).filter_by(username=username,
                                                 password=password).first()
    if result:
        print(result)
        response_object = {
            'message': 'success',
            'id': str(result[0])
        }

    else:
        response_object = {
            'message': 'Invalid username or password!'
        }

    return response_object


@app.route("/api/v1/register", methods=["POST"])
def register():

    # route for user registration
    data = request.get_json()
    username = data['username']
    password = data['password']
    check = User.query.filter_by(username=username).first()
    if check:
        print(check)
        response_object = {
            'status': 400,
            'message': 'User already exists!'
        }

    else:
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        db.session.close()
        response_object = {
            'status': 201,
            'message': 'User successfully created!'
        }

    return response_object


@app.route("/api/v1/cities", methods=["POST"])
def city_details():

    # provide pictures for given place name or coordinates
    data = request.get_json()
    image_list = []
    search = Cities.query.filter_by(name=data["city"]).all()

    if search:  # if present in db
        lat = data["lat"]
        lon = data["lon"]
        params = {
            "method": "flickr.photos.search",
            "api_key": api_key,
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
                img_url
                + photo["server"]
                + "/"
                + photo["id"]
                + "_"
                + photo["secret"]
                + ".jpg"
            )
            image_list.append(img_dict)

        response_object = {
            "page": response["photos"]["page"], "pictures": image_list}

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
            "api_key": api_key,
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
                img_url
                + photo["server"]
                + "/"
                + photo["id"]
                + "_"
                + photo["secret"]
                + ".jpg"
            )
            image_list.append(img_dict)

        response_object = {
            "page": response["photos"]["page"],
            "pictures": image_list,
            "lastpage": response['photos']['pages']
        }

    return response_object


@app.route("/api/v1/getCities", methods=["GET"])
def getCitiesNames():

    # get all preset cities' names
    response_list = []
    citiesList = db.session.query(Cities.name).all()

    for cities in citiesList:
        response_list.append(cities[0])

    response = {"cities": response_list}
    return response


@app.route("/api/v1/addtoFavourites", methods=["POST"])
def addtoFav():

    # add pictures to favourites
    data = request.get_json()
    check = db.session.query(Favourites).filter_by(url=data["url"],
                                                   user_id=data['userid']
                                                   ).first()

    if check is not None:
        response = {"present": "true",
                    "message": "Already present in favourites!"}

    else:
        new_url = Favourites(url=data["url"], user_id=data['userid'])
        db.session.add(new_url)
        db.session.commit()
        db.session.close()
        response = {"present": "false",
                    "message": "Successfully added to favourites!"}

    return response


@app.route("/api/v1/removeimage", methods=['GET'])
def removefromfavourites():

    # remove image from favourites
    new_list = []
    userid = request.args.get("userid")
    image = request.args.get("url")
    # get the id of image to be deleted
    result_id = db.session.query(Favourites.id).filter_by(user_id=userid,
                                                          url=image).first()
    # delete the image
    db.session.query(Favourites).filter_by(id=result_id[0]).delete()
    db.session.commit()
    # send updated image list to application
    req = db.session.query(Favourites.url).filter_by(user_id=userid).all()

    for items in req:
        new_list.append(items[0])

    response = {"data": new_list}
    return response


@app.route("/api/v1/getAllFavourites", methods=["GET"])
def getFavourites():

    # get all favourites pictures
    favourites_list = []
    userid = request.args.get('userid')
    print(userid)
    result = db.session.query(Favourites.url).filter_by(user_id=userid).all()

    for items in result:
        favourites_list.append(items[0])

    response = {"data": favourites_list}
    return response


@app.route("/api/v1/presetCitiesData", methods=["POST"])
def presetCities():

    # get pictures as per place name from preset list
    data = request.get_json()
    image_list = []
    place = data["place"]
    lat = db.session.query(Cities.lat).filter_by(name=place).first()[0]
    lon = db.session.query(Cities.lon).filter_by(name=place).first()[0]
    params = {
        "method": "flickr.photos.search",
        "api_key": api_key,
        "lat": lat,
        "lon": lon,
        "format": "json",
        "nojsoncallback": "?",
        "page": 1,
        "per_page": 10
    }
    response = requests.get(flickrUrl, params=params).json()

    for photo in response["photos"]["photo"]:
        img_dict = {}
        img_dict["url"] = (
            img_url
            + photo["server"]
            + "/"
            + photo["id"]
            + "_"
            + photo["secret"]
            + ".jpg"
        )
        image_list.append(img_dict)

    response_object = {
        "page": response["photos"]["page"],
        "pictures": image_list,
        "lastpage": response['photos']['pages']
    }
    return response_object


@app.route("/api/v1/nextPage", methods=['POST'])
def nextPage():

    # pictures' details from next page
    image_list = []
    data = request.get_json()
    page = data['page']
    place = data['place']
    lat = db.session.query(Cities.lat).filter_by(name=place).first()[0]
    lon = db.session.query(Cities.lon).filter_by(name=place).first()[0]
    params = {
        "method": "flickr.photos.search",
        "api_key": api_key,
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
            img_url
            + photo["server"]
            + "/"
            + photo["id"]
            + "_"
            + photo["secret"]
            + ".jpg"
        )
        image_list.append(img_dict)

    response_object = {
        "page": response["photos"]["page"],
        "pictures": image_list,
        "lastpage": response['photos']['pages']
    }
    return response_object


@app.route("/api/v1/prevPage", methods=['POST'])
def prevPage():

    # pictures' details from previous page
    image_list = []
    data = request.get_json()
    page = data['page']
    place = data['place']
    lat = db.session.query(Cities.lat).filter_by(name=place).first()[0]
    lon = db.session.query(Cities.lon).filter_by(name=place).first()[0]
    params = {
        "method": "flickr.photos.search",
        "api_key": api_key,
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
            img_url
            + photo["server"]
            + "/"
            + photo["id"]
            + "_"
            + photo["secret"]
            + ".jpg"
        )
        image_list.append(img_dict)

    response_object = {
        "page": response["photos"]["page"],
        "pictures": image_list,
        "lastpage": response['photos']['pages']
    }
    return response_object

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/g1t3-aangstay'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class House(db.Model):
    __tablename__ = 'house'
    
    houseID = db.Column(db.Integer, primary_key=True)
    houseName = db.Column(db.String(64), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    region = db.Column(db.String(50), nullable=False)
    latitude = db.Column(db.Float(11,8), nullable=False)
    longitude = db.Column(db.Float(12,8), nullable=False)
    price = db.Column(db.Float(10,0), nullable=False)


    def __init__(self, houseID, houseName, address, region, latitude, longitude, price):
        self.houseID = houseID
        self.houseName = houseName
        self.address = address
        self.region = region
        self.latitude = latitude
        self. longitude = longitude
        self.price = price


    def json(self):
        return {"houseID": self.houseID, "houseName": self.houseName, "address": self.address, "region": self.region, "latitude": self.latitude, "longitude": self.longitude, "price": self.price}


@app.route("/confirmation" , methods=['GET'])
def get_all():
    houselist = House.query.all()
    if request.is_json:
        order = request.get_json()
        result = processOrder(order)
        return jsonify(result), result["code"]
    else:
        data = request.get_data()
        print("Received an invalid order:")
        print(data)
        return jsonify({"code": 400,
                        # make the data string as we dunno what could be the actual format
                        "data": str(data),
                        "message": "Order should be in JSON."}), 400  # Bad Request input

def processOrder(order):
    print("Processing an order for shipping:")
    print(order)
    # Can do anything here, but aiming to keep it simple (atomic)
    house_list = order['houseId']
    # If customer id contains "ERROR", simulate failure
    if "ERROR" in order['houseId']:
        code = 400
        message = 'Simulated failure in retriving house data.'
    else:  # simulate success
        code = 201
        message = 'Simulated success in retriving house data.'
    print(message)
    print()  # print a new line feed as a separator

    return {
        'code': code,
        'data': {
            'house_list': house_list
        },
        'message': message
    }


@app.route("/house")
def get_all():
    houselist = House.query.all()
    if len(houselist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "House list": [house.json() for house in houselist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no available houses."
        }
    ), 404


#@app.route("/house/string:<")
# def find_by_isbn13(isbn13):
#     book = Book.query.filter_by(isbn13=isbn13).first()
#     if book:
#         return jsonify(
#             {
#                 "code": 200,
#                 "data": book.json()
#             }
#         )
#     return jsonify(
#         {
#             "code": 404,
#             "message": "Book not found."
#         }
#     ), 404


# @app.route("/book/<string:isbn13>", methods=['POST'])
# def create_book(isbn13):
#     if (Book.query.filter_by(isbn13=isbn13).first()):
#         return jsonify(
#             {
#                 "code": 400,
#                 "data": {
#                     "isbn13": isbn13
#                 },
#                 "message": "Book already exists."
#             }
#         ), 400


#     data = request.get_json()
#     book = Book(isbn13, **data)


#     try:
#         db.session.add(book)
#         db.session.commit()
#     except:
#         return jsonify(
#             {
#                 "code": 500,
#                 "data": {
#                     "isbn13": isbn13
#                 },
#                 "message": "An error occurred creating the book."
#             }
#         ), 500


#     return jsonify(
#         {
#             "code": 201,
#             "data": book.json()
#         }
#     ), 201

if __name__ == '__main__':
    app.run(port=5000, debug=True)

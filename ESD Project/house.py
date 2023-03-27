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


@app.route("/")
def get_all():
    booklist = House.query.all()
    if len(booklist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "books": [book.json() for book in booklist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no books."
        }
    ), 404



# @app.route("/book/<string:isbn13>")
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

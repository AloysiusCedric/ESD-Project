from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/g1t3-aangstay'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class House(db.Model):
    __tablename__ = 'house'
    
    houseId = db.Column(db.Integer, primary_key=True)
    houseName = db.Column(db.String(64), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float(11,8), nullable=False)
    longitude = db.Column(db.Float(12,8), nullable=False)   
    price = db.Column(db.Float(10,0), nullable=False)


    def __init__(self, houseId, houseName, address, latitude, longitude, price):
        self.houseId = houseId
        self.houseName = houseName
        self.address = address
        self.latitude = latitude
        self. longitude = longitude
        self.price = price


    def json(self):
        return {"houseId": self.houseId, "houseName": self.houseName, "address": self.address, "latitude": self.latitude, "longitude": self.longitude, "price": self.price}

@app.route("/house_record", methods=['POST'])
def get_houseId():
    if request.is_json:
        houseIds = request.json['houseId'].split(',')
        houses_data = []
        for houseId in houseIds:
            # Check if the houseId is valid
            if not houseId:
                return {
                    'code': 400,
                    'data': None,
                    'message': 'Invalid houseId'
                }
            # Retrieve the housing data based on houseId
            house_data = requests.get(f'http://127.0.0.1:5003/house/{houseId}').json()
            if house_data['code'] == 200:
                houses_data.append(house_data['data'])
            else:
                return {
                    'code': 404,
                    'data': None,
                    'message': f'House {houseId} not found'
                }
        return {
            'code': 200,
            'data': houses_data,
            'message': 'Housing data retrieved successfully'
        }
    else:
        data = request.get_data()
        print("Received an invalid request:")
        return jsonify({
            "code": 400,
            "data": str(data),
            "message": "Request should be in JSON."
        }), 400


def processOrder(order):
    houseId = int(order['houseId']) # "3" turn to 3
    
    # Check if the houseId is valid
    if not houseId: # "houseId" : "value"
        return {
            'code': 400,
            'data': None,
            'message': 'Invalid houseId'
        }
    
    # Retrieve the housing data based on houseId
    house_data = requests.get(f'http://127.0.0.1:5003/house/{houseId}').json() #return
    
    if house_data['code'] == 200:
        return {
            'code': 200,
            'data': house_data['data'],
            'message': 'Housing data retrieved successfully'
        }
    else:
        return {
            'code': 404,
            'data': None,
            'message': 'House not found'
        }
        
@app.route("/house") # normal access to all house data
def get_all_houses():
    houselist = House.query.all()
    if len(houselist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "house-list": [house.json() for house in houselist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no available houses."
        }
    ), 404
        
@app.route("/house/<string:houseId>")   # retreiving house data based on houseId 
def find_by_houseId(houseId):
        house = (House.query.filter_by(houseId=houseId).first())
        if house:
            return jsonify(
                {
                "code": 200,
                "data" : house.json()
                }
            )
        return jsonify(
        {
            "code": 404,
            "message": "House name not found."
        }
    ), 404

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5003, debug=True)

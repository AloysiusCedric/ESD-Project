from flask import Flask, request, jsonify
import requests
# import paypalrestsdk
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import datetime
import json

# paypalrestsdk.configure({
#     "mode": "sandbox", # replace with "live" for production environment
#     "client_id": "Ab4eHmG5gXRQngWEXdRWm5LilInbI5QYMUPYA49YjJwExCBybR3EROtUa1K_uZECMcGWYsm0v_T6YXob",
#     "client_secret": "EEPtruSziLc33Fo3U3EbHzYKOkPOofkvFeW3T5zhvL_1_iUsLZluvkKTlnH0UZhNWd8qduLBR6z7l3PM"
# })

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/g1t3-aangstay'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Payment(db.Model):
    __tablename__ = 'payment'
    paymentId = db.Column(db.String(64),primary_key = True)
    tDate = db.Column(db.Date, nullable=True)
    paidAmount = db.Column(db.Float(precision=2), nullable=False)
    status = db.Column(db.String(64), nullable=False)
    housepId = db.Column(db.Integer, nullable=False)

    def __init__(self,paymentId, paidAmount, status, tDate, housepId):
        self.paymentId = paymentId
        self.paidAmount = paidAmount
        self.status = status
        self.tDate = tDate
        self.housepId = housepId
 
    def json(self):
        return {"paymentId": self.paymentId, "tDate": self.tDate, "paidAmount": self.paidAmount, "status": self.status, "housepId": self.housepId}

#create entry in payment db
@app.route('/payment', methods=['POST'])
def payment_to_db():
    data = request.get_json()
    print(data)
    print(data["endDate"])
    status = "confirmed"
    if (status == 'confirmed'):
        tDate = datetime.datetime.strptime(data['tDate'], '%Y-%m-%dT%H:%M:%S')
        housepId = data['housepId']
        paidAmount = data['paidAmount']
        newPayment = Payment(tDate = tDate, paidAmount = paidAmount, status = status, housepId = housepId)
        db.session.add(newPayment)
        db.session.commit()

        payment_details = [tDate, paidAmount, status]

        if len(payment_details) != 0 :
            return jsonify({"code":201,
                        "data": payment_details,
                        "message": 'New Entry created successfully!'})
        else :
            return jsonify({"code":500,
                        "message":'Transaction FAILED!!'})

#######################################################################################################     FOR PAYPAL IF SUCCESS
# @app.route('/payment', methods=['POST'])
# def payment_to_db():
#     data = request.get_json()
#     status = data['status']
#     if (status == 'CONFIRMED'):
#         tDate = datetime.datetime.strptime(data['tDate'], '%Y-%m-%dT%H:%M:%S')
#         # paymentId = data['paymentId']// FOR PAYPAL CAPTUREID if successful
#         housepId = data['housepId']
#         paidAmount = data['paidAmount']
#         # newPayment = Payment(paymentId = paymentId, tDate = tDate, paidAmount = paidAmount, status = status, housepId = housepId)// FOR PAYPAL CAPTUREID if successful
#         newPayment = Payment(tDate = tDate, paidAmount = paidAmount, status = status, housepId = housepId)
#         db.session.add(newPayment)
#         db.session.commit()
#         result = {'message': 'New Entry created successfully!'}
#     else:
#         # result = {'message' : 'Transaction with paymentId '+paymentId+ 'is not confirmed!'} // FOR PAYPAL CAPTUREID if successful
#         result = {'message' : 'Transaction FAILED'}

#     return jsonify(result)
#######################################################################################################     

#change status from "confirmed" to "refunded"
@app.route('/refund', methods=['POST'])
def refund():
    data = request.get_json()
    paymentId = data['paymentId']
    payment = Payment.query.filter_by(paymentId=paymentId).first()
    if payment:
        if payment.status == "confirmed":
                payment.status = 'REFUNDED'
                db.session.commit()
                result = {'payment': payment.json(), 'message': 'Refund successful'}
                return jsonify(result), 200
        else:
            result = {'message': 'Failed to create refund transaction'}
            return jsonify(result), 500
    else:
        result = {'message': f'Transaction with paymentId {paymentId} not found in the database.'}
        return jsonify(result), 404

#######################################################################################################     FOR PAYPAL IF SUCCESS
# @app.route('/refund', methods=['POST'])
# def refund():
#     data = request.get_json()
#     paymentId = data['paymentId']
#     accessToken = data['accessToken']
#     payment = Payment.query.filter_by(paymentId=paymentId).first()
#     if payment:
#         if payment.status == "CONFIRMED":
#             # Construct the PayPal API endpoint URL
#             url = f"https://api-m.sandbox.paypal.com/v2/payments/captures/{paymentId}/refund"
#             headers = {
#                 "Content-Type": "application/json",
#                 "Authorization": f"Bearer {accessToken}"
#             }
#             body = {}
#             response = requests.post(url, headers=headers, json=body)
#             data = response.json()
#             if data['status'] =='COMPLETED':
#                 payment.status = 'REFUNDED'
#                 db.session.commit()
#                 result = {'payment': payment.json(), 'message': 'Refund successful'}
#                 return jsonify(result), 200
#             else:
#                 result = {'message': 'Failed to create refund transaction'}
#                 return jsonify(result), 500
#         else:
#             result = {'message': 'Payment status is not CONFIRMED'}
#             return jsonify(result), 400
#     else:
#         result = {'message': f'Transaction with paymentId {paymentId} not found in the database.'}
#         return jsonify(result), 404

# #refund completed, return status completed to booking complex microservice
# @app.route('/payment/<string:paymentId>/complete', methods=['POST'])
# def complete(paymentId):
#     payment = Payment.query.filter_by(paymentId = paymentId).first()
#     if payment:
#         payment.status = 'COMPLETED'
#         db.session.commit()
#         result = {'message': f'Transaction with paymentId {paymentId} has been refunded.'}
#         return jsonify(result)
#     else:
#         result = {'message': f'Transaction with paymentId {paymentId} not found in the database.'}
#         return jsonify(result), 404
#######################################################################################################     

if __name__ == '__main__':
    app.run(host='0.0.0.0',port = 5002, debug=True)
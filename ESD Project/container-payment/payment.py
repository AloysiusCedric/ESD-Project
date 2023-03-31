from flask import Flask, request, jsonify
import requests
import paypalrestsdk
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import datetime

paypalrestsdk.configure({
    "mode": "sandbox", # replace with "live" for production environment
    "client_id": "Ab4eHmG5gXRQngWEXdRWm5LilInbI5QYMUPYA49YjJwExCBybR3EROtUa1K_uZECMcGWYsm0v_T6YXob",
    "client_secret": "EEPtruSziLc33Fo3U3EbHzYKOkPOofkvFeW3T5zhvL_1_iUsLZluvkKTlnH0UZhNWd8qduLBR6z7l3PM"
})

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/g1t3-aangstay'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Payment(db.Model):
    __tablename__ = 'payment'
    paymentId = db.Column(db.Integer,primary_key = True)
    tDate = db.Column(db.Date, nullable=True)
    paidAmount = db.Column(db.Float(precision=2), nullable=False)
    status = db.Column(db.String(64), nullable=False)
    invoiceId = db.Column(db.String(64), nullable=False)
    housepId = db.Column(db.Integer, nullable=False)

    def __init__(self,paidAmount, status, tDate, invoiceId, housepId):
        self.paidAmount = paidAmount
        self.status = status
        self.tDate = tDate
        self.invoiceId = invoiceId
        self.housepId = housepId
 
    def json(self):
        return {"tDate": self.tDate, "paidAmount": self.paidAmount, "status": self.status, "invoiceId": self.invoiceId, "housepId": self.housepId}

#create entry in payment db
@app.route('/payment', methods=['POST'])
def payment_to_db():
    data = request.json
    status = data['status']
    if (status == 'confirmed'):
        tDate = datetime.datetime.strptime(data['tDate'], '%Y-%m-%dT%H:%M:%S')
        housepId = data['housepId']
        paidAmount = data['paidAmount']
        invoiceId = data['invoiceId']
        newPayment = Payment(tDate = tDate, paidAmount = paidAmount, status = status, invoiceId = invoiceId, housepId = housepId)
        db.session.add(newPayment)
        db.session.commit()
        result = {'message': 'New Entry created successfully!'}
    else:
        result = {'message' : 'Transaction with invoiceId {invoiceId} is not confirmed! '}
    
    return jsonify(result)

#change status from "confirmed" to "refunded"
@app.route('/payment/<string:invoiceId>', methods=['POST'])
def refund(invoiceId):
    payment = Payment.query.filter_by(invoiceId = invoiceId).first()
    if payment:
        # Update payment status to refunded
        payment.status = 'refunded'
        db.session.commit()
        # Return message with payment details
        result = {'payment': payment.json()}
        return jsonify(result)
    else:
        result = {'message': f'Transaction with invoiceId {invoiceId} not found in the database.'}
        return jsonify(result), 404

#refund completed, return status completed to booking complex microservice
@app.route('/payment/<string:invoiceId>/complete', methods=['POST'])
def complete(invoiceId):
    payment = Payment.query.filter_by(invoiceId = invoiceId).first()
    if payment:
        # change status if refund complete? 
        # payment.status = 'completed'
        db.session.commit()
        result = {'message': f'Transaction with invoiceId {invoiceId} has been refunded.'}
        return jsonify(result)
    else:
        result = {'message': f'Transaction with invoiceId {invoiceId} not found in the database.'}
        return jsonify(result), 404
    
if __name__ == '__main__':
    app.run(host='0.0.0.0',port = 5002, debug=True)
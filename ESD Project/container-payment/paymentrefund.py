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
    tDate = db.Column(db.Date, nullable=False)
    paidAmount = Column(db.Float(precision=2), nullable=False)
    status = Column(db.String(64), nullable=False)
    invoiceId = Column(db.String(64), nullable=False)
    housepId = Column(db.Integer, nullable=False)

    def __init__(self, paymentId, tDate, paidAmount, status, invoiceId, housepId):
        self.paymentId = paymentId
        self.tDate = tDate
        self.paidAmount = paidAmount
        self.status = status
        self.invoiceId = invoiceId
        self.housepId = housepId
 
    def json(self):
        return {"paymentId": self.paymentId, "tDate": self.tDate, "paidAmount": self.paidAmount, "status": self.status, "invoiceId": self.invoiceId, "housepId": self.housepId}

#change status from "confirmed" to "refunded"
@app.route('/payment/<int:transactionId>', methods=['POST'])
def refund(transactionId):
    payment = Payment.query.filter_by(paymentId = transactionId).first()
    if payment:
        # Update payment status to refunded
        payment.status = 'refunded'
        db.session.commit()
        # Return message with payment details
        result = {'payment': payment.json()}
        return jsonify(result)
    else:
        result = {'message': f'Transaction with transactionId {transactionId} not found in the database.'}
        return jsonify(result), 404

#refund completed, return status completed
@app.route('/payment/<int:transactionId>/complete', methods=['POST'])
def complete(transactionId):
    payment = Payment.query.filter_by(paymentId = transactionId).first()
    if payment:
        # payment.status = 'completed'
        db.session.commit()
        result = {'message': f'Transaction with transactionId {transactionId} has been refunded.'}
        return jsonify(result)
    else:
        result = {'message': f'Transaction with transactionId {transactionId} not found in the database.'}
        return jsonify(result), 404
    
if __name__ == '__main__':
    app.run(host='0.0.0.0',port = 5002, debug=True)
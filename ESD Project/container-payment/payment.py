from flask import Flask, request, jsonify
import paypalrestsdk
import sendgrid
from sendgrid.helpers.mail import *
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import datetime

app = Flask(__name__)

db_uri = 'mysql+mysqlconnector://root@localhost:3306/g1t3-aangstay'
engine = create_engine(db_uri)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Payment(Base):
    __tablename__ = 'payment'
    paymentId = Column(Integer,primary_key = True)
    tDate = Column(DateTime)
    paidAmount = Column(Integer)
    status = Column(String)
    houseId = Column(Integer)

Base.metadata.create_all(engine)
 
#configure Paypal API
paypalrestsdk.configure({
    "mode": "sandbox", # replace with "live" for production environment
    "client_id": "Ab4eHmG5gXRQngWEXdRWm5LilInbI5QYMUPYA49YjJwExCBybR3EROtUa1K_uZECMcGWYsm0v_T6YXob",
    "client_secret": "EEPtruSziLc33Fo3U3EbHzYKOkPOofkvFeW3T5zhvL_1_iUsLZluvkKTlnH0UZhNWd8qduLBR6z7l3PM"
})

#configure SendGrid API
sg = sendgrid.SendGridAPIClient(api_key='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')
from_email = Email("derek.wee.2021@smu.edu.sg")
to_email = Email("derek.wee.2021@smu.edu.sg")
subject = "Payment Notification"
content = Content("text/plain", "Your payment was successful")

#create an entry in payment db
@app.route('/payment', methods=['POST'])
def make_payment():
    data = request.json

    paymentId = data['paymentId']
    houseId = data['houseId']
    tDate =  datetime.datetime.strptime(data['tDate'], '%Y-%m-%dT%H:%M:%S')
    paidAmount = data['paidAmount']
    status = data['status']
    payment = Payment(paymentId = paymentId, tDate = tDate, paidAmount = paidAmount, status = status, houseId = houseId)
    
    session = Session()
    session.add(payment)
    session.commit()
    session.close()

    result = {'message': 'New Entry created successfully!'}
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
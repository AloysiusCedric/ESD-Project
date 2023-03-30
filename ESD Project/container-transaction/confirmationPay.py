# Transaction Microservice
from flask import Flask, request, jsonify
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import datetime

app = Flask(__name__)

db_uri = 'mysql+mysqlconnector://root@localhost:3306/g1t3-aangstay'
engine = create_engine(db_uri)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Transaction(Base):
    __tablename__ = 'transaction'
    id = Column(Integer, primary_key=True)
    transactionID = Column(String)
    houseid = Column(Integer)
    startdate = Column(DateTime)
    enddate = Column(DateTime)
    status = Column(String)
    bookingNum = Column(String)

Base.metadata.create_all(engine)

@app.route('/')
def home():
    return 'Hello World'

@app.route('/transaction', methods=['POST'])
def add_transaction():

    data = request.json

    transactionID = data['transactionId']   
    startdate = datetime.datetime.strptime(data['startDate'], '%Y-%m-%dT%H:%M:%S')
    enddate = datetime.datetime.strptime(data['endDate'], '%Y-%m-%dT%H:%M:%S')
    status = data['status']
    houseid = data['houseId']
    bookingNum = data['bookingNum']

    transaction = Transaction(transactionID=transactionID, startdate=startdate, enddate=enddate, status=status,houseid=houseid, bookingNum=bookingNum)

    session = Session()
    session.add(transaction)
    session.commit()
    session.close()

    result = {'message': 'New Entry created successfully!'}
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)

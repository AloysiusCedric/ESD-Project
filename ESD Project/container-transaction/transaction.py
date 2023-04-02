from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import datetime
import calendar
import string
import random

from flask_cors import CORS
app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/g1t3-aangstay'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Transaction(db.Model):
    transactionId = db.Column(db.String, primary_key=True)
    startDate = db.Column(db.Date, nullable=False)
    endDate = db.Column(db.Date, nullable=False)
    status = db.Column(db.String, nullable=False)
    houseId = db.Column(db.Integer, nullable=False)
    bookingNum = db.Column(db.String, nullable=False)
    paymentId = db.Column(db.String, nullable=False)


@app.route('/transaction_record', methods=['POST'])
def get_current_month_transactions():
    data = request.get_json()
    print("Receive an input from user for checking booking MS", data)
    start_date_str = data.get('startDate')
    end_date_str = data.get('endDate')
    if start_date_str and end_date_str:
        start_date = datetime.datetime.fromisoformat(start_date_str).date()
        end_date = datetime.datetime.fromisoformat(end_date_str).date()
    else:
        today = datetime.date.today()
        start_date = datetime.date(today.year, today.month, 1)
        end_date = datetime.date(
            today.year, today.month, calendar.monthrange(today.year, today.month)[1])

    available_house_ids = []

    transactions = Transaction.query.filter(
        Transaction.status == "confirmed",
        ((Transaction.startDate <= start_date) & (Transaction.endDate >= end_date)) |
        ((Transaction.startDate >= start_date) & (Transaction.startDate <= end_date)) |
        ((Transaction.endDate >= start_date) & (Transaction.endDate <= end_date))
    ).all()
    for house_id in range(1, 13):
        overlapping = False
        for transaction in transactions:
            if transaction.houseId == house_id:
                if (transaction.startDate <= end_date) and (transaction.endDate >= start_date):
                    overlapping = True
                    break
        if not overlapping:
            available_house_ids.append(house_id)
    if len(available_house_ids) != 0:
        return jsonify({"code": 200,
                        "data": available_house_ids,
                        "message": "Available Houses houseids successfully returned."})
    else:
        return jsonify({"code": 200,
                        "message": "There are no available houses houseids"})


@app.route('/transaction', methods=['POST'])
def add_transaction():
    data = request.get_json()
    data = data['data']  # extract data object from input
    houseId = int(data['houseID'])
    startDate = datetime.datetime.fromisoformat(data['startDate']).date()
    endDate = datetime.datetime.fromisoformat(data['endDate']).date()
    paymentId = f"{data['paymentId']}"
    hPrice = data["hPrice"]

    # Generate transactionId and bookingNum
    transactionId = ''.join(random.choices(
        string.ascii_uppercase + string.digits, k=10))
    bookingNum = ''.join(random.choices(
        string.ascii_uppercase + string.digits, k=6))

    # Create new transaction object and add to database
    new_transaction = Transaction(
        transactionId=transactionId,
        houseId=houseId,
        startDate=startDate,
        endDate=endDate,
        status="confirmed",
        bookingNum=bookingNum,
        paymentId=paymentId
    )
    db.session.add(new_transaction)
    db.session.commit()

    result = {
        "code": 201,
        "message": "Your booking is successful",
        "data": {
            "startDate": startDate,
            "endDate": endDate,
            "houseId": houseId,
            "paymentId": paymentId
        }
    }

    return jsonify(result)


@app.route('/transaction/<string:bookingNum>/cancel', methods=['POST'])
def cancel_transaction(bookingNum):
    transaction = Transaction.query.filter_by(bookingNum=bookingNum).first()

    if transaction:
        transaction.status = 'cancelled'
        db.session.commit()
        result = {"code": 200,
                  'message': f'Transaction with bookingNum {bookingNum} has been cancelled.',
                  'paymentId': transaction.paymentId}
        return jsonify(result)
    else:
        result = {
            "code": 404, 'message': f'Transaction with bookingNum {bookingNum} not found in the database.'}
        return jsonify(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

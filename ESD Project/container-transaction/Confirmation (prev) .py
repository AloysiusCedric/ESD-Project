from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import datetime
import calendar
import string
import random

app = Flask(__name__)
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


@app.route('/transaction', methods=['GET'])
def get_current_month_transactions():
    data = request.get_json()
    start_date_str = data.get('startDate')
    end_date_str = data.get('endDate')
    if start_date_str and end_date_str:
        start_date = datetime.datetime.fromisoformat(start_date_str).date()
        end_date = datetime.datetime.fromisoformat(end_date_str).date()
    else:
        today = datetime.date.today()
        start_date = datetime.date(today.year, today.month, 1)
        end_date = datetime.date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
        
    unavailable_dates = {}
    house_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    for i in range(3):
        current_month = start_date.month + i
        current_year = start_date.year
        if current_month > 12:
            current_month -= 12
            current_year += 1
        month_name = calendar.month_name[current_month]
        first_day_of_month = datetime.date(current_year, current_month, 1)
        last_day_of_month = datetime.date(current_year, current_month, calendar.monthrange(current_year, current_month)[1])
        transactions = Transaction.query.filter(
            Transaction.status == "confirmed",
            ((Transaction.startDate <= first_day_of_month) & (Transaction.endDate >= last_day_of_month)) |
            ((Transaction.startDate >= first_day_of_month) & (Transaction.startDate <= last_day_of_month)) |
            ((Transaction.endDate >= first_day_of_month) & (Transaction.endDate <= last_day_of_month))
        ).all()
        unavailable_dates[month_name] = {}
        for house_id in house_ids:
            unavailable_dates[month_name][house_id] = []
            unavailable_start_date = None
            unavailable_end_date = None
            for day in range(calendar.monthrange(current_year, current_month)[1]):
                date = datetime.date(current_year, current_month, day + 1)
                overlapping = False
                for transaction in transactions:
                    if transaction.houseId == house_id:
                        if transaction.startDate <= date <= transaction.endDate:
                            overlapping = True
                            break
                if overlapping:
                    if unavailable_start_date is None:
                        unavailable_start_date = date
                    unavailable_end_date = date
                else:
                    if unavailable_start_date is not None and unavailable_end_date is not None:
                        if end_date >= unavailable_start_date and start_date <= unavailable_end_date:
                            unavailable_dates[month_name][house_id].append(
                                f"{unavailable_start_date.strftime('%Y-%m-%d')} - {unavailable_end_date.strftime('%Y-%m-%d')}"
                            )
                        unavailable_start_date = None
                        unavailable_end_date = None
            if unavailable_start_date is not None and unavailable_end_date is not None:
                if end_date >= unavailable_start_date and start_date <= unavailable_end_date:
                    unavailable_dates[month_name][house_id].append(
                        f"{unavailable_start_date.strftime('%Y-%m-%d')} - {unavailable_end_date.strftime('%Y-%m-%d')}"
                    )

    sorted_unavailable_dates = dict(sorted(unavailable_dates.items(), key=lambda x: datetime.datetime.strptime(x[0], "%B")))
    return jsonify(sorted_unavailable_dates)




@app.route('/transaction', methods=['POST'])
def add_transaction():
    data = request.get_json()
    transactionId = data['transactionId']
    houseId = data['houseId']
    startDate = datetime.datetime.fromisoformat(data['startDate'])
    endDate = datetime.datetime.fromisoformat(data['endDate'])
    status = data['status']
    bookingNum = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    paymentId = data['paymentId']

    if status == "confirmed":
        new_transaction = Transaction(
            transactionId=transactionId,
            houseId=houseId,
            startDate=startDate,
            endDate=endDate,
            status=status,
            bookingNum=bookingNum,
            paymentId = paymentId
        )
        db.session.add(new_transaction)
        db.session.commit()

        result = {'Message': 'New entry created successfully!', 'bookingNum':bookingNum}
        return jsonify(result)
    else:
        result = {'Message': 'Transaction status must be confirmed'}
        return jsonify(result), 400


@app.route('/transaction/<string:bookingNum>/cancel', methods=['POST'])
def cancel_transaction(bookingNum):
    transaction = Transaction.query.filter_by(bookingNum=bookingNum).first()
    
    if transaction:
        transaction.status = 'cancelled'
        db.session.commit()
        result = {'message': f'Transaction with bookingNum {bookingNum} has been cancelled.', 'paymentId': transaction.paymentId}
        return jsonify(result)
    else:   
        result = {'message': f'Transaction with bookingNum {bookingNum} not found in the database.'}
        return jsonify(result), 404




if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5001, debug=True)

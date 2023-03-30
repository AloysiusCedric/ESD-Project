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
    transactionId = db.Column(db.Integer, primary_key=True)
    startDate = db.Column(db.Date, nullable=False)
    endDate = db.Column(db.Date, nullable=False)
    status = db.Column(db.String, nullable=False)
    houseId = db.Column(db.Integer, nullable=False)
    bookingNum = db.Column(db.String, nullable=False)

@app.route('/transaction', methods=['GET'])
def get_current_month_transactions():
    today = datetime.date.today()
    available_dates = {}
    house_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    for i in range(3):
        current_month = today.month + i
        current_year = today.year
        if current_month > 12:
            current_month -= 12
            current_year += 1
        month_name = calendar.month_name[current_month]
        first_day_of_month = datetime.date(current_year, current_month, 1)
        last_day_of_month = datetime.date(current_year, current_month, calendar.monthrange(current_year, current_month)[1])
        transactions = Transaction.query.filter(
            Transaction.status == True,
            ((Transaction.startDate <= first_day_of_month) & (Transaction.endDate >= last_day_of_month)) |
            ((Transaction.startDate >= first_day_of_month) & (Transaction.startDate <= last_day_of_month)) |
            ((Transaction.endDate >= first_day_of_month) & (Transaction.endDate <= last_day_of_month))
        ).all()
        available_dates[month_name] = {}
        for house_id in house_ids:
            available_dates[month_name][house_id] = []
            available_start_date = None
            available_end_date = None
            for day in range(calendar.monthrange(current_year, current_month)[1]):
                date = datetime.date(current_year, current_month, day + 1)
                overlapping = False
                for transaction in transactions:
                    if transaction.houseId == house_id:
                        if transaction.startDate <= date <= transaction.endDate:
                            overlapping = True
                            break
                if not overlapping:
                    if available_start_date is None:
                        available_start_date = date
                    available_end_date = date
                else:
                    if available_start_date is not None and available_end_date is not None:
                        available_dates[month_name][house_id].append(
                            f"{available_start_date.strftime('%Y-%m-%d')} - {available_end_date.strftime('%Y-%m-%d')}"
                        )
                        available_start_date = None
                        available_end_date = None
            if available_start_date is not None and available_end_date is not None:
                available_dates[month_name][house_id].append(
                    f"{available_start_date.strftime('%Y-%m-%d')} - {available_end_date.strftime('%Y-%m-%d')}"
                )

    sorted_available_dates = dict(sorted(available_dates.items(), key=lambda x: datetime.datetime.strptime(x[0], "%B")))
    return jsonify(sorted_available_dates)

@app.route('/transaction', methods=['POST'])
def add_transaction():
    data = request.json
    transactionId = data['transactionId']
    houseId = data['houseId']
    startDate = datetime.datetime.fromisoformat(data['startDate'])
    endDate = datetime.datetime.fromisoformat(data['endDate'])
    status = data['status']
    bookingNum = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    new_transaction = Transaction(
        transactionId=transactionId,
        houseId=houseId,
        startDate=startDate,
        endDate=endDate,
        status=status,
        bookingNum=bookingNum
    )
    db.session.add(new_transaction)
    db.session.commit()

    result = {'message': 'New entry created successfully!'}
    return jsonify(result)

@app.route('/transaction/<string:bookingNum>/cancel', methods=['POST'])
def cancel_transaction(bookingNum):
    transaction = Transaction.query.filter_by(bookingNum=bookingNum).first()
    if transaction:
        transaction.status = 'cancelled'
        db.session.commit()
        result = {'message': f'Transaction with bookingNum {bookingNum} has been cancelled.'}
        return jsonify(result)
    else:
        result = {'message': f'Transaction with bookingNum {bookingNum} not found in the database.'}
        return jsonify(result), 404



if __name__ == '__main__':
    app.run(debug=True)

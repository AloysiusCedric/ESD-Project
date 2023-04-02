##This willl be the complex micro service
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

import os, sys
from os import environ

import requests
from invokes import invoke_http

import amqp_setup
import pika
import json


app = Flask(__name__)

CORS(app)


transaction_URL = "http://localhost:5001/transaction_record" #Used for checking transaction to search a stay
create_transaction_URL="http://localhost:5001/transaction" #Used for creating entry in transaction MS when user pays
payment_URL = "http://localhost:5002/payment" #Used for creating entry in payment MS when user pays
house_record_URL = "http://localhost:5003/house_record" #Used to send houseID from transaction then get back infromation of houses when user search for a stay
refund_URL = "http://localhost:5002/refund" #Use for booking cancellation

##home
@app.route("/")
def index():
    return render_template("index.html")


##Search for a stay scenario
@app.route("/search", methods=['POST'])
def checkAvailability():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            toCheck = request.get_json()
            print("Receive an input from user for checking transaction MS", toCheck)

            #do the actual work
            #1. Send user input {start date, end date}
            result = checkTransaction(toCheck)

            return jsonify(result), result["code"]

        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            print(toCheck)
            print("hello world")

            return jsonify({
                "code": 500,
                "message": "booking.py internal error: " + ex_str
            }), 500
          

    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400


def checkTransaction(toCheck):
    # 2. Send the order info {start date, end date}
    # Invoke the transaction microservice
    print('\n-----Invoking transaction microservice-----')
    transaction_result = invoke_http(transaction_URL, method='POST', json=toCheck)
    print('result:', transaction_result)


    # Check the transaction result; if a failure, send it to the error microservice.
    code = transaction_result["code"]
    message = json.dumps(transaction_result)

    if code not in range(200, 300):
        # Inform the error microservice
        print('\n\n-----Publishing the (checking error) message with routing_key=checking.error-----')

        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="checking.error", 
            body=message, properties=pika.BasicProperties(delivery_mode = 2)) 
        # make message persistent within the matching queues until it is received by some receiver 
        # (the matching queues have to exist and be durable and bound to the exchange)

        # - reply from the invocation is not used;
        # continue even if this invocation fails        
        print("\nOrder status ({:d}) published to the RabbitMQ Exchange:".format(
            code), transaction_result)

        # 3. Return error
        return {
            "code": 500,
            "data": {"check_result": transaction_result},
            "message": "Checking failure sent for error handling."
        }

    else:
        # 4. Record checking information
        # record the activity log anyway
        print('\n\n-----Publishing the (checking info) message with routing_key=checking.info-----')      
      
        # There is an error with the code below that cause the stream error         
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="checking.info",  
            body= message)
    
    print("\nOrder published to RabbitMQ Exchange.\n")
    # - reply from the invocation is not used;
    # continue even if this invocation fails


    # 5. Send transaction details to house MS
    # Invoke the house microservice
    print('\n\n-----Invoking house microservice-----')    
    
    house_result = invoke_http(
        house_record_URL, method="POST", json=transaction_result["data"])
    print("transaction result", house_result, '\n')

    # Check the house result;
    # if a failure, send it to the error microservice.
    code = house_result["code"]
    if code not in range(200, 300):
        # Inform the error microservice
        print('\n\n-----Publishing the (house error) message with routing_key=house.error-----')

        message = json.dumps(house_result)
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="house.error", 
            body=message, properties=pika.BasicProperties(delivery_mode = 2))

        print("\nhouse status ({:d}) published to the RabbitMQ Exchange:".format(
            code), house_result)

        # 6. Return error
        return {
            "code": 400,
            "data": {
                "transaction_result": transaction_result,
                "house_result": house_result
            },
            "message": "House record error sent for error handling."
        }

    # 7. Return JSON body with transaction result and house result
    # If the code returned to HTML page is within 201, display all the available houses
    return {
        "code": 201,
        "data": {
            "transaction_result": transaction_result,
            "house_result": house_result
        }
    }

##Make payment scenario
@app.route("/pay", methods=['POST'])
def payment():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            toPass = request.get_json()
            print("Receive inputs from user to be passed for processing in the payment MS", toPass)

            #do the actual work
            #1. Send user inputs{houseId, start date, end date}

            result = storeDetails(toPass)
            return jsonify(result), result["code"]

        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            return jsonify({
                "code": 500,
                "message": "booking.py internal error: " + ex_str
            }), 500
          

    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400


def storeDetails(toPass):
    # 2. Send the information to payment microservice{start date, end date, houseID}
    # Invoke the payment microservice
    print('\n-----Invoking payment microservice-----')
    payment_result = invoke_http(payment_URL, method='POST', json=toPass)
    print('result:', payment_result)
  

    # Check the transaction result; if a failure, send it to the error microservice.
    code = payment_result["code"]
    message = json.dumps(payment_result)
    print(type(message))

    if code not in range(200, 300):
        # Inform the error microservice
        print('\n\n-----Publishing the (payment error) message with routing_key=payment.error-----')

        #Publish message to AMQP broker
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="payment.error", 
            body=message, properties=pika.BasicProperties(delivery_mode = 2)) 
        # make message persistent within the matching queues until it is received by some receiver 
        # (the matching queues have to exist and be durable and bound to the exchange)

        # - reply from the invocation is not used;
        # continue even if this invocation fails        
        print("\nOrder status ({:d}) published to the RabbitMQ Exchange:".format(
            code), payment_result)

        # 3. Return error
        return {
            "code": 500,
            "data": {"payment result": payment_result},
            "message": "failed to create entry in the payment MS."
        }

    else:
        # 4. Record payment
        # record the activity log anyway
        print('\n\n-----Publishing the (payment info) message with routing_key=payment.info-----')        
       #Publish message to AMQP broker          
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="checkTransaction.activity",  
            body= message)
    
    print("\nOrder published to RabbitMQ Exchange.\n")
    # - reply from the invocation is not used;
    # continue even if this invocation fails


    # 5. Send payment details to transaction MS
    # Invoke the transaction microservice
    print('\n\n-----Invoking transaction microservice-----')    
    
    transaction_result = invoke_http(
        create_transaction_URL, method="POST", json=payment_result)
    print("transaction result", transaction_result, '\n')

    # Check the booking results;
    # if a failure, send it to the error microservice.
    message = json.dumps(transaction_result)
    print(type(message))
    code = transaction_result["code"]
    if code not in range(200, 300):
        # Inform the error microservice
        print('\n\n-----Publishing the (transaction error) message with routing_key=transaction.error-----')

        message = json.dumps(transaction_result)

        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="transaction.error", 
            body=message, properties=pika.BasicProperties(delivery_mode = 2))

        print("\nhouse status ({:d}) published to the RabbitMQ Exchange:".format(
            code), transaction_result)

        # 6. Return error
        return {
            "code": 400,
            "data": {
                "payment result": payment_result,
                "transaction result": transaction_result
            },
            "message": "failed to create entry in the transaction MS."
        }
    else:
        # 7. Send booking notification
        # record the activity log anyway
        print('\n\n-----Publishing the (booking info) message with routing_key=booking.notification-----')        
       #Publish message to AMQP broker          
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="booking.notification",  
            body= message)

    # 7. Return JSON body with transaction result and house result, shipping record
    # If the code returned to HTML page is within 201, displayed successfully paid and display booking number
    return {
        "code": 201,
        "data": {
            "payment result": payment_result,
            "transaction result": transaction_result
        }
    }
    

##Make cancallation scenario
@app.route("/cancel", methods=['POST'])
def cancel():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            toCancel = request.get_json()
            print("Received booking number for cancellation", toCancel)

            #do the actual work
            #1. Send booking number from user{booking number}

            result = updateDetails(toCancel)
            return jsonify(result), result["code"]

        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            return jsonify({
                "code": 500,
                "message": "booking.py internal error: " + ex_str
            }), 500
          

    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400


def updateDetails(toCancel):
    # 2. Send the booking number to transaction microservice
    # Invoke the transaction microservice
    print('\n-----Invoking transaction microservice-----')
    cancel_result = invoke_http('http://localhost:5001/transaction/cancel', method='POST', json=toCancel)
    print('result:', cancel_result)
  

    # Check the transaction result; if a failure, send it to the error microservice.
    code = cancel_result["code"]
    message = json.dumps(cancel_result)
    print(type(message))

    if code not in range(200, 300):
        # Inform the error microservice
        print('\n\n-----Publishing the (payment error) message with routing_key=cancel.error-----')

        #Publish message to AMQP broker
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="cancel.error", 
            body=message, properties=pika.BasicProperties(delivery_mode = 2)) 
        # make message persistent within the matching queues until it is received by some receiver 
        # (the matching queues have to exist and be durable and bound to the exchange)

        # - reply from the invocation is not used;
        # continue even if this invocation fails        
        print("\nOrder status ({:d}) published to the RabbitMQ Exchange:".format(
            code), cancel_result)

        # 3. Return error
        return {
            "code": 500,
            "data": {"cancel_result": cancel_result},
            "message": "failed to get paymentId for cancellation in the payment MS."
        }


    else:
        # 4. Record cancellation
        # record the activity log anyway
        print('\n\n-----Publishing the (cancel info) message with routing_key=payment.info-----')        
       #Publish message to AMQP broker          
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="cancel.activity",  
            body= message)
    
    print("\nOrder published to RabbitMQ Exchange.\n")
    # - reply from the invocation is not used;
    # continue even if this invocation fails


    # 5. Send paymentID gotten from transaction MS to payment MS
    # Invoke the payment microservice
    print('\n\n-----Invoking payment microservice-----')    
    
    ctransaction_result = invoke_http(
        refund_URL, method="POST", json=cancel_result)
    print("cancel transaction result", ctransaction_result, '\n')

    # Check the refund results;
    # if a failure, send it to the error microservice.
    message = json.dumps(ctransaction_result)
    print(type(message))
    code = ctransaction_result["code"]
    if code not in range(200, 300):
        # Inform the error microservice
        print('\n\n-----Publishing the (transaction error) message with routing_key=refund.error-----')

        message = json.dumps(ctransaction_result)

        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="refund.error", 
            body=message, properties=pika.BasicProperties(delivery_mode = 2))

        print("\nhouse status ({:d}) published to the RabbitMQ Exchange:".format(
            code), ctransaction_result)

        # 6. Return error
        return {
            "code": 400,
            "data": {
                "payment result": cancel_result,
                "cpayment result": ctransaction_result
            },
            "message": "failed to update cancellation status in the transaction MS."
        }
    else:
        # 7. Send refund notification
        # record the activity log anyway
        print('\n\n-----Publishing the (refund info) message with routing_key=refund.notification-----')        
       #Publish message to AMQP broker          
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="refund.notification",  
            body= message)

    # 7. Return JSON body with transaction cancel result and cancel payment result
    # If the code returned to HTML page is within 201, display successfully refund to user
    return {
        "code": 201,
        "data": {
            "cancel result": cancel_result,
            "cpayment result": ctransaction_result
        }
    }
    


# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) +
          " checking a booking..")
    app.run( host="0.0.0.0", port=5000, debug=True)
    # Notes for the parameters:
    # - debug=True will reload the program automatically if a change is detected;
    #   -- it in fact starts two instances of the same flask program,
    #       and uses one of the instances to monitor the program changes;
    # - host="0.0.0.0" allows the flask program to accept requests sent from any IP/host (in addition to localhost),
    #   -- i.e., it gives permissions to hosts with any IP to access the flask program,
    #   -- as long as the hosts can already reach the machine running the flask program along the network;
    #   -- it doesn't mean to use http://0.0.0.0 to access the flask program.
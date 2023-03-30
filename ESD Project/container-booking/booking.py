##This willl be the complex micro service
from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys
from os import environ

import requests
# from invokes import invoke_http

import amqp_setup
import pika
import json


app = Flask(__name__)

CORS(app)


confirmation_URL = "http://localhost:5001/confirmation_record"
house_record_URL = "http://localhost:5002/house_record"

@app.route("/search", methods=['POST'])
def checkAvailability():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            toCheck = request.get_json()
            print("Receive an input from user for checking booking MS", toCheck)

            #do the actual work
            #1. Send user input {check in date, check out date, region}
            result = checkConfirmation(toCheck)
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


def checkConfirmation(toCheck):
    # 2. Send the order info {cart items}
    # Invoke the order microservice
    print('\n-----Invoking confirmation microservice-----')
    confirmation_result = invoke_http(confirmation_URL, method='POST', json=toCheck)
    print('result:', confirmation_result)
  

    # Check the confirmation result; if a failure, send it to the error microservice.
    code = confirmation_result["code"]
    message = json.dumps(confirmation_result)

    if code not in range(200, 300):
        # Inform the error microservice
        #print('\n\n-----Invoking error microservice as order fails-----')
        print('\n\n-----Publishing the (checking error) message with routing_key=order.error-----')

        # invoke_http(error_URL, method="POST", json=order_result)
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="confirmation.error", 
            body=message, properties=pika.BasicProperties(delivery_mode = 2)) 
        # make message persistent within the matching queues until it is received by some receiver 
        # (the matching queues have to exist and be durable and bound to the exchange)

        # - reply from the invocation is not used;
        # continue even if this invocation fails        
        print("\nOrder status ({:d}) published to the RabbitMQ Exchange:".format(
            code), confirmation_result)

        # 7. Return error
        return {
            "code": 500,
            "data": {"check_result": confirmation_result},
            "message": "Checking failure sent for error handling."
        }

    # Notice that we are publishing to "Activity Log" only when there is no error in order creation.
    # In http version, we first invoked "Activity Log" and then checked for error.
    # Since the "Activity Log" binds to the queue using '#' => any routing_key would be matched 
    # and a message sent to “Error” queue can be received by “Activity Log” too.

    else:
        # 4. Record new order
        # record the activity log anyway
        #print('\n\n-----Invoking activity_log microservice-----')
        print('\n\n-----Publishing the (order info) message with routing_key=order.info-----')        

        # invoke_http(activity_log_URL, method="POST", json=order_result)            
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="checkConfirmation.activity",  
            body= confirmation_result)
    
    print("\nOrder published to RabbitMQ Exchange.\n")
    # - reply from the invocation is not used;
    # continue even if this invocation fails


    # 5. Send confirmation details to house MS
    # Invoke the house microservice
    print('\n\n-----Invoking house microservice-----')    
    
    house_result = invoke_http(
        house_record_URL, method="POST", json=confirmation_result['data'])
    print("confirmation result", house_result, '\n')

    # Check the shipping result;
    # if a failure, send it to the error microservice.
    code = house_result["code"]
    if code not in range(200, 300):
        # Inform the error microservice
        #print('\n\n-----Invoking error microservice as house fails-----')
        print('\n\n-----Publishing the (house error) message with routing_key=house.error-----')

        # invoke_http(error_URL, method="POST", json=house_result)
        message = json.dumps(house_result)
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="house.error", 
            body=message, properties=pika.BasicProperties(delivery_mode = 2))

        print("\nhouse status ({:d}) published to the RabbitMQ Exchange:".format(
            code), house_result)

        # 7. Return error
        return {
            "code": 400,
            "data": {
                "confirmation_result": confirmation_result,
                "house_result": house_result
            },
            "message": "House record error sent for error handling."
        }

    # 7. Return JSON body with confirmation result and house result, shipping record
    return {
        "code": 201,
        "data": {
            "confirmation_result": confirmation_result,
            "house_result": house_result
        }
    }
    


    


# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) +
          " checking a booking..")
    app.run( host="0.0.0.0",port=5000, debug=True)
    # Notes for the parameters:
    # - debug=True will reload the program automatically if a change is detected;
    #   -- it in fact starts two instances of the same flask program,
    #       and uses one of the instances to monitor the program changes;
    # - host="0.0.0.0" allows the flask program to accept requests sent from any IP/host (in addition to localhost),
    #   -- i.e., it gives permissions to hosts with any IP to access the flask program,
    #   -- as long as the hosts can already reach the machine running the flask program along the network;
    #   -- it doesn't mean to use http://0.0.0.0 to access the flask program.
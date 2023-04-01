import json

import os

import amqp_setup

import os
from twilio.rest import Client


def receiveNoti():

    amqp_setup.check_setup()

    queue_name = 'Notification'

    # set up a consumer and start to wait for coming messages

    amqp_setup.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    amqp_setup.channel.start_consuming() # an implicit loop waiting to receive messages; 

    #it doesn't exit by default. Use Ctrl+C in the command window to terminate it.

def callback(channel, method, properties, body): # required signature for the callback; no return

    print("\nReceived Order by " + __file__)


    # Your Account SID from twilio.com/console
    account_sid = "AC5f3f823542d896540c8a8c7d300474cf"
    # Your Auth Token from twilio.com/console
    auth_token  = "c8ae493a75d77b1e2030f966fb082b9a"

    client = Client(account_sid, auth_token)

    message = client.messages.create(
        to="+6591086832", 
        from_="+15017250604",
        body="Hello from Python!")

    print(message.sid)



if __name__ == "__main__":  # execute this program only if it is run as a script (not by 'import')

    print("\nThis is " + os.path.basename(__file__), end='')

    print(": monitoring routing key '{}' in exchange '{}' ...".format(1,amqp_setup.exchangename))

    receiveNoti()
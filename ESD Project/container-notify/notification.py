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


    account_sid = 'ACc25a793016fa375e2402e95c52a1eb23'
    auth_token = '4c93f4ad82c352be558a62b45c332e0a'
    client = Client(account_sid, auth_token)

    message = client.messages.create(
    from_='whatsapp:+14155238886',
    body='Your cancellation has been received. We will work to process your refund within 3 working days.',
    to='whatsapp:+6593863745'
    )

    print(message.sid)


if __name__ == "__main__":  # execute this program only if it is run as a script (not by 'import')

    print("\nThis is " + os.path.basename(__file__), end='')

    print(": monitoring routing key '{}' in exchange '{}' ...".format(1,amqp_setup.exchangename))

    receiveNoti()
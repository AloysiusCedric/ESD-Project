import json
import os

import amqp_setup

from twilio.rest import Client


def receiveNoti():

    amqp_setup.check_setup()

    queue_name = 'Notification'

    # set up a consumer and start to wait for coming messages

    amqp_setup.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    amqp_setup.channel.start_consuming() # an implicit loop waiting to receive messages; 

    #it doesn't exit by default. Use Ctrl+C in the command window to terminate it.

def callback(channel, method, properties, body): # required signature for the callback; no return

    body = json.loads(body)

    if (body["code"] == 201):
            bookingNum = body["data"]["bookingNum"]
            startDate =  body["data"]["startDate"]
            endDate =  body["data"]["endDate"]

            account_sid = 'AC5f3f823542d896540c8a8c7d300474cf'
            auth_token = 'caff0646663f7fbfed215652ab82e421'
            print (auth_token)
            client = Client(account_sid, auth_token)

        
        

            message = client.messages.create(
            from_='whatsapp:+14155238886',
            body="Your booking from (" + str(startDate) + ") to (" + str(endDate) + ") has been confirmed. Your booking number is: " + str(bookingNum),
            to='whatsapp:+6591086832'
            )




    print("\nReceived Order by " + __file__)


    print(message.sid)


if __name__ == "__main__":  # execute this program only if it is run as a script (not by 'import')

    print("\nThis is " + os.path.basename(__file__), end='')

    print(": monitoring routing key '{}' in exchange '{}' ...".format(1,amqp_setup.exchangename))

    receiveNoti()
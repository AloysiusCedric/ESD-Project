import json

import os

import amqp_setup


def receiveError():

    amqp_setup.check_setup()

    queue_name = 'Error'

    # set up a consumer and start to wait for coming messages

    amqp_setup.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    amqp_setup.channel.start_consuming() # an implicit loop waiting to receive messages; 

    #it doesn't exit by default. Use Ctrl+C in the command window to terminate it.

def callback(channel, method, properties, body): # required signature for the callback; no return

    print("\nReceived Order by " + __file__)

    print(json.loads(body))



if __name__ == "__main__":  # execute this program only if it is run as a script (not by 'import')

    print("\nThis is " + os.path.basename(__file__), end='')

    print(": monitoring routing key '{}' in exchange '{}' ...".format(1,amqp_setup.exchangename))

    receiveError()
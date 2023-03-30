from flask import Flask, request, jsonify

import os, sys

import requests


import amqp_setup
import pika
import json

order = {'customer_id': "1", "order_id" : "1", 'qty': "10"} 
message = json.dumps(order) 
 
amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="order.error",  
            body= message)

amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="order.notification",  
            body= message)

amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="order.activity",  
            body= message)
from twilio.rest import Client 
import json 
 
account_sid = 'AC5dc0ecc9639c498d0821e67a73ea9fa7' 
auth_token = 'baab3d06975910aede6c6c633012c4bb' 
client = Client(account_sid, auth_token) 
 
 
 
order = {'customer_id': "1", "order_id" : 10, 'qty': "10"} 
order_id = json.dumps(order['order_id']) 
paymentMsg = 'Your payment for order_id ' + order_id + ' has been successfully!'  
 
 
 
message = client.messages.create( 
  from_='+14155238886', 
  body=paymentMsg, 
  to='+6591086832' 
)
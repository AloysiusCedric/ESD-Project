from twilio.rest import Client 
import json 
 
account_sid = 'AC5f3f823542d896540c8a8c7d300474cf' 
auth_token = 'c8ae493a75d77b1e2030f966fb082b9a' 
client = Client(account_sid, auth_token) 
 
 
 
order = {'customer_id': "1", "order_id" : 10, 'qty': "10"} 
order_id = json.dumps(order['order_id']) 
paymentMsg = 'Your payment for order_id ' + order_id + ' has been successfully!'  
 
 
 
message = client.messages.create( 
  from_='+14155238886', 
  body=paymentMsg, 
  to='+6591086832' 
)
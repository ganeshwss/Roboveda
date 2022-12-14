import json
from flask import Flask, Response, request, jsonify
from flask_mongoengine import MongoEngine
from os import environ
import time
from flask_cors import CORS, cross_origin #to solve cors issue
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import razorpay
# from pprint import pprint

##################################################################################################################################################################################################################

# Razorpay
keyid = environ.get('RAZORPAY_KEY_ID')
keysecret = environ.get('RAZORPAY_SECRET_KEY')

razorpay_client = razorpay.Client(auth=(keyid, keysecret))

app = Flask(__name__)
CORS(app) #set cors 

# send in blue
configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = environ.get('SENDINBLUE_API_KEY')

app.config['MONGODB_SETTINGS'] = {'db': 'roboveda','host': 'mongodb+srv://root:root@roboveda.feslyvu.mongodb.net/test','port': 27017}
# app.config["MONGODB_SETTINGS"] = {'DB': "my_app", "host":'mongodb://localhost:27017'}

db = MongoEngine()
db.init_app(app)

class emp(db.Document):
    choice_field = {'basic':'Basic',
    'premium':'premium',
    'master':'master',
    'pradarshan':'pradarshan',
    'loT':'loT',
    'drone':'drone'
    }
    ticket = db.StringField(max_length=20, choices=choice_field.keys(), required = True)
    name = db.StringField()
    mobile_no=db.IntField()
    email = db.StringField()
    amount=db.IntField()
    def to_json(self):
        return {"name": self.name, 
                "mobile_no":self.mobile_no, 
                "email": self.email,
                "ticket": self.ticket,
                "amount":self.amount}

# class amounttable(db.Document):
#     amount=db.IntField()
#     def to_json(self):
#         return {"amount":self.amount}

api_instance = sib_api_v3_sdk.ContactsApi(sib_api_v3_sdk.ApiClient(configuration))
repeat_contact_api_instance = sib_api_v3_sdk.ListsApi(sib_api_v3_sdk.ApiClient(configuration)) #lists-api
transaction_mail_api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration)) #transactional-emails-api 

@app.route('/add', methods=['POST'])
def create_record(*args, **kwargs):
    record = json.loads(request.data)
    user = emp(ticket = record['ticket'],
                name=record['name'],
                mobile_no=record['mobile_no'],
                email=record['email'],
                amount=record['amount'])
    
    data = request.get_json()
    email = data.get('email')
    amount = data.get('amount')
    create_contact = sib_api_v3_sdk.CreateContact(email=email) # CreateContact | Values to create a contact
    api_response = api_instance.create_contact(create_contact)
    currency="INR"
    client=razorpay.Client(auth=("rzp_test_hAYTO5a3WVZkPe", "RhY3gSMz6U1ejJXdliestlZu"))           #auth=(razorpay_key,rezorpay_secret ))
    payment=client.order.create({'amount':amount,'currency':currency,'payment_capture':1})
    # return jsonify(payment=payment)  
    user.save()

    # api_response.save()
    return jsonify(user.to_json(),{"message":"Data added successfully !",'status':200,'error':True})    

if __name__ == "__main__":
    app.run(debug=True)
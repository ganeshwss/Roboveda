import json
from flask import Flask, Response, request, jsonify
from flask_mongoengine import MongoEngine
import os
import time
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import razorpay
# from pprint import pprint

# Razorpay
keyid = 'rzp_test_hAYTO5a3WVZkPe'
keysecret = 'RhY3gSMz6U1ejJXdliestlZu'

razorpay_client = razorpay.Client(auth=(keyid, keysecret))

app = Flask(__name__)

# send in blue
configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = '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'

app.config['MONGODB_SETTINGS'] = {'db': 'roboveda','host': 'localhost','port': 27017}

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
    def to_json(self):
        return {"name": self.name, 
                "mobile_no":self.mobile_no, 
                "email": self.email,
                "ticket": self.ticket}

class amounttable(db.Document):
    amount=db.IntField()
    def to_json(self):
        return {"amount":self.amount}

api_instance = sib_api_v3_sdk.ContactsApi(sib_api_v3_sdk.ApiClient(configuration))
repeat_contact_api_instance = sib_api_v3_sdk.ListsApi(sib_api_v3_sdk.ApiClient(configuration)) #lists-api
transaction_mail_api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration)) #transactional-emails-api 

@app.route('/add', methods=['POST'])
def create_record():
    record = json.loads(request.data)
    user = emp(ticket = record['ticket'],
                name=record['name'],
                mobile_no=record['mobile_no'],
                email=record['email'])
    try:
        create_contact = sib_api_v3_sdk.CreateContact(email='hhhhfaa@gmail.com') # CreateContact | Values to create a contact
        api_response = api_instance.create_contact(create_contact)
    except ApiException as e:
        api_response = api_instance.create_contact(create_contact)
    user.save()
    # api_response.save()
    return jsonify(user.to_json(),{"message":"Data Succefully Add"})

@app.route('/charge', methods=['POST'])
def app_charge():
    if request.method=="POST":
        #data = request.get_json()
        global payment,name        
        name=request.form.get('name')
        mobile=request.form.get('mobile')
        email = request.form.get('email')
        amount = request.form.get('amount')
        notes={'name':name,"mobile":mobile,"email":email}
        currency="INR"
        client=razorpay.Client(auth=("rzp_test_hAYTO5a3WVZkPe", "RhY3gSMz6U1ejJXdliestlZu"))           #auth=(razorpay_key,rezorpay_secret ))
        payment=client.order.create({'amount':amount,'currency':currency,'payment_capture':1,'notes':notes})
        return jsonify(payment=payment)#,razorpay_key=razorpay_key)      

if __name__ == "__main__":
    app.run(debug=True)
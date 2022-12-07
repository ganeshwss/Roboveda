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

configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = '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'

app.config['MONGODB_SETTINGS'] = {
    'db': 'roboveda',
    'host': 'localhost',
    'port': 27017
}
db = MongoEngine()
db.init_app(app)

class emp(db.Document):
    name = db.StringField()
    mobile_no=db.IntField()
    email = db.StringField()
    def to_json(self):
        return {"name": self.name,
                "mobile_no":self.mobile_no,
                "email": self.email}

api_instance = sib_api_v3_sdk.ContactsApi(sib_api_v3_sdk.ApiClient(configuration))
repeat_contact_api_instance = sib_api_v3_sdk.ListsApi(sib_api_v3_sdk.ApiClient(configuration)) #lists-api
transaction_mail_api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration)) #transactional-emails-api 

create_contact = sib_api_v3_sdk.CreateContact(email='ganesh@gmailcom',) # CreateContact | Values to create a contact

try:
    # Create a contact
    api_response = api_instance.create_contact(create_contact)
    #pprint(api_response)
except ApiException as e:
    print("Exception when calling ContactsApi->create_contact: %s\n" % e)

@app.route('/get', methods=['GET'])
def query_records():
    name = request.args.get('name')
    user = emp.objects(name=name).first()
    if not user:
        return jsonify({'error': 'data not found'})
    else:
        return jsonify(user.to_json())

@app.route('/add', methods=['POST'])
def create_record():
            record = json.loads(request.data)
            user = emp(name=record['name'],
            mobile_no=record['mobile_no'],
            email=record['email'])
            user.save()
            return jsonify(user.to_json(),{"message":"Data Succefully Add"})

@app.route('/charge', methods=['POST'])
def app_charge():
    amount = 10
    payment_id = request.form['razorpay_payment_id']
    razorpay_client.payment.capture(payment_id, amount)
    return json.dumps(razorpay_client.payment.fetch(payment_id))

    # create_contact = sib_api_v3_sdk.CreateContact(email=email, attributes = { "FIRSTNAME" : name }, list_ids=[5])
				
	# 			#create contact of the registered user in sendinblue
    # try:
    #     contacts_api_instance.create_contact(create_contact)
    # except:
    #       try:
    #         list_id = 5                 # contact_list ID
    #         contact_emails = sib_api_v3_sdk.AddContactToList()
    #         contact_emails.emails = [email]
    #         try:
    #             repeat_contact_api_instance.add_contact_to_list(list_id, contact_emails)
    #         except ApiException as e:
    #             print("Exception when calling ListsApi->add_contact_to_list: %s\n" % e)
    #         except Exception as e:
    #             print("Exception in Repeat Add Contact")



# @app.route("/",methods=["POST"])
# def index():
#     if request.method=="POST":
#         msg = Message("Hello",
#                   sender="rutik24@gmail.com",
#                   recipients=["rutikd@wharfstreetstrategies.com"])
#         msg.body="how are you"
#         mail.send(msg)
#         return Response('meassge sent')
    
    

if __name__ == "__main__":
    app.run(debug=True)
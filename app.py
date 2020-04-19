from flask import Flask, request, make_response
import json
import os
from flask_cors import cross_origin
from SendEmail.sendEmail import EmailSender
from logger import logger
import requests
#from email_templates import template_reader

app = Flask(__name__)



# geting and sending response to dialogflow
@app.route('/webhook', methods=['POST'])
@cross_origin()
def webhook():

    req = request.get_json(silent=True, force=True)

    #print("Request:")
    #print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    #print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


# processing the request from dialogflow
def processRequest(req):
    log = logger.Log()

    sessionID=req.get('responseId')


    result = req.get("queryResult")
    user_says=result.get("queryText")
    log.write_log(sessionID, "User Says: "+user_says)
    parameters = result.get("parameters")
    name=parameters.get("name")
    #print(cust_name)
    phone = parameters.get("phone")
    Remail=parameters.get("email")
    country= parameters.get("country")
    #print(country)
    pincode=parameters.get("pincode")
    intent = result.get("intent").get('displayName')
    
    if (intent=='Data'):
        
        email_sender=EmailSender()
        
        email_file = open("email_templates/corona.html", "r")
        email_message = email_file.read()
        email_sender.send_email_to_person(Remail,email_message)
        fulfillmentText="We have sent you the mail regarding corona. do you still want to continue?"
         
        return {
                "fulfillmentText": fulfillmentText
                }
        
        log.write_log(sessionID, "Bot Says: "+fulfillmentText)
           
    elif(intent=='Press one'):
        url = "https://covid-19-data.p.rapidapi.com/country"
        querystring = {"format":"json","name":country}
        headers = {
                'x-rapidapi-host': "covid-19-data.p.rapidapi.com",
                'x-rapidapi-key': "d65751bc29msh5c7831c10864e7ap10a499jsn6ff1bfc248e2"
                }
        response = requests.request("GET", url, headers=headers, params=querystring)

        obj=response.json()
        
        line=str(obj[0]["country"])+"\n Confirmed:"+str(obj[0]["confirmed"])+"\n Recovered:"+str(obj[0]["recovered"])+"\n Deaths:"+str(obj[0]["deaths"])
        
        print(line)
        
       
        #print(response.text)
        fulfillmentText=line
        
        return {
                "fulfillmentText": fulfillmentText
                }
        log.write_log(sessionID,"Bot Says:"+country)
        
    else:
        log.write_log(sessionID, "Bot Says: " + result.fulfillmentText)


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host='0.0.0.0')

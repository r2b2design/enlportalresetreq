import urllib
import json
import os
import requests
from flask import Flask
from flask import request
from flask import make_response

#Flask app starting in global layout
app = Flask(__name__)

@app.route('/portalreq', methods=['POST'])
def webhook() :
    req = request.get_json(silent=True, force=True)
    print("Request:")
    print(json.dumps(req, indent=4))

    res = procesrequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def procesrequest(req) :
    print("Request:")
    print(json.dumps(req, indent=4))
    if req.get("result").get("action") == "PortalResetRq" :
        res = MakewebhookResultSheet(req)
    elif req.get("result").get("action") == "Auth" :
        res = makeWebhookResult(req)
    else:
        return{}
    return res


def MakewebhookResultSheet(req) :
    import pygsheets
    gc = pygsheets.authorize()
    result = req.get("result")
    parameters = result.get("parameters")
    portalname = parameters.get("PortalName")
    portallink = parameters.get("PortalLink")
    takeoutagent = parameters.get("Takeoutagent")
    dateofspoof = parameters.get("Dataofspoof")
    resonatorconfig = parameters.get("Resonaterconfig")
    originalfaction = parameters.get("Originalfaction")
    nowfaction = parameters.get("Nowfaction")
    resetfaction = parameters.get("Resetfaction")

    speech = ("We saved the following info for the request " '\n'
              "Portalname: " +str(portalname)+'\n''\n'
              "Agent that took out the portal:"'\n'
              +str(takeoutagent)+ '\n'
              "Date of Spoof: "+str(dateofspoof)+'\n'
              "Resonator config: "+str(resonatorconfig)+'\n' '\n'
              "Portal was original from:  " +str(originalfaction)+'\n'
              "At the moment the portal is: "+str(nowfaction)+'\n'
              "Portal will be restored to: "+str(resetfaction)+'\n'
               )
    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here.
    sh = gc.open("ENL Portal reset Requests")
    wks = sh.sheet1
    row = [portalname,portallink,takeoutagent,dateofspoof,resonatorconfig,originalfaction,nowfaction,resetfaction]
    wks.index = 2
    wks.insert_row(row=2, number=1, values="row")
    print("response:")
    print(speech)
    return{
    "speech": speech,
    "displayText": speech,
    "source": "/Continue_with_the_req"
    }

def makeWebhookResult(req) :
    result = req.get("result")
    parameters = result.get("parameters")
    chatid = req.get("originalRequest").get("data").get("message").get("from").get("id") #grab chat id from telegram
    verifyonrocks = ("rverify")
    rverify = requests.get('https://enlightened.rocks/comm/api/membership/' + str(chatid) + '?key=5oOG23EyGaayeBksQ8UaOLfy')
    verifydata = rverify.json()
    user = verifydata.get('user' , 'Default')
    speechdenied = "U dont have rights to talk with this bot, I am the personal assistent of a Ingress vangaurd"
    try: # Grab data from ENL.Rocks if possible
        tg_user = user.get('tg_user' , 'default')
        tg_id = user.get('tg_id' , 'default')
        agentname = user.get('agentid', 'default')
        G_id = user.get('gid', 'default')
    except AttributeError:
        return {
    "speech": speechdenied,
    "displayText": speechdenied,
    "source": "Default Welcome Intent"
    }

    speech = ("Hi agent: "+str(agentname)+ '\n' '\n'
             "U are a verified user of this bot." '\n'
             "This bot is created for Portal Reset requests." '\n' '\n'
             "By clicking on Continue i will ask u all the info needed." '\n''\n'
             "Before U continue please make sure this is ur Telgram account" '\n'
             "Telegram Username: @"+str(tg_user)+ '\n''\n'
             "Yes this is my Telegram account and i want to /Continue_with_the_req")
    print("response:")
    print(speech)
    return {
    "speech": speech,
    "displayText": speech,
    "source": "Default Welcome Intent"
    }
if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    print ("Starting app on port %d" %(port))
    app.run(debug=True, port=port, host='0.0.0.0')

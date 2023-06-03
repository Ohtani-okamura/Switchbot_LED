import requests
import json
import time
import hashlib
import hmac
import base64
import uuid
import os

# Declare empty header dictionary
apiHeader = {}
# open token
token = os.environ["SWITCHBOT_TOKEN"] # copy and paste from the SwitchBot app V6.14 or later
# secret key
secret = os.environ["SECRET"] # copy and paste from the SwitchBot app V6.14 or later
nonce = uuid.uuid4()
t = int(round(time.time() * 1000))
string_to_sign = '{}{}{}'.format(token, t, nonce)

string_to_sign = bytes(string_to_sign, 'utf-8')
secret = bytes(secret, 'utf-8')

sign = base64.b64encode(hmac.new(secret, msg=string_to_sign, digestmod=hashlib.sha256).digest())
print ('Authorization: {}'.format(token))
print ('t: {}'.format(t))
print ('sign: {}'.format(str(sign, 'utf-8')))
print ('nonce: {}'.format(nonce))

#Build api header JSON
apiHeader['Authorization']=token
apiHeader['Content-Type']='application/json'
apiHeader['charset']='utf8'
apiHeader['t']=str(t)
apiHeader['sign']=str(sign, 'utf-8')
apiHeader['nonce']=str(nonce)

##いらない！！！
# response1=\
#     requests.get("https://api.switch-bot.com/v1.1/devices",headers=apiHeader)
# print(response1.text)

# response2=\
#     requests.get("https://api.switch-bot.com/v1.1/devices/"+os.environ["DEVICE"]+"/status",headers=apiHeader)
# print(response2.text)


def get_power():
    try:
        res=requests.get("https://api.switch-bot.com/v1.1/devices/"+os.environ["DEVICE"]+"/status",headers=apiHeader)
        res.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(e)
    else:
        json_res=res.json() 
    power=json_res["body"]["power"]
    return power

def get_weather():
    try:
        res=requests.get("https://weather.tsukumijima.net/api/forecast/city/"+str(os.environ["CITY_CODE"]))
        res.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(e)
    else:
        json_res=res.json()
        # return json_res
    rain=json_res["forecasts"][0]["chanceOfRain"]
    for w in rain:
        if not rain[w]=='--%':
            return rain[w]

power=get_power()

def rgb_set(rain):
    if rain == "0%":
        lightOn('255:128:0')
    elif rain == "10%":
        lightOn('210:148:0')
    elif rain == "20%":
        lightOn('200:200:0')
    elif rain == "30%":
        lightOn('170:255:0')
    elif rain == "40%":
        lightOn('153:204:255')
    elif rain == "50%":
        lightOn('102:178:255')
    elif rain == "60%":
        lightOn('51:153:255')
    elif rain == "70%":
        lightOn('0:128:255')
    elif rain == "80%":
        lightOn('0:0:255')
    elif rain == "90%":
        lightOn('0:0:204')
    elif rain == "100%":
        lightOn('0:0:153')

def lightOn(rgb):
    turnOn={
        "command":"turnOn",
        "parameter":"default",
       "commandType":"command"
    }
    turnOff={
        "command":"turnOff",
        "parameter":"default",
        "commandType":"command"
    }
    setColor={
    "command":"setColor",
    "parameter":rgb,
    "commandType":"command"
    }
    if power=="on":
        try:
            post = requests.post("https://api.switch-bot.com/v1.1/devices/"+os.environ["DEVICE"]+"/commands",headers=apiHeader,json=setColor)
            post.raise_for_status()
            print(post.text)
        except requests.exceptions.RequestException as e:
            print('response error:',e)

weather=get_weather()
print(json.dumps(weather,indent=1,ensure_ascii=False))
rgb_set(weather)

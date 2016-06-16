from flask import *
from flask_cors import CORS, cross_origin
import requests
import sys

CVFY_TARGET = 'local'
CVFY_INJECTION_SUBPATH = '/inject'

app = Flask(__name__)
cors = CORS(app)

#################################
## common validation functions ##
#################################

def validateTOKEN(function_name):
    try:
        assert isinstance(TOKEN, str)
    except Exception as e:
        if (e.__class__.__name__ == 'NameError'):
            raise NameError("cvfy [Error Code: 001] => TOKEN undefined: {0} called before registering the app".format(function_name))
        elif (e.__class__.__name__ == 'AssertionError'):
            raise AssertionError("cvfy [Error Code: 002] => TOKEN not a string: {0} called with an invalid TOKEN value".format(function_name))          
    try:
        if (TOKEN.split(':')[0] == 'gh'):
            assert TOKEN.split(':')[1] == 'local'
            assert int(TOKEN.split(':')[3])
            assert int(TOKEN.split(':')[4])
        else:
            raise AssertionError 
    except Exception as e:
        if (e.__class__.__name__ == 'AssertionError'):
            raise ValueError("cvfy [Error Code: 003] => Malformed Token")  

##########
## CORS ##
##########

def crossdomain(*args, **kwargs):
    return (cross_origin)
    
####################
## app decorators ##
####################

def override_route(route):
    def wrapper(*args, **kwargs):
        return (route('/event', methods=['POST', ]))
    return wrapper
    
def override_run(runner, TOKEN):
    def wrapper(*args, **kwargs):
        return (runner('0.0.0.0', int(TOKEN.split(':')[4])))
    return wrapper
    
##################
## app register ##
##################
    
def register(APP_TOKEN):
    global TOKEN
    TOKEN = APP_TOKEN
    validateTOKEN(sys._getframe().f_code.co_name)
    app.listen = override_route(app.route)
    app.run = override_run(app.run, TOKEN)
    return app
    
#####################
## input functions ##
#####################

def getTextArray():
    validateTOKEN(sys._getframe().f_code.co_name)    
    textdata = []
    i = 0
    try:
        while True:
            textdata.append(request.form['input-text-{}'.format(i)])
            i += 1
    except Exception as e:
        pass
    return textdata        
            
        
        
######################
## output functions ##
######################

def sendTextArray(data):
    validateTOKEN(sys._getframe().f_code.co_name)
    tempval = data
    if (isinstance(data, basestring if (sys.version_info[0] == 2) else str) or isinstance(data, list) or isinstance(data, tuple)):
        data = json.dumps(data)
    else:
        raise ValueError("cvfy [Error Code: 005] => sendTextArray can only accept a string or an array or a tuple")
    for element in tempval:
        if (not isinstance(element, basestring if (sys.version_info[0] == 2) else str)):
            raise ValueError("cvfy [Error Code: 006] => iterable is not composed of strings")
    try:
        headers = {'Content-Type': 'application/json'}
        if (CVFY_TARGET == 'local'):
            url = 'http://0.0.0.0:' + TOKEN.split(':')[3] + CVFY_INJECTION_SUBPATH
            r = requests.post(url, headers=headers, data=data)
            if (r.status_code == 400):
                raise Exception("cvfy [Error Code: 007] => 400: Bad Request - app server says malformed request")
            elif (r.status_code == 500):
                raise Exception("cvfy [Error Code: 008] => 500: Internal Server Error - app server cannot handle your request")
            elif (r.status_code == 404):
                raise Exception("cvfy [Error Code: 009] => 404: Not Found - app server cannot be found; {0} is unreachable".format(url))
            elif (r.status_code == 200):
                return r.text
    except Exception as e:
        if (e.__class__.__name__ == 'ConnectionError'):
            raise Exception("cvfy [Error Code: 010] => Connection Error")
            
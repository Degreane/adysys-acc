'''
BackEnd API Server
'''

import base64
import os
import pathlib
import sys
from hashlib import md5

from Crypto import Random
from Crypto.Cipher import AES
from sanic import Sanic, response
from sanic_session import Session

BLOCK_SIZE = 16


def initPaths():
    paths = {
        'home': pathlib.Path.home()
    }

    paths['cfg'] = os.path.join(paths['home'], '.AdySysAcc', 'config.cfg')
    if not os.path.exists(os.path.dirname(paths['cfg'])):
        pathlib.Path(os.path.dirname(paths['cfg'])).mkdir(parents=True)
    return paths


def trans(key):
    try:
        theReturn = md5(key).digest()
    except Exception as Ex:
        theReturn = md5(key.encode('utf-8')).digest()
    finally:
        return theReturn


def encrypt(message, passphrase):
    passphrase = trans(passphrase)
    IV = Random.new().read(BLOCK_SIZE)
    aes = AES.new(passphrase, AES.MODE_CFB, IV)
    return base64.b64encode(IV + aes.encrypt(message))


def decrypt(encrypted, passphrase):
    passphrase = trans(passphrase)
    encrypted = base64.b64decode(encrypted)
    IV = encrypted[:BLOCK_SIZE]
    aes = AES.new(passphrase, AES.MODE_CFB, IV)
    return aes.decrypt(encrypted[BLOCK_SIZE:])


def initConf(cfg=None):
    '''
    Get the Configuration parameters
    Should be located in home directory
    if not then createIt and reply with default Config params.
    '''
    if cfg is not None:
        pass
    else:
        sys.exit(-1)


def initSanic():
    '''
    Initialize the webAPI server
    '''
    app = Sanic('Acc_Api')
    Session(app)
    return app


def runSanic(app: Sanic = None, port=6911, host='0.0.0.0'):
    '''
    Run the webAPI server
    '''
    if app is not None and isinstance(app, Sanic):
        app.run(port=port, host=host, workers=os.cpu_count())


def stopSanic(app: Sanic = None):
    '''
    Gracefully stop the webAPI server
    '''
    if app is not None and isinstance(app, Sanic) and app.is_running:
        app.stop()


def new_sid(request):
    sid = {
        'sid': request['session'].sid
    }
    print(sid)
    return False, sid


def addRoute(app, route, methods=['GET'],
             middlewares=[], name=None, asynchronous=True):
    '''
        Route to add to the application
        middlewares is a list of functions that returns (True/False,response_to_be_replied)
            if True then move to next function
            if False then return the response_to_be_replied
        name is the routeName
    '''
    if len(middlewares) > 0 and asynchronous is True:
        @app.route(route, methods=methods)
        async def theRoute(request):
            theResponse = {}
            for middleware in middlewares:
                verdict, resp = middleware(request)
                if verdict is False:
                    theResponse = resp
                    break
            return response.json(theResponse)


paths = initPaths()
app = initSanic()
addRoute(app, '/new', methods=['POST'], middlewares=[new_sid])
if __name__ == "__main__":

    runSanic(app)

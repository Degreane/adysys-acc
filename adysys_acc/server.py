
from sanic import Sanic, response
from sanic_session import Session
import jinja2
import os
from configparser import ConfigParser
import pathlib
from base64 import decodebytes, encodebytes
import json
from tinydb import Query, TinyDB
import requests


def initServer(name='AdySysAccServer', **cfg):
    app = Sanic(name)
    Session(app)
    return app


def initDB():
    # print('Checking DB')
    db = TinyDB(os.path.join(pathlib.Path.home(), '.AdySysAcc', 'auth.tdb'))
    User = Query()
    admins = db.search((User.groups.exists()) & User.groups.any(['admin']))
    # print(admins)
    if len(admins) > 0:
        # print('Admins Exist')
        db.close()
        return admins
    else:
        insertedAdmin = {
            'name': 'Admin User',
            'username': 'admin',
            'password': 'nimdapass',
            'groups': ['admin'],
            'enabled': True
        }
        db.insert(insertedAdmin)
        db.close()


def hooks(app=None, hookType='before_server_start', hook=[]):
    '''
    @app.listener('before_server_start')
    This function declares hooks possible hookTypes are
    before_server_start
    after_server_start
    before_server_stop
    after_server_stop
    '''
    if app is not None and isinstance(app, Sanic):
        if hookType is 'before_server_start' and len(hook) == 1:
            @app.listener('before_server_start')
            def bStart(app, loop):
                ret = hook[0]()


def read_file(file=None):
    if file is not None:
        content = ''
        with open(file, 'r') as fd:
            content = fd.read()
        # print(content)
        return content
    else:
        return 'No File To Read : {0}'.format(file)


def home(request, html):
    if not request['session'].get('loggedIn'):
        return read_file(os.path.join(www_dir, 'www', 'login.html')), True


def logIn(request, db, docID):
    '''
        Get
            1- get request['session'].sid
            2- set table to work with to the docID

    '''
    requestSessionID = request['session'].sid
    User = Query()
    print('Getting By DocID')
    theDoc = db.get(doc_id=docID)
    print(dir(theDoc))
    print(theDoc.doc_id)
    print(theDoc.eid)
    print(theDoc.__doc__)
    # db.update(set('sessionshints': ['SomeSessionHints']), doc_id == docID)
    # if not db.search(User['sessions'].exists()):
    #     sessions=set([requestSessionID])
    # else:
    #     sessions=db.search(User.doc_id == docID)
    # db.update()
    user_table = db.table(name='user_{0}'.format(docID))
    print(db.tables(), requestSessionID)


def authUserDB(db, credentials={}):
    '''
    with credentials we connect to tinyDB table 'auth'
    if 'auth' succeeds then return true
    return false
    '''
    print('authenticating User')

    User = Query()
    authedUser = db.search((User['username'] == credentials['user']) & (User['password'] == credentials['password']) & (User['enabled'] == True))
    print(authedUser)
    # db.close()
    if len(authedUser) > 0:
        print("UserAuthenticated With ", authedUser[0].doc_id)
        return authedUser[0].doc_id
    else:
        return False


def authenticate(request, html):
    '''
    in authenticate middleware function we get request.form
    request.form should contain a 'cn' key with value of []
    our interest is in first value [0] then we encode it with 'utf-8' to make it binary
    the load it to json and thus we have a jsString with auth

    authedUser shall hold the doc_id of the authenticated user thus we shall call logIn with the user being authenticated.
    '''
    # print(request.body, request.raw_args)
    # print(decodebytes(str(request.form['cn'][0]).encode('utf-8')))
    jsString = json.loads(decodebytes(str(request.form['cn'][0]).encode('utf-8')))
    credentials = {
        'user': jsString['u'],
        'password': jsString['p']
    }
    db = TinyDB(os.path.join(pathlib.Path.home(), '.AdySysAcc', 'auth.tdb'))
    authedUser = authUserDB(db, credentials=credentials)
    if authedUser is not False:
        logIn(request, db, authedUser)
        return '', True
    else:
        return read_file(os.path.join(www_dir, 'www', 'login.html')), False


def addRoutes(app, route, methods=['GET'], middleware=[], asynchronous=True, **argsv):
    if len(middleware) > 0 and asynchronous is True:
        @app.route('{0}'.format(route), methods=methods)
        async def addRoute(request):
            html = ''
            try:
                for func in middleware:
                    html, _continue = func(request, html)
                    if _continue is not True:
                        break
            except Exception as Ex:
                return response.text("Exception :{0}".format(Ex))
            return response.html(html)


def addStaticRoutes(app, route, path, name):
    if name not in app.router.routes_static_files:
        print('adding Static Route {0} => {1} AS : {2}'.format(route, path, name))
        app.static(route, path, name=name)


def runServer(app, port=6910, host='0.0.0.0'):
    app.run(port=port, host=host)


def getIniConfig():
    cfg = ConfigParser()
    cfg.read(os.path.join(pathlib.Path.home(), '.AdySysAcc', 'config.cfg'))
    return cfg


cfg = getIniConfig()
www_dir = cfg['DEFAULT']['work_dir']
app = initServer()
'''
register hooks
'''
hooks(app, hook=[initDB])

'''
Load Routes
'''
addRoutes(app, '/', middleware=[home])
addRoutes(app, '/lgn', middleware=[authenticate, home], methods=['GET', 'POST'])

'''
Load Static Libraries
'''
addStaticRoutes(app, '/bootstrap', os.path.join(
    www_dir, 'www', 'bootstrap'
), name='BootStrap')
addStaticRoutes(app, '/assets', os.path.join(
    www_dir, 'www', 'assets'
), name='assets')
addStaticRoutes(app, '/styles', os.path.join(
    www_dir, 'www', 'styles'
), name='style.css')


if __name__ == '__main__':
    '''
        If We are on main script then run the software
    '''
    print('starting Server')
    runServer(app)

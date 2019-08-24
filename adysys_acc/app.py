'''
BackEnd for FrontEnd (server=>Client)
'''
import os

from requests import Request, Session
from sanic import Sanic, response
from sanic_session import Session as sSession

'''
initialize the server
'''
app = Sanic('Acc')
sSession(app)


def initConf():
    import os
    import pathlib
    from configparser import ConfigParser
    home_page = pathlib.Path.home()
    cfg_file = os.path.join(home_page, '.AdySysAcc', 'config.cfg')
    cfg = ConfigParser()
    cfg.read(cfg_file, encoding='utf-8')
    # print(dir(cfg))
    # print(cfg.sections())
    # print(cfg.default_section)
    # if 'work_dir' in defaultSections:

    # print(list(cfg['{0}'.format(cfg.default_section)]))
    # for item in cfg['{0}'.format(cfg.default_section)]:
    #     print(item)
    return cfg


cfg = initConf()


def read_page(page):
    if page is not None and os.path.exists(page):
        with open(page, 'r', encoding='utf-8') as f:
            resp = f.read()
        return resp
    else:
        return '<html><body><h1>404 : Page {0} Not Found </h1></body></html>'.format(
            page)


def read_file(file):
    if file is not None and os.path.exists(file):
        with open(file, 'r') as f:
            resp = f.read()
        return resp


'''
Define Static Routes
'''
app.static(
    '/bootstrap',
    os.path.join(
        cfg['DEFAULT']['work_dir'],
        'www',
        'bootstrap'),
    name='bs4')
app.static(
    '/assets',
    os.path.join(
        cfg['DEFAULT']['work_dir'],
        'www',
        'assets'),
    name='assets')
app.static(
    '/styles',
    os.path.join(
        cfg['DEFAULT']['work_dir'],
        'www',
        'styles'),
    name='styles')

'''
Define Dynamic Routes
'''


def prepare_api_request(data, url, method='POST'):
    '''
    prepare request to get resources from the api
    :param data:
    :param url:
    :param method:
    :return: the prepared request along with the associated session.
            The session returned shall be included in the request['session'] server for this client and thus if subsequent requests are to be invoked
            the session saved shall be used
    '''
    if not isinstance(data, dict):
        return None, None
    api_session = Session()
    api_request_data = data
    url = url
    api_request = Request(
        method=method,
        url=url,
        data=api_request_data)
    api_request_prepared = api_request.prepare()
    return api_request_prepared, api_session


@app.route('/', methods=['GET'], name='defaultRoute')
async def defaultGet(request):
    '''
    Define Basic Route
    - get the session id (sid)
    - check if seen already defined
    - if not seen then send a request to api_server asking for new_sid (http://127.0.0.1:6911/new)
        then set the response from the api_server to seen and reply with home_page

    - get if the user authenticated (is_authd)

    '''
    # print('Initialized Configs are {0}'.format(list(cfg)))
    sid = request['session'].sid
    www_dir = os.path.join(cfg['DEFAULT']['work_dir'], 'www')
    if request['session'].get('seen') is not None:
        '''
        Request Has been seen before
        '''
        if request['session'].get('is_authd') is True:
            # request Authenitcated and logged In

            tpl = read_page(os.path.join(www_dir, 'index.html'))
            return response.html(tpl)
            # return response.text('client is authed with sid {0}'.format(sid))
        else:
            # Request Not Authenticated should popup login Panel
            tpl = read_page(os.path.join(www_dir, 'login.html'))
            return response.html(tpl)
            # request['session']['is_authd'] = True
            # return response.text('This is just simple home request on Get
            # Session({0}) not authd \n\tauthing '.format(sid))
    else:
        # Seen Not Seen Requesting New SID
        # Create api session to send to backend api server
        api_Session = Session()
        api_request_data = {
            'sid': sid
        }                                                                       # api_data to send (we send the sid thus back end should be able to handle sid)
        # method is POST
        method = 'POST'
        url = 'http://127.0.0.1:6911/new'
        # request['session']['seen'] = True
        api_request = Request(
            method=method,
            url=url,
            data=api_request_data)    # the request
        # the request prepared
        api_request_prepared = api_request.prepare()
        try:
            # the session response is actually the session object with method
            # send(theRequest)
            api_session_response = api_Session.send(api_request_prepared)
            if api_session_response.headers['Content-Type'] == 'application/json' and api_session_response.status_code == 200:
                '''
                set request[session]['seen'] = sid
                where sid is the request sid got from the api_server
                '''
                request['session']['seen'] = api_session_response.json()['sid']
                # Get CFG['DEFAULT']['work_dir']
                tpl = read_page(os.path.join(www_dir, 'login.html'))
                return response.html(tpl)
            else:
                return response.html(
                    '<html><body><h1>ERR: {0}</h1><br>{1}</body></html>'.format(sid, api_session_response.headers))
        except Exception as eid:
            return response.html(
                '<html><body><h1>ERR Ex: {0}</h1><br>{1}</body></html>'.format(sid, eid))


@app.route('/asset/<path:path>', methods=['GET'], name='EncryptedData')
async def encData(request, path):
    '''
    Should Return the obfuscated data based}
    :param request:
    :return:
    '''
    # let us prepare for the request
    return response.text('console.log("returned Data")')


@app.route('/favicon.ico')
async def favicon(request):
    faviconFile = os.path.join(
        cfg['DEFAULT']['work_dir'],
        'www',
        'Images',
        'browser.svg')

    return await response.file_stream(faviconFile)


@app.route('/lgn', methods=['POST'], name='LogInPost')
async def lgn(request):
    '''
    Connect to backend api_server with the seen encryption
    for lgn we shall invoke new request session to be saved
    - get the seen session property
    - prepare a request to be sent to backend with seen as passphrase
    :param request:
    :return:
    '''
    seen = request['session'].get('seen')
    print(seen)
    # prepared_request,prepared_request_session=prepare_api_request()
    print(dir(request))
    print(request.body)
    return response.text(seen)
app.run(host='0.0.0.0', port=6910)

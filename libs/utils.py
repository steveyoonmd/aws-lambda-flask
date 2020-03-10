import hashlib
import secrets
from base64 import b64encode
from functools import update_wrapper

import pymysql
from flask import current_app, g, request, make_response

from libs.enums import Error


def md5hex(plain_text):
    m = hashlib.md5()
    m.update(plain_text.encode('utf-8'))

    return m.hexdigest()


def with_origin():
    origin = g.req.headers.get('Origin', '')

    if origin not in g.cfg['access_allowed_http_origins']:
        origin = g.cfg['access_allowed_http_origins'][0]

    return {
        'Access-Control-Allow-Origin': origin,
        'Access-Control-Allow-Methods': 'DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT',
        'Access-Control-Allow-Headers': 'Authorization, Content-Type, Cookie, Origin, X-Amz-Date, '
                                        'X-Amz-Security-Token, X-Api-Key, x-forced-preflight',
        'Access-Control-Allow-Credentials': 'true',
    }


# https://stackoverflow.com/questions/26980713/solve-cross-origin-resource-sharing-with-flask
def respond_if_options():
    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if request.method == 'OPTIONS':
                opts_resp = current_app.make_default_options_response()
            else:
                opts_resp = make_response(f(*args, **kwargs))

            headers = with_origin()
            for key, value in headers.items():
                opts_resp.headers[key] = value

            return opts_resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)

    return decorator


def remote_ip_addr_ends_with_asterisk():
    remote_ip_addr = g.req.remote_addr
    if g.req.headers.getlist('X-Forwarded-For'):
        remote_ip_addr = g.req.headers.getlist('X-Forwarded-For')[0]

    remote_ip_addr_split = remote_ip_addr.split('.')
    remote_ip_addr_split.pop()
    remote_ip_addr_split.append('*')

    return '.'.join(remote_ip_addr_split)


def is_access_allowed_ip_addr():
    if remote_ip_addr_ends_with_asterisk() in g.cfg['access_allowed_ip_addrs_end_with_asterisk'].keys():
        return True

    g.res.err = Error.ACCESS_NOT_ALLOWED_IP_ADDR
    return False


def is_user_logged_in():
    if 'user_id' not in g.sess or g.sess.get('user_id', '') == '':
        g.res.err = Error.USER_LOGIN_REQUIRED
        g.res.url = './users_login.html'
        return False

    return True


def connect_database(key):
    if key in g.curso:
        return
    
    g.db[key] = pymysql.connect(host=g.cfg['database_' + key]['host'], user=g.cfg['database_' + key]['user'],
                                password=g.cfg['database_' + key]['password'],
                                charset=g.cfg['database_' + key]['charset'],
                                database=g.cfg['database_' + key]['database'], port=g.cfg['database_' + key]['port'],
                                cursorclass=pymysql.cursors.DictCursor)
    g.cursor[key] = g.db[key].cursor()


def is_valid_csrf_token(csrf_token):
    if 'csrf_token' not in g.req.cookies or csrf_token != g.req.cookies['csrf_token']:
        g.res.err = Error.CSRF_TOKEN_INVALID
        return False

    return True


def escape_str(s):
    return pymysql.escape_string(s)


def make_resp():
    resp = make_response(g.res)

    headers = with_origin()
    for key, value in headers.items():
        resp.headers[key] = value

    resp.set_cookie('csrf_token', b64encode(secrets.token_bytes(16)).decode('utf-8').replace('+', '_'))
    return resp

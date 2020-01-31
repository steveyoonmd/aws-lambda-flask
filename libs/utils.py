
from functools import update_wrapper

from flask import current_app, request, make_response


origins = [
    'http://ec2-52-79-228-44.ap-northeast-2.compute.amazonaws.com:5000',
]


def with_origin(req):
    origin = req.headers.get('Origin', '')

    if origin not in origins:
        origin = origins[0]

    return {
        'Access-Control-Allow-Origin': origin,
        'Access-Control-Allow-Methods': 'DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT',
        'Access-Control-Allow-Headers': 'Authorization, Content-Type, Cookie, Origin, X-Amz-Date, X-Amz-Security-Token, X-Api-Key, x-forced-preflight',
        'Access-Control-Allow-Credentials': 'true',
    }


def make_resp(req, body):
    resp = make_response(body)

    headers = with_origin(req)
    for key, value in headers.items():
        resp.headers[key] = value

    return resp


# https://stackoverflow.com/questions/26980713/solve-cross-origin-resource-sharing-with-flask
def respond_if_options():
    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if request.method == 'OPTIONS':
                opts_resp = current_app.make_default_options_response()
            else:
                opts_resp = make_response(f(*args, **kwargs))

            headers = with_origin(request)
            for key, value in headers.items():
                opts_resp.headers[key] = value

            return opts_resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)

    return decorator

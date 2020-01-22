
from functools import update_wrapper

from flask import current_app, make_response, request
from aws_lambda import AwsLambdaFlask


origins = [
    'http://wematch.com'
]


def get_headers_with_origin(request):
    origin = request.headers.get('Origin', '')

    if origin not in origins:
        origin = origins[0]

    return {
        'Access-Control-Allow-Origin': origin,
        'Access-Control-Allow-Methods': 'OPTIONS, GET, POST, DELETE',
        'Access-Control-Allow-Headers': 'Origin, Cookie, Content-Type, x-forced-preflight',
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

            opts_resp.headers = get_headers_with_origin(request)
            return opts_resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)

    return decorator


def make_response_with_origin(request, body):
    resp = make_response(body)
    resp.headers = get_headers_with_origin(request)

    return resp


def server():
    app = AwsLambdaFlask(__name__, static_folder='static', static_url_path='/static') #, template_folder='templates')

    @app.route('/', methods=['OPTIONS', 'GET', 'POST'])
    @respond_if_options()
    def index():
        return make_response_with_origin(request, {'status': 'OK'})

    return app

run = server()

# ISC License

# Copyright (c) 2018-2020 Adam Johnson

# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.

# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.

# https://github.com/adamchainz/apig-wsgi

import sys
from io import BytesIO

from flask import Flask


def wsgi_env(evt):
    env = {
        'REQUEST_METHOD': evt['httpMethod'],
        'PATH_INFO': evt['path'],
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '80',

        'wsgi.version': (1, 0),
        'wsgi.errors': sys.stderr,
        'wsgi.input': None,
        'wsgi.url_scheme': '',
        'wsgi.run_once': False,
        'wsgi.multiprocess': False,
        'wsgi.multithread': False,
    }
        
    query_string_parameters = evt.get('queryStringParameters', {}) or {}
    env['QUERY_STRING'] = '&'.join('{}={}'.format(k, v) for (k, v) in query_string_parameters.items())

    body = evt.get('body', '') or ''
    if evt.get('isBase64Encoded', False):
        body = b64decode(body)
    else:
        body = body.encode('utf-8')

    env['CONTENT_LENGTH'] = str(len(body))
    env['wsgi.input'] = BytesIO(body)

    headers = evt.get('headers', {}) or {}
    for key, value in headers.items():
        key = key.upper().replace('-', '_')

        if key == 'CONTENT_TYPE':
            env['CONTENT_TYPE'] = value
        elif key == 'HOST':
            env['SERVER_NAME'] = value
        elif key == 'X_FORWARDED_PORT':
            env["SERVER_PORT"] = value
        elif key == 'X_FORWARDED_FOR':
            env['REMOTE_ADDR'] = value.split(', ')[0]
        elif key == 'X_FORWARDED_PROTO':
            env['wsgi.url_scheme'] = value

        env['HTTP_' + key] = value

    return env


class AwsAPIGatewayResponse:
    def __init__(self):
        self.statusCode = '200'
        self.headers = []
        self.body = BytesIO()

    def start_resp(self, status_code, headers, exc_info=None):
        if exc_info is not None:
            raise exc_info[0](exc_info[1]).with_traceback(exc_info[2])

        self.statusCode = status_code[:3]
        self.headers.extend(headers)

        return self.body.write

    def write_body(self, body):
        try:
            for data in body:
                if data:
                    self.body.write(data)
        finally:
            if hasattr(body, 'close'):
                body.close()

    def as_dict(self):
        return {
            'statusCode': self.statusCode,
            'headers': dict(self.headers),
            'body': self.body.getvalue().decode('utf-8'),
        }


class AwsLambdaFlask(Flask):
    def __call__(self, evt, ctx):
        if 'httpMethod' not in evt:
            return super(AwsLambdaFlask, self).__call__(evt, ctx)

        resp = AwsAPIGatewayResponse()
        resp.write_body(self.wsgi_app(wsgi_env(evt), resp.start_resp))

        return resp.as_dict()

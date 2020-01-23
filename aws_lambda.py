# Copyright 2016 Matt Martz
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


# https://github.com/sivel/flask-lambda
# https://github.com/techjacker/flask-lambda

import sys
from io import StringIO
from typing import Dict, Any, Union
from urllib.parse import urlencode

from flask import Flask


class AwsLambdaRequest:
    env: Dict[Union[str, Any], Union[Union[str, StringIO], Any]]

    def __init__(self, evt):
        self.env = {
            'REQUEST_METHOD': '',
            'PATH_INFO': '',
            'QUERY_STRING': '',
            'SERVER_PROTOCOL': 'HTTP/1.1',
            'CONTENT_TYPE': '',
            'CONTENT_LENGTH': '',
            'REMOTE_ADDR': '',
            'HTTP_X_FORWARDED_PROTO': '',
            'SERVER_NAME': 'SERVER_NAME',
            'SERVER_PORT': '',
    
            'wsgi.version': (1, 0),
            'wsgi.errors': sys.stderr,
            'wsgi.input': None,
            'wsgi.url_scheme': '',
            'wsgi.run_once': True,
            'wsgi.multiprocess': False,
            'wsgi.multithread': False,
        }

        headers = evt.get('headers', {}) or {}
        for k, v in headers.items():
            k = k.replace('-', '_').upper()

            if k in ['CONTENT_TYPE', 'CONTENT_LENGTH']:
                self.env[k] = v
                continue

            n = 'HTTP_{}'.format(k)
            self.env[n] = v
        
        self.env['REQUEST_METHOD'] = evt.get('httpMethod', '')
        self.env['PATH_INFO'] = evt.get('path', '')

        query_string_parameters = evt.get('queryStringParameters', '')
        if query_string_parameters:
            self.env['QUERY_STRING'] = urlencode(query_string_parameters)

        body = evt.get('body', '')
        if body:
            self.env['CONTENT_LENGTH'] = str(len(body))
            self.env['wsgi.input'] = StringIO(body)

        self.env['REMOTE_ADDR'] = evt['requestContext']['identity']['sourceIp']
        self.env['SERVER_PORT'] = self.env.get('HTTP_X_FORWARDED_PORT', '')
        self.env['wsgi.url_scheme'] = self.env.get('HTTP_X_FORWARDED_PROTO', '')


class AwsLambdaResponse:
    def __init__(self):
        self.statusCode = '200'
        self.headers = {}
        self.body = ''

    def put_headers(self, status_code, headers, exc_info=None):
        self.statusCode = status_code[:3]
        self.headers = dict(headers)

    def as_dict(self):
        return {
            'statusCode': self.statusCode,
            'headers': self.headers,
            'body': self.body,
        }


class AwsLambdaFlask(Flask):
    def __call__(self, evt, ctx):
        if 'httpMethod' not in evt:
            return super(AwsLambdaFlask, self).__call__(evt, ctx)
        
        req = AwsLambdaRequest(evt)
        resp = AwsLambdaResponse()

        try:
            resp.body = next(self.wsgi_app(
                req.env,
                resp.put_headers
            )).decode('utf-8')

        except StopIteration:
            pass

        except Exception as ex:
            print(ex)  # for aws cloudWatch logs

            resp.statusCode = '500'
            resp.body = 'internal server error'

        finally:
            return resp.as_dict()

from flask import Blueprint, g, current_app, session, request

from libs.dict_as_obj import DictAsObj
from libs.enums import Error
from libs.utils import respond_if_options, is_access_allowed_ip_addr, md5hex, make_resp

users = Blueprint('users', __name__, url_prefix='/users')


@users.before_request
def before_request():
    g.cfg = current_app.config['G_CFG']
    g.sess = session
    g.req = request
    g.res = DictAsObj({
        'err': Error.UNKNOWN,
        'url': '',
        'dat': None,
    })

    g.db = {}
    g.cursor = {}


@users.teardown_request
def teardown_request(ex=None):
    for key in g.cursor.keys():
        g.cursor[key].close()

    for key in g.db.keys():
        g.db[key].close()


@users.route('/login', methods=['OPTIONS', 'POST'])
@respond_if_options()
def login():
    if not is_access_allowed_ip_addr():
        return make_resp()

    req_json = request.get_json()
    user_id = req_json.get('user_id')
    md5_hash = req_json.get('md5_hash')
    return_url = req_json.get('return_url', '/')

    if user_id == 'user1' and md5_hash == md5hex(user_id + md5hex('password1')):
        g.sess['user_id'] = 'steve'

        g.res.err = Error.NONE
        g.res.url = return_url
        return make_resp()
    else:
        g.res.err = Error.USER_LOGIN_FAILED
        return make_resp()

    g.cursor['test1'].execute('SELECT VERSION() AS version')
    row = g.cursor['test1'].fetchone()

    g.res.err = Error.NONE
    g.res.dat = {'test_get': 'OK', 'a': request.args.get('a'), 'b': request.args.get('b'), 'version': row['version']}
    return make_resp()


@users.route('/logout', methods=['OPTIONS', 'POST'])
@respond_if_options()
def logout():
    if not is_access_allowed_ip_addr():
        return make_resp()

    g.sess['user_id'] = ''

    g.res.err = Error.NONE
    g.res.url = './users_login.html'
    return make_resp()

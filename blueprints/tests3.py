from datetime import datetime

from flask import Blueprint, g, current_app, session, request

from libs.aes_crypto import AESCrypto
from libs.dict_as_obj import DictAsObj
from libs.enums import Error
from libs.sql_alchemy import db, json_serializable
from libs.utils import respond_if_options, connect_database, is_access_allowed_ip_addr, is_user_logged_in, make_resp
from models.test1 import Test1

tests3 = Blueprint('tests3', __name__, url_prefix='/tests3')


@tests3.before_request
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

    g.sess['domain'] = g.req.headers.get('Host', g.cfg['session']['domain'])
    connect_database('test1')


@tests3.teardown_request
def teardown_request(ex=None):
    for key in g.cursor.keys():
        g.cursor[key].close()

    for key in g.db.keys():
        g.db[key].close()


@tests3.route('/test_orm', methods=['OPTIONS', 'POST'])
@respond_if_options()
def test_orm():
    if not is_access_allowed_ip_addr() or not is_user_logged_in():
        return make_resp()

    new_test1 = Test1(
        col01=255,
        col02=65535,
        col03=429496729,
        col04=1844674407370955161,
        col05=5.01,
        col06=6.01,
        col07='param7',
        col08='param8',
        col09='param9'.encode('utf-8'),
        col10='{0:%Y-%m-%d %H:%M:%S}'.format(datetime.now()),
        col12='{0:%Y-%m-%d %H:%M:%S}'.format(datetime.now()),
    )
    db.session.add(new_test1)
    db.session.commit()

    rows = json_serializable(db.session.query(Test1).order_by(Test1.test1_id.desc()).limit(1).offset(0).all())

    g.res.err = Error.NONE
    g.res.dat = {'test_orm': 'OK', 'rows': rows}
    return make_resp()


@tests3.route('/test_aes', methods=['OPTIONS', 'POST'])
@respond_if_options()
def test_aes():
    if not is_access_allowed_ip_addr() or not is_user_logged_in():
        return make_resp()

    a = AESCrypto(g.cfg['aes_crypto']['key'])
    e = a.encrypt('한글')
    d = a.decrypt(e)

    g.res.err = Error.NONE
    g.res.dat = {'test_aes': 'OK', 'e': e, 'd': d}
    return make_resp()

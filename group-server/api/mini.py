# coding: utf-8

from leancloud import Object
from leancloud import Query
from leancloud import LeanCloudError

from flask import Blueprint
from flask import request
from flask import jsonify

import urllib
import json

from common.response import BadRequest


mini = Blueprint('mini', __name__)

class UserSession(Object):
    pass


@mini.route('/login', methods=['POST'])
def login():
    try:
        code = json.loads(request.get_data())['code']
        _url = 'https://api.weixin.qq.com/sns/jscode2session?appid=wx4ce6fa524f8594c3&' \
               'secret=a12ea3c16ce994903920c36ddfab646d&js_code=%s&grant_type=authorization_code' % code
        result = urllib.urlopen(_url)
        data = json.load(result)
    except Exception:
        raise BadRequest('get openid failure')

    try:
        sessions = Query(UserSession).equal_to('openID', data['openid']).find()
    except LeanCloudError as e:
        raise e

    # print data

    if len(sessions) == 0:
        session = UserSession()
        session.set('sessionKey', data['session_key'])
        session.set('openID', data['openid'])
        try:
            session.save()
        except LeanCloudError as e:
            raise e
    else:
        session = UserSession().create_without_data(sessions[0].id).set('sessionKey', data['session_key'])
        try:
            session.save()
        except LeanCloudError as e:
            raise e

    return jsonify({'openid': data['openid']})

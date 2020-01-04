#!/usr/bin/env python
# coding: utf-8
"""
Author: iceleaf<iceleaf916@gmail.com>
Date: 2018-11-02
"""

import json
import logging
import os.path
from hashlib import md5

import requests
from django.conf import settings


def fetch_wx_access_token(appid=None, secret=None):
    if not appid:
        appid = settings.WX_APPID
        secret = settings.WX_APPSECRET
    resp = requests.post(settings.REMOTE_ACCESS_TOKEN_URL, data={'appid': appid, "secret": secret})
    data = resp.json()
    return data['data']['access_token']


def getWXACode(scene, path="/pages/home/home", is_remote=False, is_hyaline=False):
    """
    获取小程序二维码
    :return:
    """
    name = "%s?%s" % (path, scene)
    if is_hyaline:
        pic_name = "qr_%s.png" % md5(name.encode("utf-8")).hexdigest()
    else:
        pic_name = "qr_%s.jpg" % md5(name.encode("utf-8")).hexdigest()
    save_folder = os.path.join(settings.QRCODE_PATH, 'origin')
    if not os.path.exists(save_folder):
        os.mkdir(save_folder)
    save_path = os.path.join(save_folder, pic_name)
    remote_url = "%s/%s/origin/%s" % (settings.SITE_HOST, settings.QRCODE_NAME, pic_name)
    return_data = remote_url if is_remote else save_path
    if os.path.exists(save_path):
        return dict(
            code=1,
            msg='success',
            data=return_data
        )
    else:
        token = fetch_wx_access_token()
        url = 'https://api.weixin.qq.com/wxa/getwxacodeunlimit?access_token={}'.format(token)
        params = {"scene": scene,
                  "page": path,
                  "width": 512,
                  "auto_color": False,
                  "line_color": {"r": "0", "g": "0", "b": "0"},
                  "is_hyaline": is_hyaline
                  }

        headers = {'Content-Type': 'application/json'}
        resp = requests.post(headers=headers, url=url, data=json.dumps(params))
        try:
            data = json.loads(resp.text)
            logging.error("[getWXACode] errcode=%s, errmsg=%s" % (data['errcode'], data['errmsg']))
            # requests.post("http://47.110.95.9:8080/reset_access_token/", data={'appid': settings.WX_APPID})
            return dict(code=data['errcode'], msg=data['errmsg'])
        except json.JSONDecodeError:
            with open(save_path, 'wb') as fp:
                fp.write(resp.content)
            return dict(
                code=1,
                msg='success',
                data=return_data
            )


def get_wx_session(js_code, app_id):
    if app_id:
        now_app_id = app_id
        now_app_secret = settings.WEAPP_CONFIGS[app_id]['app_secret']
    else:
        now_app_id = settings.WX_APPID
        now_app_secret = settings.WX_APPSECRET

    params = dict()
    params['appid'] = now_app_id
    params['secret'] = now_app_secret
    params['js_code'] = js_code
    params['grant_type'] = 'authorization_code'
    url = 'https://api.weixin.qq.com/sns/jscode2session'
    resp = requests.get(url, params)

    # 微信服务器访问失败
    if resp.status_code != 200:
        return {
            "code": -1,
            'msg': 'weixin server error, http code: %s body: %s' % (resp.status_code, resp.text)
        }

    wx_data = resp.json()

    # 接口访问有错误消息
    if wx_data.get("errcode", 0) != 0:
        return {'code': wx_data['errcode'], 'msg': wx_data['errmsg']}

    return wx_data

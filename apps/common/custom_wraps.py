#!/usr/bin/env python
# coding: utf-8
"""
Author: iceleaf<iceleaf916@gmail.com>
Date: 2018-11-12
"""
import base64
from functools import wraps
from urllib import parse

from django.conf import settings
from django.core.cache import cache
from django.http.response import JsonResponse, HttpResponseRedirect

from app_user.models import User


def lock_user(user, keyword='withdrawal'):
    lock_name = 'lock_%s_%s' % (keyword, user.pid)
    value = cache.get(lock_name)
    if value:
        return False
    else:
        cache.set(lock_name, 1)
        return True


def unlock_user(user, keyword='withdrawal'):
    lock_name = 'lock_%s_%s' % (keyword, user.pid)
    cache.delete(lock_name)


def login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        if not token:
            token = request.POST.get('token')

        if not token:
            return JsonResponse({'code': -5000, 'msg': '非法用户'})
        try:
            user = User.objects.get(token=token)
            request.user = user
            return view_func(request, *args, **kwargs)
        except User.DoesNotExist as e:
            return JsonResponse({'code': -5000, 'msg': '非法用户'})

    return _wrapped_view


def mp_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        token = request.COOKIES.get('token')

        real_redirect_url = settings.SITE_HOST + request.path
        query_str = request.META.get('QUERY_STRING ')
        if query_str:
            real_redirect_url = "{}?{}".format(real_redirect_url, query_str)

        wx_redirect_uri = "{}{}?url={}".format(
            settings.SITE_HOST,
            "/api/wexin_mp_code_auth/",
            parse.quote_plus(base64.b64encode(real_redirect_url.encode('utf-8')))
        )
        url = "https://open.weixin.qq.com/connect/oauth2/authorize?appid={}&redirect_uri={}" \
              "&response_type=code&scope=snsapi_userinfo&state=STATE#wechat_redirect".format(
            settings.WX_MP_APPID,
            parse.quote_plus(wx_redirect_uri)
        )
        if not token:
            return HttpResponseRedirect(url)
        try:
            user = User.objects.get(token=token)
            request.user = user
            return view_func(request, *args, **kwargs)
        except User.DoesNotExist as e:
            return HttpResponseRedirect(url)

    return _wrapped_view


def app_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        token = request.COOKIES.get('token')
        status = request.COOKIES.get('status')
        real_redirect_url = settings.SITE_HOST + request.path
        query_str = request.META.get('QUERY_STRING ')
        if query_str:
            real_redirect_url = "{}?{}".format(real_redirect_url, query_str)

        wx_redirect_uri = "{}{}?url={}".format(
            settings.SITE_HOST,
            "/api/wexin_app_code_auth/",
            parse.quote_plus(base64.b64encode(real_redirect_url.encode('utf-8')))
        )
        url = "https://open.weixin.qq.com/connect/oauth2/authorize?appid={}&redirect_uri={}" \
              "&response_type=code&scope=snsapi_userinfo&state=STATE#wechat_redirect".format(
            settings.WX_MP_APPID,
            parse.quote_plus(wx_redirect_uri)
        )
        if not token:
            return HttpResponseRedirect(url)
        try:
            user = User.objects.get(token=token)
            request.user = user
            request.status = status
            return view_func(request, *args, **kwargs)
        except User.DoesNotExist as e:
            return HttpResponseRedirect(url)

    return _wrapped_view

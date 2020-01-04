#!/usr/bin/env python
# coding: utf-8
"""
Author: iceleaf<iceleaf916@gmail.com>
Date: 2018-11-14
"""

import math

import urllib3

urllib3.disable_warnings()

from constance import config

import copy

from django.conf import settings

cache = settings.REDIS_CLIENT


class JsonDict(dict):
    '''
    General json object that allows attributes to be bound to and also behaves like a dict.

    >>> jd = JsonDict(a=1, b='test')
    >>> jd.a
    1
    >>> jd.b
    'test'
    >>> jd['b']
    'test'
    >>> jd.c
    Traceback (most recent call last):
      ...
    AttributeError: 'JsonDict' object has no attribute 'c'
    >>> jd['c']
    Traceback (most recent call last):
      ...
    KeyError: 'c'
    '''

    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            raise AttributeError(r"'JsonDict' object has no attribute '%s'" % attr)

    def __setattr__(self, attr, value):
        self[attr] = value


def get_constance_settings():
    data = JsonDict()
    for key in dir(config):
        data[key] = getattr(config, key)
    return data


def get_multiline_text(draw, text, font, wrap_width):
    cur_width = 0
    text_list = []
    for c in text:
        width, hwith = draw.textsize(c, font=font)
        cur_width += width
        if cur_width > wrap_width:
            text_list.append(c)
            text_list.append("\n")
            cur_width = 0
        else:
            text_list.append(c)
    return "".join(text_list)


def get_hight_text(draw, text, font, wrap_hight):
    width1, hwith1 = draw.textsize(text, font=font)
    if hwith1 < wrap_hight:
        return text

    num = -1
    text_new = copy.copy(text)
    while True:
        text1 = text[:num]
        width, hwith = draw.textsize(text1, font=font)
        num -= 1
        if hwith < wrap_hight:
            return text_new[:num]


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_page(request, total, limit=20):
    page = request.POST.get("page")
    if not page:
        page = request.GET.get("page")
    if not page or page == "undefined":
        page = 1
    page = int(page)
    start = limit * (page - 1)
    end = start + limit
    total_page = int(math.ceil(total / limit))
    return JsonDict(
        start=start,
        end=end,
        page=page,
        total_page=total_page,
        total_count=total,
    )


def get_ip_address(request):
    """
    获取ip地址
    :param request:
    :return:
    """
    ip = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if not ip:
        ip = request.META.get('REMOTE_ADDR', "")
    client_ip = ip.split(",")[-1].strip() if ip else ""
    return client_ip


def get_cache_key(key, flag):
    return "{}_{}".format(key, flag)


def hincr_userinfo_cache_value(user_id, field, flag):
    key = get_cache_key("", user_id)
    valid_orders = cache.hget(name=key, key=field)
    if valid_orders is not None:
        if flag > 0:
            cache.hincrby(name=key, key=field)
        else:
            cache.hincrby(name=key, key=field, amount=-1)

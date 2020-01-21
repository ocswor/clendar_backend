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
import lunardate
from calendar import Calendar
from common.JieQi.SolarTerms import getjieqi_info

cache = settings.REDIS_CLIENT

day_info_dic = {
    1: "初一",
    2: "初二",
    3: "初三",
    4: "初四",
    5: "初五",
    6: "初六",
    7: "初七",
    8: "初八",
    9: "初九",
    10: "初十",
    11: "十一",
    12: "十二",
    13: "十三",
    14: "十四",
    15: "十五",
    16: "十六",
    17: "十七",
    18: "十八",
    19: "十九",
    20: "二十",
    21: "二十一",
    22: "二十二",
    23: "二十三",
    24: "二十四",
    26: "二十六",
    25: "二十五",
    27: "二十七",
    28: "二十八",
    29: "二十九",
    30: "三十",
    31: "三十一",
    32: "三十二",
}


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


ca = Calendar(firstweekday=6)


def monthdatescalendar_info(year, month):
    calendar_list = []
    jieqi_data = getjieqi_info(year)
    day_date_items = ca.monthdatescalendar(year, month)
    for day_date_list in day_date_items:
        items = []
        for day_date in day_date_list:
            yinlidate = lunardate.LunarDate.fromSolarDate(day_date.year, day_date.month, day_date.day)
            if day_date.month == month:
                disable = 0
            else:
                disable = 1
            # print(day_date, yinlidate, day_info_dic[yinlidate.day], disable)
            # yinlidate = "%d-%d-%d" % (yinlidate.year, yinlidate.month, yinlidate.day)
            yinlidate = day_info_dic[yinlidate.day]
            jieqi = jieqi_data.get(str(day_date), "")
            if jieqi:
                yinlidate = jieqi

            data_info = {
                "yangli": day_date.day,
                "yinli": yinlidate,
                "disable": disable,
                "year": year,
                "month": month
            }
            items.append(data_info)
        calendar_list.append(items)
    return calendar_list

#!/usr/bin/env python
# coding: utf-8
"""
Author: iceleaf<iceleaf916@gmail.com>
Date: 2018-12-07
"""


class BaseChoices(object):
    CHOICES = (
        (0, "禁用"),
        (1, "启用"),
    )

    @classmethod
    def get_display_name(cls, status):
        for (key, display_name) in cls.CHOICES:
            if key == status:
                return display_name

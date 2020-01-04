from django.db import models

from common.base_class import BaseChoices


class GenderChoice(BaseChoices):
    CHOICES = (
        (0, "未知"),
        (1, "男"),
        (2, "女"),
    )


# Create your models here.
class User(models.Model):
    """
    用户
    """
    unionid = models.CharField(max_length=128, null=True, blank=True, verbose_name='微信unionid', db_index=True)
    avatar_url = models.CharField(max_length=512, blank=True, verbose_name='微信头像url')
    nickname = models.CharField(max_length=256, blank=True, verbose_name='微信昵称')
    wechat_id = models.CharField(max_length=256, null=True, blank=True, verbose_name='微信号')
    token = models.CharField(max_length=32, verbose_name='token', unique=True)
    openid = models.CharField(max_length=128, null=True, blank=True, verbose_name='微信openid(小程序)', db_index=True)
    session_key = models.CharField(max_length=256, blank=True, null=True, verbose_name='session_key(小程序)')

    phone = models.CharField(max_length=11, null=True, blank=True, verbose_name='手机号')
    name = models.CharField(max_length=128, null=True, blank=True, verbose_name='姓名')
    password = models.CharField(max_length=64, null=True, blank=True, verbose_name='登录密码')
    temporary_invite_pid = models.IntegerField(verbose_name='临时代理PID', null=True, blank=True)

    gender = models.IntegerField(choices=GenderChoice.CHOICES, default=0, verbose_name='性别')
    country = models.CharField(max_length=256, verbose_name='所在国家', null=True, blank=True)
    province = models.CharField(max_length=256, verbose_name='所在省份', null=True, blank=True)
    city = models.CharField(max_length=256, verbose_name='所在城市', null=True, blank=True)

    create_time = models.DateTimeField(verbose_name='注册时间', auto_now_add=True)
    last_login_time = models.DateTimeField(verbose_name='上次登录时间', null=True, blank=True)

    def __str__(self):
        return '%s(%s)' % (self.nickname, self.id)

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name


class UserLogin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    time_grading = models.CharField(max_length=32, verbose_name='时间粒度')
    login_time = models.DateTimeField(verbose_name='登录时间')

    def __str__(self):
        return "%s(%s) login at %s" % (self.user.nickname, self.user.id, self.login_time)

    class Meta:
        verbose_name = '用户登录'
        verbose_name_plural = verbose_name

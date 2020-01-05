import logging
import time
from datetime import datetime, timedelta
from hashlib import md5

from django.conf import settings
from django.db import transaction
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from app_user.models import User, UserLogin
from common import utils
from common import weixin_utils
from common.WXBizDataCrypt import WXBizDataCrypt
from common.custom_wraps import login_required


# Create your views here.
# 微信登录接口 wx.login
@csrf_exempt
def weixin_login(request):
    js_code = request.POST.get("js_code")
    app_id = request.POST.get("app_id", "")

    # 必须传入js_code 参数
    if not js_code:
        return JsonResponse({'code': -1, 'msg': 'error js_code, js_code=%s' % js_code})

    wx_data = weixin_utils.get_wx_session(js_code, app_id)
    if wx_data.get("code"):
        return JsonResponse(wx_data)

    session_key = wx_data['session_key']
    openid = wx_data['openid']
    unionid = wx_data.get('unionid', '')

    def generate_token(openid):
        _token = "%s%s" % (openid, time.time())
        _token = md5(_token.encode('utf-8')).hexdigest()
        return _token

    token = generate_token(openid)

    user = None
    try:
        user = User.objects.get(unionid=unionid)
        is_create = False
    except User.DoesNotExist:
        pass
    except User.MultipleObjectsReturned:
        logging.error("出现重复的unionid: {}".format(unionid))
        User.objects.filter(unionid=unionid).last().delete()
        return JsonResponse(dict(code=-1, msg='数据错误,请刷新'))

    if not user:
        with transaction.atomic():
            try:
                user = User.objects.select_for_update().get(openid=openid)
                is_create = False
            except User.DoesNotExist:
                user = User.objects.create(openid=openid, token=token)
                is_create = True
            except User.MultipleObjectsReturned:
                logging.error("出现重复的openid: {}".format(openid))
                User.objects.filter(openid=openid).last().delete()

    if not user:
        return JsonResponse(dict(code=-1, msg='数据错误,请刷新'))

    status = 'new' if is_create else 'old'

    if unionid and not user.unionid:
        user.unionid = unionid
    if openid and not user.openid:
        user.openid = openid

    user.session_key = session_key
    now = datetime.now()
    if not is_create and (not user.last_login_time or now - user.last_login_time > timedelta(days=7)):
        user.token = generate_token(openid)
        user.last_login_time = now
    user.save()

    res_data = dict(
        openid=wx_data['openid'],
        token=user.token,
        status=status
    )
    return JsonResponse(dict(code=1, msg='success', data=res_data))


# 微信登录接口 wx.login
@csrf_exempt
def weixin_update_session_key(request):
    js_code = request.POST.get("js_code")
    app_id = request.POST.get("app_id", "")

    # 必须传入js_code 参数
    if not js_code:
        return JsonResponse({'code': -1, 'msg': 'error js_code, js_code=%s' % js_code})

    wx_data = weixin_utils.get_wx_session(js_code, app_id)
    if wx_data.get("code"):
        return JsonResponse(wx_data)

    session_key = wx_data['session_key']
    openid = wx_data['openid']

    User.objects.filter(openid=openid).update(session_key=session_key)

    return JsonResponse(dict(code=1, msg='success'))


# 微信授权接口
@login_required
@csrf_exempt
def weixin_auth(request):
    """
    微信授权，更新用户数据
    :param request:
    :return:
    """

    nickname = request.POST.get('nickname', None)
    avatar_url = request.POST.get('avatar_url', None)
    encrypted_data = request.POST.get('encrypted_data', None)
    iv = request.POST.get('iv', None)
    js_code = request.POST.get("js_code", None)
    app_id = request.POST.get("app_id", "")

    # 必须传入的参数
    if nickname is None or avatar_url is None:
        return JsonResponse({'code': -1, 'msg': 'error params, nickname and avatar_url is required'})

    user = request.user
    user.nickname = nickname
    user.avatar_url = avatar_url

    if encrypted_data and iv:
        if js_code:
            session_data = weixin_utils.get_wx_session(js_code, app_id)
            if session_data.get('session_key'):
                user.session_key = session_data.get("session_key")
                user.save()

        session_key = user.session_key
        wx = WXBizDataCrypt(settings.WX_APPID, session_key)
        try:
            data = wx.decrypt(encrypted_data, iv)
            if 'unionId' in data:
                user.unionid = data['unionId']
            else:
                logging.error("微信授权数据无unionid, data=%s" % (data,))
            if 'openId' in data and not user.openid:
                user.openid = data['openId']
            user.gender = data.get("gender")
            user.country = data.get("country")
            user.province = data.get("province")
            user.city = data.get("city")
        except Exception as e:
            # logger.error("微信授权数据解析失败，pid=%s" % user.pid)
            return JsonResponse(dict(code=-100, msg='微信授权数据解析失败'))

    user.save()
    return JsonResponse(dict(code=1, msg='success'))


# 更新用户信息接口
@login_required
@csrf_exempt
def user_info(request):
    """
    pid, openid, agent_pid, is_agent, agent_info={'level': 'level'}
    :param request:
    :return:
    """
    user = request.user
    now = datetime.now()

    # 小程序登录统计
    time_grading = now.strftime("%Y-%m-%d")  # 按照小时的粒度进行统计
    if UserLogin.objects.filter(user=user, time_grading=time_grading).count() == 0:
        UserLogin.objects.create(
            user=user,
            time_grading=time_grading,
            login_time=now,
        )

    user.last_login_time = now
    user.save()

    return JsonResponse(dict(
        code=1,
        msg='success',
    ))


# 获取开关配置
@csrf_exempt
def get_setting(request):
    # logging.debug("test")
    settings_vaule = utils.get_constance_settings()
    return JsonResponse(dict(
        code=1,
        msg='success',
        settings=settings_vaule
    ))

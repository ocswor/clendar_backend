from django.urls import path

from app_api import views as api_views
from app_user import views as user_views

urlpatterns = [
    # login, auth, bind and user info
    path("weixin_login/", user_views.weixin_login),
    path("weixin_update_session_key/", user_views.weixin_update_session_key),
    path("weixin_auth/", user_views.weixin_auth),
    path("user_info/", user_views.user_info),
    path("get_setting/", user_views.get_setting),
    path("get_calendar/", api_views.get_calendar),
]

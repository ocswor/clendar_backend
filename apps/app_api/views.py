from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from common.custom_wraps import login_required
from common.utils import monthdatescalendar_info


# 获取日历信息
@login_required
@csrf_exempt
def get_calendar(request):
    year = int(request.POST.get("year"))
    month = int(request.POST.get("month"))
    data = monthdatescalendar_info(year=year, month=month)
    return JsonResponse(dict(code=1, msg='success', data=data))

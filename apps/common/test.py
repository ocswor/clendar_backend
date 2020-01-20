import calendar
from calendar import Calendar

import lunardate

from common.JieQi.SolarTerms import getjieqi_info

calendar.setfirstweekday(firstweekday=6)
print(calendar.month(2019, 11))
calendar_items = calendar.monthcalendar(2019, 11)
print(calendar_items)

ca = Calendar(firstweekday=6)
iter_month = ca.itermonthdates(2019, 11)
for month in iter_month:
    print(month)

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


def monthdatescalendar_info(year, month):
    jieqi_data = getjieqi_info(year)
    day_date_items = ca.monthdatescalendar(year, month)
    for day_date_list in day_date_items:
        for day_date in day_date_list:
            yinlidate = lunardate.LunarDate.fromSolarDate(day_date.year, day_date.month, day_date.day)
            if day_date.month == month:
                disable = 0
            else:
                disable = 1
            print(day_date, yinlidate, day_info_dic[yinlidate.day], disable, jieqi_data.get(str(day_date), ""))


for i in range(12):
    print(i)
    monthdatescalendar_info(2020, i + 1)

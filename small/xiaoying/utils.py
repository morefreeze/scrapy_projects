# coding: utf-8
import re
import datetime

def money2float(money):
    # Remove comma(,)
    money = money.replace(',', '')
    g = re.match('([0-9\.]+)', money)
    if not g:
        return money
    num = float(g.group(1))
    pos = 0
    while True:
        pos = money.find('万', pos+1)
        if pos != -1:
            num *= 1e4
        else:
            break
    return num


def period2timedelta(period):
    g = re.match('(?:([0-9]+)个月)?(?:([0-9]+)天)?', period)
    month = int(g.group(1)) if g.group(1) else 0
    day = int(g.group(2)) if g.group(2) else 0
    if g.group(1) is None and g.group(2) is None:
        return period
    return datetime.timedelta(days=day + month*30)



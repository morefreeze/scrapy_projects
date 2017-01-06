# coding: utf-8
from utils import period2timedelta, money2float
from datetime import timedelta as td


def test_money2float():
    assert money2float('81.87万') == 818700.0
    assert money2float('6,000') == 6000.0
    assert money2float('6,683.57') == 6683.57
    assert money2float('6,683.57') == 6683.57
    # assert money2float('6,600亿') == 6600e8
    # assert money2float('6,683亿123万') == 66830123e4


def test_period2timedelta():
    assert period2timedelta('11个月29天') == td(days=29+11*30)
    assert period2timedelta('1个月') == td(days=30)
    assert period2timedelta('29天') == td(days=29)
    assert period2timedelta('0天') == td(days=0)
    assert period2timedelta('0个月0天') == td(days=0)
    assert period2timedelta('0个月10天') == td(days=10)
    assert period2timedelta('3个月0天') == td(days=90)
    assert period2timedelta('不合法时间') == '不合法时间'



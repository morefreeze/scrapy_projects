# coding: utf-8
from checker import NormalChecker, LadderChecker
import logging

# Both test need run cow on local
def test_normal_proxy():
    test_host = 'http://127.0.0.1:7777'
    nc = NormalChecker(test_host, timeout=5)
    nc.check_proxy()
    assert nc.ret['ping']


def test_normal_proxy():
    test_host = 'http://127.0.0.1:7777'
    nc = LadderChecker(test_host, timeout=5)
    nc.check_proxy()
    assert nc.ret['ping']

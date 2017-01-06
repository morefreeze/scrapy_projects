# coding: utf-8

class Rule(object):

    """Filter fule"""

    def __init__(self, func, ok_stop=False, weight=10):
        """

        :func: filter function
        :ok_stop: if ok stop process later rule
        :weight: weight, smaller will go first

        """
        self.func = func
        self.ok_stop = ok_stop
        self.weight = weight

class Filter(object):

    """Filter good invest."""
    last_weight = 10

    def __init__(self):
        self._rules = []

    def install_rule(self, func, ok_stop=False, weight=last_weight+1):
        self._rules.append(Rule(func, ok_stop, weight))
        self.last_weight = weight + 1

    def check(self, item):
        for f in sorted(self._rules, key=lambda r: r.weight):
            ok = f.func(item)
            if f.ok_stop and ok:
                return True
            if not ok:
                return False
        return True

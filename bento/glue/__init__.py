#
# Glue utils
# 
# Copyright (c) 2020, Arm Limited. All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
#

import itertools as it


def override(super):
    """
    Assert that method is an override of a superclass's method
    """
    def override(method):
        assert method.__name__ in dir(super)
        return method
    return override


def Inherit(methods):
    """
    Allow mixins across explicit methods.
    """
    if isinstance(methods, str):
        methods = [methods]

    class Inherit:
        def inherit(self, cls):
            if not hasattr(self, '_inherits'):
                self._inherits = []
            self._inherits.append(cls)

        def inherit_all(self, classes):
            if not hasattr(self, '_inherits'):
                self._inherits = []
            self._inherits.extend(classes)

    def mkmethod(method):
        def inherit(self, *args, **kwargs):
            res = None
            for cls in getattr(self, '_inherits', []):
                if hasattr(cls, method):
                    res = getattr(cls, method)(*args, **kwargs)
            return res
        return inherit

    for method in methods:
        setattr(Inherit, method, mkmethod(method))

    return Inherit


# This class mostly acts as a marker. Because Glue should always be in
# an inheritance chain, we don't need to add any functionality
class Glue:
    pass


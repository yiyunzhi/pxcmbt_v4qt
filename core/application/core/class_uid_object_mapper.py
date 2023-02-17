# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_uid_object_mapper.py
# ------------------------------------------------------------------------------
#
# File          : class_uid_object_mapper.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
class UidObjectMapper:
    def __init__(self):
        self._map = {}

    def auto_register(self, uid):
        def _mapper(cls):
            def get_(*args, **kwargs):
                if uid not in self._map:
                    self._map[uid] = cls

            return get_

        return _mapper

    def get(self, uid):
        return self._map.get(uid)

    def set(self, uid, obj):
        if uid in self._map:
            return False
        self._map[uid] = obj
        return True

    def all(self):
        return self._map

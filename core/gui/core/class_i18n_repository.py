# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_i18n_repository.py
# ------------------------------------------------------------------------------
#
# File          : class_i18n_repository.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import weakref, addict, inspect
from pubsub import pub
from core.application.core.base import singleton
from core.application.zI18n import zI18n


class I18nRepositoryUsageRegistryItem:
    def __init__(self, i18n_ns, i18n_key, setter, getter, options):
        self.i18nNs = i18n_ns
        self.i18nKey = i18n_key
        self.setter = setter
        self.getter = getter
        self.options = options


@singleton
class I18nRepository:
    def __init__(self):
        self._map = weakref.WeakKeyDictionary()
        pub.subscribe(self.on_locale_changed, 'locale')

    @property
    def keyrefs(self):
        return self._map.keyrefs()

    @staticmethod
    def build_i18n(item: I18nRepositoryUsageRegistryItem, **options):
        return zI18n.t('%s.%s' % (item.i18nNs, item.i18nKey))

    def _get_best_color(self):
        return self._themePalette.windowText().color()

    def register(self, target_obj, i18n_ns, i18n_key, setter=None, getter=None, options: dict = None):
        _item = I18nRepositoryUsageRegistryItem(i18n_ns, i18n_key, setter, getter, options)
        self._map[target_obj] = _item
        return _item

    def unregister(self, target_obj):
        if target_obj in self._map:
            self._map.pop(target_obj)

    def get_i18n(self, target_obj, **kwargs):
        _key = target_obj
        _item = self._map.get(_key)
        if _item is None:
            _item = self.register(target_obj, **kwargs)
        return self.build_i18n(_item)

    def _retranslate(self):
        for k, v in self._map.items():
            if v.setter is not None:
                _arg_len = len(inspect.getfullargspec(v.setter).args)
                _i18n_text = self.build_i18n(v)
                if inspect.ismethod(v.setter):
                    if _arg_len == 2:
                        v.setter(_i18n_text)
                    elif _arg_len == 3:
                        v.setter(_i18n_text, k)
                elif inspect.isfunction(v.setter):
                    if _arg_len == 1:
                        v.setter(_i18n_text)
                    elif _arg_len == 2:
                        v.setter(_i18n_text, k)
                else:
                    v.setter(_i18n_text)

    def on_locale_changed(self, topic: pub.Topic = pub.AUTO_TOPIC, **msg_data):
        self._retranslate()

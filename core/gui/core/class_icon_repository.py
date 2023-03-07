# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_icon_repository.py
# ------------------------------------------------------------------------------
#
# File          : class_icon_repository.py
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
from core.gui.qtimp import QtGui, QtWidgets
import core.gui.qtawesome as qta


class IconRepositoryUsageRegistryItem:
    def __init__(self, icon_ns, icon_name, setter, getter, options):
        self.iconNs = icon_ns
        self.iconName = icon_name
        self.setter = setter
        self.getter = getter
        self.options = options
        self._cache = None

    def get_cache(self):
        return self._cache

    def set_cache(self, cache):
        self._cache = cache

    def clear_cache(self):
        self._cache = None


@singleton
class IconRepository:
    def __init__(self, app: QtWidgets.QApplication):
        self.app = app
        assert app is not None, 'QApplication instance required'
        self._map = weakref.WeakKeyDictionary()
        self._themePalette = self.app.palette()
        pub.subscribe(self.on_theme_changed, 'theme')

    @property
    def keyrefs(self):
        return self._map.keyrefs()

    @staticmethod
    def build_icon(item: IconRepositoryUsageRegistryItem, **options):
        _cached = item.get_cache()
        _force = options.get('force', False)
        if _force:
            item.clear_cache()
            _cached = None
        if _cached is None:
            if item.iconNs == 'fa':
                if item.options.color and 'color' in options:
                    options.pop('color')
                _opt = dict(item.options, **options)
                _icon = qta.icon(item.iconName, **_opt)
            else:
                _icon = QtGui.QIcon(item.iconName)
            item.set_cache(_icon)
        else:
            _icon = _cached
        return _icon

    @staticmethod
    def get_icon_silence(icon_name, icon_ns='fa', **kwargs):
        if icon_ns == 'fa':
            return qta.icon(icon_name, **kwargs)
        else:
            return QtGui.QIcon(icon_name)

    def _get_best_color(self):
        return self._themePalette.windowText().color()

    def register(self, target_obj, icon_ns, icon_name, setter=None, getter=None, options: dict = None):
        _default_best_color = self._get_best_color()
        _opt = addict.Dict(options)
        _item = IconRepositoryUsageRegistryItem(icon_ns, icon_name, setter, getter, _opt)
        self._map[target_obj] = _item
        return _item

    def unregister(self, target_obj):
        if target_obj in self._map:
            self._map.pop(target_obj)

    def get_icon(self, target_obj, **kwargs):
        _key = target_obj
        _item = self._map.get(_key)
        if _item is None:
            _item = self.register(target_obj, **kwargs)
        return self.build_icon(_item)

    def _repolish(self):
        _default_best_color = self._get_best_color()
        for k, v in self._map.items():
            if v.setter is not None:
                _options = {'color': _default_best_color}
                _icon = self.build_icon(v, force=True, **_options)
                if callable(v.setter):
                    _arg_len = len(inspect.getfullargspec(v.setter).args)
                    if inspect.ismethod(v.setter):
                        if _arg_len == 2:
                            v.setter(_icon)
                        elif _arg_len == 3:
                            v.setter(_icon, k)
                    elif inspect.isfunction(v.setter):
                        if _arg_len == 1:
                            v.setter(_icon)
                        elif _arg_len == 2:
                            v.setter(_icon, k)
                    else:
                        v.setter(_icon)
                elif isinstance(v.setter, str):
                    getattr(k, v.setter)(_icon)

    def on_theme_changed(self, topic: pub.Topic = pub.AUTO_TOPIC, **msg_data):
        self._themePalette = msg_data['palette']
        self._repolish()

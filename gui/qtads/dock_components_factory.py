import typing

from .dock_widget_tab import CDockWidgetTab

from .auto_hide_tab import CAutoHideTab
from .dock_area_tab_bar import CDockAreaTabBar
from .dock_area_title_bar import CDockAreaTitleBar

if typing.TYPE_CHECKING:
    from .dock_widget import CDockWidget
    from .dock_area_widget import CDockAreaWidget


class _CDockComponentsFactoryMgr:
    @staticmethod
    def createDockWidgetTab(dock_widget: 'CDockWidget', parent=None):
        return CDockWidgetTab(dock_widget, parent=parent)

    @staticmethod
    def createDockWidgetSideTab(dock_widget: 'CDockWidget'):
        return CAutoHideTab(dock_widget)

    @staticmethod
    def createDockAreaTabBar(dock_area: 'CDockAreaWidget'):
        return CDockAreaTabBar(dock_area)

    @staticmethod
    def createDockAreaTitleBar(dock_area: 'CDockAreaWidget'):
        return CDockAreaTitleBar(dock_area)


class CDockComponentsFactory:
    def __init__(self, factory_cls):
        self._mgr = None
        self.reset(factory_cls)

    def _register(self):
        if self._mgr is not None:
            for k, v in self._mgr.__dict__.items():
                if k.startswith('createDock'):
                    setattr(self, k, v.__get__(self))

    def get(self):
        return self._mgr

    def reset(self, factory=None):
        if factory is None:
            _factory = _CDockComponentsFactoryMgr
        else:
            _factory = factory
        self._mgr = _factory
        self._register()

    def setFactory(self, factory):
        self.reset(factory)


DEFAULT_COMPONENT_FACTORY = CDockComponentsFactory(_CDockComponentsFactoryMgr)

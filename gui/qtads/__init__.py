from .define import CDockInsertParam
from .define import EnumDockWidgetArea
from .define import EnumDockWidgetFeature
from .define import EnumTitleBarButton
from .define import EnumDockFlags
from .define import EnumDragState
from .define import EnumIconColor
from .define import EnumInsertMode
from .define import EnumOverlayMode
from .define import EnumWidgetState
from .define import EnumToggleViewActionMode
from .define import EnumInsertionOrder
from .define import EnumMinimumSizeHintMode
from .define import EnumDockMgrConfigFlag
from .define import EnumDockAreaFlag
from . import util

from .eliding_label import CElidingLabel
from .floating_dock_container import CFloatingDockContainer
from .dock_area_layout import CDockAreaLayout
from .dock_area_tab_bar import CDockAreaTabBar
from .dock_area_title_bar import CDockAreaTitleBar
from .dock_area_widget import CDockAreaWidget
from .dock_container_widget import CDockContainerWidget
from .dock_manager import CDockManager
from .dock_overlay import CDockOverlay, CDockOverlayCross
from .dock_splitter import CDockSplitter
from .dock_widget import CDockWidget
from .dock_widget_tab import CDockWidgetTab
from .floating_drag_preview import CFloatingDragPreview
# from . import examples


__all__ = [

    'CDockAreaLayout',
    'CDockAreaTabBar',
    'CDockAreaTitleBar',
    'CDockAreaWidget',
    'CDockContainerWidget',
    'CDockInsertParam',
    'CDockManager',
    'CDockOverlay',
    'CDockOverlayCross',
    'CDockSplitter',
    'CDockWidget',
    'EnumDockWidgetArea',
    'EnumDockWidgetFeature',
    'CDockWidgetTab',
    'CElidingLabel',
    'CFloatingDockContainer',
    'EnumTitleBarButton',
    'EnumDockFlags',
    'EnumDragState',
    'EnumIconColor',
    'EnumInsertMode',
    'EnumOverlayMode',
    'EnumWidgetState',
    'EnumToggleViewActionMode',
    'EnumInsertionOrder',
    'util',
]

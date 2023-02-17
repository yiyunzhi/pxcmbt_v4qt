import enum
from collections import namedtuple

from PySide6.QtCore import Qt, QEnum


class CDockInsertParam(namedtuple('DockInsertParam', ('orientation',
                                                      'append'))):
    @property
    def insert_offset(self):
        return 1 if self.append else 0


class EnumDockWidgetArea(enum.IntFlag):
    NO_AREA = 0x00
    LEFT = 0x01
    RIGHT = 0x02
    TOP = 0x04
    BOTTOM = 0x08
    CENTER = 0x10

    INVALID = NO_AREA
    OUTER_DOCK_AREAS = (TOP | LEFT | RIGHT | BOTTOM)
    ALL_DOCK_AREAS = (OUTER_DOCK_AREAS | CENTER)


AREA_ALIGNMENT = {
    EnumDockWidgetArea.TOP: Qt.AlignHCenter | Qt.AlignBottom,
    EnumDockWidgetArea.RIGHT: Qt.AlignLeft | Qt.AlignVCenter,
    EnumDockWidgetArea.BOTTOM: Qt.AlignHCenter | Qt.AlignTop,
    EnumDockWidgetArea.LEFT: Qt.AlignRight | Qt.AlignVCenter,
    EnumDockWidgetArea.CENTER: Qt.AlignCenter,

    EnumDockWidgetArea.INVALID: Qt.AlignCenter,
    EnumDockWidgetArea.OUTER_DOCK_AREAS: Qt.AlignCenter,
    EnumDockWidgetArea.ALL_DOCK_AREAS: Qt.AlignCenter,
}


class EnumTitleBarButton(enum.Enum):
    TABS_MENU = enum.auto()
    UNDOCK = enum.auto()
    CLOSE = enum.auto()
    AUTO_HIDE = enum.auto()


class EnumDragState(enum.Enum):
    INACTIVE = enum.auto()
    MOUSE_PRESSED = enum.auto()
    TAB = enum.auto()
    FLOATING_WIDGET = enum.auto()


class EnumADSIcon(enum.Enum):
    CLOSE = enum.auto()
    AUTO_HIDE = enum.auto()
    AREA_MENU = enum.auto()
    AREA_UNDOCK = enum.auto()
    AREA_CLOSE = enum.auto()
    ICON_COUNT = enum.auto()


class EnumBitwiseOP(enum.Enum):
    AND = enum.auto()
    OR = enum.auto()


# todo: use above segement
# class EnumSideBarLocation(enum.Enum):
#     TOP = enum.auto()
#     LEFT = enum.auto()
#     RIGHT = enum.auto()
#     BOTTOM = enum.auto()
#     NONE = enum.auto()
EnumSideBarLocation = enum.Enum('EnumSideBarLocation',
                                ['TOP', 'LEFT', 'RIGHT', 'BOTTOM', 'NONE'], start=0)


class EnumInsertionOrder(enum.Enum):
    BY_INSERTION = enum.auto()
    BY_SPELLING = enum.auto()


class EnumDockFlags(enum.IntFlag):
    '''
    These global configuration flags configure some global dock manager
    settings.
    '''
    # If this flag is set, the active tab in a tab area has a close button
    ACTIVE_TAB_HAS_CLOSE_BTN = 0x01
    # If the flag is set each dock area has a close button
    DOCK_AREA_HAS_CLOSE_BTN = 0x02
    # If the flag is set, the dock area close button closes the active tab, if
    # not set, it closes the complete cock area
    DOCK_AREA_CLOSE_BTN_CLOSES_TAB = 0x04
    # See QSplitter.setOpaqueResize() documentation
    OPAQUE_SPLITTER_RESIZE = 0x08
    # If enabled, the XML writer automatically adds line-breaks and indentation
    # to empty sections between elements (ignorable whitespace).
    XML_AUTO_FORMATTING = 0x10
    # If enabled, the XML output will be compressed and is not human readable
    # anymore
    XML_COMPRESSION = 0x20
    # the default configuration
    DEFAULT = (ACTIVE_TAB_HAS_CLOSE_BTN
               | DOCK_AREA_HAS_CLOSE_BTN
               | OPAQUE_SPLITTER_RESIZE
               | XML_AUTO_FORMATTING
               )


class EnumOverlayMode(enum.Enum):
    DOCK_AREA = enum.auto()
    CONTAINER = enum.auto()


class EnumIconColor(enum.Enum):
    # the color of the frame of the small window icon
    FRAME_COLOR = enum.auto()
    # the background color of the small window in the icon
    WIN_BG_COLOR = enum.auto()
    # the color that shows the overlay (the dock side) in the icon
    OVERLAY_COLOR = enum.auto()
    # the arrow that points into the direction
    ARROW_COLOR = enum.auto()
    # the color of the shadow rectangle that is painted below the icons
    SHADOW_COLOR = enum.auto()


class EnumDockWidgetFeature(enum.IntFlag):
    CLOSEABLE = 0x001  # dock widget has a close button
    MOVABLE = 0x002  # dock widget is movable and can be moved to a new position in the current dock container
    FLOATABLE = 0x004  # dock widget can be dragged into a floating window
    DELETE_ON_CLOSE = 0x008  # deletes the dock widget when it is closed
    CUSTOM_CLOSE_HANDLING = 0x010  # clicking the close button will not close the dock widget but emits the closeRequested() signal instead
    FOCUSABLE = 0x020  # if this is enabled, a dock widget can get focus highlighting
    FORCE_CLOSE_WITH_AREA = 0x040  # dock widget will be closed when the dock area hosting it is closed
    NO_TAB = 0x080  # dock widget tab will never be shown if this flag is set
    DELETE_CONTENT_ON_CLOSE = 0x100  # deletes only the contained widget on close, keeping the dock widget intact and in place. Attempts to rebuild the contents widget on show if there is a widget factory set.
    PINNABLE = 0x200  # dock widget can be pinned and added to an auto hide dock container
    DEFAULT = CLOSEABLE | MOVABLE | FLOATABLE | FOCUSABLE | PINNABLE
    ALL = DEFAULT | DELETE_ON_CLOSE | CUSTOM_CLOSE_HANDLING
    ALWAYS_CLOSE_AND_DELETE = FORCE_CLOSE_WITH_AREA | DELETE_ON_CLOSE
    NONE = 0


class EnumWidgetState(enum.Enum):
    HIDDEN = enum.auto()
    DOCKED = enum.auto()
    FLOATING = enum.auto()


class EnumInsertMode(enum.Enum):
    '''
    Sets the widget for the dock widget to widget.

    The InsertMode defines how the widget is inserted into the dock widget.
    The content of a dock widget should be resizable do a very small size to
    prevent the dock widget from blocking the resizing. To ensure, that a dock
    widget can be resized very well, it is better to insert the content+ widget
    into a scroll area or to provide a widget that is already a scroll area or
    that contains a scroll area.

    If the InsertMode is AutoScrollArea, the DockWidget tries to automatically
    detect how to insert the given widget. If the widget is derived from
    QScrollArea (i.e. an QAbstractItemView), then the widget is inserted
    directly. If the given widget is not a scroll area, the widget will be
    inserted into a scroll area.

    To force insertion into a scroll area, you can also provide the InsertMode
    ForceScrollArea. To prevent insertion into a scroll area, you can provide
    the InsertMode ForceNoScrollArea
    '''
    AUTO_SCROLL_AREA = enum.auto()
    FORCE_SCROLL_AREA = enum.auto()
    FORCE_NO_SCROLL_AREA = enum.auto()


class EnumToggleViewActionMode(enum.Enum):
    '''
    This mode configures the behavior of the toggle view action.

    If the mode if ActionModeToggle, then the toggle view action is a checkable
    action to show / hide the dock widget. If the mode is ActionModeShow, then
    the action is not checkable an it will always show the dock widget if
    clicked. If the mode is ActionModeShow, the user can only close the
    DockWidget with the close button.
    '''
    TOGGLE = enum.auto()
    SHOW = enum.auto()


class EnumMinimumSizeHintMode(enum.Enum):
    '''
     The mode of the minimumSizeHint() that is returned by the DockWidget
     minimumSizeHint() function.
     To ensure, that a dock widget does not block resizing, the dock widget
     reimplements minimumSizeHint() function to return a very small minimum
     size hint. If you would like to adhere the minimumSizeHint() from the
     content widget, then set the minimumSizeHintMode() to
     MinimumSizeHintFromContent.
    '''
    FROM_DOCK_WIDGET = enum.auto()
    FROM_CONTENT = enum.auto()


class EnumDockMgrConfigFlag(enum.IntFlag):
    ActiveTabHasCloseButton = 0x0001  # < If this flag is set, the active tab in a tab area has a close button
    DockAreaHasCloseButton = 0x0002  # < If the flag is set each dock area has a close button
    DockAreaCloseButtonClosesTab = 0x0004  # < If the flag is set, the dock area close button closes the active tab, if not set, it closes the complete dock area
    OpaqueSplitterResize = 0x0008  # < See QSplitter::setOpaqueResize() documentation
    XmlAutoFormattingEnabled = 0x0010  # < If enabled, the XML writer automatically adds line-breaks and indentation to empty sections between elements (ignorable whitespace).
    XmlCompressionEnabled = 0x0020  # < If enabled, the XML output will be compressed and is not human readable anymore
    TabCloseButtonIsToolButton = 0x0040  # If enabled the tab close buttons will be QToolButtons instead of QPushButtons - disabled by default
    AllTabsHaveCloseButton = 0x0080  # < if this flag is set, then all tabs that are closable show a close button
    RetainTabSizeWhenCloseButtonHidden = 0x0100  # < if this flag is set, the space for the close button is reserved even if the close button is not visible
    OpaqueUndocking = 0x0200  # If enabled, the widgets are immediately undocked into floating widgets, if disabled, only a draw preview is undocked and the real undocking is deferred until the mouse is released
    DragPreviewIsDynamic = 0x0400  # If opaque undocking is disabled, this flag defines the behavior of the drag preview window, if this flag is enabled, the preview will be adjusted dynamically to the drop area
    DragPreviewShowsContentPixmap = 0x0800  # If opaque undocking is disabled, the created drag preview window shows a copy of the content of the dock widget / dock are that is dragged
    DragPreviewHasWindowFrame = 0x1000  # If opaque undocking is disabled, then this flag configures if the drag preview is frameless or looks like a real window
    AlwaysShowTabs = 0x2000  # If this option is enabled, the tab of a dock widget is always displayed - even if it is the only visible dock widget in a floating widget.
    DockAreaHasUndockButton = 0x4000  # < If the flag is set each dock area has an undock button
    DockAreaHasTabsMenuButton = 0x8000  # < If the flag is set each dock area has a tabs menu button
    DockAreaHideDisabledButtons = 0x10000  # < If the flag is set disabled dock area buttons will not appear on the toolbar at all (enabling them will bring them back)
    DockAreaDynamicTabsMenuButtonVisibility = 0x20000  # < If the flag is set, the tabs menu button will be shown only when it is required - that means, if the tabs are elided. If the tabs are not elided, it is hidden
    FloatingContainerHasWidgetTitle = 0x40000  # < If set, the Floating Widget window title reflects the title of the current dock widget otherwise it displays the title set with `CDockManager::setFloatingContainersTitle` or application name as window title
    FloatingContainerHasWidgetIcon = 0x80000  # < If set, the Floating Widget icon reflects the icon of the current dock widget otherwise it displays application icon
    HideSingleCentralWidgetTitleBar = 0x100000  # < If there is only one single visible dock widget in the main dock container (the dock manager) and if this flag is set, then the titlebar of this dock widget will be hidden
    # < this only makes sense for non draggable and non floatable widgets and enables the creation of some kind of "central" widget

    FocusHighlighting = 0x200000  # < enables styling of focused dock widget tabs or floating widget titlebar
    EqualSplitOnInsertion = 0x400000  # < if enabled, the space is equally distributed to all widgets in a  splitter

    FloatingContainerForceNativeTitleBar = 0x800000  # < Linux only ! Forces all FloatingContainer to use the native title bar. This might break docking for FloatinContainer on some Window Managers (like Kwin/KDE).
    # < If neither this nor FloatingContainerForceCustomTitleBar is set (the default) native titlebars are used except on known bad systems.
    # Users can overwrite this by setting the environment variable ADS_UseNativeTitle to "1" or "0".
    FloatingContainerForceQWidgetTitleBar = 0x1000000  # < Linux only ! Forces all FloatingContainer to use a QWidget based title bar.
    # < If neither this nor FloatingContainerForceNativeTitleBar is set (the default) native titlebars are used except on known bad systems.
    # Users can overwrite this by setting the environment variable ADS_UseNativeTitle to "1" or "0".
    MiddleMouseButtonClosesTab = 0x2000000  # If the flag is set, the user can use the mouse middle button to close the tab under the mouse

    DefaultDockAreaButtons = DockAreaHasCloseButton \
                             | DockAreaHasUndockButton \
                             | DockAreaHasTabsMenuButton  # default configuration of dock area title bar buttons

    DefaultBaseConfig = DefaultDockAreaButtons | ActiveTabHasCloseButton \
                        | XmlCompressionEnabled | FloatingContainerHasWidgetTitle  # default base configuration settings

    DefaultOpaqueConfig = DefaultBaseConfig | OpaqueSplitterResize | OpaqueUndocking  # the default configuration with opaque operations - this may cause issues if ActiveX or Qt 3D windows are involved

    DefaultNonOpaqueConfig = DefaultBaseConfig | DragPreviewShowsContentPixmap  # the default configuration for non opaque operations

    NonOpaqueWithWindowFrame = DefaultNonOpaqueConfig | DragPreviewHasWindowFrame  # the default configuration for non opaque operations that show a real window with frame


class EnumAutoHideFlag(enum.IntFlag):
    """
        /**
         * These global configuration flags configure some dock manager auto hide
         * settings
         * Set the dock manager flags, before you create the dock manager instance.
         */
        """
    AutoHideFeatureEnabled = 0x01  # < enables / disables auto hide feature
    DockAreaHasAutoHideButton = 0x02  # < If the flag is set each dock area has a auto hide menu button
    AutoHideButtonTogglesArea = 0x04  # < If the flag is set, the auto hide button enables auto hiding for all dock widgets in an area, if disabled, only the current dock widget will be toggled
    AutoHideButtonCheckable = 0x08  # < If the flag is set, the auto hide button will be checked and unchecked depending on the auto hide state. Mainly for styling purposes.
    AutoHideSideBarsIconOnly = 0x10  # show only icons in auto hide side tab - if a tab has no icon, then the text will be shown
    AutoHideShowOnMouseOver = 0x20  # show the auto hide window on mouse over tab and hide it if mouse leaves auto hide container

    DefaultAutoHideConfig = AutoHideFeatureEnabled | DockAreaHasAutoHideButton  # the default configuration for left and right side bars


class EnumDockAreaFlag(enum.IntFlag):
    HideSingleWidgetTitleBar = 0x0001
    DefaultFlags = 0x0000


class EnumBorderLocation(enum.IntFlag):
    BorderNone = 0
    BorderLeft = 0x01
    BorderRight = 0x02
    BorderTop = 0x04
    BorderBottom = 0x08
    BorderVertical = BorderLeft | BorderRight
    BorderHorizontal = BorderTop | BorderBottom
    BorderTopLeft = BorderTop | BorderLeft
    BorderTopRight = BorderTop | BorderRight
    BorderBottomLeft = BorderBottom | BorderLeft
    BorderBottomRight = BorderBottom | BorderRight
    BorderVerticalBottom = BorderVertical | BorderBottom
    BorderVerticalTop = BorderVertical | BorderTop
    BorderHorizontalLeft = BorderHorizontal | BorderLeft
    BorderHorizontalRight = BorderHorizontal | BorderRight
    BorderAll = BorderVertical | BorderHorizontal


class EnumDropMode(enum.Enum):
    DropModeIntoArea = enum.auto()  # drop widget into a dock area
    DropModeIntoContainer = enum.auto()  # drop into container
    DropModeInvalid = enum.auto()  # invalid mode - do not drop


class EnumStateFileVersion(enum.IntEnum):
    InitialVersion = 0  # InitialVersion
    Version1 = 1  # Version1
    CurrentVersion = Version1  # CurrentVersion


class EnumRepolishChildOptions(enum.Enum):
    RepolishIgnoreChildren = enum.auto()
    RepolishDirectChildren = enum.auto()
    RepolishChildrenRecursively = enum.auto()


# DOCK_MANAGER_DEFAULT_CONFIG = EnumDockMgrConfigFlag.DefaultNonOpaqueConfig | EnumDockMgrConfigFlag.FocusHighlighting
DOCK_MANAGER_DEFAULT_CONFIG = EnumDockMgrConfigFlag.DefaultNonOpaqueConfig \
                              | EnumDockMgrConfigFlag.FocusHighlighting \
                              | EnumDockMgrConfigFlag.HideSingleCentralWidgetTitleBar
AUTO_HIDE_DEFAULT_CONFIG = EnumAutoHideFlag.DefaultAutoHideConfig

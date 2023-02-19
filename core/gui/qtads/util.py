import sys, enum
import functools

from typing import Optional, Any, Union, Type, TYPE_CHECKING
from core.gui.qtimp import QtGui, QtCore, QtWidgets, QTVersion

from .define import EnumRepolishChildOptions,EnumADSIcon
from .icon_provider import CIconProvider

if TYPE_CHECKING:
    from .dock_splitter import CDockSplitter
DEBUG_LEVEL = 0
PYQT5 = False
QT_VERSION_TUPLE = tuple(int(i) for i in QTVersion.split('.')[:3])

LINUX = sys.platform.startswith('linux')
WINDOWS = sys.platform == 'win32'

evtFloatingWidgetDragStartEvent = QtCore.QEvent.registerEventType()
evtDockedWidgetDragStartEvent = QtCore.QEvent.registerEventType()
ADS_ICON_PROVIDER = CIconProvider()


def testFlag(flags, flag):
    if type(flags) != type(flag):
        raise Warning('testFlag compare impossible')
    if isinstance(flags, int):
        return (flags & flag) == flag
    elif isinstance(flags, enum.IntFlag):
        return flag in flags


def setFlag(flags, flag, on):
    if on:
        flags |= flag
    else:
        flags &= ~flag
    return flags


def getQApp():
    return QtWidgets.QApplication.instance()


def emitTopLevelEventForWidget(widget: Optional['CDockWidget'], floating: bool):
    '''
    Call this function to emit a topLevelChanged() signal and to update the
    dock area tool bar visibility

    Parameters
    ----------
    widget : DockWidget
        The top-level dock widget
    floating : bool
    '''
    if widget is None:
        return

    widget.dockAreaWidget().updateTitleBarVisibility()
    widget.emitTopLevelChanged(floating)


def startDragDistance() -> int:
    '''
    The distance the user needs to move the mouse with the left button hold
    down before a dock widget start floating

    Returns
    -------
    value : int
    '''
    return int(QtWidgets.QApplication.startDragDistance() * 1.5)


def createTransparentPixmap(source: QtGui.QPixmap, opacity: float) -> QtGui.QPixmap:
    '''
    Creates a semi transparent pixmap from the given pixmap Source. The Opacity
    parameter defines the opacity from completely transparent (0.0) to
    completely opaque (1.0)

    Parameters
    ----------
    source : QPixmap
    opacity : qreal

    Returns
    -------
    value : QPixmap
    '''
    transparent_pixmap = QtGui.QPixmap(source.size())
    transparent_pixmap.fill(QtCore.Qt.GlobalColor.transparent)

    painter = QtGui.QPainter(transparent_pixmap)
    painter.setOpacity(opacity)
    painter.drawPixmap(0, 0, source)
    return transparent_pixmap


def makeIconPair(style, parent, standard_pixmap,
                 transparent_role=QtGui.QIcon.Mode.Disabled, *,
                 transparency=0.25):
    '''
    Using a standard pixmap (e.g., close button), create two pixmaps and set
    parent icon
    '''
    icon = QtGui.QIcon()
    normal_pixmap = style.standardPixmap(standard_pixmap, None, parent)
    icon.addPixmap(createTransparentPixmap(normal_pixmap, transparency),
                   transparent_role)
    icon.addPixmap(normal_pixmap, QtGui.QIcon.Mode.Normal)
    parent.setIcon(icon)
    return icon


def setButtonIcon(button: QtWidgets.QAbstractButton,
                  standard_pixmap: QtWidgets.QStyle.StandardPixmap, icon_id: EnumADSIcon):
    '''
    Set a button icon

    Parameters
    ----------
    button : QAbstractButton
    standard_pixmap: QStyle.StandardPixmap
    icon_id: int
    Returns
    -------
    icon : QIcon
    '''
    _icon = ADS_ICON_PROVIDER.customIcon(icon_id)
    if _icon is not None:
        button.setIcon(_icon)
        return
    else:
        _icon = QtGui.QIcon()
    if LINUX:
        _icon = button.style().standardIcon(standard_pixmap)
        button.setIcon(_icon)
    _normal_pm = button.style().standardPixmap(standard_pixmap, None, button)
    _icon.addPixmap(createTransparentPixmap(_normal_pm, 0.25), QtGui.QIcon.Mode.Disabled)
    _icon.addPixmap(_normal_pm, QtGui.QIcon.Mode.Normal)
    button.setIcon(_icon)


def hideEmptyParentSplitters(splitter: 'CDockSplitter'):
    '''
    This function walks the splitter tree upwards to hides all splitters that
    do not have visible content

    Parameters
    ----------
    splitter : DockSplitter
    '''
    while splitter and splitter.isVisible():
        if not splitter.hasVisibleContent():
            splitter.hide()

        splitter = findParent('CDockSplitter', splitter)


def findParent(parent_type: [type, str], widget):
    '''
    Searches for the parent widget of the given type.
    Returns the parent widget of the given widget or 0 if the widget is not
    child of any widget of type T

    It is not safe to use this function in in DockWidget because only
    the current dock widget has a parent. All dock widgets that are not the
    current dock widget in a dock area have no parent.
    '''
    import inspect

    _parent_widget = widget.parentWidget()
    while _parent_widget:
        if isinstance(parent_type, str):
            if _parent_widget.__class__.__base__.__name__ == parent_type or _parent_widget.__class__.__name__ == parent_type:
                return _parent_widget
        else:
            if isinstance(_parent_widget, parent_type):
                return _parent_widget

        _parent_widget = _parent_widget.parentWidget()


def findChild(parent: QtCore.QObject, type_: Type[QtCore.QObject], name: str = '',
              options: QtGui.Qt.FindChildOption = QtGui.Qt.FindChildOption.FindChildrenRecursively) -> object:
    '''
    Returns the child of this object that can be cast into type T and that is called name, or nullptr if there is no
    such object. Omitting the name argument causes all object names to be matched. The search is performed recursively,
    unless options specifies the option FindDirectChildrenOnly.

    If there is more than one child matching the search, the most direct ancestor is returned. If there are several
    direct ancestors, it is undefined which one will be returned. In that case, findChildren() should be used.

    WARNING: If you're using PySide, PySide2 or PyQt4, the options parameter will be discarded.
    '''

    if PYQT5:
        return parent.findChild(type_, name, options)
    else:
        # every other API (PySide, PySide2, PyQt4) has no options parameter
        return parent.findChild(type_, name, options)


def findChildren(parent: QtCore.QObject, type: Type[QtCore.QObject], name: Union[str, QtCore.QRegularExpression] = '',
                 options: QtGui.Qt.FindChildOption = QtGui.Qt.FindChildOption.FindChildrenRecursively) -> Optional[Any]:
    '''
    Returns all children of this object with the given name that can be cast to type T, or an empty list if there are no
    such objects. Omitting the name argument causes all object names to be matched. The search is performed recursively,
    unless options specifies the option FindDirectChildrenOnly.

    WARNING: If you're using PySide, PySide2 or PyQt4, the options parameter will be discarded.
    '''

    if PYQT5:
        return parent.findChildren(type, name, options)
    else:
        # every other API (PySide, PySide2, PyQt4) has no options parameter
        return parent.findChildren(type, name, options)


def eventFilterDecorator(method):
    '''
    PySide2 exhibits some strange behavior where an eventFilter may get a
    'PySide2.QtWidgets.QWidgetItem` as the `event` argument. This wrapper
    effectively just makes those specific cases a no-operation.

    NOTE::
        This is considered a work-around until the source of the issue can be
        determined.
    '''

    @functools.wraps(method)
    def wrapped(self, obj: QtCore.QObject, event: QtCore.QEvent):
        if not isinstance(event, QtCore.QEvent):
            return True
        return method(self, obj, event)

    return wrapped


def repolishStyle(widget: QtWidgets.QWidget, option: EnumRepolishChildOptions = EnumRepolishChildOptions.RepolishIgnoreChildren):
    if widget is None:
        return
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    if option == EnumRepolishChildOptions.RepolishIgnoreChildren:
        return
    _options = QtCore.Qt.FindChildOption.FindDirectChildrenOnly if option == EnumRepolishChildOptions.RepolishDirectChildren else QtCore.Qt.FindChildOption.FindChildrenRecursively
    _children = widget.findChildren(QtWidgets.QWidget, options=_options)
    for x in _children:
        x.style().unpolish(x)
        x.style().polish(x)


def globalPositionOf(ev: QtGui.QMouseEvent):
    return ev.globalPosition().toPoint()


def globalGeometry(w: QtWidgets.QWidget) -> QtCore.QRect:
    _g = w.geometry()
    _g.moveTopLeft(w.mapToGlobal(QtCore.QPoint(0, 0)))
    return _g


def isPlatformX11():
    return QtGui.QGuiApplication.platformName() == 'xcb'

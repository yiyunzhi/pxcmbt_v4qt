from typing import Dict
from PySide6 import QtCore, QtGui, QtWidgets

from .define import (EnumOverlayMode, EnumDockWidgetArea, EnumIconColor, AREA_ALIGNMENT)
from .dock_container_widget import CDockAreaWidget
from .util import LINUX


def _drop_indicator_width(label: QtWidgets.QLabel) -> float:
    '''
    Drop indicator width depending on the operating system for a given label
    '''
    if LINUX:
        return 40.
    return 3.0 * label.fontMetrics().height()


class DockOverlayMgr:
    _this: 'CDockOverlay'
    allowedAreas: EnumDockWidgetArea
    cross: 'CDockOverlayCross'
    targetWidget: QtWidgets.QWidget
    lastLocation: EnumDockWidgetArea
    dropPreviewEnabled: bool
    mode: EnumOverlayMode
    dropAreaRect: QtCore.QRect

    def __init__(self, _this: 'CDockOverlay'):
        '''
        Private data constructor

        Parameters
        ----------
        _this : DockOverlay
        '''
        self._this = _this
        self.allowedAreas = EnumDockWidgetArea.INVALID
        self.cross = None
        self.targetWidget = None
        self.lastLocation = EnumDockWidgetArea.INVALID
        self.dropPreviewEnabled = True
        self.mode = EnumOverlayMode.DOCK_AREA
        self.dropAreaRect = None


class CDockOverlay(QtWidgets.QFrame):

    def __init__(self, parent: QtWidgets.QWidget, mode: EnumOverlayMode):
        '''
        Creates a dock overlay

        Parameters
        ----------
        parent : QWidget
        mode : OverlayMode
        '''
        super().__init__(parent)
        self._mgr = DockOverlayMgr(self)
        self._mgr.mode = mode
        self._mgr.cross = CDockOverlayCross(self)
        if LINUX:
            self.setWindowFlags(QtCore.Qt.WindowType.Tool |
                                QtCore.Qt.WindowType.FramelessWindowHint |
                                QtCore.Qt.WindowType.WindowStaysOnTopHint |
                                QtCore.Qt.WindowType.X11BypassWindowManagerHint)
        else:
            self.setWindowFlags(QtCore.Qt.WindowType.Tool |
                                QtCore.Qt.WindowType.FramelessWindowHint)
        self.setWindowOpacity(1)
        self.setWindowTitle("DockOverlay")
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self._mgr.cross.setVisible(False)
        self.setVisible(False)

    def __repr__(self):
        return f'<DockOverlay mode={self._mgr.mode}>'

    def setAllowedAreas(self, areas: EnumDockWidgetArea):
        '''
        Configures the areas that are allowed for docking

        Parameters
        ----------
        areas : DockWidgetArea
        '''
        if areas != self._mgr.allowedAreas:
            self._mgr.allowedAreas = areas
            self._mgr.cross.reset()

    def allowedAreas(self) -> EnumDockWidgetArea:
        '''
        Returns flags with all allowed drop areas

        Returns
        -------
        value : DockWidgetArea
        '''
        return self._mgr.allowedAreas

    def dropAreaUnderCursor(self) -> EnumDockWidgetArea:
        '''
        Returns the drop area under the current cursor location

        Returns
        -------
        value : DockWidgetArea
        '''
        _result = self._mgr.cross.cursorLocation()
        if _result != EnumDockWidgetArea.INVALID:
            return _result

        _dock_area = self._mgr.targetWidget
        if isinstance(_dock_area, CDockAreaWidget):
            if (EnumDockWidgetArea.CENTER in _dock_area.allowedAreas()
                    and not _dock_area.titleBar().isHidde()
                    and _dock_area.titleBarGeometry().contains(QtGui.QCursor.pos())):
                return EnumDockWidgetArea.CENTER

        return _result

    def visibleDropAreaUnderCursor(self):
        if self.isHidden() or not self._mgr.dropPreviewEnabled:
            return EnumDockWidgetArea.INVALID
        else:
            return self.dropAreaUnderCursor()

    def showOverlay(self, target: QtWidgets.QWidget) -> EnumDockWidgetArea:
        '''
        Show the drop overlay for the given target widget

        Parameters
        ----------
        target : QWidget

        Returns
        -------
        value : DockWidgetArea
        '''
        if self._mgr.targetWidget is target:
            # Hint: We could update geometry of overlay here.
            _da = self.dropAreaUnderCursor()
            if _da != self._mgr.lastLocation:
                self.repaint()
                self._mgr.lastLocation = _da

            return _da
        self._mgr.targetWidget = target
        self._mgr.lastLocation = EnumDockWidgetArea.INVALID

        # Move it over the target.
        self.hide()
        self.resize(target.size())
        _top_left = target.mapToGlobal(target.rect().topLeft())
        self.move(_top_left)
        self.show()
        self._mgr.cross.updatePosition()
        self._mgr.cross.updateOverlayIcons()
        return self.dropAreaUnderCursor()

    def hideOverlay(self):
        '''
        Hides the overlay
        '''
        self.hide()
        self._mgr.targetWidget = None
        self._mgr.dropAreaRect = QtCore.QRect()
        self._mgr.lastLocation = EnumDockWidgetArea.INVALID

    def enableDropPreview(self, enable: bool):
        '''
        Enables / disables the semi transparent overlay rectangle that
        represents the future area of the dropped widget

        Parameters
        ----------
        enable : bool
        '''
        self._mgr.dropPreviewEnabled = enable
        self.update()

    def dropPreviewEnabled(self):
        return self._mgr.dropPreviewEnabled

    def paintEvent(self, event: QtGui.QPaintEvent):
        # draw rect based on the location
        if not self._mgr.dropPreviewEnabled:
            self._mgr.dropAreaRect = QtCore.QRect()
            return
        _r = QtCore.QRect()
        _da = self.dropAreaUnderCursor()
        _factor = 3 if self._mgr.mode == EnumOverlayMode.CONTAINER else 2
        if _da == EnumDockWidgetArea.TOP:
            _r.setHeight(_r.height() / _factor)
        elif _da == EnumDockWidgetArea.RIGHT:
            _r.setX(_r.width() * (1 - 1 / _factor))
        elif _da == EnumDockWidgetArea.BOTTOM:
            _r.setY(_r.height() * (1 - 1 / _factor))
        elif _da == EnumDockWidgetArea.LEFT:
            _r.setWidth(_r.width() / _factor)

        _p = QtGui.QPainter(self)
        _color = self.palette().color(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Highlight)
        _pen = _p.pen()
        _pen.setColor(_color.darker(120))
        _pen.setStyle(QtCore.Qt.PenStyle.SolidLine)
        _pen.setWidth(1)
        _pen.setCosmetic(True)
        _p.setPen(_pen)
        _color = _color.lighter(130)
        _color.setAlpha(64)
        _p.setBrush(_color)
        _p.drawRect(_r.adjusted(0, 0, -1, -1))
        self._mgr.dropAreaRect = _r

    def dropOverlayRect(self) -> QtCore.QRect:
        '''
        The drop overlay rectangle for the target area

        Returns
        -------
        value : QRect
        '''
        return self._mgr.dropAreaRect

    def event(self, e: QtCore.QEvent) -> bool:
        '''
        Handle polish events

        Parameters
        ----------
        e : QEvent

        Returns
        -------
        value : bool
        '''
        _result = super().event(e)
        if e.type() == QtCore.QEvent.Type.Polish:
            self._mgr.cross.setupOverlayCross(self._mgr.mode)
        return _result

    def showEvent(self, e: QtGui.QShowEvent):
        '''
        Showevent

        Parameters
        ----------
        e : QShowEvent
        '''
        self._mgr.cross.show()
        super().showEvent(e)

    def hideEvent(self, e: QtGui.QHideEvent):
        '''
        Hideevent

        Parameters
        ----------
        e : QHideEvent
        '''
        self._mgr.cross.hide()
        super().hideEvent(e)


class DockOverlayCrossMgr:
    _this: 'CDockOverlayCross'
    mode: EnumOverlayMode
    dockOverlay: CDockOverlay
    dropIndicatorWidgets: Dict[EnumDockWidgetArea, QtWidgets.QLabel]
    gridLayout: QtWidgets.QGridLayout
    iconColors: Dict[EnumIconColor, QtGui.QColor]
    updateRequired: bool
    lastDevicePixelRatio: float

    _areaGridPositions = {
        EnumOverlayMode.DOCK_AREA: {
            EnumDockWidgetArea.TOP: QtCore.QPoint(1, 2),
            EnumDockWidgetArea.RIGHT: QtCore.QPoint(2, 3),
            EnumDockWidgetArea.BOTTOM: QtCore.QPoint(3, 2),
            EnumDockWidgetArea.LEFT: QtCore.QPoint(2, 1),
            EnumDockWidgetArea.CENTER: QtCore.QPoint(2, 2),
        },
        EnumOverlayMode.CONTAINER: {
            EnumDockWidgetArea.TOP: QtCore.QPoint(0, 2),
            EnumDockWidgetArea.RIGHT: QtCore.QPoint(2, 4),
            EnumDockWidgetArea.BOTTOM: QtCore.QPoint(4, 2),
            EnumDockWidgetArea.LEFT: QtCore.QPoint(2, 0),
            EnumDockWidgetArea.CENTER: QtCore.QPoint(2, 2),
        },
    }

    def __init__(self, _this):
        '''
        Private data constructor

        Parameters
        ----------
        _this : DockOverlayCross
        '''
        self._this = _this
        self.mode = EnumOverlayMode.DOCK_AREA
        self.dockOverlay = None
        self.dropIndicatorWidgets = {}
        self.gridLayout = None
        self.iconColors = {
            EnumIconColor.FRAME_COLOR: None,
            EnumIconColor.WIN_BG_COLOR: None,
            EnumIconColor.OVERLAY_COLOR: None,
            EnumIconColor.ARROW_COLOR: None,
            EnumIconColor.SHADOW_COLOR: None,
        }

        self.updateRequired = False
        self.lastDevicePixelRatio = 0.1

    def areaGridPosition(self, area: EnumDockWidgetArea) -> QtCore.QPoint:
        '''
        Returns

        Parameters
        ----------
        area : DockWidgetArea

        Returns
        -------
        value : QPoint
        '''
        return self._areaGridPositions[self.mode].get(area, QtCore.QPoint())

    def defaultIconColor(self, color_index: EnumIconColor) -> QtGui.QColor:
        '''
        Palette based default icon colors

        Parameters
        ----------
        color_index : IconColor

        Returns
        -------
        value : QColor
        '''
        _pal = self._this.palette()
        if color_index == EnumIconColor.FRAME_COLOR:
            return _pal.color(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Highlight)
        if color_index == EnumIconColor.WIN_BG_COLOR:
            return _pal.color(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Base)
        if color_index == EnumIconColor.OVERLAY_COLOR:
            _color = _pal.color(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Highlight)
            _color.setAlpha(64)
            return _color
        if color_index == EnumIconColor.ARROW_COLOR:
            return _pal.color(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Base)
        if color_index == EnumIconColor.SHADOW_COLOR:
            return QtGui.QColor(0, 0, 0, 64)
        return QtGui.QColor()

    def iconColor(self, color_index: EnumIconColor) -> QtGui.QColor:
        '''
        Stylehseet based icon colors

        Parameters
        ----------
        color_index : IconColor

        Returns
        -------
        value : QColor
        '''
        _color = self.iconColors[color_index]
        if not _color:
            _color = self.defaultIconColor(color_index)
            self.iconColors[color_index] = _color

        return _color

    @staticmethod
    def dropIndicatorWidth(l: QtWidgets.QLabel):
        if LINUX:
            return 40
        return l.fontMetrics().height() * 3.0

    def createDropIndicatorWidget(self, area: EnumDockWidgetArea, mode: EnumOverlayMode) -> QtWidgets.QLabel:
        '''
        Create drop indicator widget

        Parameters
        ----------
        area : DockWidgetArea
        mode : OverlayMode

        Returns
        -------
        value : QLabel
        '''
        _l = QtWidgets.QLabel()
        _l.setObjectName("DockWidgetAreaLabel")

        _metric = self.dropIndicatorWidth(_l)
        _size = QtCore.QSizeF(_metric, _metric)
        _l.setPixmap(self.createHighDpiDropIndicatorPixmap(_size, area, mode))
        _l.setWindowFlags(QtCore.Qt.WindowType.Tool | QtCore.Qt.WindowType.FramelessWindowHint)
        _l.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        _l.setProperty("dockWidgetArea", area)
        return _l

    def updateDropIndicatorIcon(self, widget: QtWidgets.QWidget):
        '''
        Update drop indicator icon

        Parameters
        ----------
        widget : QWidget
        '''
        if isinstance(widget, QtWidgets.QLabel):
            _metric = self.dropIndicatorWidth(widget)
            _size = QtCore.QSizeF(_metric, _metric)
            _area = widget.property('dockWidgetArea')
            widget.setPixmap(self.createHighDpiDropIndicatorPixmap(_size, _area, self.mode))

    def createHighDpiDropIndicatorPixmap(
            self, size: QtCore.QSizeF, area: EnumDockWidgetArea,
            mode: EnumOverlayMode) -> QtGui.QPixmap:
        '''
        Create high dpi drop indicator pixmap

        Parameters
        ----------
        size : QSizeF
        area : DockWidgetArea
        mode : OverlayMode

        Returns
        -------
        value : QPixmap
        '''
        _border_color = self.iconColor(EnumIconColor.FRAME_COLOR)
        _background_color = self.iconColor(EnumIconColor.WIN_BG_COLOR)

        _window = self._this.window()
        _device_pixel_ratio = (_window.devicePixelRatioF()
                               if hasattr(_window, 'devicePixelRatioF')
                               else _window.devicePixelRatio())

        _pixmap_size = QtCore.QSizeF(size * _device_pixel_ratio)
        _pm = QtGui.QPixmap(_pixmap_size.toSize())
        _pm.fill(QtGui.QColor(0, 0, 0, 0))
        _p = QtGui.QPainter(_pm)
        _pen = _p.pen()
        _shadow_rect = QtCore.QRectF(_pm.rect())

        _base_rect = QtCore.QRectF()
        _base_rect.setSize(_shadow_rect.size() * 0.7)
        _base_rect.moveCenter(_shadow_rect.center())

        # Fill
        _shadow_color = self.iconColor(EnumIconColor.SHADOW_COLOR)
        if _shadow_color.alpha() == 255:
            _shadow_color.setAlpha(64)

        _p.fillRect(_shadow_rect, _shadow_color)

        # Drop area rect.
        _p.save()
        _area_rect = QtCore.QRectF()
        _area_line = QtCore.QLineF()
        _non_area_rect = QtCore.QRectF()

        if area == EnumDockWidgetArea.TOP:
            area_rect = QtCore.QRectF(_base_rect.x(), _base_rect.y(), _base_rect.width(),
                                      _base_rect.height() * .5)
            non_area_rect = QtCore.QRectF(_base_rect.x(), _shadow_rect.height() * .5,
                                          _base_rect.width(), _base_rect.height() * .5)
            area_line = QtCore.QLineF(area_rect.bottomLeft(), area_rect.bottomRight())
        elif area == EnumDockWidgetArea.RIGHT:
            area_rect = QtCore.QRectF(_shadow_rect.width() * .5, _base_rect.y(),
                                      _base_rect.width() * .5, _base_rect.height())
            non_area_rect = QtCore.QRectF(_base_rect.x(), _base_rect.y(),
                                          _base_rect.width() * .5, _base_rect.height())
            area_line = QtCore.QLineF(area_rect.topLeft(), area_rect.bottomLeft())
        elif area == EnumDockWidgetArea.BOTTOM:
            area_rect = QtCore.QRectF(_base_rect.x(), _shadow_rect.height() * .5,
                                      _base_rect.width(), _base_rect.height() * .5)
            non_area_rect = QtCore.QRectF(_base_rect.x(), _base_rect.y(),
                                          _base_rect.width(), _base_rect.height() * .5)
            area_line = QtCore.QLineF(area_rect.topLeft(), area_rect.topRight())
        elif area == EnumDockWidgetArea.LEFT:
            area_rect = QtCore.QRectF(_base_rect.x(), _base_rect.y(),
                                      _base_rect.width() * .5, _base_rect.height())
            non_area_rect = QtCore.QRectF(_shadow_rect.width() * .5, _base_rect.y(),
                                          _base_rect.width() * .5, _base_rect.height())
            area_line = QtCore.QLineF(area_rect.topRight(), area_rect.bottomRight())

        _base_size = _base_rect.size()
        if (EnumOverlayMode.CONTAINER == mode
                and area != EnumDockWidgetArea.CENTER):
            _base_rect = _area_rect

        _p.fillRect(_base_rect, _background_color)
        if _area_rect.isValid():
            _pen = _p.pen()
            _pen.setColor(_border_color)
            _color = self.iconColor(EnumIconColor.OVERLAY_COLOR)
            if _color.alpha() == 255:
                _color.setAlpha(64)

            _p.setBrush(_color)
            _p.setPen(QtCore.Qt.PenStyle.NoPen)
            _p.drawRect(_area_rect)
            _pen = _p.pen()
            _pen.setWidth(1)
            _pen.setColor(_border_color)
            _pen.setStyle(QtCore.Qt.PenStyle.DashLine)
            _p.setPen(_pen)
            _p.drawLine(_area_line)

        _p.restore()
        _p.save()

        # Draw outer border
        _pen = _p.pen()
        _pen.setColor(_border_color)
        _pen.setWidth(1)
        _p.setBrush(QtCore.Qt.BrushStyle.NoBrush)
        _p.setPen(_pen)
        _p.drawRect(_base_rect)

        # draw window title bar
        _p.setBrush(_border_color)
        frame_rect = QtCore.QRectF(_base_rect.topLeft(),
                                   QtCore.QSizeF(_base_rect.width(), _base_size.height() / 10))
        _p.drawRect(frame_rect)
        _p.restore()

        # Draw arrow for outer container drop indicators
        if (EnumOverlayMode.CONTAINER == mode and
                area != EnumDockWidgetArea.CENTER):
            _arrow_rect = QtCore.QRectF()
            _arrow_rect.setSize(_base_size)
            _arrow_rect.setWidth(_arrow_rect.width() / 4.6)
            _arrow_rect.setHeight(_arrow_rect.height() / 2)
            _arrow_rect.moveCenter(QtCore.QPointF(0, 0))

            _arrow = QtGui.QPolygonF()
            _arrow.append(_arrow_rect.topLeft())
            _arrow.append(QtCore.QPointF(_arrow_rect.right(), _arrow_rect.center().y()))
            _arrow.append(_arrow_rect.bottomLeft())

            _p.setPen(QtCore.Qt.PenStyle.NoPen)
            _p.setBrush(self.iconColor(EnumIconColor.ARROW_COLOR))
            _p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
            _p.translate(_non_area_rect.center().x(), _non_area_rect.center().y())
            if area == EnumDockWidgetArea.TOP:
                _p.rotate(-90)
            elif area == EnumDockWidgetArea.RIGHT:
                pass
            elif area == EnumDockWidgetArea.BOTTOM:
                _p.rotate(90)
            elif area == EnumDockWidgetArea.LEFT:
                _p.rotate(180)

            _p.drawPolygon(_arrow)

        _pm.setDevicePixelRatio(_device_pixel_ratio)
        return _pm


class CDockOverlayCross(QtWidgets.QWidget):
    _all_areas = [
        EnumDockWidgetArea.LEFT,
        EnumDockWidgetArea.RIGHT,
        EnumDockWidgetArea.TOP,
        EnumDockWidgetArea.BOTTOM,
        EnumDockWidgetArea.CENTER,
    ]

    def __init__(self, overlay: CDockOverlay):
        '''
        Creates an overlay cross for the given overlay

        Parameters
        ----------
        overlay : DockOverlay
        '''
        super().__init__(overlay.parentWidget())
        self._mgr = DockOverlayCrossMgr(self)
        self._mgr.dockOverlay = overlay
        if LINUX:
            self.setWindowFlags(QtCore.Qt.WindowType.Tool
                                | QtCore.Qt.WindowType.FramelessWindowHint
                                | QtCore.Qt.WindowType.X11BypassWindowManagerHint)
        else:
            self.setWindowFlags(QtCore.Qt.WindowType.Tool
                                | QtCore.Qt.WindowType.FramelessWindowHint)
        self.setWindowTitle("DockOverlayCross")
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self._mgr.gridLayout = QtWidgets.QGridLayout()
        self._mgr.gridLayout.setSpacing(0)
        self.setLayout(self._mgr.gridLayout)

    def setIconColor(self, color_index: EnumIconColor, color: QtGui.QColor):
        '''
        Sets a certain icon color

        Parameters
        ----------
        color_index : IconColor
        color : QColor
        '''
        self._mgr.iconColors[color_index] = color
        self._mgr.updateRequired = True

    def iconColor(self, color_index: EnumIconColor) -> QtGui.QColor:
        '''
        Returns the icon color given by ColorIndex

        Parameters
        ----------
        color_index : IconColor

        Returns
        -------
        value : QColor
        '''
        return self._mgr.iconColors[color_index]

    def cursorLocation(self) -> EnumDockWidgetArea:
        '''
        Returns the dock widget area depending on the current cursor location.
        The function checks, if the mouse cursor is inside of any drop
        indicator widget and returns the corresponding EnumDockWidgetArea

        Returns
        -------
        value : DockWidgetArea
        '''
        _pos = self.mapFromGlobal(QtGui.QCursor.pos())
        _allowed_areas = self._mgr.dockOverlay.allowedAreas()
        for area, widget in self._mgr.dropIndicatorWidgets.items():
            if (area in _allowed_areas and widget
                    and widget.isVisible()
                    and widget.geometry().contains(_pos)):
                return area

        return EnumDockWidgetArea.INVALID

    def setupOverlayCross(self, mode: EnumOverlayMode):
        '''
        Sets up the overlay cross for the given overlay mode

        Parameters
        ----------
        mode : OverlayMode
        '''
        self._mgr.mode = mode
        _area_widgets = {
            area: self._mgr.createDropIndicatorWidget(area, mode)
            for area in self._all_areas
        }

        self._mgr.last_device_pixel_ratio = (
            self.devicePixelRatioF()
            if hasattr(self, 'devicePixelRatioF')
            else self.devicePixelRatio())

        self.setAreaWidgets(_area_widgets)
        self._mgr.updateRequired = False

    def updateOverlayIcons(self):
        '''
        Recreates the overlay icons.
        '''
        if self.windowHandle().devicePixelRatio() == self._mgr.lastDevicePixelRatio:
            return

        for widget in self._mgr.dropIndicatorWidgets.values():
            self._mgr.updateDropIndicatorIcon(widget)

        self._mgr.lastDevicePixelRatio = (
            self.devicePixelRatioF()
            if hasattr(self, 'devicePixelRatioF')
            else self.devicePixelRatio())

    def reset(self):
        '''
        Resets and updates the
        '''

        _allowed_areas = self._mgr.dockOverlay.allowedAreas()

        # Update visibility of area widgets based on allowedAreas.
        for area in self._all_areas:
            _pos = self._mgr.areaGridPosition(area)
            _item = self._mgr.gridLayout.itemAtPosition(_pos.x(), _pos.y())
            _widget = _item.widget()
            if _item and _widget is not None:
                _widget.setVisible(area in _allowed_areas)

    def updatePosition(self):
        '''
        Updates the current position
        '''
        self.resize(self._mgr.dockOverlay.size())
        _top_left = self._mgr.dockOverlay.pos()
        _offset = QtCore.QPoint((self.width() - self._mgr.dockOverlay.width()) / 2,
                                (self.height() - self._mgr.dockOverlay.height()) / 2)
        _cross_top_left = _top_left - _offset
        self.move(_cross_top_left)

    def setIconColors(self, colors: str):
        '''
        A string with all icon colors to set. You can use this property to
        style the overly icon via CSS stylesheet file. The colors are set via a
        color identifier and a hex AARRGGBB value like in the example below.

        Parameters
        ----------
        colors : str
        '''
        _string_to_color_type = {
            "Frame": EnumIconColor.FRAME_COLOR,
            "Background": EnumIconColor.WIN_BG_COLOR,
            "Overlay": EnumIconColor.OVERLAY_COLOR,
            "Arrow": EnumIconColor.ARROW_COLOR,
            "Shadow": EnumIconColor.SHADOW_COLOR,
        }

        for color in colors.split(' '):
            try:
                _name, _value = color.replace(' ', '').split('=')
                _color_type = _string_to_color_type[_name]
            except (KeyError, IndexError):
                continue

            self._mgr.iconColors[_color_type] = QtGui.QColor(_value)

        self._mgr.updateRequired = True

    def showEvent(self, event: QtGui.QShowEvent):
        '''
        Showevent

        Parameters
        ----------
        event : QShowEvent
            Unused
        '''
        # pylint: disable=unused-argument

        if self._mgr.updateRequired:
            self.setupOverlayCross(self._mgr.mode)

        self.updatePosition()

    def setAreaWidgets(self, widgets: dict):
        '''
        Set area widgets

        Parameters
        ----------
        widgets : dict
            DockWidgetArea to QWidget
        '''
        # Delete old widgets.
        for area, widget in self._mgr.dropIndicatorWidgets.items():
            self._mgr.gridLayout.removeWidget(widget)
            widget.deleteLater()

        self._mgr.dropIndicatorWidgets.clear()

        # Insert new widgets into grid.
        self._mgr.dropIndicatorWidgets = widgets
        for area, widget in self._mgr.dropIndicatorWidgets.items():
            pos = self._mgr.areaGridPosition(area)
            self._mgr.gridLayout.addWidget(widget, pos.x(), pos.y(),
                                           AREA_ALIGNMENT[area])

        if EnumOverlayMode.DOCK_AREA == self._mgr.mode:
            self._mgr.gridLayout.setContentsMargins(0, 0, 0, 0)
            _stretch_values = [1, 0, 0, 0, 1]
        else:
            self._mgr.gridLayout.setContentsMargins(4, 4, 4, 4)
            _stretch_values = [0, 1, 1, 1, 0]

        for i, stretch in zip(range(5), _stretch_values):
            self._mgr.gridLayout.setRowStretch(i, stretch)
            self._mgr.gridLayout.setColumnStretch(i, stretch)

        self.reset()

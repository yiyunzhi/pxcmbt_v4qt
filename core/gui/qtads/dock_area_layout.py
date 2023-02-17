import logging
from typing import List
from PySide6 import QtCore, QtGui, QtWidgets

logger = logging.getLogger(__name__)


class CDockAreaLayout:
    _parentLayout: QtWidgets.QBoxLayout
    _widgets: List[QtWidgets.QWidget]
    _currentWidget: [QtWidgets.QWidget, None]
    _currentIndex: int

    def __init__(self, parent_layout: QtWidgets.QBoxLayout):
        '''
        Creates an instance with the given parent layout

        Parameters
        ----------
        parent_layout : QBoxLayout
        '''
        self._parentLayout = parent_layout
        self._widgets = []
        self._currentIndex = -1
        self._currentWidget = None

    def count(self) -> int:
        '''
        Returns the number of widgets in this layout

        Returns
        -------
        value : int
        '''
        return len(self._widgets)

    def insertWidget(self, index: int, widget: QtWidgets.QWidget):
        '''
        Inserts the widget at the given index position into the internal widget
        list

        Parameters
        ----------
        index : int
        widget : QWidget
        '''
        logger.debug('%s insertWidget: %s setParent None', self.__class__.__name__, widget)
        widget.setParent(None)
        if index < 0:
            index = len(self._widgets)

        self._widgets.insert(index, widget)
        if self._currentIndex < 0:
            self.setCurrentIndex(index)
        elif index <= self._currentIndex:
            self._currentIndex += 1

    def removeWidget(self, widget: QtWidgets.QWidget):
        '''
        Removes the given widget from the lyout

        Parameters
        ----------
        widget : QWidget
        '''
        if self.currentWidget() is widget:
            _layout_item = self._parentLayout.takeAt(1)
            if _layout_item:
                _widget = _layout_item.widget()
                logger.debug('removeWidget: %s setParent None', _widget)
                _widget.setParent(None)

            self._currentWidget = None
            self._currentIndex = -1
        elif self.indexOf(widget) < self._currentIndex:
            self._currentIndex -= 1
        self._widgets.remove(widget)

    def currentWidget(self) -> QtWidgets.QWidget:
        '''
        Returns the current selected widget

        Returns
        -------
        value : QWidget
        '''
        return self._currentWidget

    def setCurrentIndex(self, index: int):
        '''
        Activates the widget with the give index.

        Parameters
        ----------
        index : int
        '''
        _prev = self.currentWidget()
        _next = self.widget(index)
        if not _next or (_next is _prev and not self._currentWidget):
            return

        _reenable_updates = False
        _parent = self._parentLayout.parentWidget()
        if _parent and _parent.updatesEnabled():
            _reenable_updates = True
            _parent.setUpdatesEnabled(False)

        _layout_item = self._parentLayout.takeAt(1)
        if _layout_item:
            _widget = _layout_item.widget()
            logger.debug('setCurrentIndex: %s setParent None', _widget)
            _widget.setParent(None)

        self._parentLayout.addWidget(_next)
        if _prev:
            _prev.hide()

        self._currentIndex = index
        self._currentWidget = _next
        if _reenable_updates:
            _parent.setUpdatesEnabled(True)

    def currentIndex(self) -> int:
        '''
        Returns the index of the current active widget

        Returns
        -------
        value : int
        '''
        return self._currentIndex

    def isEmpty(self) -> bool:
        '''
        Returns true if there are no widgets in the layout

        Returns
        -------
        value : bool
        '''
        return len(self._widgets) == 0

    def indexOf(self, widget: QtWidgets.QWidget) -> int:
        '''
        Returns the index of the given widget

        Parameters
        ----------
        widget : QWidget

        Returns
        -------
        value : int
        '''
        return self._widgets.index(widget)

    def widget(self, index: int) -> QtWidgets.QWidget:
        '''
        Returns the widget for the given index

        Parameters
        ----------
        index : int

        Returns
        -------
        value : QWidget
        '''
        try:
            return self._widgets[index]
        except IndexError:
            return None

    def geometry(self) -> QtCore.QRect:
        '''
        Returns the geometry of the current active widget

        Returns
        -------
        value : QRect
        '''
        if not self._widgets:
            return QtCore.QRect()
        return self.currentWidget().geometry()

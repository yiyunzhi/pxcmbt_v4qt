from PySide6 import QtCore, QtWidgets


class DockSplitterMgr:
    visibleContentCount: int

    def __init__(self, _this: 'CDockSplitter'):
        self._this = _this
        self.visibleContentCount = 0


class CDockSplitter(QtWidgets.QSplitter):
    def __init__(self, orientation: QtCore.Qt.Orientation = None, parent: QtWidgets.QWidget = None):
        '''
        init

        Parameters
        ----------
        parent : QWidget
        '''
        if orientation is not None:
            super().__init__(orientation, parent)
        else:
            super().__init__(parent)
        self._mgr = DockSplitterMgr(self)
        self.setProperty("ads-splitter", True)
        self.setChildrenCollapsible(False)

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.orientation()}>'

    def hasVisibleContent(self) -> bool:
        '''
        Returns true, if any of the internal widgets is visible

        Returns
        -------
        value : bool
        '''

        for i in range(self.count()):
            if not self.widget(i).isHidden():
                return True

        return False

    def firstWidget(self):
        return self.widget(0) if self.count() > 0 else None

    def lastWidget(self):
        return self.widget(self.count() - 1) if self.count() > 0 else None

    def isResizingWithContainer(self):
        from .dock_area_widget import CDockAreaWidget
        for x in self.findChildren(CDockAreaWidget):
            if x.isCentralWidgetArea():
                return True
        return False

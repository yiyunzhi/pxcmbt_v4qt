# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_base.py
# ------------------------------------------------------------------------------
#
# File          : class_base.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from core.application.core.base import Content, ContentContainer
from core.gui.qtimp import QtCore, QtGui
from .define import EnumLayoutModifierPolicy, EnumLayoutModifierTarget


class ZView:
    def __init__(self):
        self.zViewManager = None
        self.zViewTitle = 'ZView'

    def set_view_manager(self, view_mgr):
        self.zViewManager = view_mgr

    @property
    def title(self):
        return self.zViewTitle

    @title.setter
    def title(self, title):
        pass


class ZViewContent(Content):
    def __init__(self, container=None):
        Content.__init__(self)
        self.container = container


class ZViewContentContainer(ContentContainer):

    def __init__(self, **kwargs):
        ContentContainer.__init__(self)
        self.manager = None
        self._content = kwargs.get('content')
        self._prevContent = None
        self.defaultContent = None

    def get_id(self):
        return self.manager.view_id

    def reset_to_default(self):
        self._content = self.defaultContent

    def set(self, content: Content):
        self._content = content

    def get(self):
        return self._content

    def transform_data(self):
        raise NotImplementedError

    def has_changed(self):
        pass


class ZViewManager(QtCore.QObject):
    sigChangeMainViewRequired = QtCore.Signal(str, object)
    aliveWithProject = False
    pathSep = '/'

    def __init__(self, **kwargs):
        QtCore.QObject.__init__(self, kwargs.get('parent'))
        self._view = kwargs.get('view')
        self._viewName = kwargs.get('view_name')
        self._viewId = kwargs.get('view_id')
        self._viewTitle = kwargs.get('view_title')
        self._contentContainer = kwargs.get('content_container')
        self._undoStack = kwargs.get('undo_stack', QtGui.QUndoStack(self))
        assert self._contentContainer is not None, 'contentContainer is required'
        assert self._view is not None and isinstance(self._view, ZView), 'ZView is required'
        self._contentContainer.manager = self
        self._view.set_view_manager(self)
        self._view.title = self.view_title

    @property
    def view(self):
        return self._view

    @property
    def view_name(self):
        return self._viewName

    @property
    def view_id(self):
        return self._viewName if self._viewId is None else self._viewId

    @property
    def view_title(self):
        return self._viewTitle if self._viewTitle is not None else self._view.title

    @view_title.setter
    def view_title(self, title):
        self._viewTitle = title
        self._view.title = title

    @property
    def path(self):
        _parents = [self]
        _parent = self.parent()
        while _parent:
            _parents.insert(0, _parent)
            _parent = _parent.parent()
        return _parents

    @property
    def content_container(self):
        return self._contentContainer

    @property
    def undo_stack(self) -> QtGui.QUndoStack:
        return self._undoStack

    def set_view(self, view):
        self._view = view
        setattr(self._view, 'zViewManager', self)

    def set_state(self, state):
        pass

    def set_content(self, content: Content):
        if content is None:
            self.content_container.reset_to_default()
            return
        self.content_container.set(content)
        self._undoStack.clear()

    def restore_content(self):
        pass

    def ensure_view(self):
        pass

    def update(self):
        pass


class Toggling:
    def __init__(self, disable_states: list = [], cb=None):
        self._disableStates = disable_states
        if cb is not None:
            assert callable(cb), 'cb must callable'
        self.cb = cb

    def can_enable(self, state):
        if state in self._disableStates:
            return False
        return True

    def toggle(self, state):
        if self.cb is not None:
            self.cb(self.can_enable(state))


class ZViewModifier:
    def __init__(self, **kwargs):
        self.viewName = kwargs.get('view_name')
        self.target = kwargs.get('target', EnumLayoutModifierTarget.CENTER_WIDGET)
        self.policy = kwargs.get('policy', EnumLayoutModifierPolicy.APPEND)
        self.options = kwargs.get('options', dict())

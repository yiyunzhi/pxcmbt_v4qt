# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_view.py
# ------------------------------------------------------------------------------
#
# File          : class_view.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import typing
from distutils.version import LooseVersion
from gui import QtGui, QtCore, QtWidgets, QtOpenGLWidgets
from ..core.define import (EnumGraphFlag, EnumGraphViewFlag)
from ..core.class_node_graph_interactor import NodeGraphBaseInteractor
from .class_search_widget import SearchMenuWidget
from .class_pipe_view_item import PipeViewItem
from .class_menu_widget import BaseMenuWidget
from .class_base_node_view_item import BaseNodeViewItem
from .class_node_graph_scene import NodeGraphScene
from .class_dialogs import FileDialog,FeedbackDialog

if typing.TYPE_CHECKING:
    from ..class_node_graph import NodeGraph


class NodeGraphView(QtWidgets.QGraphicsView):
    """
    The widget interface used for displaying the scene and nodes.

    functions in this class should mainly be called by the
    class:`NodeGraphQt.NodeGraph` class.
    """

    # node viewer signals.
    # (some of these signals are called by port & node items and connected
    # to the node graph slot functions)
    sigMovedNodes = QtCore.Signal(dict)
    sigSearchTriggered = QtCore.Signal(str, tuple)
    sigConnectionSliced = QtCore.Signal(list)
    sigConnectionChanged = QtCore.Signal(list, list)
    sigNodeInserted = QtCore.Signal(object, str, dict)
    sigNodeLabelChanged = QtCore.Signal(str, str)
    sigBackdropNodeUpdated = QtCore.Signal(str, str, object)

    # pass through signals that are translated into "NodeGraph()" signals.
    sigNodeSelected = QtCore.Signal(str)
    sigNodeSelectionChanged = QtCore.Signal(list, list)
    sigNodeDoubleClicked = QtCore.Signal(str)
    sigDataDropped = QtCore.Signal(QtCore.QMimeData, QtCore.QPoint)

    sigSceneUpdate = QtCore.Signal(QtCore.QObject)
    nodeNamespace = None

    def __init__(self, graph: 'NodeGraph', parent=None, undo_stack=None):
        """
        Args:
            parent:
            undo_stack (QtWidgets.QUndoStack): undo stack from the parent
                                               graph controller.
        """
        super(NodeGraphView, self).__init__(parent)
        assert graph is not None, 'NodeGraph is required.'
        self.graph = graph
        self.setScene(NodeGraphScene(self))
        self.interactor = NodeGraphBaseInteractor(self)

        self.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewportUpdateMode(self.ViewportUpdateMode.FullViewportUpdate)
        self.setCacheMode(self.CacheModeFlag.CacheBackground)
        self.setOptimizationFlag(self.OptimizationFlag.DontAdjustForAntialiasing)
        # self.viewport().setAutoFillBackground(True)

        if self.graph.has_flag(self.graph.view_flags, EnumGraphViewFlag.DND):
            self.setAcceptDrops(True)
        self.resize(850, 800)
        self._sceneRange = QtCore.QRectF(0, 0, self.size().width(), self.size().height())
        self._update_scene()
        self._lastSize = self.size()

        # workaround fix for shortcuts from the non-native menu.
        # actions don't seem to trigger so we create a hidden menu bar.
        self._ctxMenuBar = QtWidgets.QMenuBar(self)
        self._ctxMenuBar.setNativeMenuBar(False)
        # shortcuts don't work with "setVisibility(False)".
        self._ctxMenuBar.setMaximumSize(0, 0)

        # context menus.
        self._ctxGraphMenu = BaseMenuWidget('NodeGraph', self)
        self._ctxNodeMenu = BaseMenuWidget('Nodes', self)

        if undo_stack:
            self._undoAction = undo_stack.createUndoAction(self, '&Undo')
            self._redoAction = undo_stack.createRedoAction(self, '&Redo')
        else:
            self._undoAction = None
            self._redoAction = None

        self._build_context_menus()

        self._searchWidget = SearchMenuWidget()
        self._searchWidget.sigSearchSubmitted.connect(self.on_search_submitted)

    def __repr__(self):
        return '<{}() object at {}>'.format(
            self.__class__.__name__, hex(id(self)))

    @property
    def view_setting(self):
        return self.graph.view_setting

    def focusInEvent(self, event):
        """
        Args:
            event (QtGui.QFocusEvent): focus event.
        """
        # workaround fix: Re-populate the QMenuBar so the QAction shotcuts don't
        #                 conflict with parent existing host app.
        self._ctxMenuBar.addMenu(self._ctxGraphMenu)
        self._ctxMenuBar.addMenu(self._ctxNodeMenu)
        self.interactor.on_focus_in(event)
        return super(NodeGraphView, self).focusInEvent(event)

    def focusOutEvent(self, event):
        """
        Args:
            event (QtGui.QFocusEvent): focus event.
        """
        # workaround fix: Clear the QMenuBar so the QAction shotcuts don't
        #                 conflict with existing parent host app.
        self._ctxMenuBar.clear()
        self.interactor.on_focus_out(event)
        return super(NodeGraphView, self).focusOutEvent(event)

    # ----------------------------------------------------------
    # private
    # ----------------------------------------------------------

    def _build_context_menus(self):
        """
        Build context menu for the node graph.
        """
        # "node context menu" disabled by default and enabled when a action
        # is added through the "NodesMenu" interface.
        self._ctxNodeMenu.setDisabled(True)

        # add the base menus.
        self._ctxMenuBar.addMenu(self._ctxGraphMenu)
        self._ctxMenuBar.addMenu(self._ctxNodeMenu)

        # setup the undo and redo actions.
        if self._undoAction and self._redoAction:
            self._undoAction.setShortcuts(QtGui.QKeySequence.StandardKey.Undo)
            self._redoAction.setShortcuts(QtGui.QKeySequence.StandardKey.Redo)
            if LooseVersion(QtCore.qVersion()) >= LooseVersion('5.10'):
                self._undoAction.setShortcutVisibleInContextMenu(True)
                self._redoAction.setShortcutVisibleInContextMenu(True)

            # undo & redo always at the top of the "node graph context menu".
            self._ctxGraphMenu.addAction(self._undoAction)
            self._ctxGraphMenu.addAction(self._redoAction)
            self._ctxGraphMenu.addSeparator()

    def on_search_submitted(self, node_type):
        """
        Slot function triggered when the ``TabSearchMenuWidget`` has
        submitted a search.

        This will emit the "sigSearchTriggered" signal and tell the parent node
        graph to create a new node object.

        Args:
            node_type (str): node type identifier.
        """
        _pos = self.mapToScene(self.interactor.previousPos)
        self.sigSearchTriggered.emit(node_type, (_pos.x(), _pos.y()))

    def set_view_zoom(self, value, sensitivity=None, pos=None):
        """
        Sets the zoom level.

        Args:
            value (float): zoom factor.
            sensitivity (float): zoom sensitivity.
            pos (QtCore.QPoint): mapped position.
        """
        if pos:
            pos = self.mapToScene(pos)
        if sensitivity is None:
            _scale = 1.001 ** value
            self.scale(_scale, _scale, pos)
            return

        if value == 0.0:
            return

        _scale = (0.9 + sensitivity) if value < 0.0 else (1.1 - sensitivity)
        _zoom = self.get_zoom()
        if self.view_setting.zoomMin >= _zoom:
            if _scale == 0.9:
                return
        if self.view_setting.zoomMax <= _zoom:
            if _scale == 1.1:
                return
        self.scale(_scale, _scale, pos)
        self.sigSceneUpdate.emit(self)

    def set_view_pan(self, pos_x, pos_y):
        """
        Set the viewer in panning mode.

        Args:
            pos_x (float): x pos.
            pos_y (float): y pos.
        """
        self._sceneRange.adjust(pos_x, pos_y, pos_x, pos_y)
        self._update_scene()

    def scale(self, sx, sy, pos=None):
        _scale = [sx, sx]
        _center = pos or self._sceneRange.center()
        _w = self._sceneRange.width() / _scale[0]
        _h = self._sceneRange.height() / _scale[1]
        self._sceneRange = QtCore.QRectF(
            _center.x() - (_center.x() - self._sceneRange.left()) / _scale[0],
            _center.y() - (_center.y() - self._sceneRange.top()) / _scale[1],
            _w, _h
        )
        self._update_scene()

    def _update_scene(self):
        """
        Redraw the scene.
        """
        self.setSceneRect(self._sceneRange)
        self.fitInView(self._sceneRange, QtCore.Qt.AspectRatioMode.KeepAspectRatio)
        self.sigSceneUpdate.emit(self)

    def _combined_rect(self, nodes):
        """
        Returns a QRectF with the combined size of the provided node items.

        Args:
            nodes (list[BaseNodeViewItem]): list of node gqgraphics items.

        Returns:
            QtCore.QRectF: combined rect
        """
        _group = self.scene().createItemGroup(nodes)
        _rect = _group.boundingRect()
        self.scene().destroyItemGroup(_group)
        return _rect

    def get_items_near(self, pos, item_type=None, width=20, height=20):
        """
        Filter node graph items from the specified position, width and
        height area.

        Args:
            pos (QtCore.QPoint): scene pos.
            item_type: filter item type. (optional)
            width (int): width area.
            height (int): height area.

        Returns:
            list: qgraphics items from the scene.
        """
        _x, _y = pos.x() - width, pos.y() - height
        _rect = QtCore.QRectF(_x, _y, width, height)
        _items = []
        _excl = self.interactor.no_exposed_pipes
        for item in self.scene().items(_rect):
            if item in _excl:
                continue
            if not item_type or isinstance(item, item_type):
                _items.append(item)
        return _items

    # ----------------------------------------------------------
    # override events
    # ----------------------------------------------------------

    def resizeEvent(self, event):
        _w, _h = self.size().width(), self.size().height()
        if 0 in [_w, _h]:
            self.resize(self._lastSize)
        if 0 in [self._lastSize.width(), self._lastSize.height()]:
            return
        _delta = max(_w / self._lastSize.width(), _h / self._lastSize.height())
        self.set_view_zoom(_delta)
        self._lastSize = self.size()
        self.sigSceneUpdate.emit(self)
        super(NodeGraphView, self).resizeEvent(event)

    def contextMenuEvent(self, event):
        self.interactor.on_context_menu_event(event)
        _ctx_menu = None
        _ctx_menus = self.get_context_menus()
        if _ctx_menus['nodes'].isEnabled():
            _pos = self.mapToScene(self.interactor.previousPos)
            _items = self.get_items_near(_pos)
            _items = [i for i in _items if isinstance(i, BaseNodeViewItem)]
            if _items:
                _item = _items[0]
                _node = _item.node
                _ctx_menu = _ctx_menus['nodes'].get_menu(_node.type_, _node.id)
                if _ctx_menu:
                    for action in _ctx_menu.actions():
                        if not action.menu():
                            action.node_id = _node.id

        _ctx_menu = _ctx_menu or _ctx_menus['graph']
        if len(_ctx_menu.actions()) > 0:
            if _ctx_menu.isEnabled():
                _ctx_menu.exec_(event.globalPos())
            else:
                return super(NodeGraphView, self).contextMenuEvent(event)

        return super(NodeGraphView, self).contextMenuEvent(event)

    def mousePressEvent(self, event):
        super(NodeGraphView, self).mousePressEvent(event)
        if self._searchWidget.isVisible():
            self.tab_search_toggle()
        self.interactor.on_mouse_press(event)

    def mouseReleaseEvent(self, event):
        super(NodeGraphView, self).mouseReleaseEvent(event)
        self.interactor.on_mouse_release(event)

    def mouseMoveEvent(self, event):
        self.interactor.on_mouse_move(event)
        super(NodeGraphView, self).mouseMoveEvent(event)

    def wheelEvent(self, event):
        self.interactor.on_wheel(event)

    def dropEvent(self, event):
        _pos = self.mapToScene(event.pos())
        event.setDropAction(QtCore.Qt.DropAction.CopyAction)
        self.sigDataDropped.emit(
            event.mimeData(), QtCore.QPoint(_pos.x(), _pos.y()))

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('text/uri-list'):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat('text/uri-list'):
            event.accept()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        event.ignore()

    def keyPressEvent(self, event):
        """
        Key press event re-implemented to update the states for attributes:
        - ALT_state
        - CTRL_state
        - SHIFT_state

        Args:
            event (QtGui.QKeyEvent): key event.
        """
        self.interactor.on_key_press(event)
        super(NodeGraphView, self).keyPressEvent(event)

    def keyReleaseEvent(self, event):
        """
        Key release event re-implemented to update the states for attributes:
        - ALT_state
        - CTRL_state
        - SHIFT_state

        Args:
            event (QtGui.QKeyEvent): key event.
        """
        self.interactor.on_key_release(event)
        super(NodeGraphView, self).keyReleaseEvent(event)

    # ----------------------------------------------------------
    # view handle
    # ----------------------------------------------------------

    def tab_search_set_nodes(self, nodes):
        self._searchWidget.set_nodes(nodes)

    def tab_search_toggle(self):
        _search_widget = self._searchWidget
        _state = _search_widget.isVisible()
        if not _state:
            _search_widget.setVisible(_state)
            self.setFocus()
            return

        _pos = self.interactor.previousPos
        _rect = _search_widget.rect()
        _new_pos = QtCore.QPoint(int(_pos.x() - _rect.width() / 2),
                                 int(_pos.y() - _rect.height() / 2))
        _search_widget.move(_new_pos)
        _search_widget.setVisible(_state)
        _search_widget.setFocus()

        _rect = self.mapToScene(_rect).boundingRect()
        self.scene().update(_rect)

    def rebuild_tab_search(self):
        if isinstance(self._searchWidget, SearchMenuWidget):
            self._searchWidget.rebuild = True

    # ----------------------------------------------------------
    # scene events
    # ----------------------------------------------------------
    def sceneMouseMoveEvent(self, event):
        """
        triggered mouse move event for the scene.
         - redraw the connection pipe.

        Args:
            event (QtWidgets.QGraphicsSceneMouseEvent):
                The event handler from the QtWidgets.QGraphicsScene
        """
        self.interactor.on_scene_mouse_move(event)

    def sceneMousePressEvent(self, event):
        """
        triggered mouse press event for the scene (takes priority over viewer event).
         - detect selected pipe and start connection.
         - remap Shift and Ctrl modifier.

        Args:
            event (QtWidgets.QGraphicsScenePressEvent):
                The event handler from the QtWidgets.QGraphicsScene
        """
        self.interactor.on_scene_mouse_press(event)

    def sceneMouseReleaseEvent(self, event):
        """
        triggered mouse release event for the scene.

        Args:
            event (QtWidgets.QGraphicsSceneMouseEvent):
                The event handler from the QtWidgets.QGraphicsScene
        """
        self.interactor.on_scene_mouse_release(event)

    def qaction_for_undo(self):
        """
        Get the undo QAction from the parent undo stack.

        Returns:
            QtWidgets.QAction: undo action.
        """
        return self._undoAction

    def qaction_for_redo(self):
        """
        Get the redo QAction from the parent undo stack.

        Returns:
            QtWidgets.QAction: redo action.
        """
        return self._redoAction

    def get_context_menus(self):
        """
        All the available context menus for the viewer.

        Returns:
            dict: viewer context menu.
        """
        return {'graph': self._ctxGraphMenu, 'nodes': self._ctxNodeMenu}

    def question_dialog(self, text, title='Node Graph'):
        """
        Prompt node viewer question dialog widget with "yes", "no" buttons.

        Args:
            text (str): dialog text.
            title (str): dialog window title.

        Returns:
            bool: true if user click yes.
        """
        self.clear_key_state()
        return FeedbackDialog.question_dialog(text, title)

    def message_dialog(self, text, title='Node Graph'):
        """
        Prompt node viewer message dialog widget with "ok" button.

        Args:
            text (str): dialog text.
            title (str): dialog window title.
        """
        self.clear_key_state()
        FeedbackDialog.message_dialog(text, title)

    def load_dialog(self, current_dir=None, ext=None):
        """
        Prompt node viewer file load dialog widget.

        Args:
            current_dir (str): directory path starting point. (optional)
            ext (str): custom file extension filter type. (optional)

        Returns:
            str: selected file path.
        """
        self.clear_key_state()
        ext = '*{} '.format(ext) if ext else ''
        ext_filter = ';;'.join([
            'Node Graph ({}*json)'.format(ext), 'All Files (*)'
        ])
        file_dlg = FileDialog.getOpenFileName(
            self, 'Open File', current_dir, ext_filter)
        file = file_dlg[0] or None
        return file

    def save_dialog(self, current_dir=None, ext=None):
        """
        Prompt node viewer file save dialog widget.

        Args:
            current_dir (str): directory path starting point. (optional)
            ext (str): custom file extension filter type. (optional)

        Returns:
            str: selected file path.
        """
        self.clear_key_state()
        ext_label = '*{} '.format(ext) if ext else ''
        ext_type = '.{}'.format(ext) if ext else '.json'
        ext_map = {'Node Graph ({}*json)'.format(ext_label): ext_type,
                   'All Files (*)': ''}
        file_dlg = FileDialog.getSaveFileName(
            self, 'Save Session', current_dir, ';;'.join(ext_map.keys()))
        file_path = file_dlg[0]
        if not file_path:
            return
        ext = ext_map[file_dlg[1]]
        if ext and not file_path.endswith(ext):
            file_path += ext

        return file_path

    def get_all_pipes(self):
        """
        Returns all pipe qgraphic items.

        Returns:
            list[PipeItem]: instances of pipe items.
        """
        _excl = self.interactor.no_exposed_pipes
        return [i for i in self.scene().items() if isinstance(i, PipeViewItem) and i not in _excl]

    def get_all_items(self):
        """
        Returns all node qgraphic items.

        Returns:
            list[BaseNodeViewItem]: instances of node items.
        """
        return [i for i in self.scene().items()
                if isinstance(i, BaseNodeViewItem)]

    def get_selected_items(self):
        """
        Returns selected node qgraphic items.

        Returns:
            list[BaseNodeViewItem]: instances of node items.
        """
        return [i for i in self.scene().selectedItems() if isinstance(i, BaseNodeViewItem)]

    def get_selected_pipes(self):
        """
        Returns selected pipe qgraphic items.

        Returns:
            list[Pipe]: pipe items.
        """
        _pipes = [i for i in self.scene().selectedItems() if isinstance(i, PipeViewItem)]
        return _pipes

    def get_selected_items_all_type(self):
        """
        Return selected graphic items in the scene.

        Returns:
            tuple(list[BaseNodeViewItem], list[Pipe]):
                selected (node items, pipe items).
        """
        return self.get_selected_items(), self.get_selected_pipes()

    def add_item(self, item, pos=None):
        """
        Add node item into the scene.

        Args:
            item (BaseNodeViewItem): node item instance.
            pos (tuple or list): node scene position.
        """
        pos = pos or (self.interactor.previousPos.x(), self.interactor.previousPos.y())
        item.pre_init(self, pos)
        self.scene().addItem(item)
        item.post_init(self, pos)

    @staticmethod
    def remove_item(item):
        """
        Remove node item from the scene.

        Args:
            item (BaseNodeViewItem): node item instance.
        """
        if isinstance(item, BaseNodeViewItem):
            item.delete()

    def move_nodes(self, nodes, pos=None, offset=None):
        """
        Globally move specified nodes.

        Args:
            nodes (list[BaseNodeViewItem]): node items.
            pos (tuple or list): custom x, y position.
            offset (tuple or list): x, y position offset.
        """
        _group = self.scene().createItemGroup(nodes)
        _group_rect = _group.boundingRect()
        if pos:
            _x, _y = pos
        else:
            pos = self.mapToScene(self.interactor.previousPos)
            _x = pos.x() - _group_rect.center().x()
            _y = pos.y() - _group_rect.center().y()
        if offset:
            _x += offset[0]
            _y += offset[1]
        _group.setPos(_x, _y)
        self.scene().destroyItemGroup(_group)
        self.sigSceneUpdate.emit(self)

    def get_pipes_from_items(self, items=None):
        items = items or self.get_selected_items()
        if not items:
            return
        _pipes = []
        for item in items:
            _pipes.extend(item.get_pipes())
            # _n_inputs = item.inputs if hasattr(item, 'inputs') else []
            # _n_outputs = item.outputs if hasattr(item, 'outputs') else []
            # 
            # for port in _n_inputs:
            #     for pipe in port.connected_pipes:
            #         connected_node = pipe.output_port.node
            #         if connected_node in items:
            #             _pipes.append(pipe)
            # for port in _n_outputs:
            #     for pipe in port.connected_pipes:
            #         connected_node = pipe.input_port.node
            #         if connected_node in items:
            #             _pipes.append(pipe)
        return _pipes

    def center_selection(self, items=None):
        """
        Center on the given nodes or all nodes by default.

        Args:
            items (list[BaseNodeViewItem]): a list of node items.
        """
        if not items:
            _lst = self.get_selected_items()
            if _lst:
                items = _lst
            else:
                items = self.get_all_items()
            if not items:
                return

        if len(items) == 1:
            self.centerOn(items[0])
        else:
            _rect = self._combined_rect(items)
            self.centerOn(_rect.center().x(), _rect.center().y())

    def get_pipe_style(self):
        """
        Returns the pipe layout style.

        Returns:
            int: pipe layout style.
        """
        return self.view_setting.pipeStyle

    def set_pipe_style(self, style):
        """
        Sets the pipe layout mode and redraw all pipe items in the scene.

        Args:
            style (int): pipe layout style. (see the constants module)
        """
        self.view_setting.pipeStyle = style
        for pipe in self.get_all_pipes():
            pipe.update_style(style)

    def get_layout_direction(self):
        """
        Returns the layout direction set on the the node graph viewer
        used by the pipe items for drawing.

        Returns:
            int: graph layout mode.
        """
        return self.graph.layout_direction

    def set_layout_direction(self, direction):
        """
        Sets the node graph viewer layout direction for re-drawing
        the pipe items.

        Args:
            direction (int): graph layout direction.
        """
        # self.graph.layout_direction = direction
        for pipe_item in self.get_all_pipes():
            pipe_item.draw_path(pipe_item.input_port, pipe_item.output_port)

    def reset_zoom(self, cent=None):
        """
        Reset the viewer zoom level.

        Args:
            cent (QtCore.QPoint): specified center.
        """
        self._sceneRange = QtCore.QRectF(0, 0,
                                         self.size().width(),
                                         self.size().height())
        if cent:
            self._sceneRange.translate(cent - self._sceneRange.center())
        self._update_scene()

    def get_zoom(self):
        """
        Returns the viewer zoom level.

        Returns:
            float: zoom level.
        """
        _transform = self.transform()
        _cur_scale = (_transform.m11(), _transform.m22())
        return float('{:0.2f}'.format(_cur_scale[0] - 1.0))

    def set_zoom(self, value=0.0):
        """
        Set the viewer zoom level.

        Args:
            value (float): zoom level
        """
        if value == 0.0:
            self.reset_zoom()
            return
        _zoom = self.get_zoom()
        if _zoom < 0.0:
            if not (self.view_setting.zoomMin <= _zoom <= self.view_setting.zoomMax):
                return
        else:
            if not (self.view_setting.zoomMin <= value <= self.view_setting.zoomMax):
                return
        value = value - _zoom
        self.set_view_zoom(value, 0.0)

    def zoom_to_nodes(self, nodes):
        self._sceneRange = self._combined_rect(nodes)
        self._update_scene()

        if self.get_zoom() > 0.1:
            self.reset_zoom(self._sceneRange.center())

    def force_update(self):
        """
        Redraw the current node graph scene.
        """
        self._update_scene()

    def get_scene_rect(self):
        """
        Returns the scene rect size.

        Returns:
            list[float]: x, y, width, height
        """
        return [self._sceneRange.x(), self._sceneRange.y(),
                self._sceneRange.width(), self._sceneRange.height()]

    def set_scene_rect(self, rect):
        """
        Sets the scene rect and redraws the scene.

        Args:
            rect (list[float]): x, y, width, height
        """
        self._sceneRange = QtCore.QRectF(*rect)
        self._update_scene()

    def get_scene_center(self):
        """
        Get the center x,y pos from the scene.

        Returns:
            list[float]: x, y position.
        """
        _cent = self._sceneRange.center()
        return [_cent.x(), _cent.y()]

    def get_nodes_rect_center(self, nodes):
        """
        Get the center x,y pos from the specified nodes.

        Args:
            nodes (list[BaseNodeViewItem]): list of node qgrphics items.

        Returns:
            list[float]: x, y position.
        """
        _cent = self._combined_rect(nodes).center()
        return [_cent.x(), _cent.y()]

    def clear_key_state(self):
        """
        Resets the Ctrl, Shift, Alt modifiers key states.
        """
        self.interactor.clear_key_state()

    def use_OpenGL(self):
        """
        Use QOpenGLWidget as the viewer.
        """
        # use QOpenGLWidget instead of the deprecated QGLWidget to avoid
        # problems with Wayland.
        self.setViewport(QtOpenGLWidgets.QOpenGLWidget())

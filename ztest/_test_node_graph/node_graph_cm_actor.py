# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : node_graph_cm_actor.py
# ------------------------------------------------------------------------------
#
# File          : node_graph_cm_actor.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# menu command functions
# ------------------------------------------------------------------------------


def zoom_in(graph):
    """
    Set the node graph to zoom in by 0.1
    """
    _zoom = graph.get_zoom() + 0.1
    graph.set_zoom(_zoom)


def zoom_out(graph):
    """
    Set the node graph to zoom in by 0.1
    """
    _zoom = graph.get_zoom() - 0.2
    graph.set_zoom(_zoom)


def reset_zoom(graph):
    """
    Reset zoom level.
    """
    graph.reset_zoom()


def layout_h_mode(graph):
    """
    Set node graph layout direction to horizontal.
    """
    graph.set_layout_direction(0)


def layout_v_mode(graph):
    """
    Set node graph layout direction to vertical.
    """
    graph.set_layout_direction(1)


def open_session(graph):
    """
    Prompts a file open dialog to load a session.
    """
    _current = graph.get_current_session()
    _file_path = graph.load_dialog(_current)
    if _file_path:
        graph.load_session(_file_path)


def import_session(graph):
    """
    Prompts a file open dialog to load a session.
    """
    _current = graph.get_current_session()
    _file_path = graph.load_dialog(_current)
    if _file_path:
        graph.import_session(_file_path)


def save_session(graph):
    """
    Prompts a file save dialog to serialize a session if required.
    """
    _current = graph.get_current_session()
    if _current:
        graph.save_session(_current)
        _msg = 'Session layout saved:\n{}'.format(_current)
        _view = graph.get_view()
        _view.message_dialog(_msg, title='Session Saved')
    else:
        save_session_as(graph)


def save_session_as(graph):
    """
    Prompts a file save dialog to serialize a session.
    """
    _current = graph.get_current_session()
    _file_path = graph.save_dialog(_current)
    if _file_path:
        graph.save_session(_file_path)


def new_session(graph):
    """
    Prompts a warning dialog to new a node graph session.
    """
    if graph.question_dialog('Clear Current Session?', 'Clear Session'):
        graph.clear_session()


def clear_undo(graph):
    """
    Prompts a warning dialog to clear undo.
    """
    _view = graph.get_view()
    _msg = 'Clear all undo history, Are you sure?'
    if _view.question_dialog('Clear Undo History', _msg):
        graph.clear_undo_stack()


def copy_nodes(graph):
    """
    Copy nodes to the clipboard.
    """
    graph.copy_nodes()


def cut_nodes(graph):
    """
    Cut nodes to the clip board.
    """
    graph.cut_nodes()


def paste_nodes(graph):
    """
    Pastes nodes copied from the clipboard.
    """
    graph.paste_nodes()


def delete_nodes(graph):
    """
    Delete selected node.
    """
    graph.delete_nodes(graph.get_selected_nodes())


def select_all_nodes(graph):
    """
    Select all nodes.
    """
    graph.select_all()


def clear_node_selection(graph):
    """
    Clear node selection.
    """
    graph.clear_selection()


def disable_nodes(graph):
    """
    Toggle disable on selected nodes.
    """
    graph.disable_nodes(graph.get_selected_nodes())


def duplicate_nodes(graph):
    """
    Duplicated selected nodes.
    """
    graph.duplicate_nodes(graph.get_selected_nodes())


def expand_group_node(graph):
    """
    Expand selected group node.
    """
    _selected_nodes = graph.get_selected_nodes()
    if not _selected_nodes:
        graph.message_dialog('Please select a "GroupNode" to expand.')
        return
    graph.expand_group_node(_selected_nodes[0])


def fit_to_selection(graph):
    """
    Sets the zoom level to fit selected nodes.
    """
    graph.fit_to_selection()


def show_undo_view(graph):
    """
    Show the undo list widget.
    """
    graph.undo_view.show()


def curved_pipe(graph):
    """
    Set node graph pipes layout as curved.
    """
    from core.gui._ref_qtnode_graph.core.define import EnumPipeShape
    graph.set_pipe_style(EnumPipeShape.CURVED.value)


def straight_pipe(graph):
    """
    Set node graph pipes layout as straight.
    """
    from core.gui._ref_qtnode_graph.core.define import EnumPipeShape
    graph.set_pipe_style(EnumPipeShape.STRAIGHT.value)


def angle_pipe(graph):
    """
    Set node graph pipes layout as angled.
    """
    from core.gui._ref_qtnode_graph.core.define import EnumPipeShape
    graph.set_pipe_style(EnumPipeShape.ANGLE.value)


def bg_grid_none(graph):
    """
    Turn off the background patterns.
    """
    from core.gui._ref_qtnode_graph.core.define import EnumViewFeature
    graph.set_grid_mode(EnumViewFeature.GRID_DISPLAY_NONE.value)


def bg_grid_dots(graph):
    """
    Set background node graph background with grid dots.
    """
    from core.gui._ref_qtnode_graph.core.define import EnumViewFeature
    graph.set_grid_mode(EnumViewFeature.GRID_DISPLAY_DOTS.value)


def bg_grid_lines(graph):
    """
    Set background node graph background with grid lines.
    """
    from core.gui._ref_qtnode_graph.core.define import EnumViewFeature
    graph.set_grid_mode(EnumViewFeature.GRID_DISPLAY_LINES.value)


def layout_graph_down(graph):
    """
    Auto layout the nodes down stream.
    """
    _nodes = graph.get_selected_nodes() or graph.get_all_nodes()
    graph.auto_layout_nodes(nodes=_nodes, down_stream=True)


def layout_graph_up(graph):
    """
    Auto layout the nodes up stream.
    """
    _nodes = graph.get_selected_nodes() or graph.get_all_nodes()
    graph.auto_layout_nodes(nodes=_nodes, down_stream=False)


def toggle_node_search(graph):
    """
    show/hide the node search widget.
    """
    graph.toggle_node_search()
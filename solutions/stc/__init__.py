# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : __init__.py.py
# ------------------------------------------------------------------------------
#
# File          : __init__.py.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from core.application.class_application_context import ApplicationContext
from solutions.stc.gui.editor_stc import STCEditorManager, STCEditorContentContainer
from solutions.stc.gui.edit_stc_view import STCEditorView

_uuid = '12aab13d-bbae-4092-9ace-fb4c996293fd'


def setup(app_ctx: ApplicationContext):
    _z_vf = app_ctx.zViewFactory
    _z_vf.register(_uuid, STCEditorView, STCEditorContentContainer, STCEditorManager)


SOLUTION_DEF = {
    'uuid': _uuid,
    'icon': ['fa', 'mdi.state-machine'],
    'namespace': 'StateChart',
    'type': 'stc',
    'version': '1.0.1',
    'view': STCEditorView,
    'setup': setup,
    'builtinEntitiesPath': '',
}

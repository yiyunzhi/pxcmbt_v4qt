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
from .core.class_gui_factory import GUIZViewFactory
from .core.define import EnumGuiViewName
from .navigation.main_win_tb_mode_sel_view import AppModeSelectSideBar
from .navigation.main_win_tb_mode_sel_mc import AppModeSelectSideBarContentContainer, AppModeSelectSideBarManager
from .panes.pane_model_project_tree_view import ModelProjectNodeTreeViewDockPane
from .panes.pane_model_project_tree_mc import ModelProjectNodeContentContainer, ModelProjectNodeTreeManager
from .panes.pane_tester_project_tree_view import TesterProjectNodeTreeViewDockPane
from .panes.pane_tester_project_tree_mc import TesterProjectNodeContentContainer, TesterProjectNodeTreeManager
from .panes.pane_welcome_view import WelcomeDockPane
from .panes.pane_welcome_mc import WelcomeViewManager, WelcomeContentContainer
from .panes.pane_help_view import HelpDockPane
from .panes.pane_help_mc import HelpViewManager, HelpContentContainer
from .navigation.main_win_menu_bar_view import AppMenubar
from .navigation.main_win_menu_bar_mc import AppMenubarContentContainer, APPMenubarManager

GUI_VIEW_FACTORY = GUIZViewFactory()

GUI_VIEW_FACTORY.register(EnumGuiViewName.APP_MODE_SEL_SIDEBAR,
                          AppModeSelectSideBar, AppModeSelectSideBarContentContainer, AppModeSelectSideBarManager)
GUI_VIEW_FACTORY.register(EnumGuiViewName.APP_MODEL_PROJECT_TREEVIEW,
                          ModelProjectNodeTreeViewDockPane, ModelProjectNodeContentContainer, ModelProjectNodeTreeManager)
GUI_VIEW_FACTORY.register(EnumGuiViewName.APP_TESTER_PROJECT_TREEVIEW,
                          TesterProjectNodeTreeViewDockPane, TesterProjectNodeContentContainer, TesterProjectNodeTreeManager)
GUI_VIEW_FACTORY.register(EnumGuiViewName.APP_WELCOME,
                          WelcomeDockPane, WelcomeContentContainer, WelcomeViewManager)
GUI_VIEW_FACTORY.register(EnumGuiViewName.APP_HELP,
                          HelpDockPane, HelpContentContainer, HelpViewManager)
GUI_VIEW_FACTORY.register(EnumGuiViewName.APP_MENU_BAR,
                          AppMenubar, AppMenubarContentContainer, APPMenubarManager)

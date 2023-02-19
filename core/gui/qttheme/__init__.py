# -*- coding: utf-8 -*-
import os.path

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
import logging, pathlib, attrdict
from PySide6 import QtWidgets, QtCore, QtGui
import jinja2, yaml
import darkdetect
from .utils import density, opacity
from .resources import ResourcesGenerator

BASE_PATH = os.path.dirname(__file__)
THEMES_BASE_PATH = os.path.join(BASE_PATH, 'themes')
ICON_CACHE_PATH = os.path.join(BASE_PATH, '.cache')
RESOURCES_BASE_PATH = os.path.join(BASE_PATH, 'resources')
TEMPLATE_TEMPLATE_PATH = os.path.join(BASE_PATH, 'templates')

jinja2.environment.DEFAULT_FILTERS['opacity'] = opacity
jinja2.environment.DEFAULT_FILTERS['density'] = density
JINJA_ENV = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_TEMPLATE_PATH))

_logger = logging.getLogger('qtTheme')
# JINJA_ENV.filters['opacity'] = opacity
# JINJA_ENV.filters['density'] = density

DEFAULT_STYLESHEET_OPTION = {
    'qtVersion': 'pyside6',
    'densityScale': 0,
    'platform': 'windows'
}


def set_icons_theme(theme_var_map: dict, cache_path='theme'):
    """"""
    _icon_source = os.path.join(RESOURCES_BASE_PATH, 'icon')
    _resources_g = ResourcesGenerator(
        primary=theme_var_map['colors']['primaryColor'],
        secondary=theme_var_map['colors']['secondaryColor'],
        disabled=theme_var_map['colors']['secondaryLightColor'],
        source=_icon_source,
        cache_path=cache_path,
    )
    _resources_g.generate()
    QtCore.QDir.addSearchPath('icon', _resources_g.index)
    QtCore.QDir.addSearchPath('theme', RESOURCES_BASE_PATH)
    QtCore.QDir.addSearchPath('icons', os.path.join(RESOURCES_BASE_PATH, 'icons'))


# ----------------------------------------------------------------------
def list_themes():
    """"""
    _themes = os.listdir(THEMES_BASE_PATH)
    _themes = filter(lambda a: a.endswith('yaml'), _themes)
    return sorted(list(_themes))


def get_theme_context(theme='default'):
    _theme_file = os.path.join(THEMES_BASE_PATH, '%s.yaml' % theme)
    if not os.path.exists(_theme_file):
        _logger.warning('theme file %s not found, use default instead.' % _theme_file)
        _theme_file = os.path.join(THEMES_BASE_PATH, 'default.yaml')
    logging.debug('use theme file %s' % _theme_file)
    with open(_theme_file, 'r', encoding='utf-8') as f:
        _d = yaml.load(f, Loader=yaml.SafeLoader)
        return _d


def get_stylesheet(theme_context: dict, **option):
    # use theme get color->generate stylesheet
    _template = JINJA_ENV.get_template('base.css')
    return _template.render(colors=attrdict.AttrDict(theme_context.get('colors', {})),
                            font=attrdict.AttrDict(theme_context.get('font', {})),
                            extra=attrdict.AttrDict(theme_context.get('extra', {})), **option)


def do_update_palette(theme_context: dict):
    # https://doc.qt.io/qt-6/qpalette.html#ColorRole-enum
    _palette = QtGui.QPalette()
    _palette_color_role = QtGui.QPalette.ColorRole
    _palette_color_group = QtGui.QPalette.ColorGroup
    _primary = theme_context.get('colors').get('primaryColor')
    _primary_lighter = theme_context.get('colors').get('primaryLightColor')
    _secondary = theme_context.get('colors').get('secondaryColor')
    _secondary_lighter = theme_context.get('colors').get('secondaryLightColor')
    _secondary_darker = theme_context.get('colors').get('secondaryDarkColor')
    _primary_text = theme_context.get('colors').get('primaryTextColor')
    _secondary_text = theme_context.get('colors').get('secondaryTextColor')
    # base
    _palette.setColor(_palette_color_role.Text, _primary_text)
    _palette.setColor(_palette_color_role.Link, _primary_text)
    _palette.setColor(_palette_color_role.LinkVisited, _primary_text)
    _palette.setColor(_palette_color_role.WindowText, _primary_text)
    _palette.setColor(_palette_color_role.Button, _primary)
    _palette.setColor(_palette_color_role.ButtonText, _primary_text)
    _palette.setColor(_palette_color_role.Base, _secondary)
    _palette.setColor(_palette_color_role.Window, _secondary_darker)
    _palette.setColor(_palette_color_role.Highlight, _primary_lighter)
    _palette.setColor(_palette_color_role.HighlightedText, _primary)
    _palette.setColor(_palette_color_role.AlternateBase, _secondary)
    _palette.setColor(_palette_color_role.ToolTipBase, _primary)
    _palette.setColor(_palette_color_role.ToolTipText, _primary_text)
    if hasattr(_palette_color_role, "Foreground"):
        _palette.setColor(_palette_color_role.Foreground, _secondary_lighter)
    if hasattr(_palette_color_role, "PlaceholderText"):
        _palette.setColor(_palette_color_role.PlaceholderText, _primary_lighter)
    _palette.setColor(_palette_color_role.Light, _secondary_lighter)
    _palette.setColor(_palette_color_role.Midlight, _secondary)
    _palette.setColor(_palette_color_role.Dark, _secondary_darker)
    _palette.setColor(_palette_color_role.Mid, _secondary)
    _palette.setColor(_palette_color_role.Shadow, _secondary_darker)

    # disabled
    _palette.setColor(
        _palette_color_group.Disabled,
        _palette_color_role.WindowText,
        opacity(_primary, 0.2)
    )
    _palette.setColor(
        _palette_color_group.Disabled,
        _palette_color_role.ButtonText,
        opacity(_primary, 0.2),
    )
    _palette.setColor(
        _palette_color_group.Disabled,
        _palette_color_role.Highlight,
        opacity(_primary, 0.2),
    )
    _palette.setColor(
        _palette_color_group.Disabled,
        _palette_color_role.HighlightedText,
        opacity(_primary, 0.2),
    )

    # inactive
    _palette.setColor(
        _palette_color_group.Inactive,
        _palette_color_role.Highlight,
        opacity(_primary, 0.2),
    )
    _palette.setColor(
        _palette_color_group.Inactive,
        _palette_color_role.HighlightedText,
        opacity(_primary, 0.2),
    )

    _palette.setColor(
        _palette_color_group.Disabled,
        _palette_color_role.Text,
        opacity(_primary_text, 0.2),
    )

    _palette.setColor(
        _palette_color_group.Disabled,
        _palette_color_role.Link,
        opacity(_primary_text, 0.2),
    )
    _palette.setColor(
        _palette_color_group.Disabled,
        _palette_color_role.LinkVisited,
        opacity(_primary_text, 0.2),
    )
    return _palette


def format_custom_stylesheet(stylesheet: str, theme_context, **option):
    _template = jinja2.Template(stylesheet)
    return _template.render(colors=attrdict.AttrDict(theme_context.get('colors', {})),
                            font=attrdict.AttrDict(theme_context.get('font', {})),
                            extra=attrdict.AttrDict(theme_context.get('extra', {})), **option)


def apply_theme(app: QtWidgets.QApplication,
                theme: str = 'auto',
                update_palette=False, custom_styles=None, **option):
    if theme == 'auto':
        _is_dark = darkdetect.isDark()
        theme = 'dark' if _is_dark else 'default'

    _theme_context = get_theme_context(theme)
    if update_palette:
        _palette = do_update_palette(_theme_context)
        app.setPalette(_palette)
    if not option:
        option = DEFAULT_STYLESHEET_OPTION
    else:
        option = dict(DEFAULT_STYLESHEET_OPTION, **option)
    _stylesheet = get_stylesheet(_theme_context, **option)
    if custom_styles is not None:
        if isinstance(custom_styles, str):
            _stylesheet += format_custom_stylesheet(custom_styles, _theme_context, **option)
        elif isinstance(custom_styles, (list, tuple)):
            for x in custom_styles:
                _stylesheet += format_custom_stylesheet(x, _theme_context, **option)

    set_icons_theme(_theme_context, cache_path=ICON_CACHE_PATH)
    app.setStyleSheet(_stylesheet)
    return _theme_context

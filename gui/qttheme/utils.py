# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : utils.py
# ------------------------------------------------------------------------------
#
# File          : utils.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------

def density(value, density_scale, border=0, scale=1, density_interval=4):
    """"""
    # https://material.io/develop/web/supporting/density
    if isinstance(value, str) and value.startswith('@'):
        return value[1:] * scale

    if value == 'unset':
        return 'unset'

    if isinstance(value, str):
        value = float(value.replace('px', ''))

    _density = (
                       value + (density_interval * int(density_scale)) - (border * 2)
               ) * scale

    if _density < 0:
        _density = 0
    return _density


def opacity(theme, value=0.5):
    """"""
    _r, _g, _b = theme[1:][0:2], theme[1:][2:4], theme[1:][4:]
    _r, _g, _b = int(_r, 16), int(_g, 16), int(_b, 16)

    return f'rgba({_r}, {_g}, {_b}, {value})'

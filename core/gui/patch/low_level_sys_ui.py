# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : low_level_sys_ui.py
# ------------------------------------------------------------------------------
#
# File          : low_level_sys_ui.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
# inspired by https://github.com/Peticali/PythonBlurBehind/blob/main/blurWindow/blurWindow.py
import platform
import ctypes

if platform.system() == 'Darwin':
    from AppKit import *


    def MacBlur(QWidget, Material=NSVisualEffectMaterialPopover, TitleBar: bool = True):
        # WIP, trying to implement CGSSetWindowBackgroundBlurRadius too
        frame = NSMakeRect(0, 0, QWidget.width(), QWidget.height())
        view = objc.objc_object(c_void_p=QWidget.winId().__int__())

        visualEffectView = NSVisualEffectView.new()
        visualEffectView.setAutoresizingMask_(NSViewWidthSizable | NSViewHeightSizable)  # window resizable
        # visualEffectView.setWantsLayer_(True)
        visualEffectView.setFrame_(frame)
        visualEffectView.setState_(NSVisualEffectStateActive)
        visualEffectView.setMaterial_(Material)  # https://developer.apple.com/documentation/appkit/nsvisualeffectmaterial
        visualEffectView.setBlendingMode_(NSVisualEffectBlendingModeBehindWindow)

        window = view.window()
        content = window.contentView()

        try:
            from PySide6.QtWidgets import QMacCocoaViewContainer

        except:
            print('You need PyQt5')
            exit()

        container = QMacCocoaViewContainer(0, QWidget)
        content.addSubview_positioned_relativeTo_(visualEffectView, NSWindowBelow, container)

        if TitleBar:
            # TitleBar with blur
            window.setTitlebarAppearsTransparent_(True)
            window.setStyleMask_(window.styleMask() | NSFullSizeContentViewWindowMask)

        # appearance = NSAppearance.appearanceNamed_('NSAppearanceNameVibrantDark')
        # window.setAppearance_(appearance)

if platform.system() == 'Windows':
    from ctypes.wintypes import DWORD, BOOL, HRGN, HWND

    user32 = ctypes.windll.user32
    dwm = ctypes.windll.dwmapi


    class ACCENTPOLICY(ctypes.Structure):
        _fields_ = [
            ("AccentState", ctypes.c_uint),
            ("AccentFlags", ctypes.c_uint),
            ("GradientColor", ctypes.c_uint),
            ("AnimationId", ctypes.c_uint)
        ]


    class WINDOWCOMPOSITIONATTRIBDATA(ctypes.Structure):
        _fields_ = [
            ("Attribute", ctypes.c_int),
            ("Data", ctypes.POINTER(ctypes.c_int)),
            ("SizeOfData", ctypes.c_size_t)
        ]


    class DWM_BLURBEHIND(ctypes.Structure):
        _fields_ = [
            ('dwFlags', DWORD),
            ('fEnable', BOOL),
            ('hRgnBlur', HRGN),
            ('fTransitionOnMaximized', BOOL)
        ]


    class MARGINS(ctypes.Structure):
        _fields_ = [("cxLeftWidth", ctypes.c_int),
                    ("cxRightWidth", ctypes.c_int),
                    ("cyTopHeight", ctypes.c_int),
                    ("cyBottomHeight", ctypes.c_int)
                    ]


    SetWindowCompositionAttribute = user32.SetWindowCompositionAttribute
    SetWindowCompositionAttribute.argtypes = (HWND, WINDOWCOMPOSITIONATTRIBDATA)
    SetWindowCompositionAttribute.restype = ctypes.c_int


def llSetDarkWinTitlebar(hwnd):
    # enum of ATTRIBUTE https://learn.microsoft.com/zh-cn/windows/win32/api/dwmapi/ne-dwmapi-dwmwindowattribute
    _accent = ACCENTPOLICY()
    _accent.AccentState = 3  # Default window Blur #ACCENT_ENABLE_BLURBEHIND
    _accent.GradientColor=0
    _data = WINDOWCOMPOSITIONATTRIBDATA()
    _data.Attribute = 26  # 19=WCA_ACCENT_POLICY,26=WCA_USEDARKMODECOLORS
    _data.SizeOfData = ctypes.sizeof(_accent)
    _data.Data = ctypes.cast(ctypes.pointer(_accent), ctypes.POINTER(ctypes.c_int))
    SetWindowCompositionAttribute(int(hwnd), _data)

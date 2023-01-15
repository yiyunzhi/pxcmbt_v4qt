import enum
from PySide6 import QtCore


class EnumDockFlags(enum.IntFlag):
    '''
    These global configuration flags configure some global dock manager
    settings.
    '''
    # If this flag is set, the active tab in a tab area has a close button
    ACTIVE_TAB_HAS_CLOSE_BTN = 0x01
    # If the flag is set each dock area has a close button
    DOCK_AREA_HAS_CLOSE_BTN = 0x02
    # If the flag is set, the dock area close button closes the active tab, if
    # not set, it closes the complete cock area
    DOCK_AREA_CLOSE_BTN_CLOSES_TAB = 0x04
    # See QSplitter.setOpaqueResize() documentation
    OPAQUE_SPLITTER_RESIZE = 0x08
    # If enabled, the XML writer automatically adds line-breaks and indentation
    # to empty sections between elements (ignorable whitespace).
    XML_AUTO_FORMATTING = 0x10
    # If enabled, the XML output will be compressed and is not human readable
    # anymore
    XML_COMPRESSION = 0x20
    # the default configuration
    DEFAULT = (ACTIVE_TAB_HAS_CLOSE_BTN
               | DOCK_AREA_HAS_CLOSE_BTN
               | OPAQUE_SPLITTER_RESIZE
               | XML_AUTO_FORMATTING
               )


s = EnumDockFlags.DEFAULT


# print(EnumDockFlags.ACTIVE_TAB_HAS_CLOSE_BTN in s)
# s |= EnumDockFlags.XML_COMPRESSION
# print(int(s))


def testFlag(flags, flag):
    if type(flags) != type(flag):
        raise Warning('impossible')
    if isinstance(flags, int):
        return (flags & flag) == flag
    elif isinstance(flags, enum.IntFlag):
        return flag in flags


def setFlag(flags, flag, on):
    if on:
        flags |= flag
    else:
        flags &= ~flag
    return flags


print(testFlag(59, 0x11), testFlag(s, EnumDockFlags.XML_COMPRESSION))


class MyFlagContainer:
    def __init__(self):
        self.flags = EnumDockFlags.DEFAULT


fc = MyFlagContainer()
print(int(fc.flags))
_flags=setFlag(fc.flags, EnumDockFlags.OPAQUE_SPLITTER_RESIZE, 0)
print(_flags)


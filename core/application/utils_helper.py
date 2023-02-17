# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : helper.py
# ------------------------------------------------------------------------------
#
# File          : helper.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import ast, functools, json, decimal, gettext, pathlib
import os, sys, platform, math, uuid, bitstring, glob
from collections import defaultdict
from itertools import tee
import psutil
from .define import APP_CONSOLE_TIME_WX_FMT, SIZE_UNITS
#from .python.class_evaluator import DEFAULT_EXPRESSION_EVALUATOR

RGET_RSET_DELIMITER = "."

# gettext.bindtextdomain('myapplication', '/path/to/my/language/directory')
# gettext.textdomain('myapplication')
_ = gettext.gettext


def util_remove_folder(file_path):
    _pth = pathlib.Path(file_path)
    for sub in _pth.iterdir():
        if sub.is_dir():
            util_remove_folder(sub)
        else:
            sub.unlink()
    _pth.rmdir()


def util_ellipse_str(s, length):
    return s[0:length] + '...' if len(s) > length else s


def util_simple_py_script_execute(src, envs: dict):
    _ast_object = ast.parse(src)
    _code = compile(_ast_object, filename='', mode='exec')
    exec(_code, envs)
    envs.pop('__builtins__')


def util_py_script_execute(src, kwargs: dict, result_vars: list or str):
    _ast_object = ast.parse(src)
    _code = compile(_ast_object, filename='', mode='exec')
    _local_d = dict(**kwargs)
    exec(_code, _local_d)
    if isinstance(result_vars, str):
        if result_vars in _local_d:
            return _local_d.get(result_vars)
        else:
            return None
    elif isinstance(result_vars, list):
        _ret = dict()
        for x in result_vars:
            if x in _local_d:
                _ret.update({x: _local_d.get(x)})
        return _ret
    return None


def util_float_range(start, stop, step, precision=2):
    while start < stop:
        yield round(float(start), precision)
        start += step


def util_pairwise(iterable, reverse=False):
    # pairwise('ABCDEFG') --> AB BC CD DE EF FG
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b) if not reverse else zip(b, a)


def util_json_casting_test(typ, json_str):
    try:
        typ(json.loads(json_str))
    except ValueError as e:
        return False
    return True


# def util_python_casting_test(typ, string):
#     try:
#         return isinstance(DEFAULT_EXPRESSION_EVALUATOR.parse(string), typ)
#     except ValueError as e:
#         return False


def util_is_python(string):
    try:
        ast.parse(string)
    except SyntaxError:
        return False
    return True


def util_is_json(string):
    try:
        json.loads(string)
    except ValueError as e:
        return False
    return True


def util_r_get_attr(obj, path: str, *default):
    """
    :param obj: Object
    :param path: 'attr1.attr2.etc'
    :param default: Optional default value, at any point in the path
    :return: obj.attr1.attr2.etc
    """

    try:
        if RGET_RSET_DELIMITER in path:
            _attrs = path.split(RGET_RSET_DELIMITER)
            return functools.reduce(getattr, _attrs, obj)
        else:
            return getattr(obj, path)

    except AttributeError:
        if default:
            return default[0]
        raise


def util_r_set_attr(obj, path: str, val):
    """
    :param obj: Object
    :param path: 'attr1.attr2.etc'
    :param val: any
    :return: None
    """
    try:
        if RGET_RSET_DELIMITER in path:
            _pre, *_, _post = path.split(RGET_RSET_DELIMITER)
            setattr(util_r_get_attr(obj, _pre) if _pre else obj, _post, val)
        else:
            setattr(obj, path, val)
    except AttributeError:
        raise


def util_get_computer_name():
    return os.getenv('COMPUTERNAME')


def util_get_ipv4_if():
    for interface, snics in psutil.net_if_addrs().items():
        for snic in snics:
            if snic.family == -1:
                mac = snic.address
            if snic.family == 2:
                yield interface, snic.address, snic.netmask, mac


def util_is_32bit_pcap_installed():
    # todo: for linux and mac must be different
    _32_sys_path = os.environ['WINDIR'] + "\\System32\\"
    return os.path.exists(os.path.join(_32_sys_path, 'Packet.dll'))


def util_is_64bit_pcap_installed():
    # todo: for linux and mac must be different
    _64_sys_path = os.environ['WINDIR'] + "\\SysWOW64\\"
    return os.path.exists(os.path.join(_64_sys_path, 'Packet.dll'))


def util_os_is_32bit():
    return sys.maxsize <= 2 ** 32


def util_os_is_windows():
    return (bool(platform.win32_ver()[0]) or
            (sys.platform in ("win32", "cygwin")) or
            (sys.platform == "cli" and os.name in ("nt", "ce")) or
            (os.name == "java" and
             "windows" in platform.java_ver()[3][0].lower()))


def util_os_is_linux():
    return sys.platform.startswith("linux")


def util_os_is_osx():
    return sys.platform == "darwin"


def util_os_is_posix():
    return os.name == "posix"


# def util_date_now(fmt=APP_CONSOLE_TIME_WX_FMT):
#     return wx.DateTime.UNow().Format(fmt)


def util_get_segment_of_list(lst: list, seg: int):
    if seg > 0:
        return [lst[x:x + seg] for x in range(0, len(lst), seg)]
    else:
        return lst


def util_get_ascii_chr(val, char_rep='.'):
    return chr(val) if 127 >= val > 32 else char_rep


def util_get_formatted_hex_byte_str(val, char_w=0):
    return ('%.2X' % val).ljust(char_w)


def util_set_val_by_bit_rang(offset, bit_len, val, target):
    for i in range(bit_len):
        _c1 = (val & (1 << i))
        if _c1:
            target = util_set_bit(target, i + offset)
        else:
            target = util_clear_bit(target, i + offset)
    return target


def util_set_bits(offset, length, val):
    return (((pow(2, length) - 1) << offset) & val) >> offset


def util_set_bit(value, bit):
    return value | (1 << bit)


def util_clear_bit(value, bit):
    return value & ~(1 << bit)


def util_get_uuid_string():
    return uuid.uuid4().hex[:8]


def util_cvt_path_to_platform_spec(path):
    """
    Convert paths to the platform-specific separator
    """
    st = os.path.join(*tuple(path.split('/')))
    # HACK: on Linux, a leading / gets lost...
    if path.startswith('/'):
        st = '/' + st
    return st


def util_wx_tree_walk_branches(tree, item, cb):
    """
    a generator that recursively yields child nodes of a wx.TreeCtrl
    """
    _item, cookie = tree.GetFirstChild(item)
    while _item.IsOk():
        if cb(_item): break
        util_wx_tree_walk_branches(tree, _item, cb)
        _item, cookie = tree.GetNextChild(item, cookie)


def util_is_dir_exist(path):
    return os.path.exists(path)


def util_list_file_in_path(path, pattern=None, recursive=False):
    if pattern is not None:
        _path = os.path.join(path, pattern)
    else:
        _path = path
    return [os.path.basename(f) for f in glob.glob(_path, recursive=recursive)]


def util_scan_dir(dir_path, recursive=False):
    _sub_dirs = [f.path for f in os.scandir(dir_path) if f.is_dir()]
    if recursive:
        for dir_path in list(_sub_dirs):
            _sub_dirs.extend(util_scan_dir(dir_path, recursive=recursive))
    return _sub_dirs


def util_int2byte(x: int, endian='big') -> bytes:
    return x.to_bytes((x.bit_length() + 7) // 8, endian)


def util_int2chars(x: int, endian='big') -> list:
    return [chr(x) for x in util_int2byte(x, endian)]


def util_int2string(x: int, endian='big', sep=',') -> str:
    return sep.join(util_int2chars(x, endian))


def util_chars2uint8s(chars):
    return [ord(x) for x in chars]


def util_uint82int(uint8s: list):
    _fmt = ','.join(['uint:8'] * len(uint8s))
    return bitstring.pack(_fmt, *uint8s).uint


# def util_distance(pt1: wx.RealPoint, pt2: wx.RealPoint):
#     _diff_x = pt2.x - pt1.x
#     _diff_y = pt2.y - pt1.y
#     return math.sqrt(pow(_diff_x, 2) + pow(_diff_y, 2))


# def util_lines_intersection(from1, to1, from2, to2, include_extend=False, use_float=False):
#     """
#     Function to calculate the intersection point between two lines.
#     line1: from1 -> to1, line2: from2-> to2. sometimes the intersection located the line extend
#     this will be calculated if include_extend is true.
#     :param from1: Point
#     :param to1: Point
#     :param from2: Point
#     :param to2: Point
#     :param include_extend: if calculate the intersection on the extend
#     :param use_float: if use float data type
#     :return: Point or RealPoint
#     """
#     # create line 1 info
#     _a1 = to1.y - from1.y
#     _b1 = from1.x - to1.x
#     _c1 = -_a1 * from1.x - _b1 * from1.y
#     # create line 2 info
#     _a2 = to2.y - from2.y
#     _b2 = from2.x - to2.x
#     _c2 = -_a2 * from2.x - _b2 * from2.y
#     # check, whether the lines are parallel...
#     _ka = _a1 / _b1 if _b1 != 0 else -1
#     _kb = _a2 / _b2 if _b2 != 0 else -1
#     if _ka == _kb: return None
#     # find intersection point
#     _xi = ((_b1 * _c2 - _c1 * _b2) / (_a1 * _b2 - _a2 * _b1))
#     _yi = (-(_a1 * _c2 - _a2 * _c1) / (_a1 * _b2 - _a2 * _b1))
#
#     if not include_extend:
#         if (((from1.x - _xi) * (_xi - to1.x) >= 0) and
#                 ((from2.x - _xi) * (_xi - to2.x) >= 0) and
#                 ((from1.y - _yi) * (_yi - to1.y) >= 0) and
#                 ((from2.y - _yi) * (_yi - to2.y) >= 0)):
#             return wx.Point(_xi, _yi) if not use_float else wx.RealPoint(_xi, _yi)
#         else:
#             return None
#     else:
#         return wx.Point(_xi, _yi) if not use_float else wx.RealPoint(_xi, _yi)


def util_section_middle_split(length, min_dist):
    if length <= min_dist:
        return 1
    else:
        _half = length / 2
        _section_num = 1
        while _half > min_dist:
            _section_num += 1
            _half /= 2
        return _section_num


def util_sorted_groupby(iterable, key=None, reverse=False):
    """
    Return pairs (label, group) grouped and sorted by label = key(item).
    """
    _groups = defaultdict(list)
    for value in iterable:
        _groups[key(value)].append(value)

    def sort_key(e):
        return e[0]

    return sorted(_groups.items(), key=sort_key, reverse=reverse)


def util_guess_type(s):
    try:
        value = ast.literal_eval(s)
    except ValueError:
        return str
    else:
        return type(value)


def util_get_size(path):
    if os.path.isfile(path):
        return os.path.getsize(path)
    elif os.path.isdir(path):
        return util_get_dir_size(path)


def util_get_dir_size(path='.'):
    _size = 0
    _folder_cnt = 0
    _file_cnt = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                _size += entry.stat().st_size
                _file_cnt += 1
            elif entry.is_dir():
                _folder_cnt += 1
                _cnt1, _cnt2, _cnt3 = util_get_dir_size(entry.path)
                _folder_cnt += _cnt1
                _file_cnt += _cnt2
                _size += _cnt3
    return _folder_cnt, _file_cnt, _size


def util_approximate_size(size, flag_1024_or_1000=False):
    _mult = 1024 if flag_1024_or_1000 else 1000
    for unit in SIZE_UNITS[_mult]:
        size = size / _mult
        if size < _mult:
            return '{0:.3f} {1}'.format(size, unit)


def util_get_actual_pubsub_topic_for_instance(instance: object, topic_name: str):
    return '%s:%s' % (id(instance), topic_name)

# -*- coding: utf-8 -*-

"""
Ctypes bindings for libxdo
"""

import ctypes
from ctypes import (
    POINTER, c_char_p, c_int, c_ulong, c_void_p)

from ctypes.util import find_library

libxdo = ctypes.CDLL(find_library("xdo"))
libc = ctypes.CDLL(ctypes.util.find_library('c'))

libc.free.argtypes = (c_void_p,)
libc.free.restype = None
libc.free.__doc__ = """\
free data allocated from malloc
(this is useful for disposing of the results of libxdo.xdo_get_active_modifiers)
"""

XDO_ERROR = 1
XDO_SUCCESS = 0

# Window type is just defined as ``unsigned long``
window_t = c_ulong
useconds_t = c_ulong

class XdoException(Exception):
    pass

def _errcheck(result, func, arguments):
    """
    Error checker for functions returning an integer indicating
    success (0) / failure (1).

    Raises a XdoException in case of error, otherwise just
    returns ``None`` (returning the original code, 0, would be
    useless anyways..)
    """

    if result != 0:
        raise XdoException(
            'Function {0} returned error code {1}'
            .format(func.__name__, result))
    return None  # be explicit :)

# CURRENTWINDOW is a special identifier for xdo input faking (mouse and
# keyboard) functions like xdo_send_keysequence_window that indicate
# we should target the current window, not a specific window.
#
# Generally, this means we will use XTEST instead of XSendEvent when sending
# events.

CURRENTWINDOW = 0

# all the types are opaque types:
xdo_ptr = c_void_p
charcodemap_ptr = c_void_p

# ============================================================================
# xdo_t* xdo_new(const char *display);
libxdo.xdo_new.argtypes = (c_char_p,)
libxdo.xdo_new.restype = xdo_ptr
libxdo.xdo_new.__doc__ = """\
Create a new xdo_ptr instance.

:param display: the string display name, such as ":0". If null, uses the
environment variable DISPLAY just like XOpenDisplay(NULL).

:return: Pointer to a new xdo_ptr or NULL on failure
"""

# ============================================================================
# const char *xdo_version(void);
libxdo.xdo_version.argtypes = ()
libxdo.xdo_version.restype = c_char_p
libxdo.xdo_version.__doc__ = """\
Return a string representing the version of this library
"""

# ============================================================================
# void xdo_free(xdo_t *xdo);
libxdo.xdo_free.argtypes = (xdo_ptr,)
libxdo.xdo_free.__doc__ = """\
Free and destroy an xdo_ptr instance.

If close_display_when_freed is set, then we will also close the Display.
"""


# ============================================================================
# int xdo_enter_text_window(const xdo_t *xdo, Window window,
#     const char *string, useconds_t delay);
libxdo.xdo_enter_text_window.argtypes = (
    xdo_ptr, window_t, c_char_p, useconds_t)
libxdo.xdo_enter_text_window.restype = c_int
libxdo.xdo_enter_text_window.errcheck = _errcheck
libxdo.xdo_enter_text_window.__doc__ = """
Type a string to the specified window.

If you want to send a specific key or key sequence, such as "alt+l", you
want instead xdo_send_keysequence_window(...).

:param window: The window you want to send keystrokes to or CURRENTWINDOW
:param string: The string to type, like "Hello world!"
:param delay: The delay between keystrokes in microseconds.
    12000 is a decent choice if you don't have other plans.
"""

# ============================================================================
# int xdo_send_keysequence_window(const xdo_t *xdo, Window window,
#     const char *keysequence, useconds_t delay);
libxdo.xdo_send_keysequence_window.argtypes = (
    xdo_ptr, window_t, c_char_p, useconds_t)
libxdo.xdo_send_keysequence_window.restype = c_int
libxdo.xdo_send_keysequence_window.errcheck = _errcheck
libxdo.xdo_send_keysequence_window.__doc__ = """
Send a keysequence to the specified window.

This allows you to send keysequences by symbol name. Any combination
of X11 KeySym names separated by '+' are valid. Single KeySym names
are valid, too.

Examples:
  "l"
  "semicolon"
  "alt+Return"
  "Alt_L+Tab"

If you want to type a string, such as "Hello world." you want to instead
use xdo_enter_text_window.

:param window: The window you want to send the keysequence to or CURRENTWINDOW
:param keysequence: The string keysequence to send.
:param delay: The delay between keystrokes in microseconds.
"""

# ============================================================================
# int xdo_focus_window(const xdo_t *xdo, Window wid);
libxdo.xdo_focus_window.argtypes = (xdo_ptr, window_t)
libxdo.xdo_focus_window.restype = c_int
libxdo.xdo_focus_window.errcheck = _errcheck
libxdo.xdo_focus_window.__doc__ = """\
Focus a window.

:param window: the window to focus.
"""

# ============================================================================
# int xdo_get_focused_window(const xdo_t *xdo, Window *window_ret);
libxdo.xdo_get_focused_window.argtypes = (xdo_ptr, POINTER(window_t))
libxdo.xdo_get_focused_window.restype = c_int
libxdo.xdo_get_focused_window.errcheck = _errcheck
libxdo.xdo_get_focused_window.__doc__ = """\
Get the window currently having focus.

:param window_ret:
    Pointer to a window where the currently-focused window
    will be stored.
"""

# ============================================================================
# int xdo_wait_for_window_focus(const xdo_t *xdo, Window window,
#     int want_focus);
libxdo.xdo_wait_for_window_focus.argtypes = (
    xdo_ptr, window_t, c_int)
libxdo.xdo_wait_for_window_focus.restype = c_int
libxdo.xdo_wait_for_window_focus.errcheck = _errcheck
libxdo.xdo_wait_for_window_focus.__doc__ = """\
Wait for a window to have or lose focus.

:param window: The window to wait on
:param want_focus: If 1, wait for focus. If 0, wait for loss of focus.
"""


# ============================================================================
# int xdo_get_active_modifiers(const xdo_t *xdo, charcodemap_t **keys,
#                              int *nkeys);
libxdo.xdo_get_active_modifiers.argtypes = (
    xdo_ptr, POINTER(charcodemap_ptr), POINTER(c_int))
libxdo.xdo_get_active_modifiers.restype = c_int
libxdo.xdo_get_active_modifiers.errcheck = _errcheck
libxdo.xdo_get_active_modifiers.__doc__ = """\
Get a list of active keys.

:param keys: Pointer to the array of charcodemap_t that will be allocated
   by this function.
:param nkeys: Pointer to integer where the number of keys will be stored.

The returned object must be freed.
"""

# ============================================================================
# int xdo_clear_active_modifiers(const xdo_t *xdo, Window window,
#                                charcodemap_t *active_mods,
#                                int active_mods_n);
libxdo.xdo_clear_active_modifiers.argtypes = (
    xdo_ptr, window_t, charcodemap_ptr, c_int)
libxdo.xdo_clear_active_modifiers.restype = c_int
libxdo.xdo_clear_active_modifiers.errcheck = _errcheck
libxdo.xdo_clear_active_modifiers.__doc__ = """\
Send any events necesary to clear the the active modifiers.
For example, if you are holding 'alt' when xdo_get_active_modifiers is
called, then this method will send a key-up for 'alt'
"""

# ============================================================================
# int xdo_set_active_modifiers(const xdo_t *xdo, Window window,
#                              charcodemap_t *active_mods,
#                              int active_mods_n);
libxdo.xdo_set_active_modifiers.argtypes = (
    xdo_ptr, window_t, charcodemap_ptr, c_int)
libxdo.xdo_set_active_modifiers.restype = c_int
libxdo.xdo_set_active_modifiers.errcheck = _errcheck
libxdo.xdo_set_active_modifiers.__doc__ = """\
Send any events necessary to make these modifiers active.
This is useful if you just cleared the active modifiers and then wish
to restore them after.
"""

# -*- coding: utf-8 -*-

import ctypes
import os

from ._xdo import libxdo as _libxdo
from ._xdo import libc as _libc
from ._xdo import charcodemap_ptr as _charcodemap_ptr
from ._xdo import window_t as _window_t
from ._xdo import CURRENTWINDOW
from datetime import timedelta
from typing import Any, Callable, TypeVar, cast, Optional, Union
import warnings

F = TypeVar('F', bound=Callable[..., Any])

def deprecated(func: F) -> F:
    '''This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.'''
    def new_func(*args: Any, **kwargs: Any) -> Any:
        warnings.warn("Call to deprecated function {}.".format(func.__name__),
                      category=DeprecationWarning)
        return func(*args, **kwargs)
    new_func.__name__ = func.__name__
    new_func.__doc__ = func.__doc__
    new_func.__dict__.update(func.__dict__)
    return cast(F, new_func)

def version() -> str:
    return _libxdo.xdo_version().decode('utf-8')

class xdo(object):
    def __init__(self, display: Optional[str]=None) -> None:
        if display is None:
            display = os.environ.get('DISPLAY')
        self._xdo = _libxdo.xdo_new(None if display is None else display.encode('utf-8'))
        if self._xdo is None:
            raise SystemError("Could not initialize libxdo")


    def enter_text_window(self, string:Union[str,bytes], clearmodifiers: bool=True,
                          delay: Union[int, timedelta]=timedelta(microseconds=12000),
                          window: int=CURRENTWINDOW) -> None:
        """
        Type a string to the specified window.

        If you want to send a specific key or key sequence, such as
        "alt+l", you want instead the ``send_keysequence_window(...)``
        function.

        :param string:
            The string to type, like "Hello world!"
        :param delay:
            The delay between keystrokes as a datetime.timedelta. default: 12 milliseconds.
            If passed as an int, it will be treated as microseconds
        :param window:
            The window you want to send keystrokes to or (by default) xdo.CURRENTWINDOW
        :param clearmodifiers:
            Whether to clear any current modifier keys before sending
            the text (defaults to True).
        """
        if isinstance(delay, timedelta):
            delay_int = int(delay.total_seconds() * 1000000)
        elif isinstance(delay, int):
            delay_int = delay
        else:
            raise TypeError("delay parameter should be either a timedelta or an int")

        if isinstance(string, str):
            # FIXME: is it right to assume that we're going to encode
            # in UTF-8?  if the sender wants to emit a bytestring,
            # they can just send it as a bytestring in the first
            # place.
            string = string.encode('utf-8')

        if clearmodifiers:
            active_mods_n = ctypes.c_int(0)
            active_mods = _charcodemap_ptr()
            _libxdo.xdo_get_active_modifiers(self._xdo, ctypes.byref(active_mods),
                                             ctypes.byref(active_mods_n))
            _libxdo.xdo_clear_active_modifiers(self._xdo, window, active_mods,
                                               active_mods_n)
        ret = _libxdo.xdo_enter_text_window(self._xdo, window, string,
                                            delay_int)
        if clearmodifiers:
            _libxdo.xdo_set_active_modifiers(self._xdo, window, active_mods,
                                             active_mods_n)
            _libc.free(active_mods)
            
        return ret

    def send_keysequence_window(self, keysequence: Union[str,bytes], clearmodifiers: bool=True,
                                delay: Union[timedelta, int]=timedelta(microseconds=12000),
                                window: int=CURRENTWINDOW) -> None:
        """
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

        :param window:
            The window you want to send the keysequence to or CURRENTWINDOW
        :param keysequence:
            The string keysequence to send.
        :param delay:
            The delay between keystrokes as a datetime.timedelta. default: 12 milliseconds.
            If passed as an int, it will be treated as microseconds
        :param clearmodifiers:
            Whether to clear any current modifier keys before sending
            the keysequence (defaults to True).
        """
        if isinstance(delay, timedelta):
            delay_int = int(delay.total_seconds() * 1000000)
        elif isinstance(delay, int):
            delay_int = delay
        else:
            raise TypeError("delay parameter should be either a timedelta or an int")

        if isinstance(keysequence, str):
            # FIXME: is it right to assume that we're going to encode
            # in UTF-8?  if the sender wants to send a keysequence as
            # a bytestring, they can just send it as a bytestring in
            # the first place.
            keysequence = keysequence.encode('utf-8')

        if clearmodifiers:
            active_mods_n = ctypes.c_int(0)
            active_mods = _charcodemap_ptr()
            _libxdo.xdo_get_active_modifiers(self._xdo, ctypes.byref(active_mods),
                                             ctypes.byref(active_mods_n))
            _libxdo.xdo_clear_active_modifiers(self._xdo, window, active_mods,
                                               active_mods_n)
        ret = _libxdo.xdo_send_keysequence_window(self._xdo, window, keysequence,
                                                  delay_int)
        if clearmodifiers:
            _libxdo.xdo_set_active_modifiers(self._xdo, window, active_mods,
                                             active_mods_n)
            _libc.free(active_mods)

        return ret

    @deprecated
    def type(self, string: Union[str,bytes], clearmodifiers: bool=True, delay: Union[int, timedelta]=12000, window: int=CURRENTWINDOW) -> None:
        """
        Please use enter_text_window() instead of type()!  note that the delay
        parameter for enter_text_window expects a datetime.timedelta
        """
        if isinstance(delay, int):
            delay = timedelta(microseconds=delay)
        return self.enter_text_window(string, clearmodifiers=clearmodifiers,
                                      delay=delay, window=window)

    def focus_window(self, window: int=CURRENTWINDOW) -> None:
        """
        Focus a window.

        :param wid: the window to focus.
        """
        return _libxdo.xdo_focus_window(self._xdo, window)

    def get_focused_window(self) -> int:
        """
        Get the window currently having focus.

        :returns window:
        identifier for the currently-focused window
        """
        window_ret = _window_t(0)
        _libxdo.xdo_get_focused_window(self._xdo, ctypes.byref(window_ret))
        return window_ret.value

    def wait_for_window_focus(self, window: int, want_focus: bool=True) -> None:
        """
        Wait for a window to have or lose focus.

        :param window: The window to wait on
        :param want_focus: If True, wait for focus. If False, wait for loss of focus. (default: True)
        """
        return _libxdo.xdo_wait_for_window_focus(self._xdo, window, 1 if want_focus else 0)

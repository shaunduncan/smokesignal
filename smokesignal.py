"""
smokesignal.py - simple event signaling
"""
import sys
import types

from collections import defaultdict
from functools import partial


__all__ = ['emit', 'emitting', 'signals', 'responds_to', 'on', 'once',
           'disconnect', 'disconnect_from', 'clear', 'clear_all']


# Collection of receivers/callbacks
_receivers = defaultdict(set)
_pyversion = sys.version_info[:2]


def emit(signal, *args, **kwargs):
    """
    Emits a single signal to call callbacks registered to respond to that signal.
    Optionally accepts args and kwargs that are passed directly to callbacks.

    :param signal: Signal to send
    """
    for callback in set(_receivers[signal]):  # Make a copy in case of any ninja signals
        _call(callback, args=args, kwargs=kwargs)


class emitting(object):
    """
    Context manager for emitting signals either on enter or on exit of a context.
    By default, if this context manager is created using a single arg-style argument,
    it will emit a signal on exit. Otherwise, keyword arguments indicate signal points
    """
    def __init__(self, exit, enter=None):
        self.exit = exit
        self.enter = enter

    def __enter__(self):
        if self.enter is not None:
            emit(self.enter)

    def __exit__(self, exc_type, exc_value, tb):
        emit(self.exit)


def _call(callback, args=[], kwargs={}):
    """
    Calls a callback with optional args and keyword args lists. This method exists so
    we can inspect the `_max_calls` attribute that's set by `_on`. If this value is None,
    the callback is considered to have no limit. Otherwise, an integer value is expected
    and decremented until there are no remaining calls
    """
    if not hasattr(callback, '_max_calls'):
        callback._max_calls = None

    if callback._max_calls is None or callback._max_calls > 0:
        if callback._max_calls is not None:
            callback._max_calls -= 1

        return callback(*args, **kwargs)


def signals(callback):
    """
    Returns a tuple of all signals for a particular callback

    :param callback: A callable registered with smokesignal
    :returns: Tuple of all signals callback responds to
    """
    return tuple(s for s in _receivers if responds_to(callback, s))


def responds_to(callback, signal):
    """
    Returns bool if callback will respond to a particular signal

    :param callback: A callable registered with smokesignal
    :param signal: A signal to check if callback responds
    :returns: True if callback responds to signal, False otherwise
    """
    return callback in _receivers[signal]


def on(signals, callback=None, max_calls=None):
    """
    Registers a single callback for receiving an event (or event list). Optionally,
    can specify a maximum number of times the callback should receive a signal. This
    method works as both a function and a decorator::

        smokesignal.on('foo', my_callback)

        @smokesignal.on('foo')
        def my_callback():
            pass

    :param signals: A single signal or list/tuple of signals that callback should respond to
    :param callback: A callable that should repond to supplied signal(s)
    :param max_calls: Integer maximum calls for callback. None for no limit.
    """
    if isinstance(callback, int) or callback is None:
        # Decorated
        if isinstance(callback, int):
            # Here the args were passed arg-style, not kwarg-style
            callback, max_calls = max_calls, callback
        return partial(_on, signals, max_calls=max_calls)
    elif isinstance(callback, types.MethodType):
        # callback is a bound instance method, so we need to wrap it in a function
        def _callback(*args, **kwargs):
            return callback(*args, **kwargs)
        return _on(signals, _callback, max_calls=max_calls)
    else:
        # Function call
        return _on(signals, callback, max_calls=max_calls)


def _on(on_signals, callback, max_calls=None):
    """
    Proxy for `smokesignal.on`, which is compatible as both a function call and
    a decorator. This method cannot be used as a decorator

    :param signals: A single signal or list/tuple of signals that callback should respond to
    :param callback: A callable that should repond to supplied signal(s)
    :param max_calls: Integer maximum calls for callback. None for no limit.
    """
    assert callable(callback), 'Signal callbacks must be callable'

    # Support for lists of signals
    if not isinstance(on_signals, (list, tuple)):
        on_signals = [on_signals]

    callback._max_calls = max_calls

    # Register the callback
    for signal in on_signals:
        _receivers[signal].add(callback)

    # Setup responds_to partial for use later
    if not hasattr(callback, 'responds_to'):
        callback.responds_to = partial(responds_to, callback)

    # Setup signals partial for use later.
    if not hasattr(callback, 'signals'):
        callback.signals = partial(signals, callback)

    return callback


def once(signals, callback=None):
    """
    Registers a callback that will respond to an event at most one time

    :param signals: A single signal or list/tuple of signals that callback should respond to
    :param callback: A callable that should repond to supplied signal(s)
    """
    return on(signals, callback, max_calls=1)


def disconnect(callback):
    """
    Removes a callback from all signal registries and prevents it from responding
    to any emitted signal.

    :param callback: A callable registered with smokesignal
    """
    # This is basically what `disconnect_from` does, but that method guards against
    # callbacks not responding to signal arguments. We don't need that because we're
    # disconnecting all the valid ones here
    for signal in signals(callback):
        _receivers[signal].remove(callback)


def disconnect_from(callback, signals):
    """
    Removes a callback from specified signal registries and prevents it from responding
    to any emitted signal.

    :param callback: A callable registered with smokesignal
    :param signals: A single signal or list/tuple of signals
    """
    # Support for lists of signals
    if not isinstance(signals, (list, tuple)):
        signals = [signals]

    # Remove callback from receiver list if it responds to the signal
    for signal in signals:
        if responds_to(callback, signal):
            _receivers[signal].remove(callback)


def clear(*signals):
    """
    Clears all callbacks for a particular signal or signals
    """
    signals = signals if signals else _receivers.keys()

    for signal in signals:
        _receivers[signal].clear()


def clear_all():
    """
    Clears all callbacks for all signals
    """
    for key in _receivers.keys():
        _receivers[key].clear()

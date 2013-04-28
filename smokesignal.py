"""
smokesignal.py - simple event signaling
"""
import sys

from collections import defaultdict
from functools import partial, wraps


# Collection of receivers/callbacks
_receivers = defaultdict(set)
_pyversion = sys.version_info[:2]


def emit(signal, *args, **kwargs):
    """
    Emits a signal to all registered callbacks
    """
    for callback in _receivers[signal]:
        callback(*args, **kwargs)


def signals(callback):
    """
    Returns a tuple of all signals for a particular callback
    """
    return (s for s in _receivers if is_registered_for(callback, s))


def is_registered_for(callback, signal):
    """
    Returns bool if callback will respond to a particular signal
    """
    for fn in _receivers[signal]:
        if callback in (fn, getattr(fn, '__wrapped__', None)):
            return True
    return False


def on(signals, callback=None, max_calls=None):
    """
    Registers a single callback for receiving an event (or event list). Optionally,
    can specify a maximum number of times the callback should receive a signal
    """
    if isinstance(callback, int) or callback is None:
        # Decorated
        if isinstance(callback, int):
            # Here the args were passed arg-style, not kwarg-style
            callback, max_calls = max_calls, callback
        return partial(_on, signals, max_calls=max_calls)
    else:
        # Function call
        return _on(signals, callback, max_calls=max_calls)


def _on(signals, callback, max_calls=None):
    """
    Proxy for `smokesignal.on`, which is compatible as both a function call and
    a decorator. This method cannot be used as a decorator
    """
    print signals, callback, max_calls
    assert callable(callback), u'Signal callbacks must be callable'

    # Support for lists of signals
    if not isinstance(signals, (list, tuple)):
        signals = [signals]

    callback._max_calls = max_calls

    # Create a wrapper so we can ensure we limit number of calls
    @wraps(callback)
    def wrapper(*args, **kwargs):
        if callback._max_calls is None or callback._max_calls > 0:
            if callback._max_calls is not None:
                callback._max_calls -= 1
            return callback(*args, **kwargs)

    # Compatibility - Python >= 3.2 does this for us
    if _pyversion < (3, 2):
        wrapper.__wrapped__ = callback

    for signal in signals:
        _receivers[signal].add(wrapper)


def once(signals, callback=None):
    """
    Registers a callback that will receive at most one event signal
    """
    return on(signals, callback, max_calls=1)


def disconnect(callback):
    """
    Unregisters a callback from receiving any and all events
    """
    # TODO: This is inefficient. Callbacks should be aware of their signals
    disconnect_from(callback, *[s for s in _receivers if is_registered_for(callback, s)])


def disconnect_from(callback, *signals):
    """
    Unregisters a callback from receiving specified events
    """
    # XXX: This is pretty inefficient and I should be able to quickly remove
    # something without checking the entire receiver list
    for signal in signals:
        for check in _receivers[signal].copy():
            if check == callback:
                _receivers[signal].remove(callback)
            elif callback == getattr(check, '__wrapped__', None):
                _receivers[signal].remove(check)


def clear(*signals):
    """
    Clears all callbacks for a particular signal
    """
    for signal in signals:
        _receivers[signal].clear()


def clear_all():
    """
    Clears all callbacks for all signals
    """
    for key in _receivers.keys():
        _receivers[key].clear()

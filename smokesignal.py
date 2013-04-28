"""
smokesignal.py - simple event signaling
"""
import sys

from collections import defaultdict
from functools import wraps


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


# TODO: This should be a function decorator as well
# so I can register a callback more easily:
#
# @smokesignal.on('foo')
# def handle_foo():
#     pass
#
def on(signals, callback, max_calls=None):
    """
    Registers a single callback for receiving an event (or event list). Optionally,
    can specify a maximum number of times the callback should receive a signal
    """
    assert callable(callback), u'Signal callbacks must be callable'

    # Support for lists of signals
    if not isinstance(signals, (list, tuple)):
        signals = [signals]

    # Create a wrapper so we can ensure we limit number of calls
    @wraps(callback)
    def wrapper(*args, **kwargs):
        if callback._max_calls is not None and callback._max_calls > 0:
            callback._max_calls -= 1
            return callback(*args, **kwargs)

    callback._max_calls = max_calls

    # Compatibility - Python >= 3.2 does this for us
    if _pyversion < (3, 2):
        wrapper.__wrapped__ = callback

    for signal in signals:
        _receivers[signal].add(wrapper)


def once(signals, callback):
    """
    Registers a callback that will receive at most one event signal
    """
    return on(signals, callback, max_calls=1)


def disconnect(callback):
    """
    Unregisters a callback from receiving any and all events
    """
    # TODO: This is inefficient. Callbacks should be aware of their signals
    for signal in _receivers:
        if callback in _receivers[signal]:
            disconnect_from(callback, signal)


def disconnect_from(callback, *signals):
    """
    Unregisters a callback from receiving specified events
    """
    for signal in signals:
        _receivers[signal].remove(callback)


def clear(signal):
    """
    Clears all callbacks for a particular signal
    """
    _receivers[signal].clear()


def clear_all():
    """
    Clears all callbacks for all signals
    """
    for key in _receivers.keys():
        _receivers[key].clear()

"""
smokesignal.py - simple event signaling
"""
from collections import defaultdict
from functools import wraps


# Collection of receivers/callbacks
_receivers = defaultdict(set)


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
    return callback in _receivers[signal]


# TODO: This should be a function decorator as well
# so I can register a callback more easily:
#
# @smokesignal.on('foo')
# def handle_foo():
#     pass
#
def on(signal, callback):
    """
    Registers a single callback for receiving an event emit
    """
    assert callable(callback), u'Signal callbacks must be callable'
    _receivers[signal].add(callback)


def once(signal, callback):
    """
    Registers a callback that will receive at most one event signal
    """
    assert callable(callback), u'Signal callbacks must be callable'
    callback._called = False

    @wraps(callback)
    def wrapper(*args, **kwargs):
        if not callback._called:
            callback._called = True
            return callback(*args, **kwargs)

    on(signal, wrapper)


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

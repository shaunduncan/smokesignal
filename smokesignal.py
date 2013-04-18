"""
smokesignal.py - simple event signaling
"""
from collections import defaultdict
from functools import wraps


__all__ = ['emit', 'on', 'once', 'disconnect']


receivers = defaultdict(set)


def emit(signal, *args, **kwargs):
    """
    Emits a signal to all registered callbacks
    """
    for callback in receivers[signal]:
        callback(*args, **kwargs)


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
    if not callable(callback):
        raise AssertionError('Signal callbacks must be callable')

    receivers[signal].add(callback)


def once(signal, callback):
    """
    Registers a callback that will receive at most one event signal
    """
    if not callable(callback):
        raise AssertionError('Signal callbacks must be callable')

    callback._called = False

    @wraps(callback)
    def wrapper(*args, **kwargs):
        if not callback._called:
            callback._called = True
            return callback(*args, **kwargs)

    on(signal, wrapper)


def disconnect(signal, callback):
    """
    Unregisters a callback from receiving events
    """
    receivers[signal].remove(callback)


def clear(signal):
    """
    Clears all callbacks for a particular signal
    """
    receivers[signal].clear()


def clear_all():
    """
    Clears all callbacks for all signals
    """
    for key in receivers.keys():
        receivers[key].clear()

"""
smokesignal.py - simple event signaling
"""
from collections import defaultdict

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


def disconnect(signal, callback):
    """
    Unregisters a callback from receiving events
    """
    receivers[signal].remove(callback)

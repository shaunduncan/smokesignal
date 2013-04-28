smokesignal.py - simple python signaling
========================================

`smokesignal.py` is a simple python library for sending and receiving signals.
It draws some inspiration from the django signal framework but is meant as a
general purpose variant.


Requirements & Compatibility
----------------------------

`smokesignal.py` requires no dependencies outside of the python standard library.
It has been tested on and is compatible with python versions 2.6, 2.7, 3.2, and 3.3.


How To Use
----------

Most uses of `smokesignal.py` involve the functions `on`, which registers a single
method to respond to a signal, and `emit`, which sends a signal. The `on` method can
be used either as a decorator or as a plain function call::

    import smokesignal

    @smokesignal.on('foo')
    def my_callback():
        pass

    smokesignal.on('foo', my_callback)

Once registered, a callback will respond once a signal is emitted::

    import smokesignal

    smokesignal.emit('foo')

Note that `emit` also accepts argument and keyword argument lists that are passed
directly to callbacks. You can also indicate the maximum number of times a callback
should respond to a signal with the `max_calls` keyword argument for `on`, or by using
the `once` method if all you need is for a callback to respond at most once.

If you no longer wish for a callback to respond to any signals, you can use either
`disconnect_from` if you intend on removing specific signals or `disconnect` if you intend
to remove all of them::

    import smokesignal

    smokesignal.disconnect(my_callback)
    smokesignal.disconnect_from(my_callback, 'foo)

Other batteries that some with `smokesignal.py` include::

    # Remove all callbacks for a signal
    smokesignal.clear('foo')

    # Remove all callbacks for all signals
    smokesignal.clear_all()

    # Get a tuple of all signals a callback responds to
    smokesignal.signals(my_callback)

    # Check if a callback responds to a signal
    smokesignal.responds_to(my_callback, 'foo')


Contribution and License
------------------------
Developed by Shaun Duncan (shaun [dot] duncan [at] gmail [dot] com) and is
licensed under the terms of a MIT license.

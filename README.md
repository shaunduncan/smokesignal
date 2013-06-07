# smokesignal - simple python signaling

[![Build Status](https://travis-ci.org/shaunduncan/smokesignal.png)](https://travis-ci.org/shaunduncan/smokesignal)

`smokesignal` is a simple python library for sending and receiving signals.
It draws some inspiration from the django signal framework but is meant as a
general purpose variant.


## Requirements & Compatibility

`smokesignal` requires no dependencies outside of the python standard library.
It has been tested on and is compatible with python versions 2.6, 2.7, 3.2, and 3.3.


## How To Use

Most uses of `smokesignal` involve registering a single callable to respond to a signal
using `on` and sending signals using `emit`.

### Registering Callbacks

Most callback registration happens using `on`, which can be used either as a decorator
or a direct function call. This method also accepts an optional argument `max_calls` which
indicates the maximum number of times a callback should respond to an emitted signal:

```python
import smokesignal

@smokesignal.on('foo')
def my_callback():
    pass

@smokesignal.on('foo', max_calls=2)
def my_callback():
    pass

smokesignal.on('foo', my_callback, max_calls=5)
```

If you intend a callback to respond to a signal at most one time, rather than indicating
`max_calls=1`, you can use `once` as a convenience:

```python
import smokesignal

@smokesignal.once('foo')
def my_callback():
    pass
```

### Sending Signals

Signals are sent to all registered callbacks using `emit`. This method optionally accepts
argument and keyword argument lists that are passed directly to each callback:

```python
import smokesignal

# Each callback responding to 'foo' is called
smokesignal.emit('foo')

# Each callback responding to 'foo' is called with arguments
smokesignal.emit('foo', 1, 2, 3, four=4)
```

You can also send signals with the included context manager `emitting`. By default, this context
manager accepts one argument, which is a signal to send once the context manager exits. However,
you can supply keyword arguments for `enter` and `exit` that will be sent at those points of the
context manager:

```python
import smokesignal

# 'foo' emitted on exit
with smokesignal.emitting('foo'):
    pass

# 'foo' emitted on enter, 'bar' emitted on exit
with smokesignal.emitting(enter='foo', exit='bar'):
    pass
```

### Reusable Single-signal Emitters

The emitter object allows for a reusable single-signal emitter. The smokesignal signal name is stored. When emit is
called, smokesignal calls the stored signal name.

```python
import smokesignal

my_emitter = emitter('foo')

my_emitter.emit() # calls the stored signal 'foo'.
```

#### Emitter with Context

Emitters are also capable of being used as a context manager just like smokesignal.emitting. The stored signal is
called on exit.

```python
import smokesignal

my_emitter = emitter('foo')

with my_emitter.emitting:
    do_work()
    # callbacks for signal 'foo' are called.
```

Need an enter signal called?

```python
import smokesignal

my_emitter = emitter('foo', enter='bar')

with my_emitter.emitting:
    # Enter: callbacks for signal 'bar' are called
    do_work()
    # Enter: callbacks for signal 'foo' are called
```

### Disconnecting Callbacks

If you no longer wish for a callback to respond to any signals, you can use either
`disconnect_from`, if you intend on removing specific signals, or `disconnect` if you intend
to remove all of them:

```python
import smokesignal

# my_callback will no longer respond to signals
smokesignal.disconnect(my_callback)

# my_callback will no longer respond to 'foo', but may repond to others
smokesignal.disconnect_from(my_callback, 'foo')
```

### Other Batteries Included


You can clear large swaths of callbacks using either `clear` or `clear_all`.
If you call `clear` without any arguments, it effectively works like `clear_all`:

```python
# Remove all callbacks responding to a specific signal
smokesignal.clear('foo')

# Remove all callbacks responding to all signals
smokesignal.clear_all()
smokesignal.clear()
```

Sometimes you may want to get a list of signals a callback responds to or quickly
check if a callback will respond to a certain signal. The `signals` and `responds_to`
are available for this purpose. Note that registering a callback to respond to a
signal will also create callable attributes of the callback for easier interaction
with these methods:

```python
# Get a tuple of all signals a callback responds to
smokesignal.signals(my_callback)

# Check if a callback responds to a signal
smokesignal.responds_to(my_callback, 'foo')

# Or as attributes of the callback
my_callback.signals()
my_callback.responds_to('foo')
```


## Caveats

What would be great is if you could decorate instance methods using `on` or `once`. However,
that doesn't work because there is no knowledge of the class instance at the time the callback
is registered to respond to signals:

```python
import smokesignal

class Foo(object):

    # THIS DOES NOT WORK
    @smokesignal.on('bar')
    def callback(self):
        pass
```

There is a workaround if you would like instance methods to respond to callbacks:

```python
import smokesignal

class Foo(object):
    def __init__(self, *args, **kwargs):
        @smokesignal.on('bar')
        def _callback():
            self.callback()
        super(Foo, self).__init__(*args, **kwargs)

    def callback(self):
        pass
```

The above will register the callback without any argument requirements but will
also ensure that the _intended_ callback method is called correctly.


## Changelog

### 0.3
- Callbacks now have callable attributes `responds_to` and `signals`
- Calling `clear` with no arguments will clear all callbacks for all signals

### 0.2
- Added `emitting` context manager
- Updated internals no longer require decorator magic for enforcing maximum call counts

### 0.1
- Initial Version


## Contribution and License

Developed by [Shaun Duncan](mailto:shaun.duncan@gmail.com) and is
licensed under the terms of a MIT license.

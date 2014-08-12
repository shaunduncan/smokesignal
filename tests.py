""" Unit tests """
from unittest import TestCase

from mock import Mock, patch

import smokesignal


class SmokesignalTestCase(TestCase):

    def setUp(self):
        self.callback = lambda x: x
        self.mock_callback = Mock()

    def tearDown(self):
        smokesignal.clear_all()

    def test_call_no_max_calls(self):
        def foo():
            foo.call_count += 1
        foo.call_count = 0

        for x in range(5):
            smokesignal._call(foo)

        assert foo.call_count == 5

    def test_call_with_max_calls(self):
        def foo():
            foo.call_count += 1
        foo.call_count = 0
        foo._max_calls = 1

        for x in range(5):
            smokesignal._call(foo)

        assert foo.call_count == 1

    def test_clear(self):
        smokesignal.on('foo', self.callback)
        assert len(smokesignal._receivers['foo']) == 1

        smokesignal.clear('foo')
        assert len(smokesignal._receivers['foo']) == 0

    def test_clear_no_args_clears_all(self):
        smokesignal.on(('foo', 'bar', 'baz'), self.callback)
        assert len(smokesignal._receivers['foo']) == 1
        assert len(smokesignal._receivers['bar']) == 1
        assert len(smokesignal._receivers['baz']) == 1

        smokesignal.clear()
        assert len(smokesignal._receivers['foo']) == 0
        assert len(smokesignal._receivers['bar']) == 0
        assert len(smokesignal._receivers['baz']) == 0


    def test_clear_many(self):
        smokesignal.on(('foo', 'bar', 'baz'), self.callback)
        assert len(smokesignal._receivers['foo']) == 1
        assert len(smokesignal._receivers['bar']) == 1
        assert len(smokesignal._receivers['baz']) == 1

        smokesignal.clear('foo', 'bar')
        assert len(smokesignal._receivers['foo']) == 0
        assert len(smokesignal._receivers['bar']) == 0
        assert len(smokesignal._receivers['baz']) == 1

    def test_clear_all(self):
        smokesignal.on(('foo', 'bar'), self.callback)
        assert len(smokesignal._receivers['foo']) == 1
        assert len(smokesignal._receivers['bar']) == 1

        smokesignal.clear_all()
        assert len(smokesignal._receivers['foo']) == 0
        assert len(smokesignal._receivers['bar']) == 0

    def test_emit_with_no_callbacks(self):
        smokesignal.emit('foo')

    def test_emit_with_callbacks(self):
        # Register first
        smokesignal.on('foo', self.mock_callback)
        assert smokesignal.responds_to(self.mock_callback, 'foo')

        smokesignal.emit('foo')
        assert self.mock_callback.called

    def test_emit_with_callback_args(self):
        # Register first
        smokesignal.on('foo', self.mock_callback)
        assert smokesignal.responds_to(self.mock_callback, 'foo')

        smokesignal.emit('foo', 1, 2, 3, foo='bar')
        assert self.mock_callback.called_with(1, 2, 3, foo='bar')

    def test_on_raises(self):
        self.assertRaises(AssertionError, smokesignal.on, 'foo', 'bar')

    def test_on_registers(self):
        assert len(smokesignal._receivers['foo']) == 0
        smokesignal.on('foo', self.callback)
        assert len(smokesignal._receivers['foo']) == 1

    def test_on_registers_many(self):
        assert len(smokesignal._receivers['foo']) == 0
        assert len(smokesignal._receivers['bar']) == 0

        smokesignal.on(('foo', 'bar'), self.callback)

        assert len(smokesignal._receivers['foo']) == 1
        assert len(smokesignal._receivers['bar']) == 1

    def test_on_max_calls(self):
        # Make a method that has a call count
        def cb():
            cb.call_count += 1
        cb.call_count = 0

        # Register first
        smokesignal.on('foo', cb, max_calls=3)
        assert len(smokesignal._receivers['foo']) == 1

        # Call a bunch of times
        for x in range(10):
            smokesignal.emit('foo')

        assert cb.call_count == 3

    def test_on_decorator_registers(self):
        assert len(smokesignal._receivers['foo']) == 0

        @smokesignal.on('foo')
        def my_callback():
            pass

        assert len(smokesignal._receivers['foo']) == 1

    def test_on_decorator_registers_many(self):
        assert len(smokesignal._receivers['foo']) == 0
        assert len(smokesignal._receivers['bar']) == 0

        @smokesignal.on(('foo', 'bar'))
        def my_callback():
            pass

        assert len(smokesignal._receivers['foo']) == 1
        assert len(smokesignal._receivers['bar']) == 1

    def test_on_decorator_max_calls(self):
        # Make a method that has a call count
        def cb():
            cb.call_count += 1
        cb.call_count = 0

        # Register first - like a cecorator
        smokesignal.on('foo', max_calls=3)(cb)
        assert len(smokesignal._receivers['foo']) == 1

        # Call a bunch of times
        for x in range(10):
            smokesignal.emit('foo')

        assert cb.call_count == 3

    def test_disconnect(self):
        # Register first
        smokesignal.on(('foo', 'bar'), self.callback)
        assert smokesignal.responds_to(self.callback, 'foo')
        assert smokesignal.responds_to(self.callback, 'bar')

        smokesignal.disconnect(self.callback)
        assert not smokesignal.responds_to(self.callback, 'foo')
        assert not smokesignal.responds_to(self.callback, 'bar')

    def test_disconnect_from_removes_only_one(self):
        # Register first
        smokesignal.on(('foo', 'bar'), self.callback)
        assert smokesignal.responds_to(self.callback, 'foo')
        assert smokesignal.responds_to(self.callback, 'bar')

        # Remove it
        smokesignal.disconnect_from(self.callback, 'foo')
        assert not smokesignal.responds_to(self.callback, 'foo')
        assert smokesignal.responds_to(self.callback, 'bar')

    def test_disconnect_from_removes_all(self):
        # Register first
        smokesignal.on(('foo', 'bar'), self.callback)
        assert smokesignal.responds_to(self.callback, 'foo')
        assert smokesignal.responds_to(self.callback, 'bar')

        # Remove it
        smokesignal.disconnect_from(self.callback, ('foo', 'bar'))
        assert not smokesignal.responds_to(self.callback, 'foo')
        assert not smokesignal.responds_to(self.callback, 'bar')

    def test_signals(self):
        # Register first
        smokesignal.on(('foo', 'bar'), self.callback)

        assert 'foo' in smokesignal.signals(self.callback)
        assert 'bar' in smokesignal.signals(self.callback)

    def test_responds_to_true(self):
        # Register first
        smokesignal.on('foo', self.callback)
        assert smokesignal.responds_to(self.callback, 'foo') is True

    def test_responds_to_false(self):
        # Register first
        smokesignal.on('foo', self.callback)
        assert smokesignal.responds_to(self.callback, 'bar') is False

    def test_once_raises(self):
        self.assertRaises(AssertionError, smokesignal.once, 'foo', 'bar')

    def test_once(self):
        # Make a method that has a call count
        def cb():
            cb.call_count += 1
        cb.call_count = 0

        # Register first
        smokesignal.once('foo', cb)
        assert len(smokesignal._receivers['foo']) == 1

        # Call twice
        smokesignal.emit('foo')
        smokesignal.emit('foo')

        assert cb.call_count == 1

    def test_once_decorator(self):
        # Make a method that has a call count
        def cb():
            cb.call_count += 1
        cb.call_count = 0

        # Register first like a decorator
        smokesignal.once('foo')(cb)
        assert len(smokesignal._receivers['foo']) == 1

        # Call twice
        smokesignal.emit('foo')
        smokesignal.emit('foo')

        assert cb.call_count == 1

    @patch('smokesignal.emit')
    def test_emitting_arg_style(self, emit):
        with smokesignal.emitting('foo'):
            pass

        assert emit.call_count == 1

    @patch('smokesignal.emit')
    def test_emitting_kwarg_style(self, emit):
        with smokesignal.emitting(enter='foo', exit='bar'):
            pass

        assert emit.call_count == 2

    def test_on_creates_responds_to_fn(self):
        # Registering a callback should create partials to smokesignal
        # methods for later user
        smokesignal.on('foo', self.callback)

        assert hasattr(self.callback, 'responds_to')
        assert self.callback.responds_to('foo')

    def test_on_creates_signals_fn(self):
        # Registering a callback should create partials to smokesignal
        # methods for later user
        smokesignal.on(('foo', 'bar'), self.callback)

        assert hasattr(self.callback, 'signals')
        assert 'foo' in self.callback.signals()
        assert 'bar' in self.callback.signals()

    def test_instance_method(self):
        class Foo(object):
            def __init__(self):
                # Preferred way
                smokesignal.on('foo', self.foo)

                # Old way
                @smokesignal.on('foo')
                def _bar():
                    self.bar()

                self.foo_count = 0
                self.bar_count = 0

            def foo(self):
                self.foo_count += 1

            def bar(self):
                self.bar_count += 1

        foo = Foo()
        smokesignal.emit('foo')
        smokesignal.emit('bar')
        assert foo.foo_count == 1
        assert foo.bar_count == 1

    def test_instance_method_passes_args_kwargs(self):
        class Foo(object):
            def __init__(self):
                smokesignal.on('foo', self.foo)
                self.foo_count = 0

            def foo(self, n, mult=1):
                self.foo_count += (n * mult)

        foo = Foo()
        smokesignal.emit('foo', 5, mult=6)
        assert foo.foo_count == 30

    def test_instance_method_max_calls(self):
        class Foo(object):
            def __init__(self):
                smokesignal.once('foo', self.foo)
                self.foo_count = 0

            def foo(self):
                self.foo_count += 1

        foo = Foo()
        smokesignal.emit('foo')
        smokesignal.emit('foo')
        smokesignal.emit('foo')
        smokesignal.emit('foo')
        smokesignal.emit('foo')
        assert foo.foo_count == 1

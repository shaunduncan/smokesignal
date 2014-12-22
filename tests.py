""" Unit tests """
import types

from collections import defaultdict

import pytest

from mock import Mock, call, patch

import smokesignal


class TestSmokesignal(object):

    def setup(self):
        self.fn = Mock(spec=types.FunctionType)
        patch.object(smokesignal, 'receivers', defaultdict(set)).start()

    def teardown(self):
        patch.stopall()

    def test_call_no_max_calls(self):
        for x in range(5):
            smokesignal._call(self.fn)
        assert self.fn.call_count == 5

    def test_call_with_max_calls(self):
        self.fn._max_calls = 1
        for x in range(5):
            smokesignal._call(self.fn)
        assert self.fn.call_count == 1

    def test_clear(self):
        smokesignal.on('foo', self.fn)
        assert smokesignal.receivers['foo'] == set([self.fn])

        smokesignal.clear('foo')
        assert smokesignal.receivers['foo'] == set()

    def test_clear_no_args_clears_all(self):
        smokesignal.on(('foo', 'bar', 'baz'), self.fn)
        assert smokesignal.receivers == {
            'foo': set([self.fn]),
            'bar': set([self.fn]),
            'baz': set([self.fn]),
        }

        smokesignal.clear()
        assert smokesignal.receivers == {
            'foo': set(),
            'bar': set(),
            'baz': set(),
        }

    def test_clear_many(self):
        smokesignal.on(('foo', 'bar', 'baz'), self.fn)
        smokesignal.clear('foo', 'bar')
        assert smokesignal.receivers == {
            'foo': set(),
            'bar': set(),
            'baz': set([self.fn]),
        }

    def test_clear_all(self):
        smokesignal.on(('foo', 'bar'), self.fn)
        assert smokesignal.receivers == {
            'foo': set([self.fn]),
            'bar': set([self.fn]),
        }

        smokesignal.clear_all()
        assert smokesignal.receivers == {
            'foo': set(),
            'bar': set(),
        }

    def test_emit_with_no_callbacks(self):
        try:
            smokesignal.emit('foo')
        except:
            pytest.fail('Emitting a signal with no callback should not have raised')

    def test_emit_with_callbacks(self):
        # Register first
        smokesignal.on('foo', self.fn)
        smokesignal.emit('foo')
        assert self.fn.called

    def test_emit_with_callback_args(self):
        # Register first
        smokesignal.on('foo', self.fn)
        smokesignal.emit('foo', 1, 2, 3, foo='bar')
        self.fn.assert_called_with(1, 2, 3, foo='bar')

    def test_on_must_have_callables(self):
        with pytest.raises(AssertionError):
            smokesignal.on('foo', 'bar')

    def test_on_registers(self):
        smokesignal.on('foo', self.fn)
        assert smokesignal.receivers['foo'] == set([self.fn])

    def test_on_registers_many(self):
        assert smokesignal.receivers == {}

        smokesignal.on(('foo', 'bar'), self.fn)

        assert smokesignal.receivers == {
            'foo': set([self.fn]),
            'bar': set([self.fn]),
        }

    def test_on_max_calls(self):
        # Register first
        smokesignal.on('foo', self.fn, max_calls=3)

        # Call a bunch of times
        for x in range(10):
            smokesignal.emit('foo')

        assert self.fn.call_count == 3

    def test_on_decorator_registers(self):
        @smokesignal.on('foo')
        def my_callback():
            pass
        assert smokesignal.receivers['foo'] == set([my_callback])

    def test_on_decorator_registers_many(self):
        @smokesignal.on(('foo', 'bar'))
        def my_callback():
            pass

        assert smokesignal.receivers == {
            'foo': set([my_callback]),
            'bar': set([my_callback]),
        }

    def test_on_decorator_max_calls(self):
        # Register first - like a decorator
        smokesignal.on('foo', max_calls=3)(self.fn)

        # Call a bunch of times
        for x in range(10):
            smokesignal.emit('foo')

        assert self.fn.call_count == 3

    def test_on_decorator_max_calls_as_arg(self):
        # Register first - like a decorator
        smokesignal.on('foo', 3)(self.fn)

        # Call a bunch of times
        for x in range(10):
            smokesignal.emit('foo')

        assert self.fn.call_count == 3

    def test_disconnect(self):
        # Register first
        smokesignal.on(('foo', 'bar'), self.fn)
        assert smokesignal.responds_to(self.fn, 'foo')
        assert smokesignal.responds_to(self.fn, 'bar')

        smokesignal.disconnect(self.fn)
        assert not smokesignal.responds_to(self.fn, 'foo')
        assert not smokesignal.responds_to(self.fn, 'bar')

    def test_disconnect_from_removes_only_one(self):
        # Register first
        smokesignal.on(('foo', 'bar'), self.fn)
        assert smokesignal.responds_to(self.fn, 'foo')
        assert smokesignal.responds_to(self.fn, 'bar')

        # Remove it
        smokesignal.disconnect_from(self.fn, 'foo')
        assert not smokesignal.responds_to(self.fn, 'foo')
        assert smokesignal.responds_to(self.fn, 'bar')

    def test_disconnect_from_removes_all(self):
        # Register first
        smokesignal.on(('foo', 'bar'), self.fn)
        assert smokesignal.responds_to(self.fn, 'foo')
        assert smokesignal.responds_to(self.fn, 'bar')

        # Remove it
        smokesignal.disconnect_from(self.fn, ('foo', 'bar'))
        assert not smokesignal.responds_to(self.fn, 'foo')
        assert not smokesignal.responds_to(self.fn, 'bar')

    def test_signals(self):
        # Register first
        smokesignal.on(('foo', 'bar'), self.fn)

        assert 'foo' in smokesignal.signals(self.fn)
        assert 'bar' in smokesignal.signals(self.fn)

    def test_responds_to_true(self):
        # Register first
        smokesignal.on('foo', self.fn)
        assert smokesignal.responds_to(self.fn, 'foo') is True

    def test_responds_to_false(self):
        # Register first
        smokesignal.on('foo', self.fn)
        assert smokesignal.responds_to(self.fn, 'bar') is False

    def test_once_raises(self):
        with pytest.raises(AssertionError):
            smokesignal.once('foo', 'bar')

    def test_once(self):
        # Register and call twice
        smokesignal.once('foo', self.fn)
        smokesignal.emit('foo')
        smokesignal.emit('foo')

        assert self.fn.call_count == 1

    def test_once_decorator(self):
        # Register and call twice
        smokesignal.once('foo')(self.fn)
        smokesignal.emit('foo')
        smokesignal.emit('foo')

        assert self.fn.call_count == 1

    @patch('smokesignal.emit')
    def test_emitting_arg_style(self, emit):
        with smokesignal.emitting('foo'):
            pass
        emit.assert_called_with('foo')

    @patch('smokesignal.emit')
    def test_emitting_kwarg_style(self, emit):
        with smokesignal.emitting(enter='foo', exit='bar'):
            pass
        emit.assert_has_calls([call('foo'), call('bar')])

    def test_on_creates_responds_to_fn(self):
        # Registering a callback should create partials to smokesignal
        # methods for later user
        smokesignal.on('foo', self.fn)

        assert hasattr(self.fn, 'responds_to')
        assert self.fn.responds_to('foo')

    def test_on_creates_signals_fn(self):
        # Registering a callback should create partials to smokesignal
        # methods for later user
        smokesignal.on(('foo', 'bar'), self.fn)

        assert hasattr(self.fn, 'signals')
        assert 'foo' in self.fn.signals()
        assert 'bar' in self.fn.signals()

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
        for x in range(5):
            smokesignal.emit('foo')
        assert foo.foo_count == 1

""" Unit tests """
from unittest import TestCase

from mock import Mock

import smokesignal


class SmokesignalTestCase(TestCase):

    def setUp(self):
        self.callback = lambda x: x
        self.mock_callback = Mock()
        self.mock_callback.__name__ = 'mock_callback'  # So decorators work

    def tearDown(self):
        smokesignal.clear_all()

    def test_clear(self):
        smokesignal.on('foo', self.callback)
        assert len(smokesignal._receivers['foo']) == 1

        smokesignal.clear('foo')
        assert len(smokesignal._receivers['foo']) == 0

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
        assert self.mock_callback in smokesignal._receivers['foo']

        smokesignal.emit('foo')
        assert self.mock_callback.called

    def test_emit_with_callback_args(self):
        # Register first
        smokesignal.on('foo', self.mock_callback)
        assert self.mock_callback in smokesignal._receivers['foo']

        smokesignal.emit('foo', 1, 2, 3, foo='bar')
        assert self.mock_callback.called_with(1, 2, 3, foo='bar')

    def test_on_raises(self):
        self.assertRaises(AssertionError, smokesignal.on, 'foo', None)

    def test_on_registers(self):
        smokesignal.on('foo', self.callback)
        assert self.callback in smokesignal._receivers['foo']

    def test_on_registers_many(self):
        smokesignal.on(('foo', 'bar'), self.callback)
        assert self.callback in smokesignal._receivers['foo']
        assert self.callback in smokesignal._receivers['bar']

    def test_disconnect(self):
        # Register first
        smokesignal.on(('foo', 'bar'), self.callback)
        assert self.callback in smokesignal._receivers['foo']
        assert self.callback in smokesignal._receivers['bar']

        smokesignal.disconnect(self.callback)
        assert self.callback not in smokesignal._receivers['foo']
        assert self.callback not in smokesignal._receivers['bar']

    def test_disconnect_from_removes_only_one(self):
        # Register first
        smokesignal.on(('foo', 'bar'), self.callback)
        assert self.callback in smokesignal._receivers['foo']
        assert self.callback in smokesignal._receivers['bar']

        # Remove it
        smokesignal.disconnect_from(self.callback, 'foo')
        assert self.callback not in smokesignal._receivers['foo']
        assert self.callback in smokesignal._receivers['bar']

    def test_disconnect_from_removes_all(self):
        # Register first
        smokesignal.on(('foo', 'bar'), self.callback)
        assert self.callback in smokesignal._receivers['foo']
        assert self.callback in smokesignal._receivers['bar']

        # Remove it
        smokesignal.disconnect_from(self.callback, 'foo', 'bar')
        assert self.callback not in smokesignal._receivers['foo']
        assert self.callback not in smokesignal._receivers['bar']

    def test_signals(self):
        # Register first
        smokesignal.on(('foo', 'bar'), self.callback)

        assert 'foo' in smokesignal.signals(self.callback)
        assert 'bar' in smokesignal.signals(self.callback)

    def test_is_registered_for_true(self):
        # Register first
        smokesignal.on('foo', self.callback)
        assert smokesignal.is_registered_for(self.callback, 'foo') is True

    def test_is_registered_for_false(self):
        # Register first
        smokesignal.on('foo', self.callback)
        assert smokesignal.is_registered_for(self.callback, 'bar') is False

    def test_once_raises(self):
        self.assertRaises(AssertionError, smokesignal.once, 'foo', None)

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

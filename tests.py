""" Unit tests """
from unittest import TestCase

from mock import Mock

import smokesignal


class SmokesignalTestCase(TestCase):

    def setUp(self):
        self.callback = lambda x: x
        self.mock_callback = Mock()

    def test_emit_with_no_callbacks(self):
        smokesignal.emit('foo')

    def test_emit_with_callbacks(self):
        # Register first
        smokesignal.on('foo', self.mock_callback)
        assert self.mock_callback in smokesignal.receivers['foo']

        smokesignal.emit('foo')
        assert self.mock_callback.called

    def test_emit_with_callback_args(self):
        # Register first
        smokesignal.on('foo', self.mock_callback)
        assert self.mock_callback in smokesignal.receivers['foo']

        smokesignal.emit('foo', 1, 2, 3, foo='bar')
        assert self.mock_callback.called_with(1, 2, 3, foo='bar')

    def test_on_fails_for_non_callable(self):
        self.assertRaises(AssertionError, smokesignal.on, 'foo', None)

    def test_on_registers(self):
        smokesignal.on('foo', self.callback)
        assert self.callback in smokesignal.receivers['foo']

    def test_disconnect(self):
        # Register first
        smokesignal.on('foo', self.callback)
        assert self.callback in smokesignal.receivers['foo']

        # Remove it
        smokesignal.disconnect('foo', self.callback)
        assert self.callback not in smokesignal.receivers['foo']

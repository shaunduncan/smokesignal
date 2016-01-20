"""
With Twisted available, test optional Twisted support in smokesignal
"""

from twisted.internet import reactor, defer, task
from twisted.trial import unittest

from mock import patch

import smokesignal


class TestTwisted(unittest.TestCase):
    def _emit(self, expectSuccess=None, expectFailure=None):
        """
        Fire a signal and compare results to expectations
        """
        assert (not expectSuccess) != (not expectFailure), "pass either expectSuccess or expectFailure"

        if expectFailure:
            def checkFailure(f):
                assert f.type is expectFailure

            d = smokesignal.emit('hello', 'world', errback=checkFailure)
        else:
            d = smokesignal.emit('hello', 'world')

        def check(r):
            assert len(r) == 1
            assert r[0] == expectSuccess

        return d.addCallback(check)

    def test_max_calls(self):
        """
        Do I decrement _max_calls immediately when the function is called,
        even when I'm passing through a reactor loop?

        Discussion: In a naive implementation, max_calls was handled when the
        function was called, but we use maybeDeferred, which passes the call
        through a reactor loop.
        
        max_calls needs to be decremented before it passes through the
        reactor, lest we call it multiple times per loop because the decrement
        hasn't happened yet.
        """
        def cb():
            return 19

        smokesignal.on('19', cb, max_calls=19)
        d1 = smokesignal.emit('19')
        assert list(smokesignal.receivers['19'])[0]._max_calls == 18
        d2 = smokesignal.emit('19')
        assert list(smokesignal.receivers['19'])[0]._max_calls == 17
        return defer.DeferredList([d1, d2])

    def test_synchronous(self):
        """
        Blocking callbacks should simply fire the deferred
        """
        smokesignal.once('hello', synchronous)
        return self._emit(expectSuccess='synchronous done')

    def test_asynchronous(self):
        """
        Callbacks that return deferred should be resolved
        """
        smokesignal.once('hello', asynchronous)
        return self._emit(expectSuccess='asynchronous done')

    def test_synchronous_failure(self):
        """
        Callbacks that raise an exception without returning a deferred should
        trigger errbacks.
        """
        smokesignal.once('hello', synchronous_failure)
        return self._emit(expectFailure=ZeroDivisionError)

    def test_asynchronous_failure(self):
        """
        Callbacks that raise an exception inside a deferred should trigger
        errbacks.
        """
        smokesignal.once('hello', asynchronous_failure)
        return self._emit(expectFailure=KeyError)

    def test_delay(self):
        """
        Similar to test_asynchronous but use deferLater
        """
        smokesignal.once('hello', delay)
        clock = task.Clock()
        pCallLater = patch.object(reactor, 'callLater', clock.callLater)
        with pCallLater:
            r = self._emit(expectSuccess='delay done')
            clock.advance(20)
            return r


def synchronous(target):
    """
    Return synchronously
    """
    assert target == 'world'
    return 'synchronous done'

def asynchronous(target):
    """
    Return async simple value immediately 
    """
    return defer.succeed('asynchronous done')

def synchronous_failure(target):
    """
    Fail synchronously
    """
    1/0

def asynchronous_failure(target):
    """
    Fail asynchronously
    """
    def err():
        {}['key_error']

    return task.deferLater(reactor, 0, err)

def delay(target):
    """
    Succeed after a delay
    """
    def done():
        return 'delay done'

    return task.deferLater(reactor, 15, done)

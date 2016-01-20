# CHANGELOG

## 0.8.0

- When twisted is installed, emit() returns a deferred which gathers the
  results of all callbacks.

## 0.7.0

- Fixed #3: Added disconnect/disconnect_from partials to callbacks
- Fixed #6: Auto disconnect ``once`` and ``on`` with max_calls signals
- Fixed #10: converted ``smokesignal.emitting`` to contextlib.contextmanager

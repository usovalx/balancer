from contextlib import contextmanager

# context manager for temporarily disabling QT signals
@contextmanager
def block_signals(obj):
    state = obj.blockSignals(True)
    yield
    obj.blockSignals(state)

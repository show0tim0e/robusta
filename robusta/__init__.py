import threading

from tqdm.auto import tqdm as _tqdm_cls

# Workaround for `ValueError: bad_value(s) in fds_to_keep` raised by
# CPython's multiprocessing.resource_tracker when sys.stderr.fileno()
# returns -1 (Textual TUIs do this on purpose). Pre-setting a thread
# RLock on tqdm.short-circuits the lazy TqdmDefaultWriteLock ->
# create_mp_lock -> fork_exec path that triggers the crash. Proactive
# single-line fix mirroring huggingface_hub/utils/tqdm.py (>=1.13.0),
# but applied globally so the `datasets` package's own tqdm subclass
# is also covered.
_tqdm_cls.set_lock(threading.RLock())


__version__ = "0.1.0"

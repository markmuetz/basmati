from pathlib import Path
import pickle
from hashlib import sha1
from functools import wraps

import numpy as np


class Cache(dict):
    def __init__(self, hold_in_memory=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hold_in_memory = hold_in_memory
        self.cache_dir = Path('.basmati/cache')
        if not self.cache_dir.exists():
            self.cache_dir.mkdir()

        # self.update(*args, **kwargs)
        self._memory = {}

    def wrap(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return self.fn(func, *args, **kwargs)
        return wrapper

    def fn(self, fn, *args, **kwargs):
        fn_key = sha1(str((fn.__name__, fn.__code__.co_code, args, kwargs)).encode()).hexdigest()
        if fn_key in self:
            return self[fn_key]
        val = fn(*args, **kwargs)
        self[fn_key] = val
        return val

    def _load_from_cache(self, key):
        if key.endswith('.npy'):
            return np.load(str(self.cache_dir / key))
        else:
            with open(self.cache_dir / key, 'rb') as f:
                return pickle.load(f)

    def __getitem__(self, key):
        if key in self._memory:
            val = dict.__getitem__(self._memory, key)
        else:
            val = self._load_from_cache(key)
            if self.hold_in_memory:
                self._memory[key] = val
        return val

    def __setitem__(self, key, val):
        if key.endswith('.npy'):
            np.save(str(self.cache_dir / key), val)
        else:
            with open(self.cache_dir / key, 'wb') as f:
                pickle.dump(val, f)

        if self.hold_in_memory:
            dict.__setitem__(self._memory, key, val)

    def __contains__(self, key):
        return (self.cache_dir / key).exists()

    def __repr__(self):
        dictrepr = dict.__repr__(self)
        return '%s(%s)' % (type(self).__name__, dictrepr)

    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).items():
            self._memory[k] = v

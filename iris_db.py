import numpy as np

class IrisDB:
    def __init__(self):
        self._data = {}
        self.threshold = 0.35

    def add(self, name, code):
        if name not in self._data:
            self._data[name] = []
        self._data[name].append(code)

    def identify(self, code):
        best_name = None
        best_score = 1.0

        for name, codes in self._data.items():
            for c in codes:
                score = self._hamming(code, c)
                if score < best_score:
                    best_score = score
                    best_name = name

        if best_name and best_score <= self.threshold:
            return best_name, best_score
        
        return None, best_score

    def list_users(self):
        return list(self._data.keys())

    def delete_user(self, name):
        if name in self._data:
            del self._data[name]

    def _hamming(self, a, b):
        n = min(len(a), len(b))
        xor = np.bitwise_xor(a[:n], b[:n])
        return np.mean(xor)

    def _save(self):
        pass
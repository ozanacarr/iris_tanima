"""
iris_recognition.py  —  v2  (kararlı tanıma)
─────────────────────────────────────────────
Düzeltmeler:
  • normalize_iris tamamen vektörleştirildi → her seferinde aynı sonuç
  • Veritabanına tek ortalama yerine N ayrı şablon kaydediliyor
  • identify() her şablona karşı test ediyor, en düşük HD'yi alıyor
  • Eşik 0.42; CLAHE ile kontrast artırma; 3 frekans bandı
"""

import cv2
import numpy as np
import json
from pathlib import Path


# ─────────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────────

class IrisDatabase:
    DB_PATH = "iris_db.json"

    def __init__(self):
        self._data: dict[str, list] = {}
        self._load()

    def _load(self):
        if not Path(self.DB_PATH).exists():
            return
        with open(self.DB_PATH, "r") as f:
            raw = json.load(f)
        self._data = {
            k: [np.array(v, dtype=np.uint8) for v in vs]
            for k, vs in raw.items()
        }

    def _save(self):
        raw = {k: [v.tolist() for v in vs] for k, vs in self._data.items()}
        with open(self.DB_PATH, "w") as f:
            json.dump(raw, f)

    def register(self, name: str, codes: list):
        """codes: liste — birden fazla şablon saklıyoruz."""
        if name not in self._data:
            self._data[name] = []
        self._data[name].extend([c.copy() for c in codes])
        self._save()

    def identify(self, code: np.ndarray, threshold: float = 0.42):
        """Kayıtlı tüm şablonlara karşı test eder."""
        best_name = None
        best_hd   = 1.0

        for name, templates in self._data.items():
            for tmpl in templates:
                hd = _hamming(code, tmpl)
                if hd < best_hd:
                    best_hd   = hd
                    best_name = name

        if best_hd <= threshold:
            conf = max(0.0, (1.0 - best_hd / threshold) * 100.0)
            return best_name, best_hd, conf
        return None, best_hd, 0.0

    def list_users(self):
        return list(self._data.keys())

    def delete_user(self, name: str) -> bool:
        if name in self._data:
            del self._data[name]
            self._save()
            return True
        return False

    def count(self) -> int:
        return len(self._data)


def _hamming(a: np.ndarray, b: np.ndarray) -> float:
    n    = min(len(a), len(b))
    xor  = np.bitwise_xor(a[:n], b[:n])
    bits = np.unpackbits(xor)
    return float(bits.sum()) / len(bits)


# ─────────────────────────────────────────────
# SEGMENTATION
# ─────────────────────────────────────────────

def segment_iris(frame: np.ndarray):
    """
    Pupil + iris tespiti.
    Döner: (pupil=(x,y,r), iris=(x,y,r), gray)  veya  None
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape

    blurred  = cv2.GaussianBlur(gray, (9, 9), 2)
    clahe    = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(blurred)

    # Pupil
    pupils = cv2.HoughCircles(
        enhanced,
        cv2.HOUGH_GRADIENT,
        dp=1.0,
        minDist=h // 4,
        param1=50,
        param2=20,
        minRadius=max(8,  min(h, w) // 16),
        maxRadius=min(h, w) // 5,
    )
    if pupils is None:
        return None

    px, py, pr = map(int, pupils[0][0])
    if not (0.05 * w < px < 0.95 * w and 0.05 * h < py < 0.95 * h):
        return None

    # Iris — pupil bölgesini maskele
    masked = enhanced.copy()
    cv2.circle(masked, (px, py), pr + 4, int(np.mean(enhanced)), -1)

    irises = cv2.HoughCircles(
        masked,
        cv2.HOUGH_GRADIENT,
        dp=1.0,
        minDist=h // 4,
        param1=40,
        param2=18,
        minRadius=pr + 8,
        maxRadius=min(h, w) // 2,
    )

    if irises is not None:
        best = min(irises[0],
                   key=lambda c: (int(c[0]) - px)**2 + (int(c[1]) - py)**2)
        ix, iy, ir = map(int, best)
    else:
        ix, iy, ir = px, py, int(pr * 2.8)

    if ir < pr + 8:
        return None

    return (px, py, pr), (ix, iy, ir), gray


# ─────────────────────────────────────────────
# NORMALIZATION  (Daugman rubber-sheet — vektörleştirilmiş)
# ─────────────────────────────────────────────

NORM_W = 256
NORM_H = 64


def normalize_iris(gray: np.ndarray,
                   pupil: tuple,
                   iris:  tuple,
                   width: int  = NORM_W,
                   height: int = NORM_H) -> np.ndarray:
    px, py, pr = pupil
    ix, iy, ir = iris

    theta = np.linspace(0, 2 * np.pi, width,  endpoint=False)
    rho   = np.linspace(0, 1,         height, endpoint=False)[:, np.newaxis]

    cx     = px + rho * (ix - px)
    cy     = py + rho * (iy - py)
    radius = pr + rho * (ir - pr)

    xs = (cx + radius * np.cos(theta)).astype(np.float32)
    ys = (cy + radius * np.sin(theta)).astype(np.float32)

    xs = np.clip(xs, 0, gray.shape[1] - 1)
    ys = np.clip(ys, 0, gray.shape[0] - 1)

    normalized = cv2.remap(
        gray.astype(np.float32),
        xs, ys,
        interpolation=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REPLICATE,
    ).astype(np.uint8)

    return normalized


# ─────────────────────────────────────────────
# FEATURE EXTRACTION  (Log-Gabor iris code)
# ─────────────────────────────────────────────

_KERNEL_CACHE: dict = {}


def extract_iris_code(norm: np.ndarray) -> np.ndarray:
    norm_eq = cv2.equalizeHist(norm)
    norm_f  = norm_eq.astype(np.float32) / 255.0
    rows, cols = norm_f.shape
    bits = []

    for f0 in (0.08, 0.15, 0.25):
        key = (cols, f0)
        if key not in _KERNEL_CACHE:
            _KERNEL_CACHE[key] = _log_gabor_1d(cols, f0, sigma_f=0.55)
        kernel = _KERNEL_CACHE[key]

        for row in norm_f:
            filtered = np.fft.ifft(np.fft.fft(row) * kernel)
            bits.extend((np.real(filtered) >= 0).tolist())
            bits.extend((np.imag(filtered) >= 0).tolist())

    return np.packbits(np.array(bits, dtype=np.uint8))


def _log_gabor_1d(n: int, f0: float, sigma_f: float) -> np.ndarray:
    freqs       = np.fft.fftfreq(n)
    freqs[0]    = 1e-12
    log_f       = np.log(np.abs(freqs) / f0)
    kernel      = np.exp(-(log_f ** 2) / (2 * sigma_f ** 2))
    kernel[0]   = 0
    return kernel
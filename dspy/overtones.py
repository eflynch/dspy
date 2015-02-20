import numpy as np

SQUARE_AMPLITUDES = [
    (i, 1. / float(i), 0) for i in range(1, 20) if i % 2 == 1
]
SINE_AMPLITUDES = [(1, 1.0, 0.0)]
SAW_AMPLITUDES = [
    (i, (-1) ** (i + 1) * 1. / float(i), 0) for i in range(1, 20)
]
TRI_AMPLITUDES = [
    (i, 1. / (float(i) ** 2), np.pi / 2.) for i in range(1, 20) if i % 2 == 1
]

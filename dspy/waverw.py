import wave

import numpy as np

from dspy import config

SAMPLING_RATE = config['SAMPLING_RATE']

class WaveReader(object):
    def __init__(self, filepath):
        super(WaveReader, self).__init__()

        self.wave = wave.open(filepath, 'rb')
        self.channels, self.sampwidth, self.sr, self.end, \
            comptype, compname = self.wave.getparams()
        assert(self.channels == 2)
        assert(self.sampwidth == 2)
        assert(self.sr == SAMPLING_RATE)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def read(self, num_frames):
        raw_bytes = self.wave.readframes(num_frames)
        samples = np.fromstring(raw_bytes, dtype=np.int16)
        samples = samples.astype(np.float32)
        samples *= (1 / 32768.0)
        return samples

    def set_pos(self, frame):
        self.wave.setpos(frame)

    def close(self):
        self.wave.close()


class WaveWriter(object):
    def __init__(self, filepath):
        super(WaveWriter, self).__init__()

        self.wave = wave.open(filepath, 'wb')
        self.wave.setnchannels(2)
        self.wave.setsampwidth(2L)
        self.wave.setframerate(SAMPLING_RATE)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def write(self, data):
        data *= 32768.0
        data = data.astype(np.int16)
        self.wave.writeframes(data.tostring())

    def set_pos(self, frame):
        self.wave.setpos(frame)

    def close(self):
        self.wave.close()

import numpy as np

from dspy.envelope import ADSREnvelope
from dspy.generator import Generator
from dspy import config
from dspy.lib import t2f, pitch_to_frequency


SAMPLING_RATE = config['SAMPLING_RATE']


class Note(Generator):
    def __new__(cls, pitch=60, overtones=[(1, 1, 0)], detune=0, duration=0.5,
                envelope=None):
        t = Tone(pitch, overtones, detune)
        if envelope is None:
            envelope = ADSREnvelope(duration=duration)

        gen = t * envelope
        return gen


class FM(Generator):
    def __init__(self, pitch, modulator, detune=0):
        self.modulator = modulator
        self.freq = pitch_to_frequency(pitch + detune/100.)
        self._factor = self.freq * 2.0 * np.pi / SAMPLING_RATE

        Generator.__init__(self)

    def _reset(self):
        self.modulator.reset()

    def _generate(self, frame_count):
        domain = np.arange(self.frame, self.frame + frame_count)
        modulation, cf = self.modulator.generate(frame_count)
        signal = np.sin(self._factor * domain + modulation, dtype=np.float32)
        return signal


class Tone(Generator):
    def __init__(self, pitch, overtones=[(1, 1, 0)], detune=0):
        self.freq = pitch_to_frequency(pitch + detune/100.)

        def nyquist(overtone):
            return overtone[0] * self.freq < SAMPLING_RATE/2
        self.overtones = filter(nyquist, overtones)

        self._factor = self.freq * 2.0 * np.pi / SAMPLING_RATE

        Generator.__init__(self)

    def _generate(self, frame_count):
        domain = np.arange(self.frame, self.frame + frame_count)

        signal = np.zeros(frame_count, dtype=np.float32)
        for order, amp, phase in self.overtones:
            sine = np.sin(order * self._factor * domain + phase,
                          dtype=np.float32)
            signal += amp * sine
        return signal

import numpy as np

from dspy.adsr import ADSREnvelope
from dspy.generator import Generator
from dspy import config
from dspy.lib import t2f, pitch_to_frequency


SAMPLING_RATE = config['SAMPLING_RATE']


class Note(Generator):
    def __new__(cls, pitch, overtones, detune, duration=None, envelope=None):
        t = Tone(pitch, overtones, detune)
        if envelope == None:
            envelope = ADSREnvelope()
        if duration != None:
            release_frame = t2f(duration) - envelope.release_time
            envelope.set_release_frame(release_frame)

        gen = t * envelope
        return gen


class FM(Generator):
    def __init__(self, pitch, modulator, detune=0):
        self.modulator = modulator
        self.freq = pitch_to_frequency(pitch + detune/100.)
        self._factor = self.freq * 2.0 * np.pi / SAMPLING_RATE

        Generator.__init__(self)

    def release(self):
        pass

    def reset(self):
        self.modulator.reset()
        Genrator.reset(self)

    def get_buffer(self, frame_count):
        domain = np.arange(self.frame, self.frame + frame_count)
        modulation, cf = self.modulator.get_buffer(frame_count)
        signal = np.sin(self._factor * domain + modulation, dtype = np.float32)
        return signal


class Tone(Generator):
    def __init__(self, pitch, overtones=[(1,1,0)], detune=0):
        self.freq = pitch_to_frequency(pitch + detune/100.)
        self.overtones = filter(lambda x: x[0] * self.freq < SAMPLING_RATE/2, overtones)

        self._factor = self.freq * 2.0 * np.pi / SAMPLING_RATE

        Generator.__init__(self)

    def release(self):
        pass

    def get_buffer(self, frame_count):
        domain = np.arange(self.frame, self.frame + frame_count)

        signal = np.zeros(frame_count, dtype=np.float32)
        for order, amp, phase in self.overtones:
            signal += amp * np.sin(order * self._factor * domain + phase, dtype = np.float32)

        return signal

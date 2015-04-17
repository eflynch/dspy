"""
.. module:: envelope
     :platform: Unix, Windows
     :synopsis: Generators for enveloping

.. moduleauthor: Evan Lynch <evan.f.lynch@gmail.com>

"""
import numpy as np

from dspy import config
from dspy.lib import t2f
from dspy.generator import Generator


SAMPLING_RATE = config['SAMPLING_RATE']


class ExpEnvelope(Generator):
    def __init__(self, steps, initial=0.0):
        Generator.__init__(self)
        self.steps = steps
        self.initial = initial

    def create_exp(self, init, dest, start, dur, order):
        return lambda x: (init + (dest - init) * ((x - start) / dur) **
                          (1 / order))

    def _generate(self, frame_count):
        domain = np.arange(self.frame, self.frame + frame_count,
                           dtype=np.float32)
        conditions = []
        functions = []
        init = self.initial
        start = 0
        for (dest, dur, order) in self.steps:
            dur = t2f(dur)
            conditions.append((domain >= start) *
                              (domain < start + dur))
            functions.append(self.create_exp(init, dest, start, dur, order))
            start += dur
            init = dest

        conditions.append(domain >= start)
        functions.append(lambda x: init)

        return np.piecewise(domain, conditions, functions)

class DurationEnvelope(Generator):
    def __init__(self, duration):
        Generator.__init__(self)
        self.duration = t2f(duration)

    def _length(self):
        return self.duration

    def _generate(self, frame_count):
        output = np.arange(self.frame, self.frame + frame_count,
                           dtype=np.float32)
        output[output >= self.duration] = 0
        output[output < self.duration] = 1
        return output

class ReleaseEnvelope(Generator):
    def __init__(self, release_time=0.1, release_order=0.75, duration=None):
        Generator.__init__(self)
        self.release_time = t2f(release_time)
        self.release_order = release_order
        self.release_frame = float('inf')
        self.allow_release = (duration is None)
        if duration:
            self.release_frame = t2f(duration) - self.release_time

    def set_duration(self, duration):
        self.release_frame = t2f(duration)

    def _length(self):
        return self.release_frame + self.release_time

    def _release(self):
        if self.allow_release:
            self.release_frame = self.frame

    def _generate(self, frame_count):
        # print self.frame, frame_count
        domain = np.arange(self.frame, self.frame + frame_count,
                           dtype=np.float32)
        conditions = [
            domain < self.release_frame,
            (self.length() > domain) * (domain >= self.release_frame),
            domain > self.length()
        ]
        functions = [
            lambda x: 1.0,
            lambda x: (1.0 - ((x - self.release_frame) / self.release_time) **
                       (1 / self.release_order)),
            lambda x: 0.0
        ]
        return np.piecewise(domain, conditions, functions)


class ADSREnvelope(Generator):
    """Generator for producing an ADSR envelope.
    """
    def __new__(cls, attack_time=0.1, attack_order=2.0, decay_time=1.0,
                decay_order=1.5, sustain=0.3, release_time=0.1,
                release_order=0.75, duration=None):
        envelope = ExpEnvelope([
            (1.0, attack_time, attack_order),
            (sustain, decay_time, decay_order)
        ], initial=0.0)

        release = ReleaseEnvelope(release_time, release_order, duration)

        return envelope * release

from Queue import PriorityQueue

import numpy as np

from dspy.generator import Generator
from dspy.lib import rechannel, t2f


class Player(Generator):
    def __init__(self, sequence=[], channels=2, live=True):
        Generator.__init__(self)
        self._generators = PriorityQueue()
        self._gain = 0.1
        self._live = live
        self.num_channels = channels
        if sequence:
            for (f, g) in sequence:
                self._generators.put((f, g))

        if not live:
            self._length = max([f+g.length() for (f, g) in sequence] + [0])

    def add(self, gen, time=None):
        if not self._live:
            raise Exception('Cannot add generators if Player is not live')
        if time is None:
            frame = self.frame
        else:
            frame = t2f(time)
        self._generators.put((frame, gen))

    def length(self):
        if self._live:
            return float('inf')

        return self._length

    @property
    def gain(self):
        return self._gain

    @gain.setter
    def gain(self, value):
        self._gain = np.clip(value, 0, 1)

    def get_buffer(self, frame_count):
        output = np.zeros(frame_count * self.num_channels, dtype=np.float32)
        not_done = []
        while not self._generators.empty():
            frame, gen = self._generators.get()
            if frame > self.frame + frame_count:
                not_done.append((frame, gen))
                break

            delay = 0
            if frame > self.frame:
                delay = frame - self.frame

            signal, continue_flag = gen.generate(frame_count - delay)
            signal = rechannel(signal, gen.num_channels, self.num_channels)
            output[delay * self.num_channels:] += signal
            if continue_flag:
                not_done.append((frame, gen))

        for frame, gen in not_done:
            self._generators.put((frame, gen))

        output *= self.gain
        return output

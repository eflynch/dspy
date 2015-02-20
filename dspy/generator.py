import numpy as np

from dspy import config


SAMPLING_RATE = config['SAMPLING_RATE']


class Generator(object):
    def __init__(self):
        self._num_channels = 1
        self._frame = 0
        self._previous_buffer = None

    def __add__(self, other):
        return Sum([self, other])

    def __mul__(self, other):
        return Product([self, other])

    def __len__(self):
        return self.length()

    @property
    def num_channels(self):
        return self._num_channels

    @num_channels.setter
    def num_channels(self, value):
        self._num_channels = value

    @property
    def previous_buffer(self):
        if self._previous_buffer is None:
            return np.zeros(512, dtype=np.float32)
        return self._previous_buffer

    @property
    def frame(self):
        return self._frame

    def generate(self, frame_count):
        signal = self.get_buffer(frame_count)
        self._frame = self._frame + frame_count
        self._previous_buffer = signal
        continue_flag = self._frame < self.length()
        return signal, continue_flag

    def reset(self):
        self._frame = 0

    def length(self):
        return float('inf')

    def release(self):
        pass

    def get_buffer(self, frame_count):
        return np.zeros(frame_count, dtype=np.float32)


class WrapperGenerator(Generator):
    def __init__(self, generator):
        self._generator = generator
        Generator.__init__(self)

    @property
    def generator(self):
        return self._generator

    def length(self):
        return self._generator.length()
   
    def release(self):
        return self._generator.release()

    def reset(self):
        self._generator.reset()
        Generator.reset(self)


class BundleGenerator(Generator):
    def __init__(self, generators):
        self._generators = generators
        Generator.__init__(self)

    @property
    def generators(self):
        return self._generators
   
    def release(self):
        for g in self._generators:
            g.release()

    def reset(self):
        for g in self._generators:
            g.reset()
        Generator.reset(self)


class Product(BundleGenerator):
    def length(self):
        return min(g.length() for g in self.generators)

    def get_buffer(self, frame_count):
        # Stop when first factor is done
        signal = np.ones(frame_count, dtype=np.float32)
        for g in self.generators:
            data, cf = g.generate(frame_count)
            signal *= data

        return signal


class Sum(BundleGenerator):
    def length(self):
        return max(g.length() for g in self.generators)

    def get_buffer(self, frame_count):
        # Continue until all summands are done
        signal = np.zeros(frame_count, dtype=np.float32)
        for g in self.generators:
            data, cf = g.generate(frame_count)
            signal+= data

        return signal

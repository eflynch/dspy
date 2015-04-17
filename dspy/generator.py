from numbers import Number

import numpy as np

from dspy import config


SAMPLING_RATE = config['SAMPLING_RATE']


class Generator(object):
    def __init__(self):
        self._num_channels = 1
        self._frame = 0
        self._previous_buffer = None
        self._auto_reset = False

    def __add__(self, other):
        if isinstance(other, Generator):
            return Sum([self, other])
        if isinstance(other, Number):
            return Offset(self, other)

    def __mul__(self, other):
        if isinstance(other, Generator):
            return Product([self, other])
        if isinstance(other, Number):
            return Gain(self, other)

    def __len__(self):
        return self.length()

    @property
    def auto_reset(self):
        return self._auto_reset

    @auto_reset.setter
    def auto_reset(self, value):
        self._auto_reset = value

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
        if self._auto_reset and self._frame + frame_count >= self._length():
            remainder = int(self._length() - self._frame)
            signal = self._generate(remainder)
            self.reset()
            signal_2 = self._generate(frame_count - remainder)
            return np.concatenate((signal, signal_2)), True

        signal = self._generate(frame_count)
        self._frame = self._frame + frame_count
        self._previous_buffer = signal
        continue_flag = self._frame < self.length()
        return signal, continue_flag

    def reset(self):
        self._reset()
        self._frame = 0

    def length(self):
        if self._auto_reset:
            return float('inf')
        return self._length()

    def release(self):
        self._release()
        pass

    def _release(self):
        pass

    def _reset(self):
        pass

    def _generate(self, frame_count):
        return np.zeros(frame_count, dtype=np.float32)

    def _length(self):
        return float('inf')


class WrapperGenerator(Generator):
    def __init__(self, generator):
        Generator.__init__(self)
        self._generator = generator
        self.num_channels = generator.num_channels

    @property
    def generator(self):
        return self._generator

    def _length(self):
        return self._generator.length()

    def _release(self):
        return self._generator.release()

    def _reset(self):
        self._generator.reset()


class BundleGenerator(Generator):
    def __init__(self, generators):
        self._generators = generators
        Generator.__init__(self)

    @property
    def generators(self):
        return self._generators

    def _release(self):
        for g in self._generators:
            g.release()

    def _reset(self):
        for g in self._generators:
            g.reset()


class Product(BundleGenerator):
    def _length(self):
        return min(g.length() for g in self.generators)

    def _generate(self, frame_count):
        # Stop when first factor is done
        signal = np.ones(frame_count, dtype=np.float32)
        for g in self.generators:
            data, cf = g.generate(frame_count)
            signal *= data

        return signal


class Sum(BundleGenerator):
    def _length(self):
        return max(g.length() for g in self.generators)

    def _generate(self, frame_count):
        # Continue until all summands are done
        signal = np.zeros(frame_count, dtype=np.float32)
        for g in self.generators:
            data, cf = g.generate(frame_count)
            signal += data

        return signal


class Gain(WrapperGenerator):
    def __init__(self, generator, gain):
        WrapperGenerator.__init__(self, generator)
        self.gain = gain

    def _generate(self, frame_count):
        signal, continue_flag = self.generator.generate(frame_count)
        return self.gain * signal


class Offset(WrapperGenerator):
    def __init__(self, generator, offset):
        WrapperGenerator.__init__(self, generator)
        self.offset = offset

    def _generate(self, frame_count):
        signal, continue_flag = self.generator.generate(frame_count)
        return signal + self.offset


import numpy as np

from dspy.generator import WrapperGenerator
from dspy import config


SAMPLING_RATE = config['SAMPLING_RATE']


class LowPassDSP(WrapperGenerator):
    def __init__(self, generator, cutoff):
        self.h = self._get_impulse_response(cutoff, L=100)
        WrapperGenerator.__init__(self, generator)

    def _get_impulse_response(self, cutoff, L):
        omega_cut = float(cutoff) * 2.0 * np.pi / float(SAMPLING_RATE)
        # [radians/sample] = [cycles/sec] * [radians/cycle] * [sec/sample]

        l_range = np.arange(-L, L, dtype=np.float32)
        l_range[L] = 1.0  # to avoid divide by zero error
        h = np.sin(omega_cut * l_range) / (np.pi * l_range)
        h[L] = omega_cut / np.pi
        return h

    def _generate(self, frame_count):
        previous_buffer = self.generator.previous_buffer
        signal = self.generator.generate(frame_count)

        with_previous = np.concatenate((previous_buffer, signal))

        output = np.convolve(with_previous, self.h)

        end_frame = len(output) - len(self.h) + 1

        start_frame = end_frame - len(signal)

        trimmed = output[start_frame:end_frame]

        return trimmed


class Clip(WrapperGenerator):
    def __init__(self, generator, low=-1, high=1):
        self.low = low
        self.high = high
        WrapperGenerator.__init__(self, generator)

    def _generate(self, frame_count):
        signal, continue_flag = self.generator.generate(frame_count)

        signal = np.clip(signal, self.low, self.high)
        return signal


class Abs(WrapperGenerator):
    def _generate(self, frame_count):
        signal, continue_flag = self.generator.generate(frame_count)
        return np.abs(signal)


class Compressor(WrapperGenerator):
    def __init__(self, generator, threshold, ratio):
        self.threshold = threshold
        self.ratio = ratio
        WrapperGenerator.__init__(self, generator)

    def _generate(self, frame_count):
        signal, continue_flag = self.generator.generate(frame_count)
        compression = abs(signal) > self.threshold
        signal[compression] = self.threshold + (self.ratio *
                                                (signal[compression] -
                                                 self.threshold))
        return signal

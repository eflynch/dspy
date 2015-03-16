import numpy as np

from dspy import config
from dspy.generator import WrapperGenerator, Generator


SAMPLING_RATE = config['SAMPLING_RATE']


class Map(WrapperGenerator):
    def __init__(self, generator, function):
        self.function = function
        WrapperGenerator.__init__(self, generator)

    def _generate(self, frame_count):
        signal, continue_flag = self.generator.generate(frame_count)
        return self.function(signal)


class DC(Generator):
    def __init__(self, value):
        self.value = value
        Generator.__init__(self)

    def _generate(self, frame_count):
        return np.ones(frame_count, dtype=np.float32) * self.value


class Sine(Generator):
    def __init__(self, freq, phase, amp=1.0):
        self.freq = freq
        self.amp = amp
        self.phase = phase
        Generator.__init__(self)

    def _generate(self, frame_count):
        factor = self.freq * 2.0 * np.pi / SAMPLING_RATE
        domain = np.arange(self.frame, self.frame + frame_count)
        output = np.sin(factor * domain + self.phase, dtype=np.float32)
        return self.amp * output


class Rect(Generator):
    def __init__(self, freq, phase, duty=0.5, amp=1.0):
        self.freq = freq
        self.phase = phase
        self.duty = duty
        self.amp = amp
        Generator.__init__(self)

    def _generate(self, frame_count):
        width = SAMPLING_RATE / self.freq
        phase = width * self.phase / (2 * np.pi)
        domain = np.arange(self.frame, self.frame + frame_count)
        highs = (domain + phase) % width > (width * self.duty)
        domain[highs] = self.amp
        domain[~highs] = -self.amp
        return domain

# class Ramp(Generator):
#     def __init__(self, start, end, duration):
#         Generator.__init__(self)
#         self.start = start
#         self.end = end
#         self.duration = duration

#     def _generate(self, frame_count):
#         (self.end - self.start) / 
#         domain = np.arange(self.rame, self.frame + frame_count)



# TODO: Optimize this class
class WaveTable(Generator):
    def __init__(self, table):
        self.table = table
        Generator.__init__(self)

    def _generate(self, frame_count):
        domain = np.arange(self.frame, self.frame+frame_count)
        indices = (domain + len(self.table)) % len(self.table)
        output = np.array(self.table[indices], dtype=np.float32)
        return output


class Noise(Generator):
    def _generate(self, frame_count):
        return np.array(np.random.rand(frame_count) - 0.5, dtype=np.float32)


# TODO: Make this better
class Pink(Generator):
    def _generate(self, frame_count):
        alpha = 1.0
        noise = np.array(np.random.rand(frame_count) - 0.5, dtype=np.float32)
        f = np.arange(0, frame_count, dtype=np.float32) - (frame_count/2)
        f = np.abs(f)
        f[frame_count/2] = 1  # to avoid dividing by zero
        f = f ** (-alpha)
        f *= 50.0
        pink_noise = np.real(np.fft.ifft(np.fft.fft(noise)*f))
        return pink_noise

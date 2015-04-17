#####################################################################
#
# WaveReader class copied with permission:
#
# Copyright (c) 2015, Eran Egozy
#
# Released under the MIT License (http://opensource.org/licenses/MIT)
#
#####################################################################

import numpy as np

from dspy.generator import Generator
from dspy import config
from dspy.lib import t2f
from dspy.waverw import WaveReader


SAMPLING_RATE = config['SAMPLING_RATE']


class WaveFileGenerator(Generator):
    def __init__(self, filepath, gain=1):
        Generator.__init__(self)
        self.wave_reader = WaveReader(filepath)
        self.num_channels = self.wave_reader.channels
        self.gain = gain
        self.paused = False

    def stop(self):
        self.paused = True

    def start(self):
        self.paused = False

    def _generate(self, frame_count):
        if self.paused:
            return np.zeros(frame_count * self.num_channels, dtype=np.float32)

        read_frames = self.wave_reader.read(frame_count)
        output = np.zeros(frame_Count * self.num_channels, dtype=np.float32)
        output[:len(read_frames)] += read_frames
        output *= self.gain
        return output


class Sampler(object):
    def __init__(self, file_path):
        self.wave_reader = WaveReader(file_path)
        self.num_channels = self.wave_reader.channels
        self.data_cache = {}

    class Sample(Generator):
        def __init__(self, data, num_channels, loop=False, speed=1.0):
            Generator.__init__(self)
            self.num_channels = num_channels
            self.data = data
            self.loop = loop
            self.speed = speed

        def set_speed(self, speed):
            self.speed = speed

        def _length(self):
            if self.loop:
                return float('inf')
            return len(self.data) / self.num_channels

        def _generate(self, frame_count):
            output = np.zeros(frame_count * self.num_channels, dtype=np.float32)

            # Per channel Values
            channel_length = len(self.data)
            length = int(frame_count * self.speed)
            start = int(self.frame * self.speed)
            segment_domain = np.arange(start, start + length)
            in_domain = np.linspace(0, frame_count - 1, length)
            out_domain = np.arange(0, frame_count)

            for c in xrange(self.num_channels):
                indices = (c + (segment_domain * self.num_channels)) % channel_length
                data = np.array(self.data[indices], dtype=np.float32)
                interpolated = np.interp(out_domain, in_domain, data)
                output[c::self.num_channels] = interpolated

            return output

    def sample(self, start, duration, loop=False, speed=1.0):
        start_frame = t2f(start)
        num_frames = t2f(duration)
        if (start_frame, num_frames) not in self.data_cache:
            self.wave_reader.set_pos(start_frame)
            self.data_cache[(start, num_frames)] = self.wave_reader.read(num_frames)

        data = self.data_cache[(start_frame, num_frames)]
        return Sampler.Sample(data, self.num_channels, loop, speed)

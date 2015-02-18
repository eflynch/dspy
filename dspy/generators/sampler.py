#####################################################################
#
# WaveReader class copied with permission:
#
# Copyright (c) 2015, Eran Egozy
#
# Released under the MIT License (http://opensource.org/licenses/MIT)
#
#####################################################################

import wave
import struct

import numpy as np

from generator import Generator
from dspy import config


SAMPLING_RATE = config['SAMPLING_RATE']


class WaveReader(object):
    def __init__(self, filepath) :
        super(WaveReader, self).__init__()

        self.wave = wave.open(filepath)
        self.channels, self.sampwidth, self.sr, self.end, \
            comptype, compname = self.wave.getparams()
      
        # for now, we will only accept stereo, 16 bit files      
        assert(self.channels == 2)
        assert(self.sampwidth == 2)
        assert(self.sr == SAMPLING_RATE)

    # read an arbitrary chunk of an arbitrary length
    def read(self, num_frames) :
        # get the raw data from wave file as a byte string.
        # will return num_frames, or less if too close to end of file
        raw_bytes = self.wave.readframes(num_frames * self.channels)

        # convert to numpy array, where the dtype is int16 or int8
        samples = np.fromstring(raw_bytes, dtype = np.int16)

        # convert from integer type to floating point, and scale to [-1, 1]
        samples = samples.astype(np.float32)
        samples *= (1 / 32768.0)

        return samples

    def set_pos(self, frame) :
        self.wave.setpos(frame)


class Sampler(object):
    def __init__(self, file_path) :
        self.wave_reader = WaveReader(file_path)

    class Sample(Generator):
        def __init__(self, data, num_channels, loop=False) :
            Generator.__init__(self)
            self.num_channels = num_channels
            self.data = data
            self.loop = loop

        def length(self):
            if self.loop:
                return float('inf')
            else:
                return len(self.data) / self.num_channels

        def get_buffer(self, frame_count):
            sample = self.frame * self.num_channels
            length = frame_count * self.num_channels
            domain = np.arange(sample, sample + length)
            indices = (domain + len(self.data)) % len(self.data)
            output = np.array(self.data[indices], dtype=np.float32)

            continue_flag = self.frame < self.length()
            return output, continue_flag

    def make_gen(self, start_frame, num_frames, loop=False):
        self.wave_reader.set_pos(start_frame)
        data = self.wave_reader.read(num_frames)
        num_channels = self.wave_reader.channels
        return Sampler.Sample(data, num_channels, loop)

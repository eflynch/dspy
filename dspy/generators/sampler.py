import wave
import struct

import numpy as np

from generator import Generator
from dspy import config


SAMPLING_RATE = config['SAMPLING_RATE']


class Sampler(Generator):
    def __init__(self, file_name, sample):
        self.file_name = file_name
        self.sample = sample

    def length(self):
        return sample[1] - sample[0]

    def release(self):
        pass

    def get_buffer(self, frame_count):
        with f as wave.open(self.file_name, 'r')
            f.setpos(self.sample[0])
            (nchannels, sampwidth, framerate, nframes, comptype, compname) = wave.getparams()
            signal = struct.unpack_from("%dh" % self.length() * nchannels, f.readframes(self.sample[1])
            
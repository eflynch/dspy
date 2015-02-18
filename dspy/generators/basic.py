import numpy as np

from dspy import config
from dspy.generators.generator import WrapperGenerator, Generator


SAMPLING_RATE = config['SAMPLING_RATE']


class FMap(WrapperGenerator):
   def __init__(self, generator, function):
      self.function = function
      BundleGenerator.__init__(self, generator)

   def get_buffer(self, frame_count):
      signal, continue_flag = self.generator.generate(frame_count)
      return self.function(signal), continue_flag

class DC(Generator):
   def __init__(self, value):
      self.value = value
      Generator.__init__(self)

   def length(self):
      return float('inf')

   def get_buffer(self, frame_count):
      return np.ones(frame_count, dtype=np.float32) * self.value, True

class Sine(Generator):
   def __init__(self, freq, phase, amp=1.0):
      self.freq = freq
      self.amp = amp
      self.phase = phase
      Generator.__init__(self)

   def length(self):
      return float('inf')

   def get_buffer(self, frame_count):
      factor = self.freq * 2.0 * np.pi / SAMPLING_RATE
      domain = np.arange(self.frame, self.frame + frame_count)
      return self.amp * np.sin(factor * domain + self.phase, dtype=np.float32), True

class WaveTable(Generator):
   def __init__(self, table):
      self.table = table
      Generator.__init__(self)

   def length(self):
      return float('inf')

   def get_buffer(self, frame_count):
      domain = np.arange(self.frame, self.frame+frame_count)
      indices = (domain + len(self.table)) % self.table
      output = np.array(self.table[indices], dtype=np.float32)
      return output, True


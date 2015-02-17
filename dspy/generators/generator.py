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

   def reset(self):
      self._frame = 0

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
      signal, continue_flag = self.get_buffer(frame_count)
      self._frame = self._frame + frame_count
      self._previous_buffer = signal
      return signal, continue_flag

class Product(Generator):
   def __init__(self, generators):
      self.generators = generators
      Generator.__init__(self)

   def length(self):
      return min(g.length() for g in self.generators)

   def release(self):
      for g in self.generators:
         g.release()

   def get_buffer(self, frame_count):
      # Stop when first factor is done
      signal = np.ones(frame_count, dtype=np.float32)
      continue_flag = True
      for g in self.generators:
         data, cf = g.generate(frame_count)
         signal *= data
         if not cf:
            continue_flag = False

      return signal, continue_flag

class Sum(Generator):
   def __init__(self, generators):
      self.generators = generators
      Generator.__init__(self)

   def length(self):
      return max(g.length() for g in self.generators)

   def release(self):
      for g in self.generators:
         g.release()

   def get_buffer(self, frame_count):
      # Continue until all summands are done
      signal = np.zeros(frame_count, dtype=np.float32)
      continue_flag = False
      for g in self.generators:
         data, cf = g.generate(frame_count)
         signal+= data
         if cf:
            continue_flag = True

      return signal, continue_flag

class FMap(Generator):
   def __init__(self, generator, function):
      self.generator = generator
      self.function = function
      Generator.__init__(self)

   def length(self):
      return self.generator.length()

   def release(self):
      return self.generator.release()

   def get_buffer(self, frame_count):
      signal, continue_flag = self.generator.generate(frame_count)
      return self.function(signal), continue_flag

class DC(Generator):
   def __init__(self, value):
      self.value = value
      Generator.__init__(self)

   def length(self):
      return float('inf')

   def release(self):
      pass

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

   def release(self):
      pass

   def get_buffer(self, frame_count):
      factor = self.freq * 2.0 * np.pi / SAMPLING_RATE
      domain = np.arange(self.frame, self.frame + frame_count)
      return self.amp * np.sin(factor * domain + self.phase, dtype=np.float32), True

   

from Queue import PriorityQueue
from datetime import datetime
import abc

import numpy as np

from dspy import config


class Audio:
   def __init__(self):
      self._generators = PriorityQueue()
      self._gain = 0.1 

   def schedule_sequence(self, seq, time):
      for (t, gen) in seq.get_pairs():
         self._generators.put((time+t, gen))
      
   def schedule_generator(self, gen, time):
      self._generators.put((time, gen))

   def add_generator(self, gen):
      self._generators.put((datetime.now(), gen))

   @property
   def gain(self):
       return self._gain
   @gain.setter
   def gain(self, value):
       self._gain = np.clip(value, 0, 1)
   
   def get_output(self, frame_count):
      output = np.zeros( frame_count * config['OUTPUT_CHANNELS'], dtype = np.float32)
      not_done = []
      while not self._generators.empty():
         time, gen = self._generators.get()
         if time > datetime.now():
            not_done.append((time, gen))
            break

         signal, continue_flag = gen.generate(frame_count)
         output += self._rechannel(signal, gen.num_channels, config['OUTPUT_CHANNELS'])
         if continue_flag:
            not_done.append((time, gen))

      for time, gen in not_done:
         self._generators.put((time, gen))

      output *= self.gain

      return output

   def _rechannel(self, buf, in_channels, out_channels):
      if in_channels > 2 or out_channels > 2:
         raise NotImplemented()

      if in_channels == out_channels:
         return buf

      num_frames = len(buf)/in_channels
      output = np.zeros(num_frames*out_channels, dtype=np.float32)
      if in_channels < out_channels:
         in_channel = 0
         for out_channel in xrange(out_channels):
            output[out_channel::out_channels] += buf[in_channel::in_channels]
            in_channel = (in_channel + 1) % in_channels
      elif out_channels > in_channels:
         out_channel = 0
         for in_channel in xrange(out_channels):
            output[out_channel::out_channels] += buf[in_channel::in_channels]
            out_channel = (out_channel + 1) % out_channels

      return output

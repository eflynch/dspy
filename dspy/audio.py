from Queue import PriorityQueue
from datetime import datetime

import pyaudio
import numpy as np

from dspy import config


def rechannel(buf, in_channels, out_channels):
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



class Audio:
   def __init__(self):
      self.audio = pyaudio.PyAudio()
      dev_idx = self._find_best_output()
      self.stream = self.audio.open(format = pyaudio.paFloat32,
                                    channels = config['OUTPUT_CHANNELS'],
                                    frames_per_buffer = 512,
                                    rate = config['SAMPLING_RATE'],
                                    output = True,
                                    input = False,
                                    output_device_index = dev_idx,
                                    stream_callback = self._callback)
      self._generators = PriorityQueue()
      self.gain = 0.1

   def schedule_sequence(self, seq, time):
      for (t, gen) in seq.get_pairs():
         self._generators.put((time+t, gen))
      
   def schedule_generator(self, gen, time):
      self._generators.put((time, gen))

   def add_generator(self, gen):
      self._generators.put((datetime.now(), gen))

   def set_gain(self, gain):
      self.gain = np.clip(gain, 0, 1)

   def get_gain(self):
      return self.gain

   def _callback(self, in_data, frame_count, time_info, status):
      output = np.zeros( frame_count * config['OUTPUT_CHANNELS'], dtype = np.float32)
      not_done = []
      while not self._generators.empty():
         time, gen = self._generators.get()
         if time > datetime.now():
            not_done.append((time, gen))
            break

         signal, continue_flag = gen.generate(frame_count)
         output += rechannel(signal, gen.num_channels, config['OUTPUT_CHANNELS'])
         if continue_flag:
            not_done.append((time, gen))

      for time, gen in not_done:
         self._generators.put((time, gen))

      output *= self.get_gain()
      
      return (output.tostring(), pyaudio.paContinue)


   # return the best output index if found. Otherwise, return None
   def _find_best_output(self):
      # for Windows, we want to find the ASIO host API and device
      cnt = self.audio.get_host_api_count()
      for i in range(cnt):
         api = self.audio.get_host_api_info_by_index(i)
         if api['type'] == pyaudio.paASIO:
            host_api_idx = i
            print 'Found ASIO', host_api_idx
            break
      else:
         # did not find desired API. Bail out
         return None

      cnt = self.audio.get_device_count()
      for i in range(cnt):
         dev = self.audio.get_device_info_by_index(i)
         if dev['hostApi'] == host_api_idx:
            print 'Found Device', i
            return i

      # did not find desired device.
      return None

   # shut down the audio driver. It is import to do this before python quits.
   # Otherwise, python might hang without fully shutting down. 
   # core.register_terminate_func (see __init__ above) will make sure this
   # function gets called automatically before shutdown.
   def close(self):
      self.stream.stop_stream()
      self.stream.close()
      self.audio.terminate()

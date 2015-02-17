import numpy as np

from generator import Generator
from dspy import config

SAMPLING_RATE = config['SAMPLING_RATE']


class ADSREnvelope(Generator):
   def __init__(self, attack_time=4410, attack_order=2.0, decay_time=44100,
                decay_order=1.5, sustain=0.3, release_time=4410, release_order=0.75,
                duration=None):
      self.attack_time = attack_time
      self.attack_order = attack_order
      self.decay_time = decay_time
      self.decay_order = decay_order
      self.sustain = sustain
      self.release_time = release_time
      self.release_order = release_order
      self.release_frame = float('inf')
      if duration:
         self.release_frame = duration * SAMPLING_RATE - release_time
      Generator.__init__(self)

   def length(self):
      return self.release_frame + self.release_time

   def release(self):
      #Check if release already set
      if self.release_frame != float('inf'):
         return

      self.release_frame = self.frame

   def set_release_frame(self, frame):
      self.release_frame = frame

   def get_buffer(self, frame_count):
      domain = np.arange(self.frame, self.frame + frame_count, dtype= np.float32)

      conditions = [
         domain < self.attack_time,
         (self.attack_time + self.decay_time > domain) * (domain >= self.attack_time),
         domain >= self.attack_time + self.decay_time
      ]
      functions = [
         lambda x: (x/self.attack_time)**(1/self.attack_order),
         lambda x: 1 - (1-self.sustain)*((x-self.attack_time)/self.decay_time)**(1/self.decay_order),
         lambda x: self.sustain
      ]
      signal = np.piecewise(domain, conditions, functions)

      conditions = [
         domain < self.release_frame,
         (self.length() > domain) * (domain >= self.release_frame),
         domain > self.length()
      ]
      functions = [
         lambda x: 1.0,
         lambda x: 1.0 - ((x-self.release_frame)/self.release_time)**(1/self.release_order),
         lambda x: 0.0
      ]
      signal *= np.piecewise(domain, conditions, functions)

      continue_flag = self.length() > self.frame

      return signal, continue_flag

class ADDSREnvelope(Generator):
   def __init__(self, attack_time=4410, attack_order=2.0, decay_time=8820,
                decay_order=0.75, sustain=0.6, decay_time_2=44100, decay_order_2=1.5,
                sustain_2=0.3, release_time=4410, release_order=0.75, duration=None):
      self.attack_time = attack_time
      self.attack_order = attack_order
      self.decay_time = decay_time
      self.decay_order = decay_order
      self.decay_time_2 = decay_time_2
      self.decay_order_2 = decay_order_2
      self.sustain = sustain
      self.sustain_2 = sustain_2
      self.release_time = release_time
      self.release_order = release_order
      self.release_frame = float('inf')
      if duration:
         self.release_frame = duration * SAMPLING_RATE - release_time
      Generator.__init__(self)

   def length(self):
      return self.release_frame + self.release_time

   def release(self):
      #Check if release already set
      if self.release_frame != float('inf'):
         return

      self.release_frame = self.frame

   def set_release_frame(self, frame):
      self.release_frame = frame

   def get_buffer(self, frame_count):
      domain = np.arange(self.frame, self.frame + frame_count, dtype= np.float32)

      conditions = [
         domain < self.attack_time,
         (self.attack_time + self.decay_time > domain) * (domain >= self.attack_time),
         (self.attack_time + self.decay_time + self.decay_time_2 > domain) * (domain >= self.attack_time + self.decay_time),
         domain >= self.attack_time + self.decay_time + self.decay_time_2
      ]
      functions = [
         lambda x: (x/self.attack_time)**(1/self.attack_order),
         lambda x: 1 - (1-self.sustain)*((x-self.attack_time)/self.decay_time)**(1/self.decay_order),
         lambda x: self.sustain - (self.sustain-self.sustain_2)*((x-self.attack_time-self.decay_time)/self.decay_time_2)**(1/self.decay_order_2),
         lambda x: self.sustain_2
      ]
      signal = np.piecewise(domain, conditions, functions)

      conditions = [
         domain < self.release_frame,
         (self.length() > domain) * (domain >= self.release_frame),
         domain > self.length()
      ]
      functions = [
         lambda x: 1.0,
         lambda x: 1.0 - ((x-self.release_frame)/self.release_time)**(1/self.release_order),
         lambda x: 0.0
      ]
      signal *= np.piecewise(domain, conditions, functions)

      continue_flag = self.length() > self.frame

      return signal, continue_flag


if __name__ == "__main__":
   import matplotlib.pyplot as plt

   # envelope = ADSREnvelope()
   envelope = ADDSREnvelope()
   envelope = ADDSREnvelope(attack_time=500, attack_order=1.5, decay_time = 44100,
                                decay_order=.75, sustain=0.6, decay_time_2 = 44100*4, decay_order_2=1.5, sustain_2=0.00, release_time=4410,
                                release_order=0.75, duration=5.1)
   plt.figure()
   plt.plot(envelope.generate(44100*5)[0])
   plt.show()



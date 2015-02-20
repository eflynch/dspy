"""
.. module:: adsr
    :platform: Unix, Windows
    :synopsis: Generators for ADSR enveloping

.. moduleauthor: Evan Lynch <evan.f.lynch@gmail.com>

"""
import numpy as np

from dspy import config
from dspy.lib import t2f
from dspy.generator import Generator


SAMPLING_RATE = config['SAMPLING_RATE']


class ADSREnvelope(Generator):
   """Generator for producing an ADSR envelope.
   """

   def __init__(self, attack_time=0.1, attack_order=2.0, decay_time=1.0,
                decay_order=1.5, sustain=0.3, release_time=0.1, release_order=0.75,
                duration=None):
      """Generator for producing an ADSR envelope.

      :param attack_time: Duration of attack.
      :type attack_time: duration.
      :param attack_order: Exponential order of attack.
      :type attack_order: float.
      :param decay_time: Duration of decay.
      :type decay_time: duration.
      :param decay_order: Exponential order of decay.
      :type decay_order: float.
      :param sustain: Gain of sustain.
      :type sustain: float.
      :param release_time: Duration of release.
      :type release_time: duration.
      :param release_order: Exponential order of release.
      :type release_order: float.
      :param duration: Duration of envelope (sets release time).
      :type duration: duration.
      """
      self.attack_time = t2f(attack_time)
      self.attack_order = attack_order
      self.decay_time = t2f(decay_time)
      self.decay_order = decay_order
      self.sustain = sustain
      self.release_time = t2f(release_time)
      self.release_order = release_order
      self.release_frame = float('inf')
      if duration:
         self.release_frame = t2f(duration) - self.release_time
      Generator.__init__(self)

   def length(self):
      return self.release_frame + self.release_time

   def release(self):
      #Check if release already set
      if self.release_frame != float('inf'):
         return

      self.release_frame = self.frame

   def set_release_frame(self, frame):
      self.release_frame = t2f(frame)

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

      return signal

class ADDSREnvelope(Generator):
   def __init__(self, attack_time=4410, attack_order=2.0, decay_time=8820,
                decay_order=0.75, sustain=0.6, decay_time_2=44100, decay_order_2=1.5,
                sustain_2=0.3, release_time=4410, release_order=0.75, duration=None):
      self.attack_time = attack_time * SAMPLING_RATE
      self.attack_order = attack_order
      self.decay_time = decay_time * SAMPLING_RATE
      self.decay_order = decay_order
      self.decay_time_2 = decay_time_2 * SAMPLING_RATE
      self.decay_order_2 = decay_order_2
      self.sustain = sustain
      self.sustain_2 = sustain_2
      self.release_time = release_time * SAMPLING_RATE
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

      return signal


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



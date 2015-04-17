#####################################################################
#
# fluid.py
#
# Copyright (c) 2015, Eran Egozy
#
# Released under the MIT License (http://opensource.org/licenses/MIT)
#
#####################################################################
# With modifications by Evan Lynch (c) 2015

import numpy as np
import fluidsynth

from dspy.generator import Generator

# create another kind of generator that generates audio based on the fluid
# synth synthesizer
class Synth(Generator, fluidsynth.Synth):
   def __init__(self, filepath):
      Generator.__init__(self)
      fluidsynth.Synth.__init__(self)
      self.num_channels = 2
      fluidsynth.Synth()
      self.sfid = self.sfload(filepath)
      if self.sfid == -1:
         raise Exception('Error in fluidsynth.sfload(): cannot open ' + filepath)
      self.program(0, 0, 0)

   def program(self, ch, bank, preset):
      self.program_select(ch, self.sfid, bank, preset)

   def _generate(self, frame_count):
      # get_samples() returns interleaved stereo, so all we have to do is scale
      # the data to [-1, 1].
      samples = self.get_samples(frame_count).astype(np.float32) 
      samples *= (1.0/32768.0)
      return samples

   def _reset(self):
      raise Exception('Cannot reset fluidsynth generator')

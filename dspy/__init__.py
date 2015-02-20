"""A Python DSP and synthesis library built on numpy.

.. moduleauthor:: Evan Lynch <evan.f.lynch@gmail.com>

"""

__version__ = "0.0.0"

config = {}
config['SAMPLING_RATE'] = 44100

from dspy.player import Player
from dspy.generator import Generator, WrapperGenerator, BundleGenerator, Sum, Product
from dspy.basic import FMap, DC, Sine, WaveTable, Noise, Pink
from dspy.adsr import ADSREnvelope
from dspy.note import Tone, Note, FM, SQUARE_AMPLITUDES, SINE_AMPLITUDES, SAW_AMPLITUDES, TRI_AMPLITUDES
from dspy.sampler import Sampler
from dspy import dsp

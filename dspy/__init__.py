"""A Python DSP and synthesis library built on numpy.

.. moduleauthor:: Evan Lynch <evan.f.lynch@gmail.com>

"""
from ._version import __version__

config = {}
config['SAMPLING_RATE'] = 44100

from dspy.player import Player
from dspy.generator import Generator, WrapperGenerator, BundleGenerator, Sum, Product
from dspy.basic import FMap, DC, Sine, WaveTable, Noise, Pink
from dspy.adsr import ADSREnvelope
from dspy.note import Tone, Note, FM
from dspy.sampler import Sampler

from dspy import overtones
from dspy import dsp

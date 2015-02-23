"""A Python DSP and synthesis library built on numpy.

.. moduleauthor:: Evan Lynch <evan.f.lynch@gmail.com>

"""
from ._version import __version__
__version__ = __version__

config = {}
config['SAMPLING_RATE'] = 44100

from dspy.player import Player
from dspy.generator import Generator, WrapperGenerator, BundleGenerator, Sum, Product
from dspy.basic import Map, DC, Sine, WaveTable, Noise, Pink
from dspy.envelope import ExpEnvelope, ReleaseEnvelope, ADSREnvelope
from dspy.note import Tone, Note, FM
from dspy.sampler import Sampler

from dspy import overtones
from dspy import dsp

try:
    from dspy.pyaudioplayer import PyAudioPlayer
except ImportError:
    class PyAudioPlayer:
        def __init__(cls, *args, **kwargs):
            raise Warning('This feature requires pyaudio')

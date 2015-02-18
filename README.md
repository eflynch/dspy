# dspy
Python DSP and Synthesis

Copyright (c) 2015, Evan Lynch

Released under the MIT License (http://opensource.org/licenses/MIT)


## Introduction ##
dspy is a Python package for defining and playing back software-defined
signals. It is implemented with pyaudio and numpy.

## Installation ##
dspy requires:
    - pyaudio
    - numpy
These can usually be installed from pypi with pip.

You may install in the standard way with

```
python setup.py install
```
or you can install with pip from this repository with
```
pip install git+https://github.com/eflynch/dspy
```

## Useage ##
dspy packages an audio player a basic audio player class although it
may not be suitable for all purposes.
```
from dspy import Audio
audio = Audio()
```
Instantiating `Audio` starts a thread which streams data
to PortAudio. Generally, only one instance of Audio should be
used in a project.

dspy additionally packages generators. To produce a basic square wave
tone with a simple envelope:
```
from dspy.generators import Tone, ASDREnvelope
from dspy.generators import SQUARE_AMPLITUDES

tone = Tone(60, SQUARE_AMPLITUDES)
envelope = ADSREnvelope(duration=0.5)

gen = tone * envelope

audio.add_generator(gen)
```

## Generators and Operations ##
### Basic Signals ###
#### DC ####
Constant valued signal
```
dc = dspy.generators.DC(value=3.0)
```

#### Sine ####
Sine wave with set frequency, phase, and amplitude
```
sine = dspy.generators.Sine(freq=440.0, phase=np.pi, amp=0.75)
```

#### Tone ####
Harmonic oscillator bank
```
tone = dspy.generators.Tone(pitch=60, overtones=[(1,1,0), (2,0.1,0)])
```

#### ADSREnvelope ####
```
adsr = dspy.generators.ADSREnvelope(attack_time=)
```

### DSP ###

### Operations ###

### Custom Generators ###



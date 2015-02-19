import dspy
import dspy.generators as gens

from usingpyaudio import PyAudioListener

a = dspy.Audio()
with PyAudioListener(a) as p:
    n = gens.Noise()
    a.add_generator(n)
    p.start()
    raw_input('Enter to stop the noise')

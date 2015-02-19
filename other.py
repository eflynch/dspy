import dspy
import dspy.generators as gens

import numpy as np


with dspy.Audio() as a:

    a = dspy.Audio()

    p = gens.Pink()
    n = gens.Noise()
    sampler = gens.Sampler('/Users/eflynch/Desktop/heads.wav')
    g = sampler.make_gen(44100, 44100, loop=True)
    g1 = sampler.make_gen(88100, 44100, loop=True)
    g2 = sampler.make_gen(123098, 44100*8, loop=True)
    g3 = sampler.make_gen(238200, 88200, loop=True)

    a.add_generator(p)
    # a.add_generator(n)
    a.start()
    raw_input('Enter to quit')


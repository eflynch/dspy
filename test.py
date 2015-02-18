import dspy
import dspy.generators as gens


with dspy.Audio() as a:

    sampler = gens.Sampler('/Users/eflynch/Desktop/heads.wav')
    g = sampler.make_gen(44100, 44100, loop=True)
    g1 = sampler.make_gen(88100, 44100, loop=True)
    g2 = sampler.make_gen(123098, 44100*8, loop=True)
    g3 = sampler.make_gen(238200, 88200, loop=True)

    a.add_generator(g)
    a.add_generator(g1)
    a.add_generator(g2)
    a.add_generator(g3)
    a.start()
    raw_input('Enter to quit')


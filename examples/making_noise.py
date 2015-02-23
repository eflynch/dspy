import os

import dspy as dp

here = os.path.dirname(__file__)

if __name__ == "__main__":
    a = dp.Player()
    with dp.PyAudioPlayer(a) as p:
        sampler = dp.Sampler(os.path.join(here, 'data/example.wav'))
        g = sampler.sample(0, 88200, loop=True)
        a.add(g)
        p.start()
        raw_input('Enter to stop the noise:\n')

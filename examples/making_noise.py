import dspy

from usingpyaudio import PyAudioPlayer

if __name__ == "__main__":
    a = dspy.Player()
    with PyAudioPlayer(a) as p:
        s = dspy.Player([(44100*i, dspy.Noise() * dspy.ADSREnvelope(duration=0.5)) for i in xrange(5)], live=False, loop=True)
        a.add(s)
        p.start()
        raw_input('Enter to stop the noise:\n')

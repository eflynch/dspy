import dspy

from usingpyaudio import PyAudioPlayer

if __name__ == "__main__":
    a = dspy.Player()
    with PyAudioPlayer(a) as p:
        n = dspy.Noise()
        a.add(n)
        p.start()
        raw_input('Enter to stop the noise')

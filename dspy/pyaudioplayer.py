import pyaudio

from dspy import config


def _find_best_output(audio):
    # for Windows, we want to find the ASIO host API and device
    cnt = audio.get_host_api_count()
    for i in range(cnt):
        api = audio.get_host_api_info_by_index(i)
        if api['type'] == pyaudio.paASIO:
            host_api_idx = i
            print 'Found ASIO', host_api_idx
            break
    else:
        # did not find desired API. Bail out
        return None

    cnt = audio.get_device_count()
    for i in range(cnt):
        dev = audio.get_device_info_by_index(i)
        if dev['hostApi'] == host_api_idx:
            print 'Found Device', i
            return i

    # did not find desired device.
    return None


class PyAudioPlayer:
    def __init__(self, player):
        self.player = player
        self.pyaudio = pyaudio.PyAudio()
        dev_idx = _find_best_output(self.pyaudio)

        self.stream = self.pyaudio.open(format = pyaudio.paFloat32,
                       channels = player.num_channels,
                       frames_per_buffer = 512,
                       rate = config['SAMPLING_RATE'],
                       output = True,
                       input = False,
                       output_device_index = dev_idx,
                       stream_callback = self._callback,
                       start = False)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def _callback(self, in_data, frame_count, time_info, status):
        output, continue_flag = self.player.generate(frame_count)
        return (output.tostring(), pyaudio.paContinue)

    def start(self):
        self.stream.start_stream()

    def stop(self):
        self.stream.stop_stream()

    def close(self):
        self.stream.close()
        self.pyaudio.terminate()

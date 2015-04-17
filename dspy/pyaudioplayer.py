import pyaudio
import wave
import numpy as np

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
    def __init__(self, player, write_filename=None):
        self.player = player
        self.pyaudio = pyaudio.PyAudio()
        dev_idx = _find_best_output(self.pyaudio)
        self.write_filename = write_filename

        self.stream = self.pyaudio.open(format = pyaudio.paFloat32,
                       channels = player.num_channels,
                       frames_per_buffer = 1024,
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

        string = output.tostring()

        if self.write_filename is not None:
            output *= ( 32768.0)
            output = output.astype(np.int16)
            self.write_file.writeframes(output.tostring())

        return (string, pyaudio.paContinue)

    def start(self):
        if self.write_filename:
            self.write_file = wave.open(self.write_filename, 'wb')
            self.write_file.setnchannels(self.player.num_channels)
            sample_width = self.pyaudio.get_sample_size(pyaudio.paInt16)
            self.write_file.setsampwidth(sample_width)
            self.write_file.setframerate(config['SAMPLING_RATE'])
        self.stream.start_stream()


    def stop(self):
        self.stream.stop_stream()

    def close(self):
        self.stream.close()
        self.pyaudio.terminate()

        if self.write_filename is not None:
            self.write_file.close()

from datetime import timedelta

import numpy as np

from dspy import config


def rechannel(buf, in_channels, out_channels):
    if in_channels > 2 or out_channels > 2:
        raise NotImplemented()

    if in_channels == out_channels:
        return buf

    num_frames = len(buf)/in_channels
    output = np.zeros(num_frames*out_channels, dtype=np.float32)
    if in_channels < out_channels:
        in_channel = 0
        for out_channel in range(out_channels):
            output[out_channel::out_channels] += buf[in_channel::in_channels]
            in_channel = (in_channel + 1) % in_channels
    elif out_channels > in_channels:
        out_channel = 0
        for in_channel in range(out_channels):
            output[out_channel::out_channels] += buf[in_channel::in_channels]
            out_channel = (out_channel + 1) % out_channels

    return output


def t2f(t):
    if isinstance(t, timedelta):
        return int(t.total_seconds() * config['SAMPLING_RATE'])

    if isinstance(t, float):
        return int(t * config['SAMPLING_RATE'])

    if isinstance(t, int):
        return t


def pitch_to_frequency(pitch):
    return 440 * 2 ** ((pitch - 69)/12.)

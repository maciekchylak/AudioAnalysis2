import os

from scipy.io import wavfile
from sound_functions import *

import numpy as np

samplerate, data =  read_wav('gyr.wav', 'Maciej')
samplerate, data = read_wav_clip('gyr.wav', 'Maciej')

v = volume('OSR_us_000_0010_8k.wav', 'Maciej')
z = zero_crossing_rate('zdanie.wav', 'Maciej')
index_min_v = v.index(min(v))
print(data)

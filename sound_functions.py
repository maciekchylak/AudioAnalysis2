### There will be defined all sound functions
import statistics
import math

import numpy as np
from scipy.io import wavfile
import matplotlib.pyplot as plt

from conf import *

### Frame level functions
def read_wav(filename, imie):
    if imie == 'Maciej':
        key_dict = 'Maciej_' + filename
    elif imie == 'Dawid':
        key_dict = 'Dawid_' + filename
    elif imie == 'Others':
        key_dict = 'Others_' + filename
    else:
        return None

    return samplerate_dict[key_dict], data_dict[key_dict]

def read_wav_clip(filename, imie):
    samplerate, data = read_wav(filename, imie)
    return samplerate, flatten(data)

def volume2(filename, imie):
    f, data, samplerate = fourier_transformation_of_time(filename, imie)
    volume = []
    for d in data:
        v = 0
        for el in d:
            v += el ** 2
        volume.append(v / len(d))

    return volume

### napisaliśmy fft, jednak będziemy korzystali z gotowej biblioteki
def fft(data):
    n = data.shape[0]
    if n % 2 != 0:
        raise ValueError("nie jest potegi 2")
    elif n <= 2:
        data = np.asarray(data, dtype=float)
        n = len(data)
        M = np.exp(-2j * np.pi * np.arange(n).reshape((n, 1)) * np.arange(n) / n)
        return np.dot(M, data)
    else:
        data_parzyste = fft(data[::2])
        data_nieparzyste = fft(data[1::2])
        t = np.exp(-2j* np.pi * np.arange(n) / n)
        return np.concatenate([data_parzyste + t[:int(n/2)] * data_nieparzyste,
                               data_parzyste + t[int(n/2):] * data_nieparzyste])

def fourier_transformation_on_frame(data, samplerate):
    return np.fft.rfftfreq(len(data), 1/samplerate), np.abs(np.fft.rfft(data))

def fourier_transformation_of_time(filename, imie):
    samplerate, data =  read_wav(filename, imie)

    data_1=[]
    f=[]

    for i in data:
        data_1.append(np.abs(np.fft.rfft(i)))
        f.append(np.fft.rfftfreq(len(i), 1/samplerate))

    return f, data_1, samplerate

def BW(filename, imie):
    f, data, samplerate = fourier_transformation_of_time(filename, imie)
    fc = FC(filename, imie)
    bw = []
    for f1, d, fc1 in zip(f, data, fc):
        bw.append(sum((d ** 2) * ((f1 - fc1) ** 2))/sum(d ** 2))

    return np.sqrt(bw)


def FC(filename,imie):
    f,data,samplerate=fourier_transformation_of_time(filename, imie)
    fc=[]
    for f1,d in zip(f,data):
        fc.append(sum(f1*d)/sum(d))

    return fc

def BE(filename, imie, f0, f1):
    samplerate, data =  read_wav(filename, imie)
    be = []

    for frame in data:
        f, d = fourier_transformation_on_frame(frame, samplerate)
        ind = [idx for idx, element in enumerate(f) if element <= f1 and element >= f0]
        d_tmp = [d[i] for i in ind]
        s = 0
        for el in d_tmp:
            s += el ** 2
        be.append(s / len(d_tmp))
    return be

def BER(filename, imie, f0, f1):
    be = BE(filename, imie, f0, f1)
    volume = volume2(filename, imie)

    return [el1 / el2 for el1, el2 in zip(be, volume)]

def fourier_transformation(filename, imie, window_function):
    samplerate, data =  read_wav(filename, imie)

    data_1=[]
    f=[]

    for i in data:
        data_1.append(np.abs(np.fft.rfft(i))*window_function(len(i)))
        f.append(np.fft.rfftfreq(len(i), 1/samplerate))

    return f,data_1,samplerate

def identity(x):
    return [1 for i in range(x)]

def hamming(x):
    return np.hamming(x)

def hanning(x):
    return np.hanning(x)

def spectral_flatness_measure(filename,imie):
    measure=[]
    f,data,samplerate=fourier_transformation_of_time(filename, imie)
    for d1 in data:
        measure.append(len(d1)*math.prod(d1)/((1/len(d1) * sum(np.power(d1,2)))))
    return measure

def spectral_crest_factor(filename,imie):
    factor=[]
    f,data,samplerate=fourier_transformation_of_time(filename, imie)
    for d1 in data:
        l = max(np.power(d1,2))
        m = 1/len(d1) * sum(d1)
        factor.append(l/m)
    return factor

### in time

def volume(filename, imie):
    _, data = read_wav(filename, imie)
    output = []
    for frame in data:
        volume = 0
        for sample in frame:
            volume += float(sample) ** 2
        output.append(math.sqrt(volume / len(frame)))
    return [(el - min(output)) / (max(output) - min(output)) for el in output]

def energy_data(data):
    output = 0
    for el in data:
        output += float(el) ** 2
    return output

def short_time_energy(filename, imie):
    return [el ** 2 for el in volume(filename, imie)]

def zero_crossing_rate(filename, imie):
    samplerate, data = read_wav(filename, imie)
    output = []
    for frame in data:
        zero_crossing_rate = 0
        for i in range(1, len(frame)):
            zero_crossing_rate += abs(
                                np.sign(float(frame[i])) - np.sign(float(frame[i - 1]))
                            )
        output.append(int((zero_crossing_rate * samplerate / (len(frame) * 2))))
    return output

def silent_voiceless_ratio(filename, imie):
    v = volume(filename, imie)
    zcr = zero_crossing_rate(filename, imie)
    print(v)
    print(zcr)
    if imie == 'Maciej' or imie == 'Dawid':
        output = [1 if v[i] >= 0.1 else (0 if v[i] < 0.1 and zcr[i] < 3000 else 0.5) for i in range(len(v))]
    else:
        output = [1 if v[i] >= 0.1 else 0 for i in range(len(v))]
    return output

def autocorelation(data, l):
    output = 0
    for i in range(len(data) - l):
        output += data[i] * data[i + l]

    return output

def average_magnitude_difference_function(data, l):
    output = 0
    for i in range(len(data) - l):
        output += abs(data[i + l] - data[i])

    return output

def fundemental_frequency(filename, imie):

    samplerate, data= read_wav(filename,imie)
    fundemental_frequency=[0 for i in range(len(data))]
    if imie == 'Dawid' or imie == 'Maciej':
        for j,frame in enumerate(data):
            if len(frame) < 50:
                del fundemental_frequency[-1]
                continue
            auto_korelation=[0 for i in range(50,len(frame))]
            for l in range(50,len(frame)):
                for i in range(len(frame)-l):
                    auto_korelation[l-50]+=frame[i]*frame[i+l]
            fundemental_frequency[j]=1/(((auto_korelation.index(max(auto_korelation)))+50)/samplerate)

    else:
        pass
    return fundemental_frequency


### Clip level functions
def VSTD(filename, imie):

    volumes = volume(filename, imie)

    return np.std(volumes)

def volume_dynamic_range(filename, imie):

    volumes = volume(filename, imie)

    return (max(volumes) - min(volumes)) / max(volumes)

### Energy level functions
def low_short_time_energy_ratio(filename, imie):

    samplerate, data = read_wav(filename, imie)
    stes = short_time_energy(filename, imie)
    output = 0
    if len(stes) <= 1 / LEN_OF_FRAME:
        avg_ste = statistics.mean(stes)

        for i in range(len(stes)):
            output += np.sign(0.5 * avg_ste - stes[i]) + 1

    else:
        number_of_frames_in_second = int((1 / LEN_OF_FRAME) / 5)
        half_of_frames_in_second =  int(number_of_frames_in_second  / 2)

        avg_ste = statistics.mean(stes[0:number_of_frames_in_second])

        for i in range(half_of_frames_in_second):
            output += np.sign(0.5 * avg_ste - stes[i]) + 1
        for i in range(half_of_frames_in_second, len(stes) - half_of_frames_in_second):
            avg_ste = statistics.mean(stes[i - half_of_frames_in_second: i + half_of_frames_in_second])
            output += np.sign(0.5 * avg_ste - stes[i]) + 1

        avg_ste = statistics.mean(stes[(len(stes)-number_of_frames_in_second):len(stes)])
        for i in range(len(stes) - half_of_frames_in_second, len(stes)):
            output += np.sign(0.5 * avg_ste - stes[i]) + 1

    return output / (2 * len(stes))

def is_music(filename, imie):
    return low_short_time_energy_ratio(filename, imie) <= 0.3

def energy_entropy(filename, imie, K):
    samplerate, data = read_wav(filename, imie)

    output = 0
    for frame in data:
        frame_splited = np.array_split(ary = frame, indices_or_sections = K)
        energy_segment = [energy_data(segment) for segment in frame_splited]
        energy_segment_norm = [energy / max(energy_segment) for energy in energy_segment]
        for energy in energy_segment_norm:
            output -= (energy ** 2) * math.log2(energy ** 2 + 0.0001)

    return output


def standard_deviation_of_zcr(filename, imie):
    data = zero_crossing_rate(filename, imie)
    return np.std(data)

def high_zero_crossing_rate_ratio(filename, imie):

    samplerate, data = read_wav(filename, imie)
    zcrs = zero_crossing_rate(filename, imie)
    output = 0
    if len(zcrs) <= 1 / LEN_OF_FRAME:
        avg_zcr = statistics.mean(zcrs)

        for i in range(len(zcrs)):
            output += abs(np.sign(zcrs[i] - 1.5 * avg_zcr) + 1)

    else:
        number_of_frames_in_second = int(1 / LEN_OF_FRAME)
        half_of_frames_in_second =  int(number_of_frames_in_second  / 2)

        avg_zcr = statistics.mean(zcrs[0:number_of_frames_in_second])

        for i in range(half_of_frames_in_second):
            output += abs(np.sign(zcrs[i] - 1.5 * avg_zcr) + 1)

        for i in range(half_of_frames_in_second, len(zcrs) - half_of_frames_in_second):
            avg_zcr = statistics.mean(zcrs[i - half_of_frames_in_second: i + half_of_frames_in_second])
            output += abs(np.sign(zcrs[i] - 1.5 * avg_zcr) + 1)

        avg_zcr = statistics.mean(zcrs[(len(zcrs)-number_of_frames_in_second):len(zcrs)])

        for i in range(len(zcrs) - half_of_frames_in_second, len(zcrs)):
            output += abs(np.sign(zcrs[i] - 1.5 * avg_zcr) + 1)

    return output / (2 * len(zcrs))

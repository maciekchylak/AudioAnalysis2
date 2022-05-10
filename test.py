import os

from scipy.io import wavfile
import numpy as np

from sound_functions import *



print(volume2('abe.wav', 'Maciej'))
print(fft(np.sin(2 * np.pi * np.arange(512) * 1000 / 10)))

widmo_faz = np.abs(data[0])

print(widmo_faz)
f = np.fft.rfftfreq(len(widmo_faz), LEN_OF_FRAME)

print(f)
plt.plot(widmo_faz)
plt.xlabel('częstotliwość [Hz]')
plt.ylabel('faza [rad]')
plt.title('Widmo fazowe sygnału sinusoidalnego')
plt.show()

import cmath
import math
import struct
import numpy as np

neg_2_pi_i = -2*cmath.pi*complex(0,1)

#generates a waveform in the form of a list of intensity samples (-1 to 1) over 1 second
#Each frequency in the frequencies list is composed, then the final result is normalized
def create_waveform(frequencies : list, amp_shift: float):
    sample_rate = 44100
    num_samples = int(sample_rate) #1 second
    g = [0 for i in range(num_samples)]
    for f in frequencies: #compose all frequencies
        for i in range(num_samples):
            t = i/sample_rate
            g[i] += math.cos(2*math.pi*f*t)
    highest_sample = max(g)
    g = [f/highest_sample+amp_shift for f in g] #normalize each sample
    return g

#Used to prompt what times t0 and t1 should be sampled from the file to perform the FT
def prompt_time_interval(duration):
    while True:
        t0 = float(input('Sample start time: '))
        if t0 < 0 or t0 > duration:
            print('INVALID TIME(S)')
            continue
        t1 = input('Sample end time (type max to go to the end): ')
        if t1 == 'max':
            t1 = duration
        else:
            t1 = float(t1)
        if t0 > t1 or t1 > duration:
            print('INVALID TIME(S)')
            continue
        break
    return (t0, t1)

#Used to prompt what frequency will be generated by the create_waveform function
def prompt_waveform():
    frequencies = []
    while True:
        frequency = input('Input an integer frequency to compose or -1 to finish inputting frequencies:\n')
        try:
            frequency = int(frequency.strip(' '))
            if frequency == -1:
                if len(frequencies) == 0:
                    print('Need at least one frequency!')
                    continue
                break
            if frequency <= 0:
                raise Exception('')
            frequencies.append(frequency)
        except:
            print('Invalid frequency value found:', frequency)
    return frequencies

def prompt_wind_freq_max():
    while True:
        wind_freq_max = input('Input an integer frequency for the fourier plot to search to: ')
        try:
            wind_freq_max = int(wind_freq_max.strip(' '))
            if wind_freq_max <= 0:
                raise Exception('')
            return wind_freq_max
        except:
            print('Invalid frequency:', wind_freq_max)

#Reads samples indexed by the starting sample and runs until the total samples in the range have been read
def read_samples(wav, starting_sample, tot_samples):
    samples = []
    wav.setpos(starting_sample)
    for i in range(tot_samples):
        wav_read = struct.unpack("<h", wav.readframes(1))[0]
        samples.append(wav_read)
    return samples

#calculates the complex numbers for winding the function g at the given winding frequency throughout the given time interval
def calc_complex(g, f, t_range):
    neg_2_pi_i_f = neg_2_pi_i*f
    complex_vals = []
    for i in range(len(g)):
        t = t_range[i]
        g_of_t = g[i]
        complex_vals.append(g_of_t*cmath.exp(neg_2_pi_i_f*t))
    center = sum(complex_vals)/len(complex_vals)
    reals = np.array([c.real for c in complex_vals])
    imags = np.array([c.imag for c in complex_vals])
    return (reals, imags, center)

def calc_complex_center(g, f, t_range):
    neg_2_pi_i_f = neg_2_pi_i*f
    complex_val_sum = complex(0,0)
    for i in range(len(g)):
        t = t_range[i]
        g_of_t = g[i]
        complex_val_sum += g_of_t*cmath.exp(neg_2_pi_i_f*t)
    return complex_val_sum/len(g)

def calc_center_mags(g, t_range, wind_freq_sweep_max):
    center_mags = []
    for winding_freq in range(1, wind_freq_sweep_max+1):
        if winding_freq % 500 == 1:
            print(f'Searching frequency range {winding_freq}-{min(winding_freq+499,wind_freq_sweep_max)} Hz / {wind_freq_sweep_max} Hz')
        center = calc_complex_center(g, winding_freq, t_range)
        center_mags.append(abs(center))
    detect_thresh = max(center_mags)/4
    maxima = find_local_maxima(center_mags, detect_thresh)
    if len(maxima): #if a maximum was found
        end = max(maxima)
        if end < wind_freq_sweep_max-int(end/10) and end > 10:
            end += int(end/10)
        elif end < wind_freq_sweep_max-end:
            end += end
        return (center_mags[:end], end, maxima)
    else:
        return (center_mags, len(center_mags)-1, maxima)

def find_local_maxima(center_mags, detect_thresh):
    maxima = []
    if len(center_mags) > 1: #left edge maxima
        if center_mags[0] > center_mags[1] and center_mags[0] > detect_thresh:
            maxima.append(1)
    for i in range(1, len(center_mags)-1):
        if center_mags[i-1] < center_mags[i] and center_mags[i+1] < center_mags[i] and center_mags[i] >= detect_thresh:
            maxima.append(i+1)
    if len(center_mags) > 1: #right edge maxima
        if center_mags[-1] > center_mags[-2] and center_mags[-1] > detect_thresh:
            maxima.append(len(center_mags))
    if len(center_mags) == 1 and center_mags[0] > detect_thresh:
        maxima.append(1)
    return maxima

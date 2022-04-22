import helper
import wave
import time
import numpy as np
import sys
import plotter

#consts
AMP_SHIFT = 0 #shift the amplitude up/down this many units (usually 0)

if __name__ == '__main__':
    using_file = False
    #Get file
    if len(sys.argv) >= 2:
        using_file = True

    if using_file:
        #open wav file in read mode
        try:
            wav = wave.open(sys.argv[1], mode='rb')
        except:
            raise Exception('Error opening file! ' + sys.argv[1])

        #Get some wav attributes
        _, _, samp_rate, num_samps, _, _ = wav.getparams()
        duration = num_samps/samp_rate
        print(f'Sample rate: {samp_rate}')
        print(f'Number of samples: {num_samps}')
        print(f'Duration: {duration} seconds')

        #get desired sample time interval
        t0, t1 = helper.prompt_time_interval(duration)

        #get sample indices for start/end of interval
        starting_sample = int(t0*samp_rate)
        ending_sample = int(t1*samp_rate)
        tot_samples = ending_sample - starting_sample #how many total samples in interval

        print(f'Reading from sample {starting_sample} to {ending_sample} ({tot_samples} samples)...')

        #read every sample in interval and interpolate from -1 to 1 plus AMP_SHIFT
        samples = helper.read_samples(wav, starting_sample, tot_samples)
        g = [sample/((2**15)-1) + AMP_SHIFT for sample in samples]
        print('Done!')
        print('Max sample read:', max(samples))
        print('Min sample read:', min(samples))
    else:
        frequencies = helper.prompt_waveform()
        print('Frequencies selected:', str(frequencies)[1:-1])
        g = helper.create_waveform(frequencies, AMP_SHIFT)
        tot_samples = len(g)
        t0 = 0
        t1 = 1
    print('Max signal amplitude:', max(g))
    print('Min signal amplitude:', min(g))

    wind_freq_max = helper.prompt_wind_freq_max()

    #Calculate the magnitude of the center of the graph for every winding frequency
    print('Calculating fourier plot...')
    start_time = time.process_time()
    cent_mags, end_freq, detected_freqs = helper.calc_center_mags(g, np.linspace(t0, t1, tot_samples), wind_freq_max)
    winding_freq = 0 #initial windings/sec
    end_time = time.process_time()
    print(f'Done! ({end_time-start_time} seconds)')
    if len(detected_freqs):
        print('Frequencies detected (Hz):', str(detected_freqs)[1:-1])
    else:
        print('No frequencies detected.')

    t_range = np.linspace(t0,t1,tot_samples)
    #Calculate real/imag coords of each sample using sample_amplitude*e^(-2*pi*i*f*t)
    reals, imags, center = helper.calc_complex(g, winding_freq, t_range)

    #Initialize matplot
    plotter.init(reals, imags, center, cent_mags, end_freq, detected_freqs, g, t_range)

import helper
import wave
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gs
import sys
from matplotlib.widgets import Slider, TextBox

#consts
AMP_SHIFT = 0 #shift the amplitude up/down this many units (usually 0)

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
    g = helper.create_waveform(frequencies, AMP_SHIFT)
    tot_samples = len(g)
    t0 = 0
    t1 = 1
print('Max signal amplitude:', max(g))
print('Min signal amplitude:', min(g))

#Calculate the magnitude of the center of the graph for every winding frequency
print('Calculating fourier plot...')
start_time = time.process_time()
cent_mags, end_freq, detected_freqs = helper.calc_center_mags(g, np.linspace(t0, t1, tot_samples))
slider_min = 0
slider_max = end_freq
winding_freq = slider_min #initial windings/sec
end_time = time.process_time()
print(f'Done! ({end_time-start_time} seconds)')
print('Frequencies detected (Hz):', str(detected_freqs)[1:-1])

#Calculate real/imag coords of each sample using sample_amplitude*e^(-2*pi*i*f*t)
reals, imags, center = helper.calc_complex(g, winding_freq, np.linspace(t0, t1, tot_samples))

#Setup plot
plt.subplots_adjust(left=0.25,bottom=0.1)
max_r = abs(max(g))
grid = gs.GridSpec(3,1, height_ratios=[12,1,1], hspace=0.4)
wave_plt = plt.subplot(grid[0,0])
wave_plt.set_ylabel('Imaginary')
wave_plt.set_xlabel('Real')
wave_plt.set_axisbelow(True)
plt.grid(True)
wave_plt_cent = plt.subplot(grid[0,0])
wave_plt.set_aspect('equal', adjustable='box')
wave_plt_cent.set_aspect('equal', adjustable='box')
plt.xlim([-max_r-0.1,max_r+0.1])
plt.xlim([-max_r-0.1,max_r+0.1])
plt.ylim([-max_r-0.1,max_r+0.1])
plt.ylim([-max_r-0.1,max_r+0.1])
inp_plt = plt.subplot(grid[1,0])
inp_plt.set_ylabel('Intensity')
inp_plt.set_xlabel('Time (s)')
inp_plt.grid(True)
fourier_plt = plt.subplot(grid[2,0])
fourier_plt.set_ylabel('Center Dist.')
fourier_plt.set_xlabel('Winding Frequency (Hz)')
fourier_plt.grid(True)
scat_wave = wave_plt.scatter(reals, imags, s=1)
wave_plt.set_title('Waveform Wrap')
scat_wave_cent = wave_plt_cent.scatter(center.real, center.imag, s=50, c='#990000')
inp_plot = inp_plt.plot(np.linspace(t0, t1, len(g)), g)
inp_plt.set_title('Input Waveform')
fourier_plot = fourier_plt.plot([i for i in range(end_freq+1)], cent_mags)
fourier_plt.vlines(detected_freqs, 0, max(cent_mags), linestyles='dashed')
plt.xticks(list(plt.xticks()[0]) + detected_freqs)
plt.xlim(left=0)
fourier_plt.set_title('Fourier Plot (distance from center)')

#frequency slider
axfreq = plt.axes([0.1, 0.25, 0.0225, 0.63])
freq_slider = Slider(
        ax=axfreq,
        label="Winding Frequency (Hz)",
        valmin=slider_min,
        valmax=slider_max,
        valinit=winding_freq,
        orientation="vertical"
)
#frequency text input
axbox = plt.axes([0.1, 0.05, 0.1, 0.025])
text_box = TextBox(axbox, 'Jump to frequency (Hz)', initial=str(winding_freq))

def update(val): #update plot with new winding frequency, called whenever slider/text is changed/submitted
    global winding_freq
    if not freq_slider.active:
        return
    try:
        winding_freq = float(val)
    except:
        return
    reals, imags, center = helper.calc_complex(g, winding_freq, np.linspace(t0, t1, tot_samples))
    scat_wave.set_offsets(np.c_[reals, imags])
    scat_wave_cent.set_offsets(np.c_[center.real, center.imag])
    freq_slider.set_active(False)
    freq_slider.set_val(winding_freq)
    freq_slider.set_active(True)

freq_slider.on_changed(update)
text_box.on_submit(update)

#Draw plot
plt.get_current_fig_manager().full_screen_toggle()
plt.show()

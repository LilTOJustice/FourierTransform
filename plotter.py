import matplotlib.pyplot as plt
import matplotlib.gridspec as gs
import numpy as np
from matplotlib.widgets import Slider, TextBox
import helper

def update(val, freq_slider, winding_freq, scat_wave, scat_wave_cent, center, reals, imags, g, t0, t1, tot_samples): #update plot with new winding frequency, called whenever slider/text is changed/submitted
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

def init(reals, imags, center, cent_mags, end_freq, detected_freqs, g, t0, t1, tot_samples):
    #Setup plot
    winding_freq = 0
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
    fourier_plot = fourier_plt.plot([i for i in range(1, end_freq+1)], cent_mags)
    fourier_plt.vlines(detected_freqs, 0, max(cent_mags), linestyles='dashed')
    plt.xticks(list(plt.xticks()[0]) + detected_freqs)
    plt.xlim(left=0)
    fourier_plt.set_title('Fourier Plot (distance from center)')

    #frequency slider
    axfreq = plt.axes([0.1, 0.25, 0.0225, 0.63])
    freq_slider = Slider(
            ax=axfreq,
            label="Winding Frequency (Hz)",
            valmin=0,
            valmax=end_freq,
            valinit=0,
            orientation="vertical"
    )
    #frequency text input
    axbox = plt.axes([0.1, 0.05, 0.1, 0.025])
    text_box = TextBox(axbox, 'Jump to frequency (Hz)', initial=str(winding_freq))


    freq_slider.on_changed(lambda val : update(val, freq_slider, winding_freq, scat_wave, scat_wave_cent, center, reals, imags, g, t0, t1, tot_samples))
    text_box.on_submit(lambda val: update(val, freq_slider, winding_freq, scat_wave, scat_wave_cent, center, reals, imags, g, t0, t1, tot_samples))

    #Draw plot
    plt.get_current_fig_manager().full_screen_toggle()
    plt.show()

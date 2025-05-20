import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, CheckButtons
from scipy import signal


INIT_AMPLITUDE = 1.0
INIT_FREQ = 1.0
INIT_PHASE = 0.0

INIT_NOISE_MEAN = 0.0
INIT_NOISE_STD = 0.1

INIT_GAUSS_SIGMA = 2.0

t = np.linspace(0, 2 * np.pi, 500)

global_noise = np.random.normal(INIT_NOISE_MEAN, INIT_NOISE_STD, size=t.shape)


def generate_signal(time, amplitude, frequency, phase, noise, show_noise):
    pure = amplitude * np.sin(2 * np.pi * frequency * time + phase)
    if show_noise:
        return pure + noise
    else:
        return pure


def apply_gaussian_filter(raw, sigma):
    window = signal.windows.gaussian(len(raw), sigma)
    return signal.convolve(raw, window/window.sum(), mode='same')


def update_plots(val=None):
    amp = amp_slider.val
    freq = freq_slider.val
    phase = phase_slider.val
    show_noise = noise_check.get_status()[0]
    sigma = gauss_sigma_slider.val

    raw = generate_signal(t, amp, freq, phase, global_noise, show_noise)
    filt = apply_gaussian_filter(raw, sigma)

    plot_raw.set_ydata(raw)
    plot_filt.set_ydata(filt)
    plot_raw.figure.canvas.draw_idle()


def update_noise(val):
    global global_noise
    mean = noise_mean_slider.val
    std = noise_std_slider.val
    global_noise = np.random.normal(mean, std, size=t.shape)
    update_plots()


def reset_all(event):
    amp_slider.reset()
    freq_slider.reset()
    phase_slider.reset()
    noise_mean_slider.reset()
    noise_std_slider.reset()
    gauss_sigma_slider.reset()
    if noise_check.get_status()[0] != True:
        noise_check.set_active(0)
    update_plots()


fig, (ax_raw, ax_filt) = plt.subplots(2,1, figsize=(10,6), sharex=True)
plt.subplots_adjust(left=0.15, bottom=0.35, right=0.85, hspace=0.4, top=0.95)


initial_raw = generate_signal(t, INIT_AMPLITUDE, INIT_FREQ, INIT_PHASE, global_noise, True)
plot_raw, = ax_raw.plot(t, initial_raw, lw=2)
ax_raw.set_title('Зашумлений графік')
ax_raw.grid(True)

initial_filt = apply_gaussian_filter(initial_raw, INIT_GAUSS_SIGMA)
plot_filt, = ax_filt.plot(t, initial_filt, lw=2)
ax_filt.set_title('Фільтрований графік (Gaussian)')
ax_filt.grid(True)


ax_amp = plt.axes([0.15, 0.18, 0.65, 0.03])
amp_slider = Slider(ax_amp, 'Amplitude', 0.0, 10.0, valinit=INIT_AMPLITUDE)
amp_slider.on_changed(update_plots)

ax_freq = plt.axes([0.15, 0.14, 0.65, 0.03])
freq_slider = Slider(ax_freq, 'Frequency', 0.1, 10.0, valinit=INIT_FREQ)
freq_slider.on_changed(update_plots)

ax_phase = plt.axes([0.15, 0.10, 0.65, 0.03])
phase_slider = Slider(ax_phase, 'Phase', 0.0, 2*np.pi, valinit=INIT_PHASE)
phase_slider.on_changed(update_plots)


ax_noise_mean = plt.axes([0.15, 0.06, 0.65, 0.03])
noise_mean_slider = Slider(ax_noise_mean, 'Noise Mean', -1.0, 1.0, valinit=INIT_NOISE_MEAN)
noise_mean_slider.on_changed(update_noise)

ax_noise_std = plt.axes([0.15, 0.02, 0.65, 0.03])
noise_std_slider = Slider(ax_noise_std, 'Noise Std', 0.0, 1.0, valinit=INIT_NOISE_STD)
noise_std_slider.on_changed(update_noise)


ax_sigma = plt.axes([0.15, 0.22, 0.65, 0.03])
gauss_sigma_slider = Slider(ax_sigma, 'Gaussian', 0.1, 10.0, valinit=INIT_GAUSS_SIGMA)
gauss_sigma_slider.on_changed(update_plots)


ax_cb = plt.axes([0.87, 0.18, 0.12, 0.08])
noise_check = CheckButtons(ax_cb, ['Show Noise'], [True])
noise_check.on_clicked(update_plots)


ax_btn = plt.axes([0.87, 0.07, 0.12, 0.05])
btn = Button(ax_btn, 'Reset', color='lightcoral')
btn.on_clicked(reset_all)


print("Інструкції:")
print("1. Регулюйте гармоніку (Amplitude, Frequency, Phase).")
print("2. Налаштуйте шум (Noise Mean, Noise Std).")
print("3. Кнопка 'Show Noise' вмикає/вимикає шум.")
print("4. Слайдер 'Gaussian' змінює параметр фільтра.")
print("5. Кнопка 'Reset' повертає початкові налаштування.")

plt.show()

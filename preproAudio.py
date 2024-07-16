import os
import numpy as np
import scipy.signal
import librosa
import soundfile as sf
import sounddevice as sd
import matplotlib.pyplot as plt

def plot_signal(signal, sr, title="Signal"):
    plt.figure(figsize=(10, 4))
    plt.plot(np.arange(len(signal)) / sr, signal)
    plt.title(title)
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.show()

def clean_audio(signal, noise_level=0.02):
    noise_mask = np.abs(signal) < noise_level
    signal[noise_mask] = 0
    return signal

def apply_preemphasis(signal, coefficient=0.97):
    return scipy.signal.lfilter([1, -coefficient], [1], signal)

def normalize_audio(signal):
    return librosa.util.normalize(signal)

def segment_audio(signal, frame_length=2048, hop_length=512):
    frames = librosa.util.frame(signal, frame_length=frame_length, hop_length=hop_length).T
    return frames

def record_audio(duration, sample_rate=44100):
    print("Recording...")
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
    sd.wait()
    print("Recording finished.")
    return recording.flatten(), sample_rate

def trim_audio(signal, sr, top_db=20):
    trimmed_signal, index = librosa.effects.trim(signal, top_db=top_db)
    return trimmed_signal

def play_audio(signal, sr):
    sd.play(signal, sr)
    sd.wait()
    print("Playback finished.")

def merekam():
    input_audio_dir = 'C:\\Users\\kurni\\Downloads\\oping\\coba-coba\\datasetRecap\\original'
    output_audio_dir = 'C:\\Users\\kurni\\Downloads\\oping\\coba-coba\\datasetRecap'

    if not os.path.exists(input_audio_dir):
        os.makedirs(input_audio_dir)

    if not os.path.exists(output_audio_dir):
        os.makedirs(output_audio_dir)

    duration = 3
    recorded_signal, recorded_sr = record_audio(duration)
    recorded_audio_path = os.path.join(input_audio_dir, 'coba.wav')
    sf.write(recorded_audio_path, recorded_signal, recorded_sr)

    input_audio_files = [file for file in os.listdir(input_audio_dir) if file.endswith('.wav')]

    for audio_file in input_audio_files:
        input_audio_path = os.path.join(input_audio_dir, audio_file)
        signal, sr = librosa.load(input_audio_path, sr=None)

        # plot_signal(signal, sr, title="Original Signal")

        trimmed_signal = trim_audio(signal, sr)
        # plot_signal(trimmed_signal, sr, title="Trimmed Signal")

        cleaned_signal = clean_audio(trimmed_signal)
        # plot_signal(cleaned_signal, sr, title="Cleaned Signal")

        preemphasized_signal = apply_preemphasis(cleaned_signal)
        # plot_signal(preemphasized_signal, sr, title="Pre-emphasized Signal")

        normalized_signal = normalize_audio(preemphasized_signal)
        # plot_signal(normalized_signal, sr, title="Normalized Signal")

        frames = segment_audio(normalized_signal)
        
        base_name, ext = os.path.splitext(audio_file)
        new_file_name = f"{base_name}_processed{ext}"
        output_audio_path = os.path.join(output_audio_dir, new_file_name)
        sf.write(output_audio_path, normalized_signal, sr)

        print(f"Processing {audio_file}:")
        print(f"Original Signal Shape: {signal.shape}")
        print(f"Cleaned Signal Shape: {cleaned_signal.shape}")
        print(f"Pre-emphasized Signal Shape: {preemphasized_signal.shape}")
        print(f"Normalized Signal Shape: {normalized_signal.shape}")
        print(f"Segmented Frames Shape: {frames.shape}")
        print(f"Preprocessed audio saved to {output_audio_path}")
        print('\n')

    play_audio(recorded_signal, recorded_sr)
# # Uncomment the following line to run the recording and processing
# merekam()

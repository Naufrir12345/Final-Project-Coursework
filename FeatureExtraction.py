import os
import numpy as np
import scipy.io.wavfile as wav
from scipy.fftpack import dct
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import sounddevice as sd
import pandas as pd
import librosa.display
import csv
# from preproAudio import merekam

def pre_emphasis(signal, alpha=0.97):
    emphasized_signal = np.append(signal[0], signal[1:] - alpha * signal[:-1])
    return emphasized_signal

def plot_waveform(signal, title="Waveform"):
    plt.figure(figsize=(10, 4))
    plt.plot(np.linspace(0, len(signal) / sampling_rate, num=len(signal)), signal)
    plt.title(title)
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.show()

def frame_audio(signal, frame_size, hop_size):
    num_samples = len(signal)
    num_frames = 1 + int(np.floor((num_samples - frame_size) / hop_size))
    frames = np.zeros((num_frames, frame_size))
    for i in range(num_frames):
        start = i * hop_size
        frames[i] = signal[start:start + frame_size]
    return frames

def apply_window(frames, window_type='hamming'):
    if window_type == 'hamming':
        window = np.hamming(len(frames[0]))
    elif window_type == 'hanning':
        window = np.hanning(len(frames[0]))
    elif window_type == 'blackman':
        window = np.blackman(len(frames[0]))
    else:
        raise ValueError("Unsupported window type. Supported types: 'hamming', 'hanning', 'blackman'")
    
    return frames * window

def filter_bank_spectrum(frames, filters, nfilt=40):
    filter_bank_output = np.zeros((len(frames), nfilt))
    for i in range(nfilt):
        filter_bank_output[:, i] = np.sum(frames * filters[i], axis=1)
    return filter_bank_output

def compute_mfcc_with_ceptrum(frames, sampling_rate, num_ceps=13, ceps_liftering=12):
    mfccs = librosa.feature.mfcc(S=librosa.power_to_db(np.abs(frames)), sr=sampling_rate, n_mfcc=num_ceps)
    cepstral_coefficents = dct(mfccs, axis=0, type=2, norm='ortho')
    lifter = 1 + (ceps_liftering / 2) * np.sin(np.pi * np.arange(1, num_ceps + 1) / ceps_liftering)
    liftered_ceps = cepstral_coefficents * lifter[:, np.newaxis]
    liftered_ceps_int = liftered_ceps.astype(np.int32)
    return liftered_ceps_int

def normalize_mfcc(mfcc_features):
    norm = np.linalg.norm(mfcc_features, axis=1, keepdims=True)
    normalized_mfcc = mfcc_features / norm
    return normalized_mfcc

def process_audio_file(file_path, output_folder, nfilt=40, frame_size=2800, hop_size=2400, num_ceps=13, ceps_liftering=12):
    sampling_rate, signal = wav.read(file_path)
    cepstrum_results = []

    output_file_path = os.path.join(output_folder, f"{os.path.basename(file_path)[:-4]}.wav")
    wav.write(output_file_path, sampling_rate, signal.astype(np.float32))
    print(f"Processed audio saved to: {output_file_path}")

    emphasized_signal = pre_emphasis(signal)
    audio_frames = frame_audio(emphasized_signal, frame_size, hop_size)
    window_type = 'hamming'
    windowed_frames = apply_window(audio_frames, window_type)
    fft_frames = np.fft.fft(windowed_frames, axis=1)
    selected_bins = 500
    sum_fft = np.sum(np.abs(fft_frames[:, :selected_bins]), axis=0)
    normalized_sum_fft = sum_fft / np.sum(sum_fft)
    df_sum_fft = pd.DataFrame(normalized_sum_fft, columns=["Magnitude Sum"])

    filters = np.zeros((nfilt, len(fft_frames[0])))
    mel_points = np.linspace(0, (sampling_rate / 2), nfilt + 2)
    mfccs = librosa.feature.mfcc(S=librosa.power_to_db(np.abs(fft_frames)), sr=sampling_rate, n_mfcc=13)
    
    for i in range(1, nfilt + 1):
        filters[i - 1] = np.interp(np.arange(len(fft_frames[0])), ((mel_points[i - 1], mel_points[i], mel_points[i + 1])), (0, 1, 0))

    filter_bank_output = filter_bank_spectrum(fft_frames, filters, nfilt)
    cepstrum_result = compute_mfcc_with_ceptrum(filter_bank_output.T, sampling_rate, num_ceps=num_ceps, ceps_liftering=ceps_liftering)
    normalized_cepstrum_result = normalize_mfcc(cepstrum_result)
    cepstrum_results.append((os.path.basename(file_path), normalized_cepstrum_result))

    output_emphasis_path = os.path.join(output_folder, 'process emphasis', os.path.basename(file_path))
    output_windowed_path = os.path.join(output_folder, 'process windowed', f"{os.path.basename(file_path)[:-4]}_PE_framed_windowed.wav")
    output_fft_path = os.path.join(output_folder, 'process fft', f"{os.path.basename(file_path)[:-4]}_PE_framed_windowed_fft.wav")
    
    if not os.path.exists(os.path.join(output_folder, 'process emphasis')):
        os.makedirs(os.path.join(output_folder, 'process emphasis'))
    if not os.path.exists(os.path.join(output_folder, 'process windowed')):
        os.makedirs(os.path.join(output_folder, 'process windowed'))
    if not os.path.exists(os.path.join(output_folder, 'process fft')):
        os.makedirs(os.path.join(output_folder, 'process fft'))

    wav.write(output_emphasis_path, sampling_rate, emphasized_signal.astype(np.float32))
    wav.write(output_windowed_path, sampling_rate, windowed_frames.flatten().astype(np.float32))
    wav.write(output_fft_path, sampling_rate, np.abs(fft_frames).flatten().astype(np.float32))

    # plt.figure(figsize=(14, 6))
    # plt.subplot(311)
    # plt.plot(np.linspace(0, len(signal) / sampling_rate, num=len(signal)), signal, label='Original Signal')
    # plt.title("Original Signal")
    # plt.xlabel("Time (s)")
    # plt.ylabel("Amplitude")
    # plt.legend()

    # plt.subplot(312)
    # plt.plot(np.linspace(0, len(emphasized_signal) / sampling_rate, num=len(emphasized_signal)), emphasized_signal, label='Pre-emphasized Signal', color='orange')
    # plt.title("Pre-emphasized Signal")
    # plt.xlabel("Time (s)")
    # plt.ylabel("Amplitude")
    # plt.legend()

    # plt.subplot(313)
    # plt.plot(np.linspace(0, len(signal) / sampling_rate, num=len(signal)), signal, label='Original Signal')
    # plt.plot(np.linspace(0, len(emphasized_signal) / sampling_rate, num=len(emphasized_signal)), emphasized_signal, label='Pre-emphasized Signal', color='orange')
    # plt.title("Original vs Pre-emphasized Signal")
    # plt.xlabel("Time (s)")
    # plt.ylabel("Amplitude")
    # plt.legend()
    # plt.show()

    # print("Playing original audio...")
    # sd.play(signal, samplerate=sampling_rate)
    # sd.wait()

    # plt.figure(figsize=(10, 4))
    # for i in range(len(audio_frames)):
    #     plt.plot(np.linspace(0, frame_size / sampling_rate, num=frame_size), audio_frames[i], label=f"Frame {i+1}")

    # plt.title("Audio Frames")
    # plt.xlabel("Time (s)")
    # plt.ylabel("Amplitude")
    # plt.legend()
    # plt.show()

    # plt.figure(figsize=(10, 4))
    # for i in range(len(windowed_frames)):
    #     plt.plot(np.linspace(0, frame_size / sampling_rate, num=frame_size), windowed_frames[i], label=f"Frame {i+1}")
    # plt.title("Windowed Frames")
    # plt.xlabel("Time (s)")
    # plt.ylabel("Amplitude")
    # plt.legend()
    # plt.show()

    # plt.figure(figsize=(10, 4))
    # for i in range(min(5, len(fft_frames))):
    #     plt.plot(np.abs(fft_frames[i]), label=f"Frame {i+1}")

    # plt.title("FFT of Windowed Frames")
    # plt.xlabel("Frequency Bin")
    # plt.ylabel("Magnitude")
    # plt.legend()
    # plt.show()

    # plt.imshow(filter_bank_output.T, aspect='auto', cmap='viridis', origin='lower', extent=[0, len(emphasized_signal), 0, nfilt])
    # plt.title("Filter Bank Output")
    # plt.xlabel("Time (samples)")
    # plt.ylabel("Filter Index")
    # plt.show()

    # plt.imshow(cepstrum_result, aspect='auto', cmap='viridis', origin='lower', extent=[0, len(emphasized_signal), 0, num_ceps])
    # plt.title("Cepstrum Output")
    # plt.xlabel("Time (samples)")
    # plt.ylabel("Cepstrum Coefficient")
    # plt.show()

    # print(f"Pre-emphasized audio saved to: {output_emphasis_path}")
    # print(f"Windowed frames audio saved to: {output_windowed_path}")
    # print(f"FFT frames audio saved to: {output_fft_path}")
    print(f"Shape of framed signal: {audio_frames.shape}")
    print(f"Number of frames: {audio_frames.shape[0]}")
    print(f"FFT Result :{df_sum_fft}")
    print(f"MFCCs Array :", mfccs)
    print(f"Ceptrum Result :", cepstrum_result)

    max_value = np.max(cepstrum_result)
    max_index = np.argmax(cepstrum_result)
    row_index, col_index = np.unravel_index(max_index, np.shape(cepstrum_result))
    print("Nilai maksimum:", max_value)
    print("Indeks nilai maksimum:", max_index)
    print("Posisi nilai maksimum (baris, kolom):", row_index, col_index)
    print("Nilai maksimum di posisi tersebut:", cepstrum_result[row_index][col_index])

    return cepstrum_results

def process_audio_folder(input_folder, output_folder, nfilt=40, frame_size=2800, hop_size=2400, num_ceps=13, ceps_liftering=12):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    audio_files = [os.path.join(input_folder, file) for file in os.listdir(input_folder) if file.endswith('.wav')]
    all_cepstrum_results = []
    for idx, audio_file in enumerate(audio_files):
        print(f"Processing file: {audio_file}")
        cepstrum_results = process_audio_file(audio_file, output_folder, nfilt, frame_size, hop_size, num_ceps, ceps_liftering)
        all_cepstrum_results.extend(cepstrum_results)
    save_all_cepstrum_to_csv(all_cepstrum_results, output_folder)

def save_all_cepstrum_to_csv(cepstrum_results, output_folder):
    all_rows = []
    max_cepstrum_length = max(len(cepstrum_array.flatten()) for _, cepstrum_array in cepstrum_results)
    
    for file_name, cepstrum_array in cepstrum_results:
        max_value = np.max(cepstrum_array)
        max_index = np.argmax(cepstrum_array)
        row_index, col_index = np.unravel_index(max_index, cepstrum_array.shape)

        max_position = f"({row_index}, {col_index})"

        flattened_cepstrum = cepstrum_array.flatten()
        # Fill missing values with 0 to make all rows have the same length
        filled_cepstrum = np.pad(flattened_cepstrum, (0, max_cepstrum_length - len(flattened_cepstrum)), mode='constant', constant_values=0)

        row_values = [file_name, max_value, max_position] + list(filled_cepstrum)
        all_rows.append(row_values)
 
    column_names = ["File_Name", "Max_Value", "Max_Position"] + [f"mfcc_{i+1}" for i in range(max_cepstrum_length)]
    cepstrum_df = pd.DataFrame(all_rows, columns=column_names)
    output_csv_path = os.path.join(output_folder, "dataCoba.csv")
    cepstrum_df.to_csv(output_csv_path, index=False)
    print(f"All cepstrum results saved to: {output_csv_path}")



# if __name__ == "__main__":
# #     # input_folder = '../MainDataset/preproAudio/'
# #     # output_folder = '../afterLearning/'

# #     # input_folder = '../MainDataset/datacoba/'
# #     # output_folder = '../audio/'
# #     # merekam()
#     input_folder = "C:\\Users\\kurni\\Downloads\\oping\\coba-coba\\datasetRecap\\afterAudioCut\\untukmatinyala"
#     output_folder = "C:\\Users\\kurni\\Downloads\\oping\\coba-coba\\datasetRecap\\dataGenerate\\untukmatinyala"
# #     # Process audio files in the input folder
#     process_audio_folder(input_folder, output_folder, nfilt=40, frame_size=2800, hop_size=2400, num_ceps=13, ceps_liftering=12)

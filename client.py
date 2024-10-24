import grpc
import wave
import pyaudio
import keyboard
import speech_pb2, speech_pb2_grpc
import os

# Koneksi gRPC ke server STT dan TTS
channel = grpc.insecure_channel('localhost:50051')
stub = speech_pb2_grpc.SpeechServiceStub(channel)

# Pengaturan pyaudio untuk perekaman audio
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

def record_audio(output_file_path):
    audio = pyaudio.PyAudio()
    
    # Buka stream audio
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    print("Tekan spasi untuk mulai merekam...")
    keyboard.wait('space')  # Tunggu penekanan spasi untuk memulai rekaman
    print("Mulai merekam...")

    frames = []
    
    # Merekam sampai spasi dilepas
    while True:
        data = stream.read(CHUNK)
        frames.append(data)
        # Cek jika tombol spasi tidak ditekan lagi (dilepas)
        if not keyboard.is_pressed('space'):
            print("Rekaman selesai.")
            break

    # Tutup stream dan terminasi pyaudio
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Simpan ke file WAV
    with wave.open(output_file_path, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    print(f"Audio disimpan di {output_file_path}")

def speech_to_text():
    audio_file_path = 'C:/Users/Daffa Nur Fiat/OneDrive/Documents/UNITY/test2/input-source/input_audio.wav'
    record_audio(audio_file_path)

    # Buka file audio yang direkam
    with open(audio_file_path, 'rb') as f:
        audio_data = f.read()

    # Kirim data audio ke server gRPC untuk transkripsi
    response = stub.Listen(speech_pb2.STTRequest(audio_data=audio_data))
    
    # Kembalikan hasil transkripsi
    print(f"Hasil transkripsi: {response.text}")

def text_to_speech(text):
    # Mengirimkan teks ke server untuk sintesis suara
    response = stub.ConvertToWav(speech_pb2.TTSRequest(text=text))
    
    # Simpan audio ke file WAV
    output_wav_path = 'C:/Users/Daffa Nur Fiat/OneDrive/Documents/UNITY/test2/output/output_audio.wav'
    with open(output_wav_path, 'wb') as f:
        f.write(response.audio_data)
    
    print(f"Audio TTS disimpan di {output_wav_path}")

if __name__ == '__main__':
    try:
        while True:
            print("1. Speech to Text")
            print("2. Text to Speech")
            print("3. Keluar")
            choice = input("Pilih opsi: ")

            if choice == '1':
                speech_to_text()
            elif choice == '2':
                text_input = input("Masukkan teks untuk diubah menjadi suara: ")
                text_to_speech(text_input)
            elif choice == '3':
                print("Keluar dari program.")
                break
            else:
                print("Pilihan tidak valid, silakan coba lagi.")
    except KeyboardInterrupt:
        print("\nProgram dihentikan oleh pengguna.")

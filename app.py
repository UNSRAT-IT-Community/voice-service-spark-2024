import os
import grpc
import wave
import pyaudio
from flask import Flask, request, send_file, jsonify
import speech_pb2, speech_pb2_grpc
import tempfile
import edge_tts
import asyncio
import keyboard

app = Flask(__name__)

# Folder untuk menyimpan file input dan output
SOURCE_INPUT_FOLDER = 'C:/Users/Daffa Nur Fiat/OneDrive/Documents/UNITY/test2/input-source'
OUTPUT_FOLDER = 'C:/Users/Daffa Nur Fiat/OneDrive/Documents/UNITY/test2/output'
os.makedirs(SOURCE_INPUT_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

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
    print("Mulai merekam, tekan spasi lagi untuk berhenti...")
    frames = []

    # Mulai merekam sampai tombol spasi ditekan lagi
    while True:
        data = stream.read(CHUNK)
        frames.append(data)
        if keyboard.is_pressed('space'):
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

# Fungsi TTS (Text-to-Speech) secara sinkron
def synthesize_speech_sync(text, voice):
    communicate = edge_tts.Communicate(text, voice)
    
    # Simpan TTS output langsung ke WAV
    output_wav_path = os.path.join(OUTPUT_FOLDER, 'output_audio.wav')
    asyncio.run(communicate.save(output_wav_path))
    
    print(f"File WAV disimpan di: {output_wav_path}")
    
    return output_wav_path

# Endpoint untuk STT (Speech-to-Text)
@app.route('/stt', methods=['POST'])
def speech_to_text():
    # Path untuk file audio yang direkam melalui STT
    audio_file_path = os.path.join(SOURCE_INPUT_FOLDER, 'input_audio.wav')

    print("Tekan spasi untuk mulai merekam...")
    keyboard.wait('space')  # Tunggu penekanan spasi untuk memulai rekaman
    record_audio(audio_file_path)

    # Buka file audio yang direkam
    with open(audio_file_path, 'rb') as f:
        audio_data = f.read()

    # Kirim data audio ke server gRPC untuk transkripsi
    response = stub.Listen(speech_pb2.STTRequest(audio_data=audio_data))
    
    # Kembalikan hasil transkripsi sebagai JSON
    return jsonify({'text': response.text})

# Endpoint untuk TTS (Text-to-Speech)
@app.route('/tts', methods=['POST'])
def text_to_speech():
    # Ambil teks input dari parameter kueri
    text = request.args.get('text', '')
    
    # Sintesis suara secara sinkron
    try:
        output_wav_path = synthesize_speech_sync(text, 'id-ID-ArdiNeural')
    except ValueError as e:
        return {'error': str(e)}, 500

    # Kirim file WAV sebagai respons untuk diunduh
    return send_file(output_wav_path, mimetype="audio/wav", as_attachment=True, download_name="response.wav")

# Menjalankan server Flask
if __name__ == '__main__':
    app.run(debug=True)

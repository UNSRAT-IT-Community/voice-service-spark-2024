import grpc
from concurrent import futures
import speech_pb2, speech_pb2_grpc
import speech_recognition as sr
import keyboard
import os
import time
import edge_tts
import asyncio

# Konfigurasi suara untuk TTS
VOICES = ['id-ID-ArdiNeural', 'id-ID-GadisNeural']
VOICE = VOICES[0]

# gRPC service untuk STT dan TTS
class SpeechService(speech_pb2_grpc.SpeechServiceServicer):
    # STT (Speech to Text)
    def Listen(self, request, context):
        # Path ke file WAV yang sudah disimpan
        input_wav_path = './input-source/input_audio.wav'
        
        # Baca audio dari file WAV
        with open(input_wav_path, 'rb') as f:
            audio_data = f.read()

        # Buat recognizer
        recognizer = sr.Recognizer()
        audio_file = sr.AudioFile(input_wav_path)

        with audio_file as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.record(source)

            try:
                text = recognizer.recognize_google(audio, language="id-ID")
                print(f"Anda mengatakan: {text}")
                return speech_pb2.STTResponse(text=text.encode('utf-8'))  # Mengembalikan hasil transkripsi sebagai bytes
            except sr.UnknownValueError:
                return speech_pb2.STTResponse(text="Audio tidak bisa dikenali".encode('utf-8'))
            except sr.RequestError:
                return speech_pb2.STTResponse(text="Terjadi kesalahan pada request".encode('utf-8'))

    # TTS (Text to Speech)
    async def synthesize_speech(self, text, voice):
        communicate = edge_tts.Communicate(text, voice)
        temp_wav_path = './output/output_audio.wav'
        await communicate.save(temp_wav_path)
        return temp_wav_path

    def ConvertToWav(self, request, context):
        text = request.text

        # Konversi teks ke audio (TTS)
        temp_wav_path = asyncio.run(self.synthesize_speech(text, VOICE))

        # Print file type (extension)
        file_extension = os.path.splitext(temp_wav_path)[1]
        print(f"Tipe file audio: {file_extension}")

        # Kembalikan file WAV sebagai bytes
        with open(temp_wav_path, 'rb') as f:
            wav_data = f.read()

        return speech_pb2.TTSResponse(audio_data=wav_data)

# Menjalankan server gRPC
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    speech_pb2_grpc.add_SpeechServiceServicer_to_server(SpeechService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC Server berjalan pada port 50051")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()

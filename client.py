import grpc
import speech_pb2, speech_pb2_grpc

# Koneksi gRPC ke server STT dan TTS
channel = grpc.insecure_channel('localhost:50051')
stub = speech_pb2_grpc.SpeechServiceStub(channel)

def speech_to_text():
    # Path ke file audio yang ingin diubah menjadi teks
    audio_file_path = './input-source/input_audio.wav'

    # Baca file audio yang ada
    with open(audio_file_path, 'rb') as f:
        audio_data = f.read()

    # Kirim data audio ke server gRPC untuk transkripsi
    response = stub.Listen(speech_pb2.STTRequest(audio_data=audio_data))
    
    # Kembalikan hasil transkripsi
    print(f"Hasil transkripsi: {response.text}")

def text_to_speech(text):
    # Mengirimkan teks ke server untuk sintesis suara
    response = stub.ConvertToWav(speech_pb2.TTSRequest(text=text.encode('utf-8')))
    
    # Simpan audio ke file WAV
    output_wav_path = './output/output_audio.wav'
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

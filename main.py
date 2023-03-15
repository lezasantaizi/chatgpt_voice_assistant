import pvporcupine
import os
import pyaudio
import struct
from pyaudio import PyAudio
import openai
import time 
import wave
import pvcobra

porcupine = pvporcupine.create(access_key='mKByxcjpUVaAtWV/JsM5zmJqZDBSxcn2kCQqd2ycXL/r+vLhcD+OFg==',keywords=['ok google'])
cobra = pvcobra.create(access_key='mKByxcjpUVaAtWV/JsM5zmJqZDBSxcn2kCQqd2ycXL/r+vLhcD+OFg==')
openai.api_key = ""

def chatgpt_api(message):
    messages = []
    # message = input("")
    messages.append({"role":"user","content": message})

    response=openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=messages
    )
    reply = response["choices"][0]["message"]["content"]
    return reply

def wake():
    pa = pyaudio.PyAudio()
    audio_stream = pa.open(
                        rate=porcupine.sample_rate,
                        channels=1,
                        format=pyaudio.paInt16,
                        input=True,
                        frames_per_buffer=porcupine.frame_length)
    # recording = False
    # silence_count = 0
    # buffer = []
    while True:
        pcm = audio_stream.read(porcupine.frame_length)
        _pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
        keyword_index = porcupine.process(_pcm)
        if keyword_index >= 0:
            print("wake !!")
            break
    audio_stream.stop_stream()
    audio_stream.close()
    pa.terminate()

def record_audio(wave_out_path):
    p = pyaudio.PyAudio()  
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=porcupine.sample_rate,
                    input=True,
                    frames_per_buffer=porcupine.frame_length)  
    wf = wave.open(wave_out_path, 'wb')  
    wf.setnchannels(1) 
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16,)) 
    wf.setframerate(porcupine.sample_rate)  

    # vad
    pcm = stream.read(porcupine.frame_length)
    _pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
    is_voiced = cobra.process(_pcm)  # 表示人声检测

    silence_count = 0
    while is_voiced:
      silence_count = 0 if is_voiced > 0.5 else silence_count + 1
      if silence_count <= 50:
          if silence_count < 10:
              wf.writeframes(pcm)
      else:
        break

      pcm = stream.read(porcupine.frame_length)
      _pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
      is_voiced = cobra.process(_pcm)
    p.terminate()
    wf.close()
    print('Finished recording')

def whisper_api(wav_path):
    file = open(wav_path, "rb")
    transcription = openai.Audio.transcribe("whisper-1", file)
    return(transcription["text"])

def main(): 
    while True:
      wake()
      print("start record")
      wav_path = "/Users/xiaoming/Downloads/hello.wav"
      record_audio(wav_path)
      print("start whisper_api")
      message = whisper_api(wav_path)
      print(message)
      reply = chatgpt_api(message)
      print(reply)
    
if __name__ == '__main__':
    main()




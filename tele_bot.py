# -*- coding: utf-8 -*-
"""
a private voice chat bot

"""

import requests
import json

labs_url = 'https://api.elevenlabs.io/v1/text-to-speech/EXAVITQu4vr4xnSDxMaL'
labs_headers = {
    'accept': 'audio/mpeg',
    'xi-api-key': 'fc1ec64b81f741204450cb34299d945b',
    'Content-Type': 'application/json'
}


import telebot
BOT_TOKEN = '6145204806:AAEq03B3lasUHxvNE-Bj35U6yEHB4_0VYT0'
import openai
openai.api_key = "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"


from urllib.request import urlretrieve
import os
from pydub import AudioSegment



bot = telebot.TeleBot(BOT_TOKEN)

# 打招呼
@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Hello, I am Theodus, how are you doing?")
    
# 回答所有问题 （仅限文本，不含表情）
@bot.message_handler(content_types=['text',])
def echo_all_text(message):
    bot.reply_to(message, chat_gpt(message.text))
    #return chat_gpt(message.text)

    
# 回答所有问题 （仅限语音，不含视频）
@bot.message_handler(content_types=['voice',])
def echo_all_voice(message):
    
    '''Download ogg file'''
    file_info = bot.get_file(message.voice.file_id)
    file_url = f'https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}'
    file_name = f'{message.chat.id}.ogg'
    urlretrieve(file_url, file_name)
    
    # Convert the file from OGG to WAV using PyDub
    audio = AudioSegment.from_file(file_name, format="ogg")
    audio.export(file_name.replace(".ogg", ".mp3"), format="mp3")

    '''voice to text by whisper'''
    input_text = whisper(file_name.replace(".ogg", ".mp3"))

    
    '''remove question voice'''
    os.remove(file_name)
    os.remove(file_name.replace(".ogg", ".mp3"))
    
    '''text to text chat by chatgpt'''
    ans_text = chat_gpt(input_text)
    
    '''answer text to voice by 11labs'''
    text_voice(ans_text) #写入磁盘，是否必要？

    voice_back = open('temp.mp3', 'rb')
    """Send a voice message to the user"""
    bot.send_voice(chat_id=message.chat.id, voice=voice_back)
  



# 文字回复文字
def chat_gpt(prompt):
    # 你的问题
    prompt = prompt
    
    # 调用 ChatGPT 接口
    model_engine = "text-davinci-003"
    completion = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=1, #随机性
    )

    response = completion.choices[0].text
    return response
    #print(response)



#语音转文字
def whisper(file):
    audio_file= open(file, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript["text"]


# 文字转语音
def text_voice(text):
    data = {
        "text": text,
        "voice_settings": {
            "stability": 0,
            "similarity_boost": 0
        }
    }
    
    response = requests.post(labs_url, headers=labs_headers, data=json.dumps(data))
    with open('temp.mp3', 'wb') as f:
        f.write(response.content)



bot.infinity_polling()




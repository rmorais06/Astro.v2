import speech_recognition as sr
import os
from gtts import gTTS
import random
import webbrowser
import pyttsx3
import playsound
import google.generativeai as genai

# Substitua pela sua chave da API Gemini
gemini_api_key = 'SUA CHAVE API'

genai.configure(api_key=gemini_api_key)

generative_model = genai.GenerativeModel('gemini-pro')

class VirtualAssist:
    def __init__(self, assist_name, person):
        self.person = person
        self.assist_name = assist_name

        self.engine = pyttsx3.init()
        self.r = sr.Recognizer()

        self.voice_data = ''

    def engine_speak(self, audio_string):
        audio_string = str(audio_string)
        tts = gTTS(text=audio_string, lang='pt')
        r = random.randint(1, 20000)
        audio_file = 'audio' + str(r) + '.mp3'
        tts.save(audio_file)
        playsound.playsound(audio_file)
        print(self.assist_name + ':', audio_string)
        os.remove(audio_file)

    def record_audio(self, ask=''):
        with sr.Microphone() as source:
            if ask:
                self.engine_speak(ask)
            print('Gravando...')
            audio = self.r.listen(source, 5, 5)
            print('Analisando...')
            try:
                self.voice_data = self.r.recognize_google(audio, language='pt-BR')
                print('Você disse:', self.voice_data)
            except sr.UnknownValueError:
                self.engine_speak(f'Desculpe {self.person}, não entendi. Pode repetir?')
            except sr.RequestError:
                self.engine_speak('Erro ao acessar o serviço de reconhecimento.')

            self.voice_data = self.voice_data.lower()
            return self.voice_data

    def there_exist(self, terms):
        for term in terms:
            if term in self.voice_data:
                return True
        return False

    def ia_response(self, prompt):
        try:
            response = generative_model.generate_content(
                [{"role": "user", "parts": [prompt]}]
            )
            reply = response.text
            return reply.strip()
        except Exception as e:
            print(f"Erro ao obter resposta da IA: {e}")
            return "Desculpe, não consegui acessar minha base de conhecimento no momento."

    def respond(self, voice_data):
        if self.there_exist(['oi', 'olá', 'bom dia', 'boa noite', 'boa tarde']):
            cumprimentos = [
                f'Oi, {self.person}, o que temos para hoje?',
                'Oi, humano, como posso ajudar?',
                'Olá, terráqueo, do que você precisa?'
            ]
            cumprimento = random.choice(cumprimentos)
            self.engine_speak(cumprimento)

        elif self.there_exist(['procure por']) and 'youtube' not in voice_data:
            search_term = voice_data.split('por')[-1].strip()
            url = 'http://google.com/search?q=' + search_term
            webbrowser.get().open(url)
            self.engine_speak('Aqui está o que encontrei sobre ' + search_term + ' no Google.')

        elif self.there_exist(['procure no youtube']):
            search_term = voice_data.split('youtube')[-2].strip()
            url = 'http://www.youtube.com/results?search_query=' + search_term
            webbrowser.get().open(url)
            self.engine_speak('Aqui está o que encontrei sobre ' + search_term + ' no YouTube.')

        elif self.there_exist(['tchau', 'adeus', 'até logo']):
            self.engine_speak('Até mais, terráqueo.')
            exit()

        else:
            # Chamando a IA do Google para responder perguntas gerais
            resposta_ia = self.ia_response(voice_data)
            self.engine_speak(resposta_ia)

# Loop principal
if __name__ == '__main__':
    assistente = VirtualAssist('Astro', 'INSIRA UM NOME')
    while True:
        voice_data = assistente.record_audio('Estou ouvindo...')
        assistente.respond(voice_data)
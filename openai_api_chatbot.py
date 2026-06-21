print('### LOADING CREDENTIALS ###')
from dotenv import load_dotenv
import os

from Assistant.research_mode import ResearchAssistant

load_dotenv()

if len(os.getenv('OPENAI_API_KEY', '')) == 0:
    print('openai API key not detected in .env')
    raise Exception("[$] openai API key is required. Learn more at https://platform.openai.com/account/api-keys")

if len(os.getenv('IBM_API_KEY', '')) == 0: print('[free] IBM cloud API Key not detected in .env\nLearn more at: https://cloud.ibm.com/catalog/services/text-to-speech')

if len(os.getenv('IBM_TTS_SERVICE', '')) == 0: print('[free] IBM cloud TTS service not detected in .env\nLearn more at: https://cloud.ibm.com/catalog/services/text-to-speech')

# RAPHAEL is the target assistant identity. Porcupine may require a custom
# keyword model for non-built-in wake words, so the runtime falls back to the
# passive listener if Porcupine cannot initialize the configured keyword.
ASSISTANT_NAME = os.getenv('RAPHAEL_ASSISTANT_NAME', 'RAPHAEL')
WAKE_KEYWORDS = [kw.strip().lower() for kw in os.getenv('RAPHAEL_WAKE_KEYWORDS', 'raphael').split(',') if kw.strip()]

use_porcupine = True
if len(os.getenv('PORCUPINE_KEY', '')) == 0:
    print('[free] PicoVoice not detected in .env\nLearn more at: https://picovoice.ai/platform/porcupine/')
    use_porcupine = False


print('DONE\n')

print('### IMPORTING DEPENDANCIES ###')
import pygame

from Assistant import get_audio as myaudio
from Assistant.RaphaelAssistant import RaphaelAssistant
from Assistant.tools import count_tokens

print('DONE\n')

### MAIN
if __name__=="__main__":
    print("### SETTING UP ENVIROMENT ###")
    OFFLINE = False
    pygame.mixer.init()

    # INITIATE RAPHAEL
    print(f'initiating {ASSISTANT_NAME} voice...')
    raphael = RaphaelAssistant(
        openai_api   = os.getenv('OPENAI_API_KEY'),
        ibm_api      = os.getenv('IBM_API_KEY'),
        ibm_url      = os.getenv('IBM_TTS_SERVICE'),
        elevenlabs_api = os.getenv('ELEVENLABS_API_KEY'),
        elevenlabs_voice = 'Antoni',
        # Keep the existing voice sample for now to avoid breaking the repaired baseline.
        # The extraction phase can replace this with a RAPHAEL-specific voice asset.
        voice_id     = {'en':'jarvis_en'},
        whisper_size = 'medium',
        awake_with_keywords=WAKE_KEYWORDS,
        model= "gpt-3.5-turbo",
        embed_model= "text-embedding-ada-002",
        RESPONSE_TIME = 3,
        SLEEP_DELAY = 30,
        mode = 'CHAT'
        )

    while True:
        if not(raphael.is_awake):
            print(f'\n awaiting {ASSISTANT_NAME} wake word: {", ".join(WAKE_KEYWORDS)}...')

            # Block until the wakeword is heard. If Porcupine cannot use the
            # configured RAPHAEL keyword, fall back to passive speech recognition.
            if use_porcupine:
                try:
                    raphael.block_until_wakeword()
                except Exception as e:
                    print(f'Porcupine wake word failed for {WAKE_KEYWORDS}: {e}')
                    print('falling back to passive RAPHAEL listener...')
                    use_porcupine = False
            if not use_porcupine:
                while not(raphael.is_awake):
                    raphael.listen_passively()
        
        raphael.record_to_file('output.wav')
        

        if raphael.is_awake:
            prompt, detected_language = myaudio.whisper_wav_to_text('output.wav', raphael.interpreter, prior=raphael.languages.keys())

            # check exit command
            if "THANKS" in prompt.upper() or len(prompt.split())<=1:
                raphael.go_to_sleep()
                continue
            
            if detected_language=='en':
                VoiceIdx = 'jarvis'
            else:
                VoiceIdx = detected_language
            
            raphael.expand_conversation(role="user", content=prompt)

            # PROMPT MANAGING [BETA]
            flag = raphael.analyze_prompt(prompt)

            # redirect the conversation to an action manager or to the LLM
            if (("1" in flag or "tool" in flag) and '-' not in flag):
                print('(thought): action')
                response = raphael.use_tools(prompt)
                response = response
            
            elif "2" in flag or "respond" in flag:
                print('(thought): response')
                response = raphael.get_answer(prompt)
            elif "-1" in flag:
                response = raphael.switch_mode()
            else:
                print('(thought): internet')
                response = raphael.secondary_agent(prompt)

            raphael.expand_conversation(role='assistant', content=response)
            pygame.mixer.stop()
            raphael.say(response, VoiceIdx=VoiceIdx, IBM=True)

            print('\n')

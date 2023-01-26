import asyncio
import time
from pygame import mixer
import pyttsx3
import os
import re
import random
import signal
import openai
import speech_recognition as sr

from viam.components.servo import Servo
from viam.robot.client import RobotClient
from viam.services.vision import VisionServiceClient
from viam.rpc.dial import Credentials, DialOptions

viam_secret = os.getenv('VIAM_SECRET')
viam_address = os.getenv('VIAM_ADDRESS')
openai.organization = os.getenv('OPENAPI_ORG')
openai.api_key = os.getenv('OPENAPI_KEY')

vision_confidence = .4
completion_types = ['expression', 'question', 'something']
robot_command_prefix = "hey robot"
char_command = "act like"
observe_list = ["what are you thinking", "what do you think", "what do you see", "whats thats"]
char_list = ["yoda", 'c-3po', "c3po", "darth vader", "homer simpson", "tony soprano"]

mixer.init(devicename = 'Built-in Audio Analog Stereo (2)')
robot = ''
current_char = ""

async def connect():
    creds = Credentials(
        type='robot-location-secret',
        payload=viam_secret)
    opts = RobotClient.Options(
        refresh_interval=0,
        dial_options=DialOptions(credentials=creds)
    )
    return await RobotClient.at_address(viam_address, opts)

async def say(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 140)
    engine.save_to_file(text, "test.mp3")
    engine.runAndWait()

    time.sleep(1)

    try:
        mixer.music.load("test.mp3") 
        mixer.music.play() # Play it

        while mixer.music.get_busy():  # wait for music to finish playing
            time.sleep(1)
    except RuntimeError:
        await say("nevermind")

    os.remove("test.mp3")

async def make_something_up(seen):
    tones = ['angry', 'happy', 'sad']
    prefix = {'angry': ['Damn, is that a', 'Damn, I see a', 'Shoot, its a'], 
        'happy': ['Well look, its a', "Yes! I see a", "Yay, its a"], 'sad': ['Oh no, its a', 'I fear I see a', 'Sadly, I think thats a']}
    
    chosen_tone = random.choice(tones)
    command = "say a short " + chosen_tone + " " + random.choice(completion_types) + " about a " + ' and a '.join(seen)
    if (current_char != ""):
        command = command + " in the style of " + current_char
    print(command)
    await move_servo(chosen_tone)
    await say(random.choice(prefix[chosen_tone]) + " " + ' and a '.join(seen))
    resp = await ai_command(command)
    resp = re.sub('Q:',  'Question: ', resp)
    resp = re.sub('A:',  'Answer: ', resp)
    await say(resp)

async def ai_command(command):
    try:
        completion = openai.Completion.create(engine="text-davinci-003", max_tokens=1024, prompt=command)
        print(completion)
        return completion.choices[0].text
    except openai.error.ServiceUnavailableError:
        errors = ["Sorry, I am feeling tired", "Sorry, I had a brain fart", "Never mind, I don't know"]
        return random.choice(errors)

async def move_servo(pos):
    pos_angle = {
                1: 4,
                2: 37,
                3: 71,
                "angry": 106,
                "happy": 173,
                "sad": 138
            }
    service = Servo.from_robot(robot, 'servo1')
    await service.move(angle=pos_angle[pos])

async def see_something():
    service = VisionServiceClient.from_robot(robot, 'vision')
    found = False
    while not found:
        # if you are using a detection model instead of classifier...
        #detections = await service.get_detections_from_camera(camera_name='cam', detector_name='stuff_detector')
        detections = await service.get_classifications_from_camera(camera_name='cam', classifier_name='stuff_detector', count=1)
        for d in detections:
            if d.confidence > vision_confidence:
                print(detections)
                if d.class_name != '???':
                    found = True
                    await make_something_up([d.class_name])


async def sig_handler():
    print("exiting...")
    try:
        await robot.close()
    except:
        exit

async def main():
    global robot
    robot = await connect()
    loop = asyncio.get_event_loop()
    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, signame),lambda: asyncio.create_task(sig_handler()))

    r = sr.Recognizer()
    m = sr.Microphone()
    while True:
        with m as source:
            r.adjust_for_ambient_noise(source) 
            audio = r.listen(source)
        try:
            transcript = r.recognize_google(audio_data=audio, show_all=True)
            if type(transcript) is dict and transcript.get("alternative"):
                text = transcript["alternative"][0]["transcript"].lower()
                print(text)
                if re.search("^" + robot_command_prefix, text):
                    command = re.sub(robot_command_prefix + "\s+",  '', text)
                    print(command)
                    if re.search("^" + '|'.join(observe_list), command):
                        await see_something()
                    elif re.search("^" + char_command +" (" + '|'.join(char_list) + ")", command):
                        global current_char
                        current_char = re.sub(char_command, "", command)
                        await say("OK, I am " + current_char)

        except sr.UnknownValueError:
            print("Speech recognition could not understand audio")
        except Exception as e:
            print(e)

        
    #service = VisionServiceClient.from_robot(robot, 'vision')
   
    #seen = {}
    #target_seen = random.randint(1, 3)
    #while True:
        #detections = await service.get_detections_from_camera(camera_name='cam', detector_name='stuff_detector')
    #    detections = await service.get_classifications_from_camera(camera_name='cam', classifier_name='stuff_detector', count=1)

     #   for d in detections:
     #       if d.confidence > vision_confidence:
     #           print(detections)
     #           if d.class_name != '???':
     #               if seen.get(d.class_name) == None:
     #                   seen[d.class_name] = True
     #                   seen_count = len(seen)
     #                   await move_servo(seen_count)
     #                   print(d.class_name)
     #                   prefix = ['I see a', 'Oh, there is a', 'Look, a', 'Oh snap, a', 'I spy a']
     #                   await say(random.choice(prefix) + " " + d.class_name)
     #                   if seen_count == target_seen:
     #                       await make_something_up(seen)
     #                       seen = {}
     #                       target_seen = random.randint(1, 3)
     #   time.sleep(.05)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except:
        exit
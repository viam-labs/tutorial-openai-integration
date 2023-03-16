import asyncio
import time
from pygame import mixer
import pygame._sdl2 as sdl2
from gtts import gTTS
import os
import re
import random
import signal
import openai
import speech_recognition as sr
import params

from viam.components.servo import Servo
from viam.components.base import Base
from viam.robot.client import RobotClient
from viam.services.vision import VisionServiceClient
from viam.rpc.dial import Credentials, DialOptions

openai.organization = params.openai_organization
openai.api_key = params.openai_api_key

# if you want to specify a specific device, you can pass devicename = params.mixer_device
# see https://pypi.org/project/SpeechRecognition/ for troubleshooting tips
mixer.init()
robot = ''
current_char = ""
current_mood = ""
current_person_name = ""

async def connect():
    creds = Credentials(
        type='robot-location-secret',
        payload=params.viam_secret)
    opts = RobotClient.Options(
        refresh_interval=0,
        dial_options=DialOptions(credentials=creds)
    )
    return await RobotClient.at_address(params.viam_address, opts)

async def say(text):
    myobj = gTTS(text=text, lang='en', slow=False)
    myobj.save("test.mp3")

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
    prefix = {'angry': ['Really? Is that a', 'No! I see a', 'Shoot, its a'], 
        'happy': ['Well look, its a', "Yes! I see a", "Yay, its a"], 'sad': ['Oh no, its a', 'I fear I see a', 'Sadly, I think thats a']}
    
    if current_mood == "":
        chosen_tone = random.choice(tones)
    else:
        chosen_tone = current_mood

    command = "say a short " + chosen_tone + " " + random.choice(params.completion_types) + " about a " + ' and a '.join(seen)
    seen_sentence = "say '" + current_person_name + "," + random.choice(prefix[chosen_tone]) + " " + ' and a '.join(seen) + "'"
    print(seen_sentence)
    print(command)
    await move_servo(chosen_tone)    
    await say(await ai_command(seen_sentence))
    resp = await ai_command(command)
    resp = re.sub('Q:',  'Question: ', resp)
    resp = re.sub('A:',  'Answer: ', resp)
    await say(resp)

async def ai_command(command):
    try:
        if (current_char != ""):
            command = command + " in the style of " + current_char
        completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", max_tokens=1024, messages=[{"role": "user", "content": command}])
        completion = completion.choices[0].message.content
        completion = re.sub('[^0-9a-zA-Z.!? ]+', '', completion)
        print(completion)
        return completion
    except openai.error.ServiceUnavailableError:
        errors = ["Sorry, I am feeling tired", "Sorry, I had a brain fart", "Never mind, I don't know"]
        return random.choice(errors)

async def move_servo(pos):
    if params.enable_emotion_wheel == True:
        pos_angle = {
                    "happy": 0,
                    "angry": 75,
                    "sad": 157
                }
        service = Servo.from_robot(robot, 'servo1')
        await service.move(angle=pos_angle[pos])

async def see_something():
    service = VisionServiceClient.from_robot(robot, 'vision')
    found = False
    count = 0
    while not found:
        # if you are using a detection model instead of classifier...
        #detections = await service.get_detections_from_camera(camera_name='cam', detector_name='stuff_detector')
        detections = await service.get_classifications_from_camera(camera_name='cam', classifier_name='stuff_classifier', count=1)
        for d in detections:
            if d.confidence > params.vision_confidence:
                print(detections)
                if d.class_name != '???':
                    found = True
                    await make_something_up([d.class_name])
            count = count + 1
            if count > 20:
                found = True
                # nothing significant seen, so stop trying
                await say("nothing")

async def main():
    global robot
    robot = await connect()
    base = Base.from_robot(robot, 'viam_base')
    r = sr.Recognizer()
    r.energy_threshold = 1568 
    r.dynamic_energy_threshold = True
    m = sr.Microphone()

    while True:
        with m as source:
            r.adjust_for_ambient_noise(source) 
            audio = r.listen(source)
        try:
            global current_char
            global current_mood
            global current_person_name
            transcript = r.recognize_google(audio_data=audio, show_all=True)
            if type(transcript) is dict and transcript.get("alternative"):
                text = transcript["alternative"][0]["transcript"].lower()
                print(text)
                if re.search(".*" + params.robot_command_prefix, text):
                    command = re.sub(".*" + params.robot_command_prefix + "\s+",  '', text)
                    print(command)
                    if command == "spin":
                        await base.spin(angle=720, velocity=500)
                    elif command == "turn a little right":
                        await base.spin(angle=-45, velocity=500)
                    elif command == "turn right":
                        await base.spin(angle=-90, velocity=500)
                    elif command == "turn a little left":
                        await base.spin(angle=90, velocity=500)
                    elif command == "turn left":
                        await base.spin(angle=90, velocity=500)
                    elif command == "turn around":
                        await base.spin(angle=180, velocity=500)
                    elif command == "move forward":
                        await base.move_straight(distance=1000, velocity=500)
                    elif command == "move backwards":
                        await base.move_straight(distance=-1000, velocity=500)
                    elif command == "reset":
                        current_char = ""
                        current_mood = ""
                        current_person_name = ""
                    elif re.search("^" + '|'.join(params.observe_list), command):
                        await see_something()
                    elif command == "act random":
                        current_char = random.choice(params.char_list)
                        await say(await ai_command("Say hi " + current_person_name))
                    elif re.search("^" + params.intro_command, command):
                        current_person_name = re.sub(params.intro_command, "", command)
                        await say(await ai_command("Say hi " + current_person_name))
                    elif re.search("^" + params.char_command +" (" + '|'.join(params.char_list) + ")", command):
                        current_char = re.sub(params.char_command, "", command)
                        await say(await ai_command("Say hi"))
                    elif re.search("^" + params.char_guess_command +" (" + '|'.join(params.char_list) + ")", command):
                        if current_char != "":
                            char_guess = re.sub(params.char_guess_command, "", command)
                            print("guess: |" + char_guess + "|actual: |" + current_char + "|")
                            if char_guess == current_char:
                                await say(await ai_command("say 'You are correct'"))
                            else:
                                await say(await ai_command("say 'You are wrong, try again'"))
                    elif re.search("^you seem", command):
                        current_mood = re.sub("you seem ", "", command)
                        await move_servo(current_mood)
                        await say(await ai_command("Say 'yeah, I am " + current_mood +  "'"))
                    else:
                        await say(await ai_command(command))

        except sr.UnknownValueError:
            print("Speech recognition could not understand audio")
        except Exception as e:
            print(e)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except:
        exit

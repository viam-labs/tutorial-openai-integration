import asyncio
import time
from pygame import mixer
import pyttsx3
import os
import re
import random
import signal
import openai

from viam.components.servo import Servo
from viam.robot.client import RobotClient
from viam.services.vision import VisionServiceClient
from viam.rpc.dial import Credentials, DialOptions

viam_secret = os.getenv('VIAM_SECRET')
viam_address = os.getenv('VIAM_ADDRESS')
openai.organization = os.getenv('OPENAPI_ORG')
openai.api_key = os.getenv('OPENAPI_KEY')
vision_confidence = .4

mixer.init(devicename = 'Built-in Audio Analog Stereo (2)')
robot = ''

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
    types = ['haiku', 'poem', 'slogan', 'expression', 'joke', 'tagline', 'assertion', 'question']
    tones = ['angry', 'happy', 'sad']
    prefix = ['I will', 'I am going to', 'OK, now I will', 'Ready? I am about to']
    
    chosen_tone = random.choice(tones)
    command_core = "say a " + chosen_tone + " " + random.choice(types) + " about a " + ' and a '.join(seen)
    command = random.choice(prefix) + " " + command_core
    await move_servo(chosen_tone)
    await say(command)
    resp = await ai_command(command_core)
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

    service = VisionServiceClient.from_robot(robot, 'vision')
   
    seen = {}
    target_seen = random.randint(1, 3)
    while True:
        #detections = await service.get_detections_from_camera(camera_name='cam', detector_name='stuff_detector')
        detections = await service.get_classifications_from_camera(camera_name='cam', classifier_name='stuff_detector', count=1)

        for d in detections:
            if d.confidence > vision_confidence:
                print(detections)
                if d.class_name != '???':
                    if seen.get(d.class_name) == None:
                        seen[d.class_name] = True
                        seen_count = len(seen)
                        await move_servo(seen_count)
                        print(d.class_name)
                        prefix = ['I see a', 'Oh, there is a', 'Look, a', 'Oh snap, a', 'I spy a']
                        await say(random.choice(prefix) + " " + d.class_name)
                        if seen_count == target_seen:
                            await make_something_up(seen)
                            seen = {}
                            target_seen = random.randint(1, 3)
        time.sleep(.05)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except:
        exit
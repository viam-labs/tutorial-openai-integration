import os

viam_secret = os.getenv('VIAM_SECRET')
viam_address = os.getenv('VIAM_ADDRESS')
openai_organization = os.getenv('OPENAPI_ORG')
openai_api_key = os.getenv('OPENAPI_KEY')
elevenlabs_key = os.getenv('ELEVENLABS_KEY')

mixer_device = 'Built-in Audio Analog Stereo'

vision_confidence = .3
enable_emotion_wheel = True
completion_types = ['expression', 'question', 'something']
robot_command_prefix = "so"
char_command = "act like"
char_guess_command = "i think you are"
intro_command = "my name is"
observe_list = ["what do you see", "whats that"]
char_list = {"yoda": {}, "scooby-doo": {}, "cheech and chong": {}, "fred from flintstones": {}, "eric cartman": {},
    "c-3po": {"voice": "Sam"}, "c3po": {}, "darth vader": {}, "homer simpson": {}, "tony soprano": {"voice": "Arnold"}, "spongebob": {}, "bender rodriguez": {}, 
    "michael scott": {"voice": "Josh"}, "harley quinn": {"voice": "Elli"}, "paris hilton": {}, "doctor evil": {}, "linda belcher": {}, 
    "donkey from shrek": {}, "daenerys targaryen": {"voice": "Bella"}, "eeyore": {}}

elevenlabs_default_voice="Elli"
# tutorial-openai-integration

A demo of integrating OpenAI's ChatGPT with robotics. 
This [tutorial](http://docs.viam.com/tutorials/integrating-viam-with-openai/) expects that you'll be running [viam-server](https://docs.viam.com/) on Raspberry Pi.

## Prerequisites

``` bash
sudo apt update && sudo apt upgrade -y
sudo apt-get install python3
sudo apt install python3-pip
sudo apt install python3-pyaudio
sudo apt-get install alsa-tools alsa-utils
sudo apt-get install flac
```

 Viam robot credentials and OpenAI API credentials are also required in order to run the software. Viam credentials can be copied from the CODE SAMPLE tab on your [Viam robot page](https://app.viam.com). In order to acquire OpenAI credentials, you’ll need to [sign up for OpenAI](https://openai.com/api/) and [set up API keys](https://platform.openai.com/account/api-keys).

Once you have both sets of credentials, create a file called `run.sh`, adding the following and updating the credentials within:

``` sh
export OPENAPI_KEY=abc
export OPENAPI_ORG=xyz
export VIAM_SECRET=123
export VIAM_ADDRESS=789
python rosey.py
```

## Elevenlabs voice support

By default, Google TTS is used for audio voice generation.  However, [ElevenLabs](https://elevenlabs.io) can be used for enhanced AI voice generation.
To use Elevenlabs, add your ElevenLabs API key to `run.sh` as follows:

``` sh
export ELEVENLABS_KEY=mykey
```

You can then assign voices to Rosey or any characters by adding the Elevenlabs voice name (including any generated names) in `params.py`.  For example:

``` json
{ "linda belcher": { "voice": "domi" } }
```

Please visit the Viam docs site for the full [tutorial walk-through](http://docs.viam.com/tutorials/integrating-viam-with-openai/)

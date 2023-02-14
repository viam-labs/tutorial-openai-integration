# tutorial-openai-integration

This tutorial expects that you'll be running [viam-server](https://docs.viam.com/) on Raspberry Pi.

## Prerequisites

sudo apt update && sudo apt upgrade -y
sudo apt-get install python3
sudo apt install python3-pip
sudo apt install python3-pyaudio
sudo apt-get install alsa-tools alsa-utils
sudo apt-get install flac

 Viam robot credentials and OpenAI API credentials are also required in order to run the software. Viam credentials can be copied from the CODE SAMPLE tab on your [Viam robot page](https://app.viam.com). In order to acquire OpenAI credentials, you’ll need to [sign up for OpenAI](https://openai.com/api/) and [set up API keys](https://platform.openai.com/account/api-keys).

Once you have both sets of credentials, create a file called run.sh, adding the following and updating the credentials within:

export OPENAPI_KEY=abc
export OPENAPI_ORG=xyz
export VIAM_SECRET=123
export VIAM_ADDRESS=789
python rosey.py

Please visit the Viam docs site for the full [tutorial walk-through](http://docs.viam.com/tutorials/integrating-viam-with-openai/)

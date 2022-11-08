# LibAnt

[![Build Status](https://travis-ci.org/half2me/libant.svg?branch=master)](https://travis-ci.org/half2me/libant)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/half2me/libant/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/half2me/libant/?branch=master)
[![MIT licensed](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/half2me/libant/master/LICENSE) 
[![Join the chat at https://gitter.im/libant/Lobby](https://badges.gitter.im/libant/Lobby.svg)](https://gitter.im/libant/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)  
A Python implementation of the ANT+ Protocol  

The goal of this project is to provide a clean, Python-only implementation of the [ANT+ Protocol](https://www.thisisant.com). Usage of the library should require little to no knowledge of the ANT+ Protocol internals. It should be easy to use, easy to read, and have proper error handling.

This project was born when I decided to completely rewrite the [python-ant library](https://github.com/mvillalba/python-ant) from scratch, after not finding a fork that suited my needs. There were so many different forks of the original project, each with their own patches, but not a properly useable one. Because of this, there may be parts of the code which look similar to the python-ant library, as I have their code as a reference.

## Installing
For the stable version: `pip3 install antlib`  
For the latest clone the repo and do `./setup.py install` under UNIX systems or `python setup.py install` on windows (Make sure to use python3)

## Usage
See usage examples in the `demos` folder.
If you want to use the serial driver under linux, either run the script as root, or add your user to the `dialout` group with:
```bash
sudo adduser yourusername dialout
```

## Known bugs
The usb driver has a bug which requires you to replug your ANT+ stick every time you run a demo script. So until we get that fixed, I suggest you stick to the serial driver, which is stable.

# How to run on Raspberry pi
The best thing you can do is to create a virtual environment and install this project's dependencies etc.

```
python3 -m venv env
source env/bin/activate`
pip install -r requirements.txt`
python setup.py install
```

You also have to add udev rules (otherwise you'll need sudo, which is not the Python from your virtual enironment).

Add a new file `99-ant-usb.rules` in `/etc/udev/rules.d` containing the following

```
SUBSYSTEM=="usb", ATTRS{idVendor}=="VID (hex)", ATTRS{idProduct}=="PID (hex)", MODE="0666"
```

You can find vendor id and product id with `lsusb -v`

Reload udev rules with `udevadm control --reload-rules`

It might be helpfull to un- and re-plug the USB ant key as well.

Now start the project with `python websocket_aggregator.py`
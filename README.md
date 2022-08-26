# Kodi PulseEqualizer GUI Addon

A graphical frontend in Kodi based linux systems to control the pulse audio equalizer. 

Version 2.1.5

Features include:

*	Graphical configuration of the pulseaudio equalizer
*	Digital Room Correction
*	Management of equalizer profiles (add, remove and change)
*	Automatic filter profile switching based on output device
*	Audio latency-offset slider and automatic switch based on device
*	System volume control in Kodi 
*	Automatic switch to Bluetooth headset, if it becomes available
*	Mini keymap editor

Tested on i386 Linux Mint / Debian 10/11 headless / Raspberry PI 2b and 3b / Ubuntu 18 headless

More information can be found on [Wiki](https://github.com/wastis/PulseEqualizerGui/wiki)

Help can be found in the Kodi forum within this [thread](https://forum.kodi.tv/showthread.php?tid=360514&pid=3094412#pid3094412)

2022 wastis

![Pulse Equalizer](/resources/images/Equalizer.png)

## Installation

This addon requires pulseaudio-equalizer installed on the system

	sudo apt install pulseaudio-equalizer	

### Install Addon in Kodi

Launch *Kodi >> Add-ons >> Get More >> .. >> Install from zip file*

### Configuration

In Kodi, select a pulseaudio hardware ouptut device and start a playback. Select an equalizer profile. The equalizer is then automatically inserted into the playback stream. 


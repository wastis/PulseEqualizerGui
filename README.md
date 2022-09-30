# Kodi PulseEqualizer GUI Addon

A graphical frontend in Kodi based on linux for control the pulseaudio equalizer. 

Version 2.1.9 / 
[Linux Addon Repo](https://github.com/wastis/LinuxAddonRepo) / 
[*OSMC setup*](https://github.com/wastis/OSMCEqualizerSetup)

Features include:

*	Graphical configuration of the pulseaudio equalizer
*	Digital Room Correction
*	Management of equalizer profiles (add, remove and change)
*	Automatic filter profile switching based on output device
*	Audio latency control based on device
*	System volume control 
*	Automatic switch to Bluetooth device
*	Mini keymap editor

Tested on i386 Linux Mint / Debian 10/11 headless / Raspberry PI 2b and 3b / Ubuntu 18 headless / OSMC 9/22

More information can be found on [Wiki](https://github.com/wastis/PulseEqualizerGui/wiki)

Help can be found in the Kodi forum within this [thread](https://forum.kodi.tv/showthread.php?tid=360514&pid=3094412#pid3094412)

2022 wastis

| <img src="resources/images/Equalizer.png" alt="drawing" width="350"/> | <img src="resources/images/Room Correction.png" alt="drawing" width="350"/> |
|:--------------:|:-----------:|

## Installation

### System Prerequisites
This addon requires pulseaudio-equalizer installed on the system

	sudo apt install pulseaudio-equalizer	

### Install Addon in Kodi
This addon is included into the [Linux Addon Repository](https://github.com/wastis/LinuxAddonRepo). It is recommended to use the repository for the installation of the addon. This will enable automatic version upgrades.

### Configuration

In Kodi, select a pulseaudio hardware ouptut device and start a playback. Select an equalizer profile. The equalizer is then automatically inserted into the playback stream. 

### OSMC
If you run on OSMC, the [OSMC Equalizer Setup](https://github.com/wastis/OSMCEqualizerSetup) addon does the whole system configuration for you. 
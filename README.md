# Kodi PulseEqualizer GUI Addon

PulseEqualizer GUI provides a pulsaudio configuration frontend for Kodi on linux systems. 

Version 2.1.2

This includes:
- Graphical configuration of pulseaudio equalizer
- Manage and switch between equalizer profiles (add, remove and change)
- Digital Room Correction
- Import, remove and select digital room correction profile
- Configure latency-offset (for video/audio sync)
- Control system volume (needed if a compressor is used in the filter chain)

- tested on i386 Linux Mint / Debian 10/11 headless / Raspberry PI 2b and 3b / Ubuntu 18 headless

- currently not working with: LibreElec / OSMC / OpenElec  

2022 wastis

**Before upgrade, please backup your setting directory in (~/.kodi/addon/script.pulseequalizer.gui/settings)**


![Pulse Equalizer](/resources/images/Equalizer.png)

# Installation

This addon requires pulseaudio-equalizer installed on the system

	sudo apt install pulseaudio-equalizer	

If you run Kodi 18, in addition the module python-dbus is required
	
	sudo apt install pulseaudio-equalizer
	sudo apt install python-dbus

## Install Addon in Kodi

Launch *Kodi >> Add-ons >> Get More >> .. >> Install from zip file*

## Configuration

In Kodi, select a pulseaudio hardware ouptut device and start a playback. Select an equalizer profile. The equalizer is then automatically inserted into the playback stream. 

With *Addon >> Manage Profiles >> Insert predefined Profiles*, it is possible to load a default profile set. 

More information can be found on [Wiki](https://github.com/wastis/PulseEqualizerGui/wiki)

Help can be found in the Kodi forum in this [thread](https://forum.kodi.tv/showthread.php?tid=360514&pid=3076706#pid3076706)


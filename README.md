# Kodi PulseEqualizer GUI Addon

PulseEqualizer GUI is an addon that provides a pulsaudio configuration frontend for Kodi on linux based systems. 

Version 2.1.1

**Before upgrade, please backup your setting directory in (~/.kodi/addon/script.pulseequalizer.gui/settings)**

This includes:
- Configuration of the pulseaudio equalizer with sliders
- Switch between equalizer profiles
- Manage equalizer profiles (add, remove and change)

- Digital Room Correction for each channel
- Import, remove and select digital room correction profile

- Configure latency-offset (for video/audio sync)

- Control system volume (needed if a compressor is used in the filter chain)
- Hotkey support for each

- tested on i386 Linux Mint / Debian 10/11 server / Raspberry PI 2b and 3b, OS v. Jan 22 / Ubuntu 18 server  

2022 wastis

![Pulse Equalizer](/resources/images/Equalizer.png)

# Installation

This addon requires pulseaudio-equalizer and python3-pil installed on the system

	sudo apt install pulseaudio-equalizer
	sudo apt install python3-pil

If you run Kodi 18, in addition the module python-dbus is required
	
	sudo apt install pulseaudio-equalizer
	sudo apt install python-dbus
	sudo apt install python-pil

## Install Addon in Kodi

Launch *Kodi >> Add-ons >> Get More >> .. >> Install from zip file*

## Configuration

In Kodi, select a pulseaudio hardware ouptut device and start a playback. Select an equalizer profile. The equalizer is then automatically inserted into the playback stream. 

With *Addon >> Manage Profiles >> Insert predefined Profiles*, it is possible to load a default profile set. 

For basic equalizer functionality, no further configuration is required. This is different to previous versions of the addon.  

More information can be found on [Wiki](https://github.com/wastis/PulseEqualizerGui/wiki)

Help can be found in the Kodi forum in this [thread](https://forum.kodi.tv/showthread.php?tid=360514&pid=3076706#pid3076706)


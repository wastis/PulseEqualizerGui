# Kodi PulseEqualizer GUI Addon

PulseEqualizer GUI is an addon that provides configuration frontend for Kodi. 

This includes:
- Configuration of the equalizer with sliders
- Manage equalizer profiles (add, remove and change)
- Switch between equalizer profiles
- Switch equalizer to specific output device and port
- Hotkey support for each
- v.1.0.2 Filter chain support
- tested on i386 Mint 20.4 / Debian 10 server / raspberry PI 3 OS v. May 7th 2021  

Supports Kodi 18 and 19


2021 wastis

![Pulse Equalizer](/resources/images/Kodi.png)

# Installation

This addon requires pulseaudio-equalizer installed on the system

	sudo apt install pulseaudio-equalizer

If you run Kodi 18, the module python-dbus is required
	
	sudo apt install python-dbus
	
Kodi 19 is based on dbussy, which is included in the package

Requires the module-equalizer-sink and module-dbus-protocol to be loaded
either manual with

	pactl load-module module-equalizer-sink
	pactl load-module module-dbus-protocol

or on startup by configuring pulseaudio

add the lines

	module-equalizer-sink
	module-dbus-protocol

at the end of either

	/etc/pulse/default.pa

or

	~/.config/pulse/default.pa

warning: on some systems, ~/.config/pulse/default.pa 
overwrites /etc/pulse/default.pa, pulse audio will not work anymore
in this case you can copy /etc/pulse/default.pa to ~/.config/pulse/default.pa 
and add the lines in there.

## Attach equalizer to specific device

This is usefull if you want to set a default device or handle more then 2 channels. The number of channels is set at the time the module is loaded. 
To copy the configuration of a specific device, the module can be loaded with the following command

	pactl load-module module-equalizer-sink sink_master=SINK_NAME

to get the SINK_NAME run
	
	pactl list short sinks

## Filter chain
As of version 1.0.2 PulseEqualizer GUI support filter chains. For this, chains can be defined within the file default.pa. A filter chain is a list of module-ladspa-sink’s and one optional module-equalizer-sink connected in a row to each other.

To define a chain, the modules need to be loaded in the reverse order always referring to next filter or module in stream direction. To do this, a unique name must be given to the module via the  sink_name parameter and the following filter must be set by it’s nave via the  sink_master parameter.

As an example withing the default.pa:
connect the equalizer to the audio device 

	load-module module-equalizer-sink sink_name=equalizer_1

connect a ladspa filter to the equalizer_1 (given the sc4 ladspa filter is available on the system)

	load-module module-ladspa-sink sink_master=equalizer_1 sink_name=Compressor_1 plugin=sc4_1882 label=sc4 control=1,1.5,401,-20,20,5,15

and so on.

The OS does currently not connect those chains automatically together, the would need to be manually connected via pavucontrol. And sometimes these connections get lost. 

PulseEqualizer GUI does the connection automatically, now. Within Kodi settings, the Audio output device must be set to the first filter in the row. When a file is played within Kodi, the PulseEqualizer GUI will recognize this and will connect all the filters in the chain together.  It is possible to observe this with  an open  pavucontrol on the play tab.

In addition, with PulseEqualizer GUI, it is possible to select the final output device via the Menu or shortcut key. 

The equalizer front-end will only come up, if a module-equalizer-sink is within the selected chain.  

Of course, a collection of ladspa filters need to be available on the system. See thread.

## Install Addon in Kodi

Launch Kodi >> Add-ons >> Get More >> .. >> Install from zip file

## Configuration

In Kodi, select the Equalizer as output for Kodi

	System->Audio->Audio Output Device --- select "FFT-based-equalizer...."

Configure the Addon to stream to a Device

	Start Addon and Menuentry "Select Output Device"

A stream needs to be played in order to select the output device. 

## Configure Hotkeys

The following will enable the keyboard keys l,m,n and o to launch the different modules.

Create a file ~/.kodi/userdata/keymaps/equalizer.xml

insert

	<keymap>
		<global>
			<keyboard>
				<l>RunScript(script.pulseequalizer.gui,profile)</l>
				<m>RunScript(script.pulseequalizer.gui,equalizer)</m>
				<n>RunScript(script.pulseequalizer.gui,device)</n>
				<o>RunScript(script.pulseequalizer.gui,manager)</o>
			</keyboard>
		</global>
	</keymap>

restart Kodi

## Headless OS installations

On Debian 10 server or raspberry PI OS Lite, Kodi needs to be launched with a dbus session

Both systems currently use /etc/rc.local as custom init script. Replace [path] with the path to your script, replace [user] with the user name Kodi shall run in

	#!/bin/sh -e
	### BEGIN INIT INFO
	# Provides:          kodi
	# Required-Start:    $remote_fs $syslog
	# Required-Stop:     $remote_fs $syslog
	# Default-Start:     2 3 4 5
	# Default-Stop:      0 1 6
	# Short-Description: Start daemon at boot time
	# Description:       Enable service provided by daemon.
	### END INIT INFO
	sudo -u [user] [path]/run_session.sh &
	exit 0

[path]/run_session.sh starts up the dbus session

	#!/bin/sh -e
	exec dbus-run-session -- [path]/run_kodi.sh

[path]/run_kodi.sh starts kodi

	#!/bin/sh -e
	
	KODI_AE_SINK=PULSE      #<-- those two lines are needed on raspberry to tell Kodi 
	export KODI_AE_SINK     #<-- to use pulseaudio instead of ALSA
	
	/usr/bin/pulseaudio -D  #<-- start pulseaudio in the dbus session as daemon 
	/usr/bin/kodi 
	exit 0
	
## raspberry PI 3 pitfall

if you install Kodi on the headless OS Lite, you might want to increase the video memory from 64MB to 256MB to avoid crashes. 

## raspberry PI 3 performance

pulse audio with equalizer enabled consumes about 20% of one CPU core. 

## LibreELEC, OSMC and OpenELEC
 
To my knowledge, to date, those distributions do not have module-equalizer-sink included in their minimal system, so the PulseEqualizer GUI Addon might not run. 

Enjoy


See https://forum.kodi.tv/showthread.php?tid=360514

Feel free to ask any questions on the Kodi Forums.

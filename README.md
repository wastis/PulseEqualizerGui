# Kodi PulseEqualizer GUI Addon

Version 2.0.0

PulseEqualizer GUI is an addon that provides a pulsaudio configuration frontend for Kodi. 

This includes:
- Configuration of the pulseaudio equalizer with sliders
- Manage equalizer profiles (add, remove and change)
- Switch between equalizer profiles
- Configure latency-offset (for video/audio sync)
- Control system volume (needed if a compressor is used in the filter chain)
- Hotkey support for each

- tested on i386 Linux Mint / Debian 10 server / raspberry PI 3 OS v. May 7th 2021  

Supports Kodi 18 and 19


2021 wastis

![Pulse Equalizer](/resources/images/Kodi.png)

# Installation

This addon requires pulseaudio-equalizer installed on the system

	sudo apt install pulseaudio-equalizer

If you run Kodi 18, the module python-dbus is required
	
	sudo apt install python-dbus
	
Since version 2.0.0 the modules "module-equalizer-sink" and "module-dbus-protocol" are loaded automatically when addon starts, no need to configure pulseaudio for this.

## Install Addon in Kodi

Launch Kodi >> Add-ons >> Get More >> .. >> Install from zip file

## Configuration

In Kodi, select a pulseaudio hardware ouptut device and start a playback. Select an equalizer profile. The equalizer is then automatically inserted into the playback stream. This is different to previouse versions of the addon.   


# Advanced configuration

## Filter chains
PulseEqualizer GUI support preconfigured filter chains. Filter chains can be defined within the file default.pa. A filter chain is a list of module-ladspa-sink’s and one optional module-equalizer-sink connected in a row to each other.

To define a chain, the modules need to be loaded in the reverse order always referring to next filter or module in stream direction. To do this, a unique name must be given to the module via the  sink_name parameter and the following filter must be set by it’s name via the sink_master parameter. It is possible to also set a display name for the filter by e.g. sink_properties="device.description=EQ-1"

As an example within the pulse/default.pa:

Connect the equalizer to the audio device 

	load-module module-equalizer-sink sink_name=eq_1 sink_properties="device.description=EQ-1"

Connect a ladspa filter to the equalizer_1 (given the sc4 ladspa filter is available on the system)

	load-module module-ladspa-sink sink_master=eq_1 sink_name=co_1 sink_properties="device.description=CO-1" plugin=sc4_1882 label=sc4 control=1,1.5,401,-20,20,5,15

The sc4_1882 filter needs to be installed on the system. 


On playback, PulseEqualizer GUI will connect the chain together based on the sink_master, when first element of the chain is selected within Kodi.

Warning: you might experience instability of pulseaudio, when using chains in combination with removable devices (bluetooth, usb-dongle, etc). In this case, disable the module loading of "load-module module-switch-on-connect" and "load-module module-switch-on-port-available" in default.pa by commenting them out.


## Configure Hotkeys

The following will enable the keyboard keys l,m,n,o,p to launch the different modules. It is also possible to control the system wide volume by f and e:

Create a file ~/.kodi/userdata/keymaps/equalizer.xml

	<keymap>
		<global>
			<keyboard>
				<l>xbmc.RunScript(script.pulseequalizer.gui,profile)</l>
				<m>xbmc.RunScript(script.pulseequalizer.gui,equalizer)</m>
				<n>xbmc.RunScript(script.pulseequalizer.gui,device)</n>
				<o>xbmc.RunScript(script.pulseequalizer.gui,manager)</o>
				<p>xbmc.RunScript(script.pulseequalizer.gui,latency)</p>
			</keyboard>
		</global>
		<FullscreenVideo>
			<keyboard>
				<f>xbmc.RunScript(script.pulseequalizer.gui,volup)</f>
				<e>xbmc.RunScript(script.pulseequalizer.gui,voldown)</e>
			</keyboard>
		</FullscreenVideo>
	</keymap>


Restart Kodi. 

Do not insert volup / voldown into the "gloal" section, as every time you press the key, an new instance of the script and the pyhton module is started. This may slow the system down. 
If you use volup/voldown on a headless system, you may want to disable the flat volume control of pulseaudio to avoid conflict between Kodi and PulseEqualizerGui. 

This is done by inserting a line into pulse/daemon.conf.

	...
	flat-volumes = no
	...

Restart pulseaudio.

## Headless OS installations

This works with Debian 10 and raspberry Pi 3 with a small modification of the startup script.

Pulseaudio needs to run in a user session together with Kodi.

create two files:
~/.config/systemd/user/pulseaudio.service

	[Unit]
	Description=Pulseaudio Sound Service
	Requires=pulseaudio.socket
	
	[Service]
	Type=notify
	ExecStart=/usr/bin/pulseaudio --verbose --daemonize=no
	Restart=on-failure
	
	[Install]
	Also=pulseaudio.socket
	WantedBy=default.target

~/.config/systemd/user/pulseaudio.socket

	[Unit]
	Description=Pulseaudio Sound System
	
	[Socket]
	Priority=6
	Backlog=5
	ListenStream=%t/pulse/native
	
	[Install]
	WantedBy=sockets.target

### Debian 10 
/etc/rc.local

	#!/bin/sh -e
	### BEGIN INIT INFO
	# Provides:          kodi
	# Required-Start:    $remote_fs $syslog $inputlirc
	# Required-Stop:     $remote_fs $syslog $inputlirc
	# Default-Start:     2 3 4 5
	# Default-Stop:      0 1 6
	# Short-Description: Start daemon at boot time
	# Description:       Enable service provided by daemon.
	### END INIT INFO
	su -c '/usr/bin/kodi' [username] &
	exit 0
where [username] is your user name.
	
### Raspberry Pi
For raspberry PI, create a startup script to tell Kodi to use pulseaudio instead of alsa
	
/home/pi/start_kodi.sh
	
	#!/bin/sh -e
	KODI_AE_SINK=PULSE
	export KODI_AE_SINK
	/usr/bin/kodi 
	exit 0
	
and in /etc/rc.local

	#!/bin/sh -e
	### BEGIN INIT INFO
	# Provides:          kodi
	# Required-Start:    $remote_fs $syslog $inputlirc
	# Required-Stop:     $remote_fs $syslog $inputlirc
	# Default-Start:     2 3 4 5
	# Default-Stop:      0 1 6
	# Short-Description: Start daemon at boot time
	# Description:       Enable service provided by daemon.
	### END INIT INFO
	su -c '/home/pi/start_kodi.sh' pi &
	exit 0
	
To start pulseaudio run

	systemctl --user daemon-reload
	systemctl --user enable pulseaudio.service
	systemctl --user enable pulseaudio.socket
	systemctl --user start pulseaudio.service
	systemctl --user status pulseaudio.{service,socket}

You might need to install sudo on a fresh system. 
	
	apt install sudo	

## raspberry PI 3 pitfall

If you install Kodi on the headless OS Lite, you might want to increase the video memory from 64MB to 256MB to avoid crashes. 

## raspberry PI 3 performance

Pulseaudio with equalizer enabled consumes about 20% of one CPU core. 

## LibreELEC, OSMC and OpenELEC
 
To my knowledge, to date, those distributions do not have module-equalizer-sink included in their minimal system, so the PulseEqualizer GUI Addon might not run. 

Enjoy

See https://forum.kodi.tv/showthread.php?tid=360514

Feel free to ask any questions on the Kodi Forums.


THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

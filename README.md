

# Kodi PulseEqualizer GUI Addon

Version 2.1.1

**Before upgrade, please backup your setting directory in (~/.kodi/addon/script.pulseequalizer.gui/settings)**

PulseEqualizer GUI is an addon that provides a pulsaudio configuration frontend for Kodi. 

This includes:
- Configuration of the pulseaudio equalizer with sliders
- Switch between equalizer profiles
- Manage equalizer profiles (add, remove and change)

- [Digital Room Correction](#digital-room-correction) for each channel
- Import, remove and select digital room correction profile

- Configure latency-offset (for video/audio sync)

- Control system volume (needed if a compressor is used in the filter chain)
- Hotkey support for each

- tested on i386 Linux Mint / Debian 10/11 server / Raspberry PI 2b and 3b, OS v. Jan 22 / Ubuntu 18 server  

2022 wastis

![Pulse Equalizer](/resources/images/Equalizer.png)

# Content of this readme

[Installation](#installation)

[Configuration](#configuration)

[Advanced configuration (optional)](#advanced-configuration)

[Filter chains](#filter-chains)

[Latency optimizations](#latency-optimizations)

[Digital Room Correction](#digital-room-correction)

[Configure Hotkeys](#configure-hotkeys)

[Headless OS installations](#headless-os-installations)

[Raspberry PI 2b & 3](https://github.com/wastis/PulseEqualizerGui/wiki/Raspberry-PI)

[Forum](#finally)


# Installation

This addon requires pulseaudio-equalizer installed on the system

	sudo apt install pulseaudio-equalizer
	sudo apt install python3-pil

If you run Kodi 18, the module python-dbus is required
	
	sudo apt install python-dbus
	sudo apt install python-pil

Since version 2.0.0 the modules "module-equalizer-sink" and "module-dbus-protocol" are loaded automatically when the addon is started, no need to configure pulseaudio for this.

## Install Addon in Kodi

Launch *Kodi >> Add-ons >> Get More >> .. >> Install from zip file*

## Configuration

In Kodi, select a pulseaudio hardware ouptut device and start a playback. Select an equalizer profile. The equalizer is then automatically inserted into the playback stream. 

With *Addon >> Manage Profiles >> Insert predefined Profiles*, it is possible to load a default profile set. 

For basic equalizer functionality, no further configuration is required. This is different to previous versions of the addon.   


# Advanced configuration

Fist make sure you have the configuration files *daemon.conf* *default.pa* and in ~/.config/pulse/. If not, create directory and copy the two files from /etc/pulse/

	mkdir -p ~/.config/pulse
	cp /etc/pulse/daemon.conf /etc/pulse/default.pa ~/.config/pulse/

## Filter chains
PulseEqualizer GUI support preconfigured filter chains. Filter chains can be defined within the file default.pa. A filter chain is a list of module-ladspa-sink’s and one optional module-equalizer-sink connected in a row to each other.

To define a chain, the modules need to be loaded in the reverse order always referring to next filter or module in stream direction. To do this, a unique name must be given to the module via the  sink_name parameter and the following filter must be set by it’s name via the sink_master parameter. It is possible to also set a display name for the filter by e.g. sink_properties="device.description=EQ-1"

As an example within the ~/.config/pulse/default.pa:

Connect the equalizer to the audio device 

	load-module module-equalizer-sink sink_name=eq_1 sink_properties="device.description=EQ-1"

Connect a ladspa filter to the equalizer_1 (given the sc4 ladspa filter is available on the system)

	load-module module-ladspa-sink sink_master=eq_1 sink_name=co_1 sink_properties="device.description=CO-1" plugin=sc4_1882 label=sc4 control=1,1.5,401,-20,20,5,15

The sc4_1882 filter is a compressor to keep audio volume at about the same level and needs to be installed with the swh-plugins package.

	sudo apt install swh-plugins


On playback, PulseEqualizer GUI will connect the chain together based on the sink_master, when first element of the chain is selected within Kodi.

Warning: you might experience instability of pulseaudio, when using chains in combination with removable devices (bluetooth, usb-dongle, etc). In this case, disable the module loading of "load-module module-switch-on-connect" and "load-module module-switch-on-port-available" in default.pa by commenting them out.

## Latency optimizations

Other than in games, audio latency on media players is not a big problem, as long as audio and video are in sync. On pulseaudio, I have identified two types of latency, the filter latency introduced by pulseaudio equalizer and the buffer latency between the different pulse filter and sound modules, both with different symptoms.

#### 1. Latency introduced by pulseaudio equalizer module

Unfortunately it seems that the pulseaudio module does not report the correct latency back to the media players (not only Kodi). On my different systems, this causes an audio delay of 350ms compared to the video stream. 

To compensate for this, the latency offset slider has been introduced to the addon. This setting will be saved depended on the output device and whether equalizer is in the playback chain or not. 

This method also provides the possibility do compensate for latencies introduced by the output device. For example my Bose bt-earphones have a latency of 150ms on the raspberry pi. So to playback over *equalizer -> BT-Bose* gives a total latency of 500ms. With the latency-offset slider, it is possible to configure pulseaudio for this and get video and audio perfect in sync. 

This settings will be saved, so whenever I choose *equalizer -> BT-Bose* as output, the correct latency of 500ms will be set in the system.

#### 2. Latency introduced by pulseaudio buffers

Especially in case of chains, the latency between different pulseaudio modules will sum up. This does not affect the audio/video synch, however may be a bit disturbing if you start / stop / seek the playerback, as the audio playback will start and stop a bit later than the video playback. 

This can be optimized by configuring pulseaudio buffer sizes. 

edit ~/.config/pulse/default.pa, find and change the line          

	...
	load-module module-udev-detect
	...

to

	...
	load-module module-udev-detect tsched=no
	...

edit ~/.config/pulse/daemon.conf, find and change the lines

	...
	; default-fragments = 8
	; default-fragment-size-msec = 25
	...

and change them to

	...
	default-fragments = 2
	default-fragment-size-msec = 15
	...
 
restart pulseaudio or reboot. 

This will reduce the buffer sizes and with this start the audio playback more immediate. If the buffer size becomes to small however, the audio quality can be affected.    

## Digital Room Correction

PulseEqualizer now has some functions that supports digital room correction for each channel. 

1. Play a sweep	- to measure the channel
2. Import the recorded spectrum of the previous sweep and save it as room correction
3. Select the room correction per audio device

The digital room correction is then fixed for the channel and not changed by the slider settings or the filter profiles. Those come on top to the room correction and stored separately.

The sweep is a linear sweep and produces a flat horizontal level line for all frequencies between 50Hz and 20kHz. This is different to other programs that produce a logarithmic sweep, so it is not possible to process sweep profiles from other tools with the PulseEqualizer import filter. 

The file format used by PulseEqualizer however is an open csv file format and of course open for manual changes. With this it is possible to configure the filter in any way.

The room correction filter are stored internally as filter coefficients and range from 0 (off) to 1 (no change to volume) to 2(double volume) and so on.

The files to imported are in dB and follow a specific naming convention, one file per channel.

	name.[channel_nr].txt
	
	livingroom.1.txt   (front-left)
	livingroom.2.txt   (front-right)
	...

Audacity is a tool to produce those files. 

1. record a number of sweeps for one channel, ensure there is no clipping.
2. amplify the recording so it is easy to see the sweeps. (Effect->Amplify)
3. select all sweeps for one channel and create Spectrum Plot (Analyse->Plot Spectrum)
4. Export (Size 1024 is sufficient in most cases)
5. repeat this for all channels
 
More info can be found here. 
[HOWTO Digital Room Correction](https://forum.kodi.tv/showthread.php?tid=365874)

## Configure Hotkeys

PulseEqualizer allows direct access to the main menus via hotkey configurations.

Following commands are available and can be inserted in the keymaps.xml:
	
- xbmc.RunScript(script.pulseequalizer.gui)			: 	Main menu
- xbmc.RunScript(script.pulseequalizer.gui,profile)	:	Profile selection menu
- xbmc.RunScript(script.pulseequalizer.gui,equalizer)	:	Equalizer Window
- xbmc.RunScript(script.pulseequalizer.gui,device)	:	Output device selection
- xbmc.RunScript(script.pulseequalizer.gui,correction):	Room Correction menu
- xbmc.RunScript(script.pulseequalizer.gui,latency)	:	latency slider

- xbmc.RunScript(script.pulseequalizer.gui,volup)		:	increase system volume
- xbmc.RunScript(script.pulseequalizer.gui,voldown)	:	decrease system volume
 
Example of a file keymap file: ~/.kodi/userdata/keymaps/equalizer.xml

	<keymap>
		<global>
			<keyboard>
				<l>xbmc.RunScript(script.pulseequalizer.gui,profile)</l>
				<m>xbmc.RunScript(script.pulseequalizer.gui,equalizer)</m>
				<n>xbmc.RunScript(script.pulseequalizer.gui,device)</n>
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

Do not insert volup / voldown into the "gloal" section, as every time you press the key, an new instance of the script and the pyhton module is started. This may slow the system down. 

If you use volup/voldown on a headless system, you may want to disable the flat volume control of pulseaudio to avoid conflict between Kodi and PulseEqualizerGui. 

This is done by inserting a line into pulse/daemon.conf followed by a pulseaudio restart.

	...
	flat-volumes = no
	...


# Headless OS installations

This works with Debian 10/11 

In general, pulseaudio needs to run in a user session together with Kodi. Here we create systemd start-up scripts in the user folder and use linger to execute the script as user. 

### Enable Pulseaudio

	systemctl --user daemon-reload
	systemctl --user enable pulseaudio.service
	systemctl --user enable pulseaudio.socket

### Autostart Kodi

	mkdir -p ~/.config/systemd/user/

create ~/.config/systemd/user/kodi.service with following content

	[Unit]
	 Description=kodi startup service
	 After = pulseaudio.service
	
	[Service]
	 Environment = KODI_AE_SINK=PULSE
	 ExecStart=/usr/bin/kodi
	 TimeoutSec=0
	 StandardOutput=journal
	 StandardError=journal
	 Restart = on-abort
	 RemainAfterExit=yes
	
	[Install]
	 WantedBy=default.target

Enable kodi service

	systemctl --user daemon-reload
	systemctl --user enable kodi.service	

Enable linger, this will start the user's systemd start up scripts

	loginctl enable-linger [username]

where [username] is your user name.


## Raspberry Pi 2 / 3

Please read the [Wiki page](https://github.com/wastis/PulseEqualizerGui/wiki/Raspberry-PI)

#### LibreELEC, OSMC and OpenELEC
 
To my knowledge, to date, those distributions do not have module-equalizer-sink included in their minimal system, so the PulseEqualizer GUI Addon might not run. 

# Finally
Enjoy

Feel free to ask any questions in the Kodi Forums.

[Trouble shooting](https://forum.kodi.tv/showthread.php?tid=360514&pid=3075095#pid3075095)

Digital room correction related topics go here
[HOWTO Digital Room Correction](https://forum.kodi.tv/showthread.php?tid=365874)


THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

### Kodi on Debian 11 and equalizer fresh install walk through

Install Debian without desktop environment but with ssh and a user named e.g. "john"

	#
	# console login as root
	#
	apt update
	
	# basic tools
	apt install sudo net-tools
	
	#check ip address
	ifconfig
	exit
	
	#
	# ssh-login as user (ssh john@ip)
	#
		
	#install required packages
	sudo apt install vim samba kodi pulseaudio pulseaudio-equalizer swh-plugins python3-pil
	
	# add john to the required groups 
	usermod -a -G sudo,input,pulse john
	
	#disable vim visuell mode
	echo "set mouse-=a" >> ~/.vimrc
	
	#prepare pulseaudio startup in user session
	mkdir -p ~/.config/systemd/user/
		
	#create Kodi startup script
	echo -e '[Unit]\n Description=kodi startup service\n After = pulseaudio.service\n\n[Service]\n Environment = KODI_AE_SINK=PULSE\n ExecStart=/usr/bin/kodi\n TimeoutSec=0\n StandardOutput=journal\n StandardError=journal\n Restart = on-abort\n RemainAfterExit=yes\n SysVStartPriority=99\n\n[Install]\n WantedBy=default.target\n' > ~/.config/systemd/user/kodi.service
	
	#enable pulseaudio
	systemctl --user daemon-reload
	systemctl --user enable pulseaudio.service
	systemctl --user enable pulseaudio.socket
	systemctl --user enable kodi.service	
	
	#enable user linger for john. this will load the user's systemd scripts at start up
	loginctl enable-linger john
	
	
	#configure samba to have public access to ~/.kodi folder 
	sudo mv /etc/samba/smb.conf /etc/samba/smb.conf.bk
	sudo bash -c "echo -e ""'[global]\n   workgroup = WORKGROUP\n   security = user\n   guest account = john\n   log file = /var/log/samba/log.%m\n   max log size = 1000\n   logging = file\n   panic action = /usr/share/samba/panic-action %d\n   server role = standalone server\n   obey pam restrictions = yes\n   unix password sync = yes\n   passwd program = /usr/bin/passwd %u\n   passwd chat = *Enter\snew\s*\spassword:* %n\n *Retype\snew\s*\spassword:* %n\n *password\supdated\ssuccessfully* .\n   pam password change = yes\n   map to guest = bad user\n   usershare allow guests = yes\n[kodi]\n   comment = kodi\n   path = /home/john/.kodi\n   available = yes\n   browsable = yes\n   writable = yes\n   create mask = 0766\n   directory mask = 0766\n   guest ok = yes\n   public = yes\n'"" > /etc/samba/smb.conf"
	
	#restart samba
	sudo service smbd restart
	
	#configure faster bootup
	sudo mv /etc/default/grub /etc/default/grub.bk
	sudo bash -c "echo -e ""'GRUB_HIDDEN_TIMEOUT_QUIET=true\nGRUB_TIMEOUT=0\nGRUB_CMDLINE_LINUX_DEFAULT="quiet"\nGRUB_CMDLINE_LINUX="quite"\nGRUB_RECORDFAIL_TIMEOUT=0'"" > /etc/default/grub"
	sudo update-grub
	
	#create pulseaudio user configuration
	mkdir -p ~/.config/pulse
	
	cp /etc/pulse/daemon.conf /etc/pulse/default.pa ~/.config/pulse/
	
	#create static filter
	echo -e 'load-module module-equalizer-sink sink_name=eq_1 sink_properties="device.description=EQ-1"\nload-module module-ladspa-sink sink_master=eq_1 sink_name=co_1 sink_properties="device.description=CO-1" plugin=sc4_1882 label=sc4 control=1,1.5,401,-20,20,5,15' >>  ~/.config/pulse/default.pa
	
	#finally reboot
	sudo reboot
	


*Allow Kodi to shutdown or reboot system* 

in /usr/share/polkit-1/actions/org.freedesktop.login1.policy, find sections

	<action id="org.freedesktop.login1.reboot">	
	and
	<action id="org.freedesktop.login1.power-off">

and change them to 
	
               <defaults>
                        <allow_any>yes</allow_any>
                        <allow_inactive>yes</allow_inactive>
                        <allow_active>yes</allow_active>
                </defaults>


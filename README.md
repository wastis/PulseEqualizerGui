# Kodi PulseEqualizer GUI Addon

Version 2.1.0 - beta

PulseEqualizer GUI is an addon that provides a pulsaudio configuration frontend for Kodi. 

This includes:
- Configuration of the pulseaudio equalizer with sliders
- Digital Room Correction for each channel
- Manage equalizer profiles (add, remove and change)
- Switch between equalizer profiles
- Configure latency-offset (for video/audio sync)
- Control system volume (needed if a compressor is used in the filter chain)
- Hotkey support for each

- tested on i386 Linux Mint / Debian 10 server / raspberry PI 3 OS v. May 7th 2021  

Supports Kodi 18 and 19


2021 wastis

![Pulse Equalizer](/resources/images/Equalizer.png)

# Installation

This addon requires pulseaudio-equalizer installed on the system

	sudo apt install pulseaudio-equalizer

If you run Kodi 18, the module python-dbus is required
	
	sudo apt install python-dbus

Since version 2.0.0 the modules "module-equalizer-sink" and "module-dbus-protocol" are loaded automatically when the addon is started, no need to configure pulseaudio for this.

## Install Addon in Kodi

Launch *Kodi >> Add-ons >> Get More >> .. >> Install from zip file*

## Configuration

In Kodi, select a pulseaudio hardware ouptut device and start a playback. Select an equalizer profile. The equalizer is then automatically inserted into the playback stream. 

With *Addon >> Manage Profiles >> Insert predefined Profiles*, it is possible to load a default profile set. 

For basic equalizer functionality, no further configuration is required. This is different to previous versions of the addon.   


# Advanced configuration (optional)

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
https://forum.kodi.tv/showthread.php?tid=365874

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

# Headless OS installations

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

To start pulseaudio run

	systemctl --user daemon-reload
	systemctl --user enable pulseaudio.service
	systemctl --user enable pulseaudio.socket
	systemctl --user start pulseaudio.service
	systemctl --user status pulseaudio.{service,socket}

### Autostart Kodi

### Debian 10 / 11
/etc/systemd/system/kodi.service

	[Unit]
	 Description=kodi startup service
	
	[Service]
	 Type=simple
	 ExecStart=su -c '/usr/bin/kodi' [username] &
	 TimeoutSec=0
	 StandardOutput=tty
	 RemainAfterExit=yes
	 SysVStartPriority=99
	
	[Install]
	 WantedBy=multi-user.target

where [username] is your user name.

	sudo systemctl enable kodi.service	

### Raspberry Pi
For raspberry PI, create a startup script to tell Kodi to use pulseaudio instead of alsa

/etc/systemd/system/kodi.service

	[Unit]
	 Description=kodi startup service
	
	[Service]
	 Type=simple
	 ExecStart=su -c 'KODI_AE_SINK=PULSE /usr/bin/kodi' pi &
	 TimeoutSec=0
	 StandardOutput=tty
	 RemainAfterExit=yes
	 SysVStartPriority=99
	
	[Install]
	 WantedBy=multi-user.target


## Raspberry specials

If you install Kodi on the headless OS Lite, you might want to increase the video memory from 64MB to 256MB to avoid crashes. 

#### Raspberry PI 3 performance

Pulseaudio with equalizer enabled consumes about 20% of one CPU core. 

#### LibreELEC, OSMC and OpenELEC
 
To my knowledge, to date, those distributions do not have module-equalizer-sink included in their minimal system, so the PulseEqualizer GUI Addon might not run. 

# Finally
Enjoy

Feel free to ask any questions in the Kodi Forums.

https://forum.kodi.tv/showthread.php?tid=360514


THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

### Kodi on Debian 11 and equalizer fresh install walk through

Install Debian without desktop environment but with ssh and a user named e.g. "john"

	#
	# console login as root
	#
	apt update
	
	# basic tools
	apt install sudo net-tools
	
	# add john to the required groups 
	usermod -a -G sudo,input,pulse john
	
	#check ip address
	ifconfig
	exit
	
	#
	# ssh-login as user (ssh john@ip)
	#
		
	#install required packages
	sudo apt install vim samba kodi pulseaudio pulseaudio-equalizer swh-plugins
	
	#disable vim visuell mode
	echo "set mouse-=a" >> ~/.vimrc
	
	#prepare pulseaudio startup in user session
	mkdir -p ~/.config/systemd/user/
		
	#create pulseaudio.service	
	echo -e '[Unit]\nDescription=Pulseaudio Sound Service\nRequires=pulseaudio.socket\n\n[Service]\nType=notify\nExecStart=/usr/bin/pulseaudio --verbose --daemonize=no\nRestart=on-failure\n\n[Install]\nAlso=pulseaudio.socket\nWantedBy=default.target\n' > ~/.config/systemd/user/pulseaudio.service
	
	#create pulseaudio.socket	
	echo -e '[Unit]\nDescription=Pulseaudio Sound System\n\n[Socket]\nPriority=6\nBacklog=5\nListenStream=%t/pulse/native\n\n[Install]\nWantedBy=sockets.target\n' > ~/.config/systemd/user/pulseaudio.socket
	
	#enable pulseaudio
	systemctl --user daemon-reload
	systemctl --user enable pulseaudio.service
	systemctl --user enable pulseaudio.socket
	systemctl --user start pulseaudio.service
	
	#configure samba to have public access to ~/.kodi folder 
	sudo mv /etc/samba/smb.conf /etc/samba/smb.conf.bk
	sudo bash -c "echo -e ""'[global]\n   workgroup = WORKGROUP\n   security = user\n   guest account = john\n   log file = /var/log/samba/log.%m\n   max log size = 1000\n   logging = file\n   panic action = /usr/share/samba/panic-action %d\n   server role = standalone server\n   obey pam restrictions = yes\n   unix password sync = yes\n   passwd program = /usr/bin/passwd %u\n   passwd chat = *Enter\snew\s*\spassword:* %n\n *Retype\snew\s*\spassword:* %n\n *password\supdated\ssuccessfully* .\n   pam password change = yes\n   map to guest = bad user\n   usershare allow guests = yes\n[kodi]\n   comment = kodi\n   path = /home/john/.kodi\n   available = yes\n   browsable = yes\n   writable = yes\n   create mask = 0766\n   directory mask = 0766\n   guest ok = yes\n   public = yes\n'"" > /etc/samba/smb.conf"
	
	#restart samba
	sudo service smbd restart
	
	#configure faster bootup
	sudo mv /etc/default/grub /etc/default/grub.bk
	sudo bash -c "echo -e ""'GRUB_HIDDEN_TIMEOUT_QUIET=true\nGRUB_TIMEOUT=0\nGRUB_CMDLINE_LINUX_DEFAULT="quiet"\nGRUB_CMDLINE_LINUX="quite"\nGRUB_RECORDFAIL_TIMEOUT=0'"" > /etc/default/grub"
	sudo update-grub
	
	#create Kodi startup script
	sudo bash -c "echo -e ""'[Unit]\n Description=kodi startup service\n\n[Service]\n Type=simple\n ExecStart=su -c '/usr/bin/kodi' john &\n TimeoutSec=0\n StandardOutput=tty\n RemainAfterExit=yes\n SysVStartPriority=99\n\n[Install]\n WantedBy=multi-user.target'"" > /etc/systemd/system/kodi.service"
	
	# enable kodi startup
	sudo systemctl enable kodi.service
	
	
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


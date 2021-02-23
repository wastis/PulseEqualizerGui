Kodi PulseEqualizer GUI Addon

PulseEqualizer GUI is an addon that provides configuration frontend for Kodi. 

This includes:
- Configuration of the equalizer with sliders
- Manage equalizer profiles (add, remove and change)
- Switch between equalizer profiles
- Switch equalizer to specific output device and port
- Hotkey support for each

Supports Kodi 18 and 19

2021 wastis


Installation

Requires pulseaudio-equalizer installed on the system

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


Install Addon in Kodi

Launch Kodi >> Add-ons >> Get More >> .. >> Install from zip file

Configuration

In Kodi, select the Equalizer as output for Kody

	System->Audio->Audio Output Device --- select "FFT-based-equalizer...."

Configure the Addon to stream to a Device

	Start Addon and Menuentry "Select Output Device"


Configure Hotkeys

The following will enable the keyboard keys l,m,n and o to lauch the different modules.

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


Enjoy


See https://forum.kodi.tv/showthread.php?tid=360514

Feel free to ask any questions on the Kodi Forums.

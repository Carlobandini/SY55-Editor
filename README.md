SY-55 VOICE EDITOR
------------------

When I bought a Yamaha sy55, I noticed that there was not a decent voice / drum editor, so i decided to build it by myself.

I coded it entirely in python, so it can be executed from the zipped binaries for Windows, Mac Silicon and Mac Intel or from the source if having all the dependences installed.

I don't have a lot of time to test and debug, any help is appreciated.

File list:
* source: the python source code folder.
* LICENSE: The BSD new License.
* README.md: this text file.
* mac intel.zip: Mac Intel executable (working on Monterey)
* windows.zip: Windows 10/11 executable

Python dependencies:
Tested and working on python 3.11 - 3.12.
* dearpygui (pip install dearpygui)
* mido (pip install mido)
* mido backends rtmidi (pip install python-rtmidi) --> be sure to don't "pip install rtmidi", since it will not work !!.
* filedialpy (pip install filedialpy)

MANUAL:
-------

--- USING THE SOFTWARE --- 

This software works in two different modes: Voice and drum set, having each of them different parameters to edit.

In both modes, the main window is divided in two parts; the upper part shows the parameters that are common to the voices with 1,2 or 4 elements and drum sets, 
however, not all the controllers are available in the drum set mode.

The lower area is divided by tabs containing the elements, drums and controllers used by the current patch.

* The tabs will change depending on the elements number and the patch mode.

Each element tab contain the same parameters and is divided in 4 sections vertically: 

1- Wave and volume, including element on/off, pan and effect balance.

2- Pitch parameters.

3- Filters.

4- This window is also divided in two sections: Note and Vel limit (left), and LFO (right)

* For more info. about the synthesizer parameters, please consult the SY55 manual.

It is possible to copy / paste patchs and elements, as well as saving and loading patches in your computer.

When the SY55 is connected, when a parameter is edited on the screen, it will change in the SY55 immediately, so you can hear the changes on real time.

The computer keyboard can be used as a controller as follows: 

'Z','S','X','D','C','V','G','B','H','N','J','M': Notes C to B

'Q','2','W','3','E','R','5','T','6','Y','7','U': Notes C to B + 1 octave

'I','9','O','0','P','[','=',']': Notes C to G + 2 octaves

'+': octave up

'-': octave dowm

* The keyboard control is polyphonic and sends note on / note off signals.

--- MENUS --- 

FILE: 
Includes load patch, save patch and to exit the program.

* The patches can have any extensions and can be saved and loaded from anywhere in your computer, network or external drives.

* Since there is a difference between the voice and drum sets, The drum patches cannot be loaded when a voice patch is selected on the synthesizer, and vice-versa.

* The drum presets in the SY55 are limited to the programs number 63 and 64.

* When editing a drum set, most of the parameters will change.

PATCH:
Request current patch: Loads the SY55 edit buffer into the software controls.

Request on start: When this option is active, is marked with a (*), and the patch is requested everytime the software starts.

Initialize patch: Reset the patch loading the default values.

ELEMENT:
This menu has the actions to copy, paste and initialize an element to the default values. 

* This menus are not available in drum set mode.

MIDI:
Reset midi configuration: Resets the stored midi controllers info. and reads all the midi inputs and outputs.

Reset midi device: Reset the current midi input and output.

Midi input: Set up a midi input

Midi output: Set up a midi output

* When a midi input / output is selected, it is saved on the preferences and will be loaded everytime the software starts.

HELP: This menu.

--- CREDITS ---

Programming and testing: Carlo Bandini, 2024.

carlobandini@gmail.com

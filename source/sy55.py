'''
Copyright 2024 Carlo Bandini

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the 
documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this 
software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE 
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE 
GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT 
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''
import mido
import mido.backends.rtmidi
import sys
import os
import dearpygui.dearpygui as dpg
import time
import math
import filedialpy
import json

# # Set path
application_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(application_path) 

####################################################### Define variables #######################################################
global outport, inport, outdevicelist, indevicelist, mouserelease, previous, requestok, NoWriteRequest, copyel, nosend, EL, elnumber, ELCOPY, OCTAVE

requestok = 0 # Read the knob values from the request instead of the mouse input.
NoWriteRequest = 0 # : Request datalist from the keyboard without drawing the knobs
previous = 0 # previous position of the knob, to add new values when draggin the mouse instead of reseting it.
mouserelease = 1 # mouse button is released
OCTAVE = 48 # keyboard input octave
key = [] # array of keys from the keyboard input
ELCOPY =-1 # Element that is being copied
elnumber = 4 # number of elements (1,2,4, 0=drums)
EL = 'el1' # Selected element to draw.
copyel = 0 # While copying an element do or not certain actions.
nosend = 0 # Opposite to Nowriterequest, draw the controls in the softwer from the datalist but don't send them to the keyboard.
prefdir='files/prefs'
outport = '' # selected midi out
inport = '' # selected midi in
loading = 0 # When loading an instrument don't do certain things.

indevicelist = mido.get_input_names() # list of midi input devices
outdevicelist = mido.get_output_names() # list of midi output devices
INI = 'F0 43 1F 35 ' # first part of the sysex message (hex)
END = ' F7' # last part of the sysex message (hex)

# Controllers list
controllerlist = ['00:','01: MODULATION','02: BREATH CTRL.','03:','04: FOOT CTRL.','05: PORTAMENTO TM.','06: DATA ENTRY','07: VOLUME','08: BALANCE','09:','10: PAN','11: EXPRESSION',]
for i in range(12,64):
    controllerlist.append((str(i).zfill(2))+':')
controllerlist.extend(['64: HOLD 1','65: PORTAMENTO SW.','66: SOSTENUTO','67: SOFT PEDAL','68:','69: HOLD 2'])
for i in range(70,91):
    controllerlist.append(str(i)+':')
controllerlist.extend(['91: EFFECT SW.','92: TREMOLO','93: CHORUS','94: CELESTE','95: PHASER','96: INCREMENT','97: DECREMENT',
                       '98: NR.PARAM. LSB','99: NR.PARAM. MSB','100: REG.PARAM. LSB','101: REG.PARAM. MSB'])
for i in range(102,121):
    controllerlist.append(str(i)+':')
controllerlist.append('AFTER TOUCH')
# Effects list
effectslist = ['1: Rev.Hall','2: Rev.Room','3: RevPlate','4: RevChrch','5: Rev.Club','6: RevStage','7: BathRoom','8: RevMetal','9: Delay','10: DelayL/R','11: St.Echo','12: Doubler1',
               '13: Doubler2','14: PingPong','15: Pan Ref.','16: EarlyRef','17: Gate Rev','18: Rvs Gate','19: FB E/R','20: FB Gate','21: FB Rvs','22: Dly1&Rev','23: Dly2&Rev',
               '24: Tunnel','25: Tone 1','26: Dly1&T1','27: Dly2&T1','28: Tone 2','29: Dly1&T2','30: Dly2&T2','31: Dist&Rev','32: Dst&Dly1','33: Dst&Dly2','34: Dist.']
# AWM voice list
voicelist = ['1: Piano','2: E.Piano1','3: E.Piano2','4: E.Piano3','5: E.Piano4','6: E.Piano5','7: E.Piano6','8: E.Piano7','9: Harpsi','10: Organ 1','11: Organ 2','12: Pipe',
             '13: Trumpet','14: Mute Tp','15: Trombone','16: Flugel','17: Sax','18: Flute','19: Brass','20: SynBrass','21: GtrSteel','22: Gtr Gut','23: 12String','24: E.Guitar',
             '25: E.Bass','26: Popping','26: WoodBass','28: Syn Bass','29: Violin','30: Strings','31: Chorus','32: Itopia','33: Vibe','34: Marimba','35: Glocken','36: Shamisen',
             '37: Harp','38: Mtl Reed','39: Saw','40: Digital1','41: Digital2','42: Digital3','43: Pulse10','44: Pulse25','45: Pulse50','46: Tri','47: Voice','48: Piano Np',
             '49: EpianoNp','50: Vibe Np','51: Bottle','52: Tuba','53: Vocal Ga','54: Bamboo','55: Noise','56: Styroll','57: Bulb','58: Bell Mix','59: BD 1','60: BD 2','61: BD 3',
             '62: SD 1','63: SD 2','64: SD 3','65: Rim','66: Tom 1','67: Tom 2','68: HHclosed','69: HH open','70: Crash','71: Ride','72: Claps','73: Cowbell','74: Shaker']
# drum voice list
drumvoicelist = ['********']
for i in range(len(voicelist)):
    drumvoicelist.append(voicelist[i].split(': ')[1])
# interface images
imageslist = ['LOGO','REDLIGHT','LPF','HPF','NOFILTER','TRI','SAWDOWN','SAWUP','SQUARE','SINE','S-H','DOT','KNOB']
# LFO mode
modeslist = ['TRI','DWN','UP','SQU','SIN','S/H']
# amp envelope points
ampenvlist = ['R1','R2','L2','R3','L3','R4','RR']
# pitch envelope points
pitchenvlist = ['L0','R1','L1','R2','L2','R3','L3','RR','RL']
# filter envelope points
filterenvlist = ['L0','R1','L1','R2','L2','R3','L3','R4','L4','RR1','RL1','RR2','RL2']
# knobs list, to apply the knobs theme
knoblist = ['pan','efbal','ampvelsens','ampmodsens','noteshift','detune','oscfreqtune','pitchmodsens','filtervelsens','filtermodsens','lfospeed','lfodelay','lfophase','lfoampmod','lfopitchmod','lfocutoffmod']
# keyboard input keys list
if sys.platform == 'darwin':
    keyplaylist = ['Z','S','X','D','C','V','G','B','H','N','J','M','Q','2','W','3','E','R','5','T','6','Y','7','U','I','9','O','0','P','[','=',']']
if sys.platform == 'win32':
    keyplaylist = ['Ȼ','ȴ','ȴ','ȥ','Ȥ','ȷ','Ȩ','ȣ','ȩ','ȯ','ȫ','Ȯ','Ȳ','Ț','ȸ','ț','Ȧ','ȳ','ȝ','ȵ','Ȟ','Ⱥ','ȟ','ȶ','Ȫ','ȡ','Ȱ','Ș','ȱ','ɛ','ɚ','ɝ']
# all available notes list for voice
scale = ['C', 'C#','D','D#','E','F','F#','G','G#','A','A#','B'] # 1 scale
notelist = []
for i in range(-2,9,1):
    for a in range(12):
        value = str(scale[a]+str(i))
        notelist.append(value)
        if value == 'G8':
            break
# all available notes list for drums
drumnotelist = []
for i in range(1,6):
    for a in range(12):
        value = str(scale[a]+str(i))
        drumnotelist.append(value)
drumnotelist.append('C6')
# Envelopes location
AmpHini, AmpVini, VHSum = 578, 75, 63
PitchHini, PitchVini = 578, 256
FilterHini, FilterVini = 516, 80
# KNOBS POSITION
panknobx,panknoby = 58,128
efbalknobx, efbalknoby = 125,128
ampvelsensknobx, ampvelsensknoby = 207,128
ampmodsensknobx, ampmodsensknoby = 298,128
noteshiftknobx, noteshiftknoby = 150,226
detuneknobx, detuneknoby = 150,310
oscfreqtuneknobx, oscfreqtuneknoby = 240,226
pitchmodsensknobx, pitchmodsensknoby = 240,310
filtervelsensknobx, filtervelsensknoby = 78,420
filtermodsensknobx, filtermodsensknoby = 78,505
lfospeedknobx, lfospeedknoby = 640,610
lfodelayknobx, lfodelayknoby = 735,610
lfophaseknobx, lfophaseknoby = 830,610
lfoampmodknobx, lfoampmodknoby = 925,610
lfopitchmodknobx, lfopitchmodknoby = 1020,610
lfocutoffmodknobx, lfocutoffmodknoby = 1115,610

####################################################### MOUSE CALLBACKS ########################################################
def mouseclickCallback():
    global mouseclickx, mouseclicky
    mouseclickx, mouseclicky = dpg.get_mouse_pos(local=False)
    mouselocx, mouselocy = dpg.get_mouse_pos(local=True)

def mousedownCallback():
    global mouseposx, mouseposy
    # si tenemos un element tab activo
    mouseposx, mouseposy = dpg.get_mouse_pos(local=False)
    y = mouseposy - mouseclicky
    if dpg.get_value(item='controllers') == False: 
        if panknobx < mouseclickx < panknobx+50 and panknoby+161-20 < mouseclicky < panknoby+161+28:
            elpan(y)
        if efbalknobx < mouseclickx < efbalknobx+50 and efbalknoby+161-20 < mouseclicky < efbalknoby+161+28:
            elefxbalance(y)
        if ampvelsensknobx < mouseclickx < ampvelsensknobx+50 and ampvelsensknoby+161-20 < mouseclicky < ampvelsensknoby+161+28:
            elampvelsens(y)
        if ampmodsensknobx < mouseclickx < ampmodsensknobx+50 and ampmodsensknoby+161-20 < mouseclicky < ampmodsensknoby+161+28:
            elampmodsens(y)
        if noteshiftknobx < mouseclickx < noteshiftknobx+50 and noteshiftknoby+161-20 < mouseclicky < noteshiftknoby+161+28:
            elnoteshift(y)
        if detuneknobx < mouseclickx < detuneknobx+50 and detuneknoby+161-20 < mouseclicky < detuneknoby+161+28:
            eldetune(y)
        if oscfreqtuneknobx < mouseclickx < oscfreqtuneknobx+50 and oscfreqtuneknoby+161-20 < mouseclicky < oscfreqtuneknoby+161+28:
            eloscfreqtune(y)       
        if pitchmodsensknobx < mouseclickx < pitchmodsensknobx+50 and pitchmodsensknoby+161-20 < mouseclicky < pitchmodsensknoby+161+28:
            elpitchmodsens(y)  
        if lfospeedknobx < mouseclickx < lfospeedknobx+50 and lfospeedknoby+161-20 < mouseclicky < lfospeedknoby+161+28:
            ellfospeed(y)  
        if lfodelayknobx < mouseclickx < lfodelayknobx+50 and lfodelayknoby+161-20 < mouseclicky < lfodelayknoby+161+28:
            ellfodelay(y)
        if lfophaseknobx < mouseclickx < lfophaseknobx+50 and lfophaseknoby+161-20 < mouseclicky < lfophaseknoby+161+28:
            ellfophase(y)
        if lfoampmodknobx < mouseclickx < lfoampmodknobx+50 and lfoampmodknoby+161-20 < mouseclicky < lfoampmodknoby+161+28:
            ellfoampmod(y)
        if lfopitchmodknobx < mouseclickx < lfopitchmodknobx+50 and lfopitchmodknoby+161-20 < mouseclicky < lfopitchmodknoby+161+28:
            ellfopitchmod(y)
        if lfocutoffmodknobx < mouseclickx < lfocutoffmodknobx+50 and lfocutoffmodknoby+161-20 < mouseclicky < lfocutoffmodknoby+161+28:
            ellfocutoffmod(y)
        if dpg.get_value(item='el1_FILTER12') == True or dpg.get_value(item='el2_FILTER12') == True or dpg.get_value(item='el3_FILTER12') == True or dpg.get_value(item='el4_FILTER12') == True:        
            if filtervelsensknobx < mouseclickx < filtervelsensknobx+50 and filtervelsensknoby+161-20 < mouseclicky < filtervelsensknoby+161+28:
                elfiltervelsens(y)  
            if filtermodsensknobx < mouseclickx < filtermodsensknobx+50 and filtermodsensknoby+161-20 < mouseclicky < filtermodsensknoby+161+28:
                elfiltermodsens(y)  

def mousereleaseCallback():
    global mouserelease, EL
    for i in range(4):
        if dpg.get_value(item='el'+str(i+1)+'_tab') == True:
            EL = 'el'+str(i+1)
    mouserelease = 1

######################################################## KEY CALLBACKS #########################################################
def keydownCallback(sender,app_data):
    global key
    # detect output port
    if outport == '':
        dpg.configure_item(item = 'interface_error', show=True)
        return
    if dpg.is_item_focused('voice_name') == True:
        return
    keyascii = chr(app_data[0])
    if keyascii in key:
        return
    # ignore any other keys
    if keyascii not in keyplaylist:
        if keyascii not in ['+','-']:
            return
    key.append(keyascii)
    if keyascii in keyplaylist:
        NUM = (keyplaylist.index(keyascii))
        if OCTAVE+NUM >127:
            return
        outport.send(mido.Message('note_on', channel=0, note=OCTAVE+NUM, velocity=64, time=0))

def keyreleaseCallback(sender,app_data):
    global OCTAVE, key
    # octave up
    if app_data == 334 and OCTAVE < 108:
        OCTAVE = OCTAVE + 12
        key = []
        for i in range(128):
            outport.send(mido.Message('note_off', channel=0, note=i, velocity=64, time=0))
    # octave down
    if app_data == 333 and OCTAVE > 0:
        OCTAVE = OCTAVE - 12
        key = []
        for i in range(128):
            outport.send(mido.Message('note_off', channel=0, note=i, velocity=64, time=0))
    # 
    if dpg.is_item_focused('voice_name') == True:
        return
    keyascii = chr(app_data)
    try:
        key.remove(keyascii)
    except ValueError:
        return
    if keyascii in keyplaylist:
        NUM = (keyplaylist.index(keyascii))
        if OCTAVE+NUM >127:
            return
        outport.send(mido.Message('note_off', channel=0, note=OCTAVE+NUM, velocity=64, time=0))

########################################################## VOICE EDIT ##########################################################
def voicemode(sender):
    global elnumber
    PARAM = '02 00 00 00 00 '
    decvalue = dpg.get_value(sender)
    if decvalue == '1 Element':
        VALUE = '05'
        elnumber = 1
        dpg.configure_item(item='el2_tab', show = False)
        dpg.configure_item(item='el3_tab', show = False)
        dpg.configure_item(item='el4_tab', show = False)
    if decvalue == '2 Elements':
        VALUE = '06'
        elnumber = 2
        dpg.configure_item(item='el2_tab', show = True)
        dpg.configure_item(item='el3_tab', show = False)
        dpg.configure_item(item='el4_tab', show = False)
    if decvalue == '4 Elements':
        VALUE = '07'
        elnumber = 4
        dpg.configure_item(item='el2_tab', show = True)
        dpg.configure_item(item='el3_tab', show = True)
        dpg.configure_item(item='el4_tab', show = True)
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)
    changemode()

def voicevolume(sender):
    PARAM = '02 00 00 22 00 '
    decvalue = dpg.get_value(sender)
    VALUE = (hex(decvalue)[2:].zfill(2)).upper() # 00 TO 7F (0 TO 127)
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)
 
def voicename(sender):
    text = dpg.get_value('voice_name')
    if len(text) > 10:
        text = text[:10]
        dpg.set_value('voice_name', text)

    for i in range(10):
        POSITION = (hex(i+1)[2:].zfill(2)).upper()
        PARAM = '02 00 00 ' + POSITION + ' 00 '
        if i < len(text):
            valuetext = text[i]
        else:
            valuetext = ' '
        valueascii = ord(valuetext)
        VALUE = (hex(valueascii)[2:].zfill(2)).upper()
        MESSAGE = INI+PARAM+VALUE+END
        if nosend == 0:
            sendmessage(MESSAGE)
        # [space]!'#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[¥]^_`abcdefghijklmnopqrstuvwxyz{|}→←

def pitchbendrange(sender):
    PARAM = '02 00 00 10 00 '
    decvalue = dpg.get_value(sender)
    VALUE = (hex(decvalue)[2:].zfill(2)).upper()  # 00 TO 0C (0 TO 12)
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)

def aftertouchpitchbias(sender):
    PARAM = '02 00 00 11 00 '
    decvalue = dpg.get_value(sender)
    if decvalue <0:
        decvalue = abs(decvalue) + 16
    VALUE = (hex(decvalue)[2:].zfill(2)).upper()
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)
    # # 11, 12, 13, 14, 15, 16, 17, 18, 19, 1A, 1B, 1C (-1 TO -12)
    # # 00 (0)
    # # 01, 02, 03, 04, 05, 06, 07, 08, 09, 0A, 0B, 0C (+1 TO +12)

def randompitchrange(sender):
    PARAM = '02 00 00 20 00 '
    decvalue = dpg.get_value(sender)
    VALUE = '0' + str(int(decvalue)) # 00 TO 07
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)

def effecttype(sender):
    global param1range,param2range,param3range, NoWriteRequest, loading
    PARAM = '08 00 00 00 00 '
    decvalue = dpg.get_value(sender)
    i = effectslist.index(decvalue)
    VALUE = (hex(i+1)[2:].zfill(2)).upper()
    if elnumber == 0:
        MESSAGE = 'F0 43 10 35 ' + PARAM + VALUE + END # drums: F0 43 10 35 08 00 00 00 00 VALUE F7
    else:
        MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)

    # 1: Rev.Hall 2: Rev.Room 3: RevPlate 4: RevChrch 5: Rev.Club 6: RevStage 7: BathRoom 8: RevMetal 9: Delay
    # 10: DelayL/R 11: St.Echo 12: Doubler1 13: Doubler2 14: PingPong 15: Pan Ref. 16: EarlyRef 17: Gate Rev 
    # 18: Rvs Gate 19: FB E/R 20: FB Gate 21: FB Rvs 22: Dly1&Rev 23: Dly2&Rev 24: Tunnel 25: Tone 1 
    # 26: Dly1&T1 27: Dly2&T1 28: Tone 2 29: Dly1&T2 30: Dly2&T2 31: Dist&Rev 32: Dst&Dly1 33: Dst&Dly2 34: Dist.
    # PARAMETRO 1 NOMBRE
    if i+1 in (1,2,3,4,5,6,7,8,22,23,24,31):
        dpg.set_value('Param1_title','EF\Time: sec')
    if i+1 in (9,14,32,33):
        dpg.set_value('Param1_title','EF\Time: ms')
    if i+1 in (10,11,13):
        dpg.set_value('Param1_title','EF\Lch Delay: ms')
    if i+1 == 12:
        dpg.set_value('Param1_title','EF\Delay: ms')
    if i+1 in (15,16,17,18,19,20,21):
        dpg.set_value('Param1_title','EF\Room Size')
    if i+1 == 25:
        dpg.set_value('Param1_title','EF\Low: db')
    if i+1 in (26,27,29,30):
        dpg.set_value('Param1_title','EF\Brilliance')
    if i+1 == 28:
        dpg.set_value('Param1_title','EF\HPF: Hz')
    if i+1 == 34:
        dpg.set_value('Param1_title','EF\Level: %')
    
    # PARAMETRO 1 - RANGE
    if i+1 in (1,2,3,4,5,6,7,8,22,23,24,31):
        param1range = ['0.3']
        for a in range(4, 21):
            param1range.append(str(a/10))
        for a in range(22, 42,2):
            param1range.append(str(a/10))
        for a in range(45, 75,5):
            param1range.append(str(a/10))
        param1range.extend(['8.0','9.0','10.0'])
    if i+1 in (9,10,32,33):
        param1range = ['0.1']
        for a in range(4,301,4):
            param1range.append(str(a))
    if i+1 in (11,14):
        param1range = ['0.1']
        for a in range(4,153,4):
            param1range.append(str(a))
    if i+1 in (12,13):
        param1range = ['0.1']
        for a in range(5,501,5):
            param1range.append(str(a/10))
    if i+1 in (15,16,17,18,19,20,21):
        param1range = ['0.5']
        for a in range(6,33):
            param1range.append(str(a/10))
    if i+1 == 25:
        param1range = ['-12']
        for a in range (1,25):
            param1range.append(str(a-12))
    if i+1 in (26,27,29,30):
        param1range = ['0']
        for a in range (1,13):
            param1range.append(str(a))
    if i+1 == 28:
        param1range = ['thru', '160','250','315','400','500','630','800','1000']
    if i+1 == 34:
        param1range = ['0']
        for a in range (1,101):
            param1range.append(str(a))

    # PARAMETRO 2 NOMBRE
    if i+1 in (1,2,3,4,5,6,7,8,16,17,18,19,20,21):
        dpg.set_value('Param2_title','EF\LPF: Khz')
    if i+1 in (9,22,24,26,27,29,30):
        dpg.set_value('Param2_title','EF\LPF: Khz')
    if i+1 in (10,11,13):
        dpg.set_value('Param2_title','EF\Rch Delay: ms')
    if i+1 in (12,34):
        dpg.set_value('Param2_title','EF\HPF: Hz')
    if i+1 == 14:
        dpg.set_value('Param2_title','EF\Pre Delay: ms')
    if i+1 in (15,32,33):
        dpg.set_value('Param2_title','EF\FB Gain %')
    if i+1 == 23:
        dpg.set_value('Param2_title','EF\Lch Delay: ms')
    if i+1 in (25,28):
        dpg.set_value('Param2_title','EF\Mid: db')
    if i+1 == 31:
        dpg.set_value('Param2_title','EF\Depth: %')

    # PARAMETRO 2 - RANGE
    if i+1 in (1,2,3,4,5,6,7,8,16,17,18,19,20,21):
        param2range = ['1.25','1.6','2.0','2.5','3.15']
        for a in range(4, 13):
            param2range.append(str(a))
        param2range.append('thru')
    if i+1 in (9,10,26,27,29,30):
        param2range = ['0.1']
        for a in range(4,301,4):
            param2range.append(str(a))
    if i+1 in (11,14,22,23,24):
        param2range = ['0.1']
        for a in range(4,153,4):
            param2range.append(str(a))
    if i+1 in (12,34):
        param2range = ['thru', '160','250','315','400','500','630','800','1000']
    if i+1 == 13:
        param2range = ['0.1']
        for a in range(5,501,5):
            param2range.append(str(a/10))        
    if i+1 in (15,32,33):
        param2range = ['0']
        for a in range(1,100):
            param2range.append(str(a))   
    if i+1 in (25,28):
        param2range = ['-12']
        for a in range (1,25):
            param2range.append(str(a-12))     
    if i+1 == 31:
        param2range = ['0']
        for a in range(1,101):
            param2range.append(str(a))      
        
    # PARAMETRO 3 NOMBRE
    if i+1 in (1,2,3,4,5,6,7,8,16,17,18):
        dpg.set_value('Param3_title','EF\Delay: ms')
    if i+1 in (9,10,11,14,19,20,21,22,24,26,27,29,30):
        dpg.set_value('Param3_title','EF\FB Gain %')
    if i+1 in (12,13,28,34):
        dpg.set_value('Param3_title','EF\LPF: Khz')
    if i+1 == 15:
        dpg.set_value('Param3_title','EF\Direction')
    if i+1 == 23:
        dpg.set_value('Param3_title','EF\Rch Delay: ms')
    if i+1 == 25:
        dpg.set_value('Param3_title','EF\High: db')
    if i+1 == 31:
        dpg.set_value('Param3_title','EF\Balance %')
    if i+1 in (32,33):
        dpg.set_value('Param3_title','EF\Depth: %')

    # PARAMETRO 3 - RANGE
    if i+1 in (1,2,3,4,5,6,7,8,16,17,18):
        param3range = ['0.1']
        for a in range(10,501,10):
            param3range.append(str(a/10))        
    if i+1 in (9,10,11,14,19,20,21,22,24,26,27,29,30):
        param3range = ['0']
        for a in range(1,100):
            param3range.append(str(a))   
    if i+1 in (12,13,28,34):
        param3range = ['1.25','1.6','2.0','2.5','3.15']
        for a in range(4, 13):
            param3range.append(str(a))
        param3range.append('thru')
    if i+1 == 15:
        param3range = ['L->R','R->L']
    if i+1 == 23:
        param3range = ['0.1']
        for a in range(4,153,4):
            param3range.append(str(a))
    if i+1 == 25:
        param3range = ['-12']
        for a in range (1,25):
            param3range.append(str(a-12))     
    if i+1 in (31,32,33):
        param3range = ['0']
        for a in range(1,101):
            param3range.append(str(a))   

    dpg.configure_item(item='param1_slider', max_value = len(param1range)-1)
    dpg.configure_item(item='param2_slider', max_value = len(param2range)-1)
    dpg.configure_item(item='param3_slider', max_value = len(param3range)-1)

    if loading == 1:
        return

    if nosend == 0:
        NoWriteRequest = 1
        # update midi prefs
        checkmidiprefs()
        requestvoice()

    try:
        parameter1 = int(datalist[44],16)
        parameter2 = int(datalist[45],16)
        parameter3 = int(datalist[46],16)
        # break
    except:
        dpg.configure_item('midi_error', show=True)
        return
        
    dpg.configure_item(item='param1_slider', default_value = parameter1)
    dpg.configure_item(item='param2_slider', default_value = parameter2)
    dpg.configure_item(item='param3_slider', default_value = parameter3)
    dpg.configure_item(item='param1_value', default_value = param1range[parameter1])
    dpg.configure_item(item='param2_value', default_value = param2range[parameter2])
    dpg.configure_item(item='param3_value', default_value = param3range[parameter3])

def effectlevel(sender):
    PARAM = '08 00 00 01 00 '
    decvalue = dpg.get_value(sender)
    VALUE = (hex(decvalue)[2:].zfill(2)).upper() # 00 TO 64 (0 TO 100%)
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)

def effectparam1(sender):
    if dpg.get_value('effect_type') == '':
        return
    slidervalue = int(dpg.get_value(sender))
    value = param1range[slidervalue]
    posX = 708-(3*len(value))
    dpg.configure_item(item='param1_value', default_value = value, pos = (posX,29))
    PARAM = '08 00 00 02 00 '
    VALUE = (hex(slidervalue)[2:].zfill(2)).upper() # Each Efx has a different VALUE RANGE
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)

def effectparam2(sender):
    if dpg.get_value('effect_type') == '':
        return
    slidervalue = int(dpg.get_value(sender))
    value = param2range[slidervalue]
    posX = 708-(3*len(value))
    dpg.configure_item(item='param2_value', default_value = value, pos = (posX,69))
    PARAM = '08 00 00 03 00 '
    VALUE = (hex(slidervalue)[2:].zfill(2)).upper() # Each Efx has a different VALUE RANGE
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)

def effectparam3(sender):
    if dpg.get_value('effect_type') == '':
        return
    slidervalue = int(dpg.get_value(sender))
    value = param3range[slidervalue]
    posX = 708-(3*len(value))
    dpg.configure_item(item='param3_value', default_value = value, pos = (posX,109))
    PARAM = '08 00 00 04 00 '
    VALUE = (hex(slidervalue)[2:].zfill(2)).upper() # Each Efx has a different VALUE RANGE
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)
 
######################################################## ELEMENTS EDIT ######################################################### 
def elementenable(sender):
    PARAM = '02 00 00 7F 00 '
    x1,x2,x3,x4 = 0,0,0,0
    if dpg.get_value('el1_enable') == True:
        x1 = 1
        dpg.configure_item('el1_enabled', show=True)
    else:
        dpg.configure_item('el1_enabled', show=False)
    if dpg.get_value('el2_enable') == True:
        x2 = 2  
        dpg.configure_item('el2_enabled', show=True)
    else:
        dpg.configure_item('el2_enabled', show=False)
    if dpg.get_value('el3_enable') == True:
        x3 = 4
        dpg.configure_item('el3_enabled', show=True)
    else:
        dpg.configure_item('el3_enabled', show=False)
    if dpg.get_value('el4_enable')== True:
        x4 = 8
        dpg.configure_item('el4_enabled', show=True)
    else:
        dpg.configure_item('el4_enabled', show=False)

    decvalue = x1+x2+x3+x4 
    VALUE = (hex(decvalue)[2:].zfill(2)).upper() # bin: 0,0,0,0,e3,e2,e1,e0 (on=1, off=0)
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)       

def AWMwaveform(sender):
    ELEMENT = str(int(EL[2:3])-1)+'0' # 00,10,20,30
    PARAM = '07 ' + ELEMENT + ' 00 01 00 '
    name = dpg.get_value(sender)
    VALUE = (hex(voicelist.index(name))[2:].zfill(2)).upper()
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)  

def elementvol(sender):
    ELEMENT = str(int(sender[2:3])-1)+'0' # 00,10,20,30
    PARAM = '03 ' + ELEMENT + ' 00 00 00 '
    decvalue = dpg.get_value(sender)
    VALUE = (hex(decvalue)[2:].zfill(2)).upper() # 00 TO 7F (0 TO 127)
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)

def elpan(sender):
    global mouserelease, previous
    ELEMENT = str(int(EL[2:3])-1)+'0' # 00,10,20,30
    PARAM = '03 ' + ELEMENT + ' 00 07 00 '
    if mouserelease == 1:
        previous = float(dpg.get_value(item='el'+EL[2:3]+'_pan_value'))*3.174
        mouserelease = 0
    pos = -int(sender)+previous
    if pos > 100:
        pos = 100
    if pos < -100:
        pos = -100
    decvalue = int(pos/3.174)
    if requestok == 1:
        decvalue = sender-32
        pos = int(decvalue*3.174)

    posX = panknobx+24-(4*len(str(decvalue)))
    dpg.configure_item(item='el'+EL[2:3]+'_pan_value', default_value = decvalue, pos = (posX,panknoby-20))
    VALUE = (hex(decvalue+32)[2:].zfill(2)).upper()  # 01 TO 3F (-31 TO +31, CENTER = 20)
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)
    ang = ((((100+pos)*(1/20))*math.pi)/6)# angulo desde 1pi/6 radianes hasta 11pi/6 radianes (total son 10 pasos)
    ang = ang + 2.05 # centramos
    x = math.cos(ang)*15
    y = math.sin(ang)*15
    dpg.configure_item(item='el'+EL[2:3]+'_pan_dot',pos = (panknobx+20+x,panknoby+20+y))

def elefxbalance(sender):
    global mouserelease, previous
    
    ELEMENT = str(int(EL[2:3])-1)+'0' # 00,10,20,30
    PARAM = '03 ' + ELEMENT + ' 00 08 00 '
    if mouserelease == 1:
        previous = (float(dpg.get_value(item='el'+EL[2:3]+'_efbal_value'))*2)-100
        mouserelease = 0
    pos = -int(sender)+previous
    if pos > 100:
        pos = 100
    if pos < -100:
        pos = -100
    decvalue = int(pos/2)+50
    if requestok == 1:
        decvalue = sender
        pos =  (decvalue-50)*2
    posX = efbalknobx+24-(4*len(str(decvalue)))
    dpg.configure_item(item='el'+EL[2:3]+'_efbal_value', default_value = decvalue, pos = (posX,efbalknoby-20))
    VALUE = (hex(decvalue)[2:].zfill(2)).upper()# 01 TO 64 (1 TO 100)
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)
    ang = ((((100+pos)*(1/20))*math.pi)/6)# angulo desde 1pi/6 radianes hasta 11pi/6 radianes (total son 10 pasos)
    ang = ang + 2.05 # centramos
    x = math.cos(ang)*15
    y = math.sin(ang)*15
    dpg.configure_item(item='el'+EL[2:3]+'_efbal_dot',pos = (efbalknobx+20+x,efbalknoby+20+y))

def elsensvelrate(sender): #(Sens. to Amp. Envelope on/off)
    ELEMENT = str(int(EL[2:3])-1)+'0' # 00,10,20,30
    PARAM = '07 ' + ELEMENT + ' 00 61 00 '
    decvalue = dpg.get_value(sender)
    VALUE = (hex(int(1-decvalue))[2:].zfill(2)).upper() # 01 on, 00 off
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)

def elampvelsens(sender): #(Sens. to Velocity (volume))
    global mouserelease, previous
    
    ELEMENT = str(int(EL[2:3])-1)+'0' # 00,10,20,30
    PARAM = '07 ' + ELEMENT + ' 00 60 00 '
    if mouserelease == 1:
        previous = float(dpg.get_value(item='el'+EL[2:3]+'_ampvelsens_value'))*14
        mouserelease = 0
    pos = -int(sender)+previous
    if pos > 100:
        pos = 100
    if pos < -100:
        pos = -100
    decvalue = int(pos/14)
    if requestok == 1:
        decvalue = sender
        if decvalue > 8:
            decvalue = 8-decvalue
        pos =  (decvalue*14)
    posX = ampvelsensknobx+24-(4*len(str(decvalue)))
    dpg.configure_item(item='el'+EL[2:3]+'_ampvelsens_value', default_value = decvalue, pos = (posX,ampvelsensknoby-20))
    if decvalue <0:
        decvalue = (-decvalue)+8
    VALUE = (hex(decvalue)[2:].zfill(2)).upper()# 
    # 0F, 0E, 0D, 0C, 0D, 0A, 09 (-7 TO -1) 
    # 00 (0)
    # 01, 02, 03, 04, 05, 06, 07 (+1 TO +7)
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)
    ang = ((((100+pos)*(1/20))*math.pi)/6)# angulo desde 1pi/6 radianes hasta 11pi/6 radianes (total son 10 pasos)
    ang = ang + 2.05 # centramos
    x = math.cos(ang)*15
    y = math.sin(ang)*15
    dpg.configure_item(item='el'+EL[2:3]+'_ampvelsens_dot',pos = (ampvelsensknobx+20+x,ampvelsensknoby+20+y))

def elampmodsens(sender): #(sens. to amp mod)
    global mouserelease, previous
    
    ELEMENT = str(int(EL[2:3])-1)+'0' # 00,10,20,30
    PARAM = '07 ' + ELEMENT + ' 00 62 00 '
    if mouserelease == 1:
        previous = float(dpg.get_value(item='el'+EL[2:3]+'_ampmodsens_value'))*14
        mouserelease = 0
    pos = -int(sender)+previous
    if pos > 100:
        pos = 100
    if pos < -100:
        pos = -100
    decvalue = int(pos/14)
    if requestok == 1:
        decvalue = sender
        if decvalue > 8:
            decvalue = 8-decvalue
        pos =  (decvalue*14)
    posX = ampmodsensknobx+24-(4*len(str(decvalue)))
    dpg.configure_item(item='el'+EL[2:3]+'_ampmodsens_value', default_value = decvalue, pos = (posX,ampmodsensknoby-20))
    if decvalue <0:
        decvalue = (-decvalue)+8
    VALUE = (hex(decvalue)[2:].zfill(2)).upper()# 
    # 0F, 0E, 0D, 0C, 0D, 0A, 09 (-7 TO -1) 
    # 00 (0)
    # 01, 02, 03, 04, 05, 06, 07 (+1 TO +7)
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)
    ang = ((((100+pos)*(1/20))*math.pi)/6)# angulo desde 1pi/6 radianes hasta 11pi/6 radianes (total son 10 pasos)
    ang = ang + 2.05 # centramos
    x = math.cos(ang)*15
    y = math.sin(ang)*15
    dpg.configure_item(item='el'+EL[2:3]+'_ampmodsens_dot',pos = (ampmodsensknobx+20+x,ampmodsensknoby+20+y))

def elampenvmode(sender):
    ELEMENT = str(int(EL[2:3])-1)+'0' # 00,10,20,30
    PARAM = '07 ' + ELEMENT + ' 00 4F 00 '
    decvalue = dpg.get_value(sender)
    VALUE = (hex(decvalue)[2:].zfill(2)).upper()# 00 = NORMAL, 01 = HOLD
    if VALUE == '00':
        dpg.configure_item(item='el'+str(int(EL[2:3]))+'_amp_R1',p1 = (AmpHini,AmpVini+VHSum))
    if VALUE == '01':
        dpg.configure_item(item='el'+str(int(EL[2:3]))+'_amp_R1',p1 = (AmpHini,AmpVini))
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)

def elampenvelope(sender):
    ELEMENT = str(int(EL[2:3])-1)+'0' # 00,10,20,30
    if sender[12:14] == 'R1':
        POINT = '50'
    if sender[12:14] == 'R2':
        POINT = '51'
    if sender[12:14] == 'L2':
        POINT = '55'
    if sender[12:14] == 'R3':
        POINT = '52'
    if sender[12:14] == 'L3':
        POINT = '56'
    if sender[12:14] == 'R4':
        POINT = '53'
    if sender[12:14] == 'RR':
        POINT = '54'
    PARAM = '07 ' + ELEMENT + ' 00 ' + POINT + ' 00 '
    decvalue = dpg.get_value(sender)
    VALUE = (hex(decvalue)[2:].zfill(2)).upper() # 00 TO 3F (0 TO 63) 
    MESSAGE = INI + PARAM + VALUE + END

    # draw Envelope
    X1 = (63-dpg.get_value('el'+str(int(EL[2:3]))+'_amp_env_R1')) 
    X2 = (63-dpg.get_value('el'+str(int(EL[2:3]))+'_amp_env_R2')) 
    Y1 = (dpg.get_value('el'+str(int(EL[2:3]))+'_amp_env_L2')) 
    X3 = (63-dpg.get_value('el'+str(int(EL[2:3]))+'_amp_env_R3')) 
    Y2 = (dpg.get_value('el'+str(int(EL[2:3]))+'_amp_env_L3')) 
    X4 = (63-dpg.get_value('el'+str(int(EL[2:3]))+'_amp_env_R4')) 
    X5 = (63-dpg.get_value('el'+str(int(EL[2:3]))+'_amp_env_RR')) 

    dpg.configure_item(item='el'+str(int(EL[2:3]))+'_amp_R1',p2 =(AmpHini+X1,AmpVini))
    dpg.configure_item(item='el'+str(int(EL[2:3]))+'_amp_R2',p1 =(AmpHini+X1,AmpVini), p2 = (AmpHini+X1+X2,AmpVini+VHSum-Y1))
    dpg.configure_item(item='el'+str(int(EL[2:3]))+'_amp_R3',p1 =(AmpHini+X1+X2,AmpVini+VHSum-Y1), p2 = (AmpHini+X1+X2+X3,AmpVini+VHSum-Y2))
    dpg.configure_item(item='el'+str(int(EL[2:3]))+'_amp_R4',p1 =(AmpHini+X1+X2+X3,AmpVini+VHSum-Y2), p2 = (AmpHini+X1+X2+X3+X4,AmpVini+VHSum))
    dpg.configure_item(item='el'+str(int(EL[2:3]))+'_amp_RR',p1 =(AmpHini+X1+X2+X3+X4,AmpVini+VHSum), p2 = (AmpHini+X1+X2+X3+X4+X5,AmpVini+VHSum))
    for i in range(AmpVini,AmpVini+VHSum,8):
        dpg.configure_item(item='el'+str(int(sender[2:3]))+'_amp_RE'+str(i),p1 =(AmpHini+X1+X2+X3+X4,i),p2 = (AmpHini+X1+X2+X3+X4,i+4))
    if nosend == 0:
        sendmessage(MESSAGE)
    # 50 = Rate 1 - Hold Time, ATTACK, LOWER VALUE = LONGER
    # 51 = Rate 2 - TIME TO ACHIEVE LEVEL 2, LOWER VALUE = LONGER 
    # 55 = Level 2
    # 52 = Rate 3 - TIME TO ACHIEVE LEVEL 3, LOWER VALUE = LONGER 
    # 56 = Level 3
    # 53 = Rate 4 TIME TO DECAY TO ZERO, LOWER VALUE = LONGER 
    # 54 = Release time

def ampenvratescale(sender):
    ELEMENT = str(int(sender[2:3])-1)+'0' # 00,10,20,30
    PARAM = '07 ' + ELEMENT + ' 00 57 00 '
    decvalue = dpg.get_value(sender)
    if decvalue <0:
        decvalue = abs(decvalue) + 8
    VALUE = (hex(decvalue)[2:].zfill(2)).upper()
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)
    # Lower = longer rate
    # 0F, 0E, 0D, 0C, 0D, 0A, 09 (-7 TO -1) 
    # 00 (0)
    # 01, 02, 03, 04, 05, 06, 07 (+1 TO +7)

def elampenvbp(sender):
    global NoWriteRequest
    ELEMENT = str(int(EL[2:3])-1)+'0' # 00,10,20,30
    if requestok == 0:
        dec_breakpoint = 87+int(str(int(sender[14:15])))# 58, 59, 60, 5B (88:BP1, 89:BP2, 90:BP3, 91:BP4)
        decvalue = dpg.get_value(sender)
    else:
        dec_breakpoint = ELBP+87
        decvalue = notelist[sender]

    BREAKPOINT = (hex(dec_breakpoint)[2:].zfill(2)).upper()
    PARAM = '07 ' + ELEMENT + ' 00 ' + BREAKPOINT + ' 00 '
    note = decvalue
    VALUE = (hex(notelist.index(note))[2:].zfill(2)).upper() # 00 TO 7F (C-2 TO G8) 

    # VALUE = '00' 
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)

    if requestok == 1:    
        return

    #### RULES: BP1 < BP2 < BP3 < BP4, ---> LEO LOS CAMBIOS
    NoWriteRequest = 1
    # update midi prefs
    checkmidiprefs()
    requestvoice()

    try:
        a = datalist[31]
    except:
        dpg.configure_item(item=sender, default_value = '')
        dpg.configure_item('midi_error', show=True)
        return

    if datalist[31] == '05': # 1 elemento
        valor = int(174+(dec_breakpoint-88)) # el 1 amp env BreakPoint 1,2,3,4 = 174,175,176,177

    if datalist[31] == '06': # 2 elementos
        if ELEMENT == '00':
            valor = int(183+(dec_breakpoint-88)) # el 1 amp env BreakPoint 1,2,3,4 = 183,184,185,186
        if ELEMENT == '10':
            valor = int(295+(dec_breakpoint-88)) # el 2 amp env BreakPoint 1,2,3,4 = 295,296,297,298

    if datalist[31] == '07': # 4 elementos
        if ELEMENT == '00':
            valor = int(201+(dec_breakpoint-88)) # el 1 amp env BreakPoint 1,2,3,4 = 201,202,203,204
        if ELEMENT == '10':
            valor = int(313+(dec_breakpoint-88)) # el 2 amp env BreakPoint 1,2,3,4 = 313,314,315,316
        if ELEMENT == '20':
            valor = int(425+(dec_breakpoint-88)) # el 3 amp env BreakPoint 1,2,3,4 = 425,426,427,428
        if ELEMENT == '30':
            valor = int(537+(dec_breakpoint-88)) # el 4 amp env BreakPoint 1,2,3,4 = 537,538,539,540

    i = int('0x'+datalist[valor],16)
    dpg.configure_item(item=sender, default_value = notelist[i])

def elampenvscoff(sender):
    ELEMENT = str(int(EL[2:3])-1)+'0' # 00,10,20,30
    dec_breakpoint = 91+int(str(int(sender[19:20])))# 5C, 5D, 5E, 5F (92:BP1, 93:BP2, 94:BP3, 95:BP4)
    BREAKPOINT = (hex(dec_breakpoint)[2:].zfill(2)).upper()
    PARAM = '07 ' + ELEMENT + ' 00 ' + BREAKPOINT
    decvalue = dpg.get_value(sender)
    
    if decvalue < 0:
        VALUE1 = ' 00'
        VALUE2 =  VALUE = (hex(128+decvalue)[2:].zfill(2)).upper()
    else:
        VALUE1 = ' 01'
        VALUE2 =  VALUE = (hex(decvalue)[2:].zfill(2)).upper()
    VALUE = str(VALUE1) + ' ' + str(VALUE2)
    # '00 01' (-127) TO '00 7F' (-1)
    # '01 00' (0) TO '01 7F' (+127)
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)

def elnoteshift(sender):
    global mouserelease, previous
    ELEMENT = str(int(EL[2:3])-1)+'0' # 00,10,20,30
    PARAM = '03 ' + ELEMENT + ' 00 02 00 '
    if mouserelease == 1:
        previous = float(dpg.get_value(item='el'+EL[2:3]+'_noteshift_value'))*1.5503876
        mouserelease = 0
    pos = -int(sender)+previous
    if pos > 100:
        pos = 100
    if pos < -100:
        pos = -100
    decvalue = int(pos/1.5503876)
    if requestok == 1:
        decvalue = sender-64
        pos =  int(decvalue*1.5503876)
    posX = noteshiftknobx+24-(4*len(str(decvalue)))
    if decvalue>63:
        decvalue = 63
    dpg.configure_item(item='el'+EL[2:3]+'_noteshift_value', default_value = decvalue, pos = (posX,noteshiftknoby-20))
    VALUE = (hex(decvalue+64)[2:].zfill(2)).upper() # 00(-64) TO 7F(+63)
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)
    ang = ((((100+pos)*(1/20))*math.pi)/6)# angulo desde 1pi/6 radianes hasta 11pi/6 radianes (total son 10 pasos)
    ang = ang + 2.05 # centramos
    x = math.cos(ang)*15
    y = math.sin(ang)*15
    dpg.configure_item(item='el'+EL[2:3]+'_noteshift_dot',pos = (noteshiftknobx+20+x,noteshiftknoby+20+y))

def eldetune(sender):
    global mouserelease, previous
    ELEMENT = str(int(EL[2:3])-1)+'0' # 00,10,20,30
    PARAM = '03 ' + ELEMENT + ' 00 01 00 '
    if mouserelease == 1:
        previous = float(dpg.get_value(item='el'+EL[2:3]+'_detune_value'))*14
        mouserelease = 0
    pos = -int(sender)+previous
    if pos > 100:
        pos = 100
    if pos < -100:
        pos = -100
    decvalue = int(pos/14)
    if requestok == 1:
        decvalue = sender
        if decvalue > 8:
            decvalue = 8-decvalue
        pos =  (decvalue*14)
    posX = detuneknobx+24-(4*len(str(decvalue)))
    dpg.configure_item(item='el'+EL[2:3]+'_detune_value', default_value = decvalue, pos = (posX,detuneknoby-20))
    if decvalue <0:
        decvalue = (-decvalue)+8
    VALUE = (hex(decvalue)[2:].zfill(2)).upper()# 
    # 0F, 0E, 0D, 0C, 0D, 0A, 09 (-7 TO -1) 
    # 00 (0)
    # 01, 02, 03, 04, 05, 06, 07 (+1 TO +7)
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)
    ang = ((((100+pos)*(1/20))*math.pi)/6)# angulo desde 1pi/6 radianes hasta 11pi/6 radianes (total son 10 pasos)
    ang = ang + 2.05 # centramos
    x = math.cos(ang)*15
    y = math.sin(ang)*15
    dpg.configure_item(item='el'+EL[2:3]+'_detune_dot',pos = (detuneknobx+20+x,detuneknoby+20+y))

def eloscfreqmode(sender):
    ELEMENT = str(int(EL[2:3])-1)+'0' # 00,10,20,30
    PARAM = '07 ' + ELEMENT + ' 00 02 00 '
    decvalue = dpg.get_value(sender)
    VALUE = (hex(decvalue)[2:].zfill(2)).upper() # (00 NORMAL, 01 FIXED)
    MESSAGE = INI + PARAM + VALUE + END
    if decvalue == 1:
        dpg.configure_item(item='el'+str(int(EL[2:3]))+'_osc_freq_note',enabled = True)
    else:
        dpg.configure_item(item='el'+str(int(EL[2:3]))+'_osc_freq_note',default_value = '')
        dpg.configure_item(item='el'+str(int(EL[2:3]))+'_osc_freq_note',enabled = False)

    if nosend == 0:
        sendmessage(MESSAGE)
    
def eloscfreqnote(sender):
    ELEMENT = str(int(EL[2:3])-1)+'0' # 00,10,20,30
    PARAM = '07 ' + ELEMENT + ' 00 03 00 '
    note = dpg.get_value(sender)
    VALUE = (hex(notelist.index(note))[2:].zfill(2)).upper() # 00 TO 7F (C-2 TO G8) 
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)

def eloscfreqtune(sender):
    global mouserelease, previous
    ELEMENT = str(int(EL[2:3])-1)+'0' # 00,10,20,30
    PARAM = '07 ' + ELEMENT + ' 00 04 00 '
    if mouserelease == 1:
        previous = float(dpg.get_value(item='el'+EL[2:3]+'_oscfreqtune_value'))*1.5503876
        mouserelease = 0
    pos = -int(sender)+previous
    if pos > 100:
        pos = 100
    if pos < -100:
        pos = -100
    decvalue = int(pos/1.5503876)
    if requestok == 1:
        decvalue = int(sender) - 64
        pos = decvalue * 1.5503876
    posX = oscfreqtuneknobx+24-(4*len(str(decvalue)))
    if decvalue>63:
        decvalue = 63
    dpg.configure_item(item='el'+EL[2:3]+'_oscfreqtune_value', default_value = decvalue, pos = (posX,oscfreqtuneknoby-20))
    VALUE = (hex(decvalue+64)[2:].zfill(2)).upper() # 00(-64) TO 7F(+63)
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)
    ang = ((((100+pos)*(1/20))*math.pi)/6)# angulo desde 1pi/6 radianes hasta 11pi/6 radianes (total son 10 pasos)
    ang = ang + 2.05 # centramos
    x = math.cos(ang)*15
    y = math.sin(ang)*15
    dpg.configure_item(item='el'+EL[2:3]+'_oscfreqtune_dot',pos = (oscfreqtuneknobx+20+x,oscfreqtuneknoby+20+y))

def elpitchmodsens(sender): # (sens. to pitch mod)
    global mouserelease, previous
    ELEMENT = str(int(EL[2:3])-1)+'0' # 00,10,20,30
    PARAM = '07 ' + ELEMENT + ' 00 05 00 '
    if mouserelease == 1:
        previous = ((float(dpg.get_value(item='el'+EL[2:3]+'_pitchmodsens_value'))-40)*2.5)
        mouserelease = 0
    pos = -int(sender)+previous
    if pos > 100:
        pos = 100
    if pos < -100:
        pos = -100
    decvalue = int((100+pos)/2.5)
    if requestok == 1:
        decvalue = int(sender)
        decvalue = decvalue * 10
        pos = 2.5*decvalue-100
    if decvalue>70:
        decvalue = 70
    posX = pitchmodsensknobx+24-(4*len(str(int(decvalue/10))))
    dpg.configure_item(item='el'+EL[2:3]+'_pitchmodsens_value', default_value = decvalue)
    dpg.configure_item(item='el'+EL[2:3]+'_pitchmodsens_valuex', default_value = int(decvalue/10), pos = (posX,pitchmodsensknoby-20))
    VALUE = (hex(int(decvalue/10))[2:].zfill(2)).upper() # 00 TO 07
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)
    ang = ((((100+pos)*(1/20))*math.pi)/6)# angulo desde 1pi/6 radianes hasta 11pi/6 radianes (total son 10 pasos)
    ang = ang + 2.05 # centramos
    x = math.cos(ang)*15
    y = math.sin(ang)*15
    dpg.configure_item(item='el'+EL[2:3]+'_pitchmodsens_dot',pos = (pitchmodsensknobx+20+x,pitchmodsensknoby+20+y))

def elpitchenvelope(sender):
    # Pitch Envelope 
    ELEMENT = str(int(sender[2:3])-1)+'0' # 00,10,20,30
    decvalue = dpg.get_value(sender)

    if sender[14:16] == 'L0':
        POINT = '0A'
        decvalue = decvalue + 64
    if sender[14:16] == 'R1':
        POINT = '06'
    if sender[14:16] == 'L1':
        POINT = '0B'
        decvalue = decvalue + 64
    if sender[14:16] == 'R2':
        POINT = '07'
    if sender[14:16] == 'L2':
        POINT = '0C'
        decvalue = decvalue + 64
    if sender[14:16] == 'R3':
        POINT = '08'
    if sender[14:16] == 'L3':
        POINT = '0D'
        decvalue = decvalue + 64
    if sender[14:16] == 'RR':
        POINT = '09'
    if sender[14:16] == 'RL':
        POINT = '0E'
        decvalue = decvalue + 64
    
    PARAM = '07 ' + ELEMENT + ' 00 ' + POINT + ' 00 '
    VALUE = (hex(decvalue)[2:].zfill(2)).upper() 
    # L0, L1, L2, L3 AND RL: 00 TO 7F (-63 TO +63, 40 = 0)
    # R1, R2, R3 AND RR: 00 TO 3F (0 TO 63)
    MESSAGE = INI + PARAM + VALUE + END

    # draw Envelope
    Y0 = (63-dpg.get_value('el'+str(int(sender[2:3]))+'_pitch_env_L0'))/2
    X1 = (63-dpg.get_value('el'+str(int(sender[2:3]))+'_pitch_env_R1'))
    Y1 = int((dpg.get_value('el'+str(int(sender[2:3]))+'_pitch_env_L1'))/2)-31.5
    X2 = (63-dpg.get_value('el'+str(int(sender[2:3]))+'_pitch_env_R2'))
    Y2 = int((dpg.get_value('el'+str(int(sender[2:3]))+'_pitch_env_L2'))/2)+31.5
    X3 = (63-dpg.get_value('el'+str(int(sender[2:3]))+'_pitch_env_R3'))
    Y3 = int((dpg.get_value('el'+str(int(sender[2:3]))+'_pitch_env_L3'))/2)+31.5
    X4 = (63-dpg.get_value('el'+str(int(sender[2:3]))+'_pitch_env_RR'))
    Y4 = int((dpg.get_value('el'+str(int(sender[2:3]))+'_pitch_env_RL'))/2)+31.5

    dpg.configure_item(item='el'+str(int(sender[2:3]))+'_pitch_R1',p1 =(PitchHini,PitchVini+Y0), p2 =(PitchHini+X1,PitchVini-Y1))
    dpg.configure_item(item='el'+str(int(sender[2:3]))+'_pitch_R2',p1 =(PitchHini+X1,PitchVini-Y1), p2 = (PitchHini+X1+X2,PitchVini+VHSum-Y2))
    dpg.configure_item(item='el'+str(int(sender[2:3]))+'_pitch_R3',p1 =(PitchHini+X1+X2,PitchVini+VHSum-Y2), p2 = (PitchHini+X1+X2+X3,PitchVini+VHSum-Y3))
    dpg.configure_item(item='el'+str(int(sender[2:3]))+'_pitch_RR',p1 =(PitchHini+X1+X2+X3,PitchVini+VHSum-Y3), p2 = (PitchHini+X1+X2+X3+X4,PitchVini+VHSum-Y4))
    for i in range(PitchVini,PitchVini+VHSum,8):
        dpg.configure_item(item='el'+str(int(sender[2:3]))+'_pitch_RE'+str(i),p1 =(PitchHini+X1+X2+X3,i),p2 = (PitchHini+X1+X2+X3,i+4))
    if nosend == 0:
        sendmessage(MESSAGE)
    # 0A = LEVEL 0
    # 06 = RATE 1 (TIME TO REACH LEVEL 1, LOWER = LONGER TIME)
    # 0B = LEVEL 1
    # 07 = RATE 2 (TIME TO REACH LEVEL 2)
    # 0C = LEVEL 2
    # 08 = RATE 3 (TIME TO REACH LEVEL 3)
    # 0D = LEVEL 3
    # 09 = RELEASE RATE (TIME FROM KEY RELEASED TO RELEASE LEVEL) 
    # 0E = RELEASE LEVEL

def elpitchenvratescale(sender):
    ELEMENT = str(int(EL[2:3])-1)+'0' # 00,10,20,30
    PARAM = '07 ' + ELEMENT + ' 00 10 00 '
    if requestok == 0:
        decvalue = dpg.get_value(sender)
    else:
        decvalue = int(sender)
    if decvalue <0:
        decvalue = abs(decvalue) + 8
    VALUE = (hex(decvalue)[2:].zfill(2)).upper()
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)
    # Lower = longer rate
    # 0F, 0E, 0D, 0C, 0D, 0A, 09 (-7 TO -1) 
    # 00 (0)
    # 01, 02, 03, 04, 05, 06, 07 (+1 TO +7)

def elpitchenvrange(sender):
    ELEMENT = str(int(EL[2:3])-1)+'0' # 00,10,20,30
    PARAM = '07 ' + ELEMENT + ' 00 0F 00 '
    decvalue = 4-(dpg.get_value(sender)+1)
    if decvalue == 3:
        dpg.configure_item(item='el'+EL[2:3]+'_pitch_env_range_value',default_value = '1/2oct')
    if decvalue == 2:
        dpg.configure_item(item='el'+EL[2:3]+'_pitch_env_range_value',default_value = '1oct')
    if decvalue == 1:
        dpg.configure_item(item='el'+EL[2:3]+'_pitch_env_range_value',default_value = '2oct')
    VALUE = (hex(decvalue)[2:].zfill(2)).upper()
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE) # 03 = 1/2 OCT, 02 = 1 OCT, 01 = 2 OCT

def elpitchenvvelsw(sender):
    ELEMENT = str(int(EL[2:3])-1)+'0' # 00,10,20,30
    decvalue = 1-dpg.get_value(sender)
    PARAM = '07 ' + ELEMENT + ' 00 11 00 '
    VALUE = (hex(decvalue)[2:].zfill(2)).upper()# 00 = OFF, 01 = ON
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE) 

def elfilter12cutoff(sender):
    if requestok == 0:
        if sender[10:11] =='1':
            ELEMENT = str(int(EL[2:3])-1)+'0' # FILTER 1: 00,10,20,30
        else:
            ELEMENT = str(int(EL[2:3])+3)+'0' # FILTER 2: 40,50,60,70
        decvalue = dpg.get_value(sender)

    else:
        ELEMENT = ELFILTER12
        decvalue = sender

    PARAM = '09 ' + ELEMENT + ' 00 01 00 '
    VALUE = (hex(decvalue)[2:].zfill(2)).upper() # LPF: 00 TO 7F (0 TO 127) , HPF: 00 TO 72 (0 TO 114)
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)

def elfilter12reso(sender):
    ELEMENT = str(int(sender[2:3])-1)+'0' # FILTER 1: 00,10,20,30
    PARAM = '09 ' + ELEMENT + ' 00 32 00 '
    decvalue = dpg.get_value(sender)
    VALUE = (hex(decvalue)[2:].zfill(2)).upper() # 00 TO 63 (0 TO 99)
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)

def elfiltervelsens(sender): #(Sens. to Velocity (filter))
    global mouserelease, previous
    ELEMENT = str(int(EL[2:3])-1)+'0' # 00,10,20,30
    PARAM = '09 ' + ELEMENT + ' 00 33 00 '
    if mouserelease == 1:
        previous = float(dpg.get_value(item='el'+EL[2:3]+'_filtervelsens_value'))*14
        mouserelease = 0
    pos = -int(sender)+previous
    if pos > 100:
        pos = 100
    if pos < -100:
        pos = -100
    decvalue = int(pos/14)
    if requestok == 1:
        decvalue = sender
        if decvalue > 8:
            decvalue = 8-decvalue
        pos =  (decvalue*14)
    posX = filtervelsensknobx+24-(4*len(str(decvalue)))
    dpg.configure_item(item='el'+EL[2:3]+'_filtervelsens_value', default_value = decvalue, pos = (posX,filtervelsensknoby-20))
    if nosend == 0:
        if decvalue <0:
            decvalue = (-decvalue)+8
    VALUE = (hex(decvalue)[2:].zfill(2)).upper()# 
    # 0F, 0E, 0D, 0C, 0D, 0A, 09 (-7 TO -1) 
    # 00 (0)
    # 01, 02, 03, 04, 05, 06, 07 (+1 TO +7)
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)
    ang = ((((100+pos)*(1/20))*math.pi)/6)# angulo desde 1pi/6 radianes hasta 11pi/6 radianes (total son 10 pasos)
    ang = ang + 2.05 # centramos
    x = math.cos(ang)*15
    y = math.sin(ang)*15
    dpg.configure_item(item='el'+EL[2:3]+'_filtervelsens_dot',pos = (filtervelsensknobx+20+x,filtervelsensknoby+20+y))

def elfiltermodsens(sender): #(Sens. to Modulation (filter))
    global mouserelease, previous
    ELEMENT = str(int(EL[2:3])-1)+'0' # 00,10,20,30
    PARAM = '09 ' + ELEMENT + ' 00 34 00 '
    if mouserelease == 1:
        previous = float(dpg.get_value(item='el'+EL[2:3]+'_filtermodsens_value'))*14
        mouserelease = 0
    pos = -int(sender)+previous
    if pos > 100:
        pos = 100
    if pos < -100:
        pos = -100
    decvalue = int(pos/14)
    if requestok == 1:
        decvalue = sender
        if decvalue > 8:
            decvalue = 8-decvalue
        pos =  (decvalue*14)
    posX = filtermodsensknobx+24-(4*len(str(decvalue)))
    dpg.configure_item(item='el'+EL[2:3]+'_filtermodsens_value', default_value = decvalue, pos = (posX,filtermodsensknoby-20))
    if decvalue <0:
        decvalue = (-decvalue)+8
    VALUE = (hex(decvalue)[2:].zfill(2)).upper()# 
    # 0F, 0E, 0D, 0C, 0D, 0A, 09 (-7 TO -1) 
    # 00 (0)
    # 01, 02, 03, 04, 05, 06, 07 (+1 TO +7)
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)
    ang = ((((100+pos)*(1/20))*math.pi)/6)# angulo desde 1pi/6 radianes hasta 11pi/6 radianes (total son 10 pasos)
    ang = ang + 2.05 # centramos
    x = math.cos(ang)*15
    y = math.sin(ang)*15
    dpg.configure_item(item='el'+EL[2:3]+'_filtermodsens_dot',pos = (filtermodsensknobx+20+x,filtermodsensknoby+20+y))

def elfilter12type(sender):
    if requestok == 0:
        n = sender[10:11]
        if n =='1':
            ELEMENT = str(int(EL[2:3])-1)+'0' # FILTER 1: 00,10,20,30
        else:
            ELEMENT = str(int(EL[2:3])+3)+'0' # FILTER 2: 40,50,60,70
        decvalue = dpg.get_value(sender)

    else:
        ELEMENT = ELFILTER12
        n='1'
        if int(ELFILTER12)>30:
            n='2'
        decvalue = sender
    PARAM = '09 ' + ELEMENT + ' 00 00 00 '
    VALUE = (hex(decvalue)[2:].zfill(2)).upper()# 00 = THU (NO FILTER), 01 = LPF, 02 = HPF
    if VALUE == '00':
            dpg.configure_item(item='el'+str(int(EL[2:3]))+'_filter'+n+'_type_value', default_value = 'THU')
            dpg.configure_item(item='el'+str(int(EL[2:3]))+'_LPF'+n+'_img', show = False)
            if int(ELEMENT) < 40:
                dpg.configure_item(item='el'+str(int(EL[2:3]))+'_HPF'+n+'_img', show = False)
            dpg.configure_item(item='el'+str(int(EL[2:3]))+'_NOFILTER'+n+'_img', show = True)
            dpg.configure_item(item='el'+str(int(EL[2:3]))+'_filter'+n+'_cutoff',max_value = 127)
    if VALUE == '01':
            dpg.configure_item(item='el'+str(int(EL[2:3]))+'_filter'+n+'_type_value', default_value = 'LPF')
            dpg.configure_item(item='el'+str(int(EL[2:3]))+'_LPF'+n+'_img', show = True)
            if int(ELEMENT) < 40:
                dpg.configure_item(item='el'+str(int(EL[2:3]))+'_HPF'+n+'_img', show = False)
            dpg.configure_item(item='el'+str(int(EL[2:3]))+'_NOFILTER'+n+'_img', show = False)
            dpg.configure_item(item='el'+str(int(EL[2:3]))+'_filter'+n+'_cutoff',max_value = 127)
    if VALUE == '02':
            dpg.configure_item(item='el'+str(int(EL[2:3]))+'_filter'+n+'_type_value', default_value = 'HPF')   
            dpg.configure_item(item='el'+str(int(EL[2:3]))+'_LPF'+n+'_img', show = False)
            if int(ELEMENT) < 40:
                dpg.configure_item(item='el'+str(int(EL[2:3]))+'_HPF'+n+'_img', show = True)
            dpg.configure_item(item='el'+str(int(EL[2:3]))+'_NOFILTER'+n+'_img', show = False)
            dpg.configure_item(item='el'+str(int(EL[2:3]))+'_filter'+n+'_cutoff',max_value = 114)
            if dpg.get_value('el'+str(int(EL[2:3]))+'_filter'+n+'_cutoff') > 114:
                dpg.configure_item(item='el'+str(int(EL[2:3]))+'_filter'+n+'_cutoff',default_value = 114)

    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)

def elfilter12mode(sender): #(controlled by)
    if requestok == 0:
        n = sender[10:11]
        if n =='1':
            ELEMENT = str(int(EL[2:3])-1)+'0' # FILTER 1: 00,10,20,30
        else:
            ELEMENT = str(int(EL[2:3])+3)+'0' # FILTER 2: 40,50,60,70
        decvalue = dpg.get_value(sender)

    else:
        ELEMENT = ELFILTER12
        n='1'
        if int(ELFILTER12)>30:
            n='2'
        decvalue = sender
    PARAM = '09 ' + ELEMENT + ' 00 02 00 '
    VALUE = (hex(decvalue)[2:].zfill(2)).upper() # 00 TO 63 (0 TO 99) 
    if VALUE == '00':
        dpg.configure_item(item='el'+str(int(EL[2:3]))+'_filter'+n+'_mode_value', default_value = '  EG')
    if VALUE == '01':
        dpg.configure_item(item='el'+str(int(EL[2:3]))+'_filter'+n+'_mode_value', default_value = ' LFO')
    if VALUE == '02':
        dpg.configure_item(item='el'+str(int(EL[2:3]))+'_filter'+n+'_mode_value', default_value = 'EGVA')
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)
    # 00 = EG (FILTER ENVELOPE GENERATOR, ALL POINTS CONTROLLED BY VELOCITY)
    # 01 = LFO (BYPASS EG)
    # 02 = EGVA (FILTER ENVELOPE GENERATOR, ONLY R1 AND L1 CONTROLED BY VELOCITY)

def elfilter12envelope(sender):
    if requestok == 0:
        n = sender[10:11]
        if n =='1':
            ELEMENT = str(int(EL[2:3])-1)+'0' # FILTER 1: 00,10,20,30
        else:
            ELEMENT = str(int(EL[2:3])+3)+'0' # FILTER 2: 40,50,60,70
    else:
        ELEMENT = ELFILTER12
        n='1'
        if int(ELFILTER12)>30:
            n='2'
    decvalue = dpg.get_value(sender)
    if sender[16:19] == 'L0':
        POINT = '09'
        decvalue = decvalue + 64
    if sender[16:19] == 'R1':
        POINT = '03'
    if sender[16:19] == 'L1':
        POINT = '0A'
        decvalue = decvalue + 64
    if sender[16:19] == 'R2':
        POINT = '04'
    if sender[16:19] == 'L2':
        POINT = '0B'
        decvalue = decvalue + 64
    if sender[16:19] == 'R3':
        POINT = '05'
    if sender[16:19] == 'L3':
        POINT = '0C'
        decvalue = decvalue + 64
    if sender[16:19] == 'R4':
        POINT = '06'
    if sender[16:19] == 'L4':
        POINT = '0D'     
        decvalue = decvalue + 64
    if sender[16:19] == 'RR1':
        POINT = '07'
    if sender[16:19] == 'RL1':
        POINT = '0E'
        decvalue = decvalue + 64
    if sender[16:19] == 'RR2':
        POINT = '08'
    if sender[16:19] == 'RL2':
        POINT = '0F'
        decvalue = decvalue + 64
    PARAM = '09 ' + ELEMENT + ' 00 ' + POINT + ' 00 '
    VALUE = (hex(decvalue)[2:].zfill(2)).upper()
    # L0, L1, L2, L3, L4,RL1 AND RL2: 00 TO 7F (-63 TO +63, 40 = 0)
    # R1, R2, R3, R4, RR1 AND RR2: 00 TO 3F (0 TO 63)
    MESSAGE = INI + PARAM + VALUE + END

    Y0 = (63-dpg.get_value('el'+str(int(EL[2:3]))+'_filter'+n+'_env_L0'))/2
    X1 = (63-dpg.get_value('el'+str(int(EL[2:3]))+'_filter'+n+'_env_R1')) 
    Y1 = int((dpg.get_value('el'+str(int(EL[2:3]))+'_filter'+n+'_env_L1'))/2)-31.5
    X2 = (63-dpg.get_value('el'+str(int(EL[2:3]))+'_filter'+n+'_env_R2')) 
    Y2 = int((dpg.get_value('el'+str(int(EL[2:3]))+'_filter'+n+'_env_L2'))/2)+31.5
    X3 = (63-dpg.get_value('el'+str(int(EL[2:3]))+'_filter'+n+'_env_R3')) 
    Y3 = int((dpg.get_value('el'+str(int(EL[2:3]))+'_filter'+n+'_env_L3'))/2)+31.5
    X4 = (63-dpg.get_value('el'+str(int(EL[2:3]))+'_filter'+n+'_env_R4')) 
    Y4 = int((dpg.get_value('el'+str(int(EL[2:3]))+'_filter'+n+'_env_L4'))/2)+31.5
    X5 = (63-dpg.get_value('el'+str(int(EL[2:3]))+'_filter'+n+'_env_RR1')) 
    Y5 = int((dpg.get_value('el'+str(int(EL[2:3]))+'_filter'+n+'_env_RL1'))/2)+31.5
    X6 = (63-dpg.get_value('el'+str(int(EL[2:3]))+'_filter'+n+'_env_RR2')) 
    Y6 = int((dpg.get_value('el'+str(int(EL[2:3]))+'_filter'+n+'_env_RL2'))/2)+31.5            
        # draw Envelope
    dpg.configure_item(item='el'+str(int(EL[2:3]))+'_filter'+n+'_R1',p1 =(FilterHini,FilterVini+Y0), p2 =(FilterHini+X1,FilterVini-Y1))
    dpg.configure_item(item='el'+str(int(EL[2:3]))+'_filter'+n+'_R2',p1 =(FilterHini+X1,FilterVini-Y1), p2 = (FilterHini+X1+X2,FilterVini+VHSum-Y2))
    dpg.configure_item(item='el'+str(int(EL[2:3]))+'_filter'+n+'_R3',p1 =(FilterHini+X1+X2,FilterVini+VHSum-Y2), p2 = (FilterHini+X1+X2+X3,FilterVini+VHSum-Y3))
    dpg.configure_item(item='el'+str(int(EL[2:3]))+'_filter'+n+'_R4',p1 =(FilterHini+X1+X2+X3,FilterVini+VHSum-Y3), p2 = (FilterHini+X1+X2+X3+X4,FilterVini+VHSum-Y4))
    dpg.configure_item(item='el'+str(int(EL[2:3]))+'_filter'+n+'_RR1',p1 =(FilterHini+X1+X2+X3+X4,FilterVini+VHSum-Y4), p2 = (FilterHini+X1+X2+X3+X4+X5,FilterVini+VHSum-Y5))
    dpg.configure_item(item='el'+str(int(EL[2:3]))+'_filter'+n+'_RR2',p1 =(FilterHini+X1+X2+X3+X4+X5,FilterVini+VHSum-Y5), p2 = (FilterHini+X1+X2+X3+X4+X5+X6,FilterVini+VHSum-Y6))
    for i in range(FilterVini,FilterVini+VHSum,8):
        dpg.configure_item(item='el'+str(int(EL[2:3]))+'_filter'+n+'_RE'+str(i),p1 =(FilterHini+X1+X2+X3+X4,i),p2 = (FilterHini+X1+X2+X3+X4,i+4))
    if nosend == 0:
        sendmessage(MESSAGE)
    # 09 = LEVEL 0
    # 03 = RATE 1 (TIME TO REACH LEVEL 1, HIGHER = LONGER TIME)
    # 0A = LEVEL 1
    # 04 = RATE 2 (TIME TO REACH LEVEL 2)
    # 0B = LEVEL 2
    # 05 = RATE 3 (TIME TO REACH LEVEL 3)
    # 0C = LEVEL 3
    # 06 = RATE 4 (TIME TO REACH LEVEL 4)
    # 0D = LEVEL 4
    # 07 = RELEASE RATE 1 (TIME FROM KEY RELEASED TO RELEASE LEVEL 1)
    # 0E = RELEASE LEVEL 1
    # 08 = RELEASE RATE 2(RELEASE LEVEL 1 TO RELEASE LEVEL 2)
    # 0F = RELEASE LEVEL 2
        
def elfilter12envratescale(sender):
    if requestok == 0:
        n = sender[10:11]
        decvalue = dpg.get_value(sender)
        if n =='1':
            ELEMENT = str(int(EL[2:3])-1)+'0' # FILTER 1: 00,10,20,30
        else:
            ELEMENT = str(int(EL[2:3])+3)+'0' # FILTER 2: 40,50,60,70
    else:
        ELEMENT = ELFILTER12
        decvalue = sender
    PARAM = '09 ' + ELEMENT + ' 00 10 00 '
    if decvalue <0:
        decvalue = abs(decvalue) + 8
    VALUE = (hex(decvalue)[2:].zfill(2)).upper()
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)
    # Lower = longer rate
    # 0F, 0E, 0D, 0C, 0D, 0A, 09 (-7 TO -1) 
    # 00 (0)
    # 01, 02, 03, 04, 05, 06, 07 (+1 TO +7)

def elfilter12envbp(sender):
    global NoWriteRequest
    if requestok == 0:
        n = sender[10:11]
        decvalue = dpg.get_value(sender)
        if n =='1':
            ELEMENT = str(int(EL[2:3])-1)+'0' # FILTER 1: 00,10,20,30
        else:
            ELEMENT = str(int(EL[2:3])+3)+'0' # FILTER 2: 40,50,60,70
        dec_breakpoint = 16+int(str(int(sender[18:19])))# 11, 12, 13, 14 (16:BP1, 17:BP2, 18:BP3, 19:BP4)
        
    else:
        ELEMENT = ELFILTER12
        dec_breakpoint = ELBP+16
        decvalue = notelist[sender]
    
    BREAKPOINT = (hex(dec_breakpoint)[2:].zfill(2)).upper()
    PARAM = '09 ' + ELEMENT + ' 00 ' + BREAKPOINT + ' 00 '
    note = decvalue
    VALUE = (hex(notelist.index(note))[2:].zfill(2)).upper() # 00 TO 7F (C-2 TO G8) 
    MESSAGE = INI + PARAM + VALUE + END

    if nosend == 0:
        sendmessage(MESSAGE)

    if requestok == 1:    
        return

    #### RULES: BP1 < BP2 < BP3 < BP4, ---> LEO LOS CAMBIOS
    NoWriteRequest = 1
    # update midi prefs
    checkmidiprefs()
    requestvoice()
    try:
        a = datalist[31]
    except:
        dpg.configure_item(item=sender, default_value = '')
        dpg.configure_item('midi_error', show=True)
        return

    if datalist[31] == '05': # 1 elemento
        if ELEMENT == '00':
            valor = int(121+(dec_breakpoint-17)) # el 1 filter1 env BreakPoint 1,2,3,4 = 121,122,123,124
        if ELEMENT == '40':
            valor = int(136+(dec_breakpoint-17)) # el 1 filter2 env BreakPoint 1,2,3,4 = 136,137,138,139

    if datalist[31] == '06': # 2 elementos
        if ELEMENT == '00':
            valor = int(130+(dec_breakpoint-17)) # el 1 filter1 env BreakPoint 1,2,3,4 = 130,131,132,133
        if ELEMENT == '10':
            valor = int(242+(dec_breakpoint-17)) # el 2 filter1 env BreakPoint 1,2,3,4 = 242,243,244,245
        if ELEMENT == '40':
            valor = int(159+(dec_breakpoint-17)) # el 1 filter2 env BreakPoint 1,2,3,4 = 159,160,161,162
        if ELEMENT == '50':
            valor = int(271+(dec_breakpoint-17)) # el 2 filter2 env BreakPoint 1,2,3,4 = 271,272,273,274

    if datalist[31] == '07': # 4 elementos
        if ELEMENT == '00':
            valor = int(148+(dec_breakpoint-17)) # el 1 filter1 env BreakPoint 1,2,3,4 = 148,149,150,151
        if ELEMENT == '10':
            valor = int(260+(dec_breakpoint-17)) # el 2 filter1 env BreakPoint 1,2,3,4 = 260,261,262,263
        if ELEMENT == '20':
            valor = int(372+(dec_breakpoint-17)) # el 3 filter1 env BreakPoint 1,2,3,4 = 372,373,374,375
        if ELEMENT == '30':
            valor = int(484+(dec_breakpoint-17)) # el 4 filter1 env BreakPoint 1,2,3,4 = 484,485,486,487
        if ELEMENT == '40':
            valor = int(177+(dec_breakpoint-17)) # el 1 filter2 env BreakPoint 1,2,3,4 = 177,178,179,180
        if ELEMENT == '50':
            valor = int(289+(dec_breakpoint-17)) # el 2 filter2 env BreakPoint 1,2,3,4 = 289,290,291,292
        if ELEMENT == '60':
            valor = int(401+(dec_breakpoint-17)) # el 3 filter2 env BreakPoint 1,2,3,4 = 401,402,403,404
        if ELEMENT == '70':
            valor = int(513+(dec_breakpoint-17)) # el 4 filter2 env BreakPoint 1,2,3,4 = 513,514,515,516
    i = int('0x'+datalist[valor],16)
    dpg.configure_item(item=sender, default_value = notelist[i])

def elfilter12envscoff(sender):
    n = sender[10:11]
    decvalue = dpg.get_value(sender)
    if n =='1':
        ELEMENT = str(int(EL[2:3])-1)+'0' # FILTER 1: 00,10,20,30
    else:
        ELEMENT = str(int(EL[2:3])+3)+'0' # FILTER 2: 40,50,60,70    
    dec_breakpoint = 20+int(str(int(sender[23:24])))# 15,16,17,18 (21:BP1, 22:BP2, 23:BP3, 24:BP4)
    decvalue = dpg.get_value(sender)

    BREAKPOINT = (hex(dec_breakpoint)[2:].zfill(2)).upper()
    PARAM = '09 ' + ELEMENT + ' 00 ' + BREAKPOINT
    if decvalue < 0:
        VALUE1 = ' 00'
        VALUE2 =  VALUE = (hex(128+decvalue)[2:].zfill(2)).upper()
    else:
        VALUE1 = ' 01'
        VALUE2 =  VALUE = (hex(decvalue)[2:].zfill(2)).upper()
    VALUE = str(VALUE1) + ' ' + str(VALUE2)
    # '00 01' (-127) TO '00 7F' (-1)
    # '01 00' (0) TO '01 7F' (+127)
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)

def elnotelimitL(sender):
    global datalist
    ELEMENT = str(int(sender[2:3])-1)+'0' # 00,10,20,30
    PARAM = '03 ' + ELEMENT + ' 00 03 00 '
    note = dpg.get_value(sender)
    for i in range(len(notelist)):
        if note == notelist[i]:
            VALUE = (hex(i)[2:].zfill(2)).upper() # 00 TO 7F (C-2 TO G8), en el sinte el low puede ser mayor que el high.
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)

def elnotelimitH(sender):
    ELEMENT = str(int(sender[2:3])-1)+'0' # 00,10,20,30
    PARAM = '03 ' + ELEMENT + ' 00 04 00 '
    note = dpg.get_value(sender)
    for i in range(len(notelist)):
        if note == notelist[i]:
            VALUE = (hex(i)[2:].zfill(2)).upper() # 00 TO 7F (C-2 TO G8), en el sinte el low puede ser mayor que el high.
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)

def elvellimitL(sender):
    ELEMENT = str(int(sender[2:3])-1)+'0' # 00,10,20,30
    PARAM = '03 ' + ELEMENT + ' 00 05 00 '
    decvalue = dpg.get_value(sender)
    VALUE = (hex(decvalue)[2:].zfill(2)).upper() # 00 TO 7F 1 to 127
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)

def elvellimitH(sender):
    ELEMENT = str(int(sender[2:3])-1)+'0' # 00,10,20,30
    PARAM = '03 ' + ELEMENT + ' 00 06 00 '
    decvalue = dpg.get_value(sender)
    VALUE = (hex(decvalue)[2:].zfill(2)).upper() # 00 TO 7F (C-2 TO G8) 
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)

def ellfowave(sender):
    ELEMENT = str(int(EL[2:3])-1)+'0' # 00,10,20,30
    if requestok == 0:
        decvalue = dpg.get_value(sender)
    else:
        decvalue = sender
    VALUE = (hex(decvalue)[2:].zfill(2)).upper() # 00 TO 05 (tri, dwn, up, squ, sin, S/H)
    for i in range(6):
        dpg.configure_item(item='el'+str(int(EL[2:3]))+'_'+imageslist[5+i]+'_img', show = False)
    dpg.configure_item(item='el'+str(int(EL[2:3]))+'_lfo_wave_value', default_value = modeslist[decvalue])
    dpg.configure_item(item='el'+str(int(EL[2:3]))+'_'+imageslist[5+decvalue]+'_img', show = True)
    PARAM = '07 ' + ELEMENT + ' 00 17 00 '
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)

def ellfospeed(sender):
    global mouserelease, previous
    ELEMENT = str(int(EL[2:3])-1)+'0' # 00,10,20,30
    PARAM = '07 ' + ELEMENT + ' 00 12 00 '
    if mouserelease == 1:
        previous = (float(dpg.get_value(item='el'+EL[2:3]+'_lfospeed_value'))*2)-100
        mouserelease = 0
    pos = -int(sender)+previous
    if pos > 99:
        pos = 99
    if pos < -100:
        pos = -100
    decvalue = int(pos/2)+50
    if requestok == 1:
        decvalue = sender
        pos =  (decvalue-50)*2
    posX = lfospeedknobx+24-(4*len(str(decvalue)))
    dpg.configure_item(item='el'+EL[2:3]+'_lfospeed_value', default_value = decvalue, pos = (posX,lfospeedknoby-20))
    VALUE = (hex(decvalue)[2:].zfill(2)).upper()# 01 TO 64 (1 TO 100)
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)
    ang = ((((100+pos)*(1/20))*math.pi)/6)# angulo desde 1pi/6 radianes hasta 11pi/6 radianes (total son 10 pasos)
    ang = ang + 2.05 # centramos
    x = math.cos(ang)*15
    y = math.sin(ang)*15
    dpg.configure_item(item='el'+EL[2:3]+'_lfospeed_dot',pos = (lfospeedknobx+20+x,lfospeedknoby+20+y))

def ellfodelay(sender):
    global mouserelease, previous
    ELEMENT = str(int(EL[2:3])-1)+'0' # 00,10,20,30
    PARAM = '07 ' + ELEMENT + ' 00 13 00 '
    if mouserelease == 1:
        previous = (float(dpg.get_value(item='el'+EL[2:3]+'_lfodelay_value'))*2)-100
        mouserelease = 0
    pos = -int(sender)+previous
    if pos > 99:
        pos = 99
    if pos < -100:
        pos = -100
    decvalue = int(pos/2)+50
    if requestok == 1:
        decvalue = sender
        pos =  (decvalue-50)*2
    posX = lfodelayknobx+24-(4*len(str(decvalue)))
    dpg.configure_item(item='el'+EL[2:3]+'_lfodelay_value', default_value = decvalue, pos = (posX,lfodelayknoby-20))
    VALUE = (hex(decvalue)[2:].zfill(2)).upper()# 00 TO 63 (0 TO 99) HIGHER = LONGER
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)
    ang = ((((100+pos)*(1/20))*math.pi)/6)# angulo desde 1pi/6 radianes hasta 11pi/6 radianes (total son 10 pasos)
    ang = ang + 2.05 # centramos
    x = math.cos(ang)*15
    y = math.sin(ang)*15
    dpg.configure_item(item='el'+EL[2:3]+'_lfodelay_dot',pos = (lfodelayknobx+20+x,lfodelayknoby+20+y))

def ellfophase(sender):
    global mouserelease, previous
    ELEMENT = str(int(EL[2:3])-1)+'0' # 00,10,20,30
    PARAM = '07 ' + ELEMENT + ' 00 18 00 '
    if mouserelease == 1:
        previous = (float(dpg.get_value(item='el'+EL[2:3]+'_lfophase_value'))*2)-100
        mouserelease = 0
    pos = -int(sender)+previous
    if pos > 99:
        pos = 99
    if pos < -100:
        pos = -100
    decvalue = int(pos/2)+50
    if requestok == 1:
        decvalue = sender
        pos =  (decvalue-50)*2
    posX = lfophaseknobx+24-(4*len(str(decvalue)))
    dpg.configure_item(item='el'+EL[2:3]+'_lfophase_value', default_value = decvalue, pos = (posX,lfophaseknoby-20))
    VALUE = (hex(decvalue)[2:].zfill(2)).upper()# 00 TO 63 (0 TO 99) HIGHER = LONGER
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)
    ang = ((((100+pos)*(1/20))*math.pi)/6)# angulo desde 1pi/6 radianes hasta 11pi/6 radianes (total son 10 pasos)
    ang = ang + 2.05 # centramos
    x = math.cos(ang)*15
    y = math.sin(ang)*15
    dpg.configure_item(item='el'+EL[2:3]+'_lfophase_dot',pos = (lfophaseknobx+20+x,lfophaseknoby+20+y))

def ellfoampmod(sender):
    global mouserelease, previous
    
    ELEMENT = str(int(EL[2:3])-1)+'0' # 00,10,20,30
    PARAM = '07 ' + ELEMENT + ' 00 15 00 '
    if mouserelease == 1:
        previous = (float(dpg.get_value(item='el'+EL[2:3]+'_lfoampmod_value'))*1.56)-99
        mouserelease = 0
    pos = -int(sender)+previous
    if pos > 99:
        pos = 99
    if pos < -100:
        pos = -100
    decvalue = int(pos/1.56)+64
    if requestok == 1:
        decvalue = sender
        pos =  (decvalue-64)*1.56
    posX = lfoampmodknobx+24-(4*len(str(decvalue)))
    dpg.configure_item(item='el'+EL[2:3]+'_lfoampmod_value', default_value = decvalue, pos = (posX,lfoampmodknoby-20))
    VALUE = (hex(decvalue)[2:].zfill(2)).upper()# 00 TO 7f (0 TO 127)
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)
    ang = ((((100+pos)*(1/20))*math.pi)/6)# angulo desde 1pi/6 radianes hasta 11pi/6 radianes (total son 10 pasos)
    ang = ang + 2.05 # centramos
    x = math.cos(ang)*15
    y = math.sin(ang)*15
    dpg.configure_item(item='el'+EL[2:3]+'_lfoampmod_dot',pos = (lfoampmodknobx+20+x,lfoampmodknoby+20+y))

def ellfopitchmod(sender):
    global mouserelease, previous
    
    ELEMENT = str(int(EL[2:3])-1)+'0' # 00,10,20,30
    PARAM = '07 ' + ELEMENT + ' 00 14 00 '
    if mouserelease == 1:
        previous = (float(dpg.get_value(item='el'+EL[2:3]+'_lfopitchmod_value'))*1.56)-99
        mouserelease = 0
    pos = -int(sender)+previous
    if pos > 99:
        pos = 99
    if pos < -100:
        pos = -100
    decvalue = int(pos/1.56)+64
    if requestok == 1:
        decvalue = sender
        pos =  (decvalue-64)*1.56
    posX = lfopitchmodknobx+24-(4*len(str(decvalue)))
    dpg.configure_item(item='el'+EL[2:3]+'_lfopitchmod_value', default_value = decvalue, pos = (posX,lfopitchmodknoby-20))
    VALUE = (hex(decvalue)[2:].zfill(2)).upper()# 00 TO 7f (0 TO 127)
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)
    ang = ((((100+pos)*(1/20))*math.pi)/6)# angulo desde 1pi/6 radianes hasta 11pi/6 radianes (total son 10 pasos)
    ang = ang + 2.05 # centramos
    x = math.cos(ang)*15
    y = math.sin(ang)*15
    dpg.configure_item(item='el'+EL[2:3]+'_lfopitchmod_dot',pos = (lfopitchmodknobx+20+x,lfopitchmodknoby+20+y))

def ellfocutoffmod(sender):
    global mouserelease, previous
    
    ELEMENT = str(int(EL[2:3])-1)+'0' # 00,10,20,30
    PARAM = '07 ' + ELEMENT + ' 00 16 00 '
    if mouserelease == 1:
        previous = (float(dpg.get_value(item='el'+EL[2:3]+'_lfocutoffmod_value'))*1.56)-99
        mouserelease = 0
    pos = -int(sender)+previous
    if pos > 99:
        pos = 99
    if pos < -100:
        pos = -100
    decvalue = int(pos/1.56)+64
    if requestok == 1:
        decvalue = sender
        pos =  (decvalue-64)*1.56
    posX = lfocutoffmodknobx+24-(4*len(str(decvalue)))
    dpg.configure_item(item='el'+EL[2:3]+'_lfocutoffmod_value', default_value = decvalue, pos = (posX,lfocutoffmodknoby-20))
    VALUE = (hex(decvalue)[2:].zfill(2)).upper()# 00 TO 7f (0 TO 127)
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)
    ang = ((((100+pos)*(1/20))*math.pi)/6)# angulo desde 1pi/6 radianes hasta 11pi/6 radianes (total son 10 pasos)
    ang = ang + 2.05 # centramos
    x = math.cos(ang)*15
    y = math.sin(ang)*15
    dpg.configure_item(item='el'+EL[2:3]+'_lfocutoffmod_dot',pos = (lfocutoffmodknobx+20+x,lfocutoffmodknoby+20+y))

########################################################## DRUMS EDIT ##########################################################
def drumwave(sender):
    # NOTE = 24 to 60 hex
    # VALUE = 00 TO 4B hex
    # F0 43 10 35 04 NOTE 02 00 00 07 F7: inst off
    # F0 43 10 35 04 NOTE 02 00 00 27 F7: inst on
    # F0 43 10 35 04 NOTE 00 02 00 VALUE 7F
    INI = 'F0 43 10 35 '
    numbers = ''.join(filter(str.isdigit, sender))
    NOTE = (hex(36+int(numbers))[2:].zfill(2)).upper() # hex(24 to 60)
    PARAM = '04 '+NOTE+' 00 02 00 '
    END = ' F7'
    VALUE = (hex(drumvoicelist.index(dpg.get_value(sender))-1)[2:].zfill(2)).upper()
    if VALUE == 'X1':
        if nosend == 0:
            sendmessage('F0 43 10 35 04 '+ NOTE +' 02 00 00 07 F7') # INST OFF
    else:
        if nosend == 0:
            MESSAGE = 'F0 43 10 35 04 '+ NOTE +' 02 00 00 27 F7'
            sendmessage(MESSAGE) # INST ON
            MESSAGE = INI+PARAM+VALUE+END
            sendmessage(MESSAGE) # Set Waveform
    
def drumvolume(sender):
    # NOTE = 24 to 60 hex
    # VALUE = 00 to 7F hex
    # F0 43 10 35 04 NOTE 00 03 00 VALUE F7 = instrument volume
    INI = 'F0 43 10 35 04 '
    numbers = ''.join(filter(str.isdigit, sender))
    NOTE = (hex(36+int(numbers))[2:].zfill(2)).upper() # hex(24 to 60)
    PARAM = ' 00 03 00 '
    END = ' F7'
    VALUE = (hex(dpg.get_value(sender))[2:].zfill(2)).upper()
    MESSAGE = INI+NOTE+PARAM+VALUE+END
    if nosend == 0:
        sendmessage(MESSAGE)

def drumnoteshift(sender):
    # NOTE = 24 to 60 hex
    # VALUE : (10 TO 64 HEX)
    # F0 43 10 35 04 NOTE 00 05 00 VALUE F7
    INI = 'F0 43 10 35 04 '
    numbers = ''.join(filter(str.isdigit, sender))
    NOTE = (hex(36+int(numbers))[2:].zfill(2)).upper() # hex(24 to 60)
    PARAM = ' 00 05 00 '
    END = ' F7'
    decvalue = dpg.get_value(sender)+64
    VALUE = (hex(decvalue)[2:].zfill(2)).upper()
    MESSAGE = INI+NOTE+PARAM+VALUE+END
    if nosend == 0:
        sendmessage(MESSAGE)

def drumtune(sender):
    # NOTE = 24 to 60 hex
    # VALUE : (0 TO 7F HEX,40) -64 TO +63 (40 = 0)
    # F0 43 10 35 04 NOTE 00 04 00 VALUE F7
    INI = 'F0 43 10 35 04 '
    numbers = ''.join(filter(str.isdigit, sender))
    NOTE = (hex(36+int(numbers))[2:].zfill(2)).upper() # hex(24 to 60)
    PARAM = ' 00 04 00 '
    END = ' F7'
    decvalue = dpg.get_value(sender) + 64
    VALUE = (hex(decvalue)[2:].zfill(2)).upper()
    MESSAGE = INI+NOTE+PARAM+VALUE+END
    if nosend == 0:
        sendmessage(MESSAGE)

def drumaltgroup(sender):
    # F0 43 10 35 04 NOTE 03 00 00 67 F7 # (hex 67 on / 27 off)
    INI = 'F0 43 10 35 04 '
    numbers = ''.join(filter(str.isdigit, sender))
    NOTE = (hex(36+int(numbers))[2:].zfill(2)).upper() # hex(24 to 60)
    PARAM = ' 03 00 00 '
    END = ' F7'
    decvalue = 39+(dpg.get_value(sender)*64)
    VALUE = (hex(decvalue)[2:].zfill(2)).upper()
    MESSAGE = INI+NOTE+PARAM+VALUE+END
    if nosend == 0:
        sendmessage(MESSAGE)

def drumpan(sender):
    # NOTE = 24 to 60 hex
    # VALUE : (01 TO 3F HEX,20 CENTER) -31 TO 31
    # F0 43 10 35 04 NOTE 00 06 00 VALUE F7 
    INI = 'F0 43 10 35 04 '
    numbers = ''.join(filter(str.isdigit, sender))
    NOTE = (hex(36+int(numbers))[2:].zfill(2)).upper() # hex(24 to 60)
    PARAM = ' 00 06 00 '
    END = ' F7'
    decvalue = dpg.get_value(sender) + 32
    VALUE = (hex(decvalue)[2:].zfill(2)).upper()
    MESSAGE = INI+NOTE+PARAM+VALUE+END
    if nosend == 0:
        sendmessage(MESSAGE)
    
def drumfxbal(sender):
    # NOTE = 24 to 60 hex
    # VALUE : (00 TO 64 HEX) 0 TO 100
    # F0 43 10 35 04 NOTE 00 07 00 VALUE F7
    INI = 'F0 43 10 35 04 '
    numbers = ''.join(filter(str.isdigit, sender))
    NOTE = (hex(36+int(numbers))[2:].zfill(2)).upper() # hex(24 to 60)
    PARAM = ' 00 07 00 '
    END = ' F7'
    decvalue = dpg.get_value(sender)
    VALUE = (hex(decvalue)[2:].zfill(2)).upper()
    MESSAGE = INI+NOTE+PARAM+VALUE+END
    if nosend == 0:
        sendmessage(MESSAGE)

####################################################### CONTROLLERS EDIT #######################################################
def ampmodcc(sender):
    PARAM = '02 00 00 14 00 '
    decvalue = dpg.get_value(sender)
    for i in range(len(controllerlist)):
        if controllerlist[i] == decvalue:
            VALUE = (hex(i)[2:].zfill(2)).upper() # 00 TO 78, 79 (0 TO 120, AT)
            MESSAGE = INI + PARAM + VALUE + END
            if nosend == 0:
                sendmessage(MESSAGE)
            break

def ampmodrng(sender):
    PARAM = '02 00 00 15 00 '
    decvalue = dpg.get_value(sender)
    VALUE = (hex(decvalue)[2:].zfill(2)).upper()  # 00 TO 7F (0 TO 127)
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)

def pitchmodcc(sender):
    PARAM = '02 00 00 12 00 '
    decvalue = dpg.get_value(sender)
    for i in range(len(controllerlist)):
        if controllerlist[i] == decvalue:
            VALUE = (hex(i)[2:].zfill(2)).upper() # 00 TO 78, 79 (0 TO 120, AT)
            MESSAGE = INI + PARAM + VALUE + END
            if nosend == 0:
                sendmessage(MESSAGE)
            break

def pitchmodrng(sender):
    PARAM = '02 00 00 13 00 '
    decvalue = dpg.get_value(sender)
    VALUE = (hex(decvalue)[2:].zfill(2)).upper()  # 00 TO 7F (0 TO 127)
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)

def cutoffmodcc(sender):
    PARAM = '02 00 00 16 00 '
    decvalue = dpg.get_value(sender)
    for i in range(len(controllerlist)):
        if controllerlist[i] == decvalue:
            VALUE = (hex(i)[2:].zfill(2)).upper() # 00 TO 78, 79 (0 TO 120, AT)
            MESSAGE = INI + PARAM + VALUE + END
            if nosend == 0:
                sendmessage(MESSAGE)
            break

def cutoffmodrng(sender):
    PARAM = '02 00 00 17 00 '
    decvalue = dpg.get_value(sender)
    VALUE = (hex(decvalue)[2:].zfill(2)).upper()  # 00 TO 7F (0 TO 127)
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)

def cutofffreqcc(sender):
    PARAM = '02 00 00 18 00 '
    decvalue = dpg.get_value(sender)
    for i in range(len(controllerlist)):
        if controllerlist[i] == decvalue:
            VALUE = (hex(i)[2:].zfill(2)).upper() # 00 TO 78, 79 (0 TO 120, AT)
            MESSAGE = INI + PARAM + VALUE + END
            if nosend == 0:
                sendmessage(MESSAGE)
            break

def cutofffreqrng(sender):
    PARAM = '02 00 00 19 00 '    
    decvalue = dpg.get_value(sender)
    VALUE = (hex(decvalue)[2:].zfill(2)).upper()  # 00 TO 7F (0 TO 127)
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)

def envgenbiascc(sender):
    PARAM = '02 00 00 1C 00 '
    decvalue = dpg.get_value(sender)
    for i in range(len(controllerlist)):
        if controllerlist[i] == decvalue:
            VALUE = (hex(i)[2:].zfill(2)).upper() # 00 TO 78, 79 (0 TO 120, AT)
            MESSAGE = INI + PARAM + VALUE + END
            if nosend == 0:
                sendmessage(MESSAGE)
            break

def envgenrng(sender):
    PARAM = '02 00 00 1D 00 '
    decvalue = dpg.get_value(sender)
    VALUE = (hex(decvalue)[2:].zfill(2)).upper()  # 00 TO 7F (0 TO 127)
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)

def volumecc(sender):
    PARAM = '02 00 00 1E 00 '
    decvalue = dpg.get_value(sender)
    for i in range(len(controllerlist)):
        if controllerlist[i] == decvalue:
            VALUE = (hex(i)[2:].zfill(2)).upper() # 00 TO 78, 79 (0 TO 120, AT)
            MESSAGE = INI + PARAM + VALUE + END
            if nosend == 0:
                sendmessage(MESSAGE)
            break

def volumerngmin(sender):
    PARAM = '02 00 00 1F 00 '
    decvalue = dpg.get_value(sender)
    VALUE = (hex(decvalue)[2:].zfill(2)).upper()  # 00 TO 7F (0 TO 127)
    MESSAGE = INI + PARAM + VALUE + END
    if nosend == 0:
        sendmessage(MESSAGE)

######################################################### MENU ACTIONS #########################################################

############################# FILE #############################
def loadpatch():
    global datalist, ELCOPY, ELPASTE, elnumber, copyel, EL, NoWriteRequest, loading
    NoWriteRequest == 1
    requestvoice()
    NoWriteRequest == 0
    copyel = 0
    ELCOPY = 1
    loading = 1
    # update midi prefs
    checkmidiprefs()

    # LOAD DATALIST
    file=filedialpy.openFile()
    if file == '':
        return
    f = open(file, 'r')
    try:
        datalist = json.load(f)
    except:
        dpg.configure_item('load_error', show=True)
        return
    f.close()
    if len (datalist) not in (190,311,553,618):
        dpg.configure_item('load_error', show=True)
        datalist = []
        return

    if datalist[4] == '64':
        if elnumber != 0:
            dpg.configure_item('drums_error', show=True)
            return
    if datalist[4] != '64':
        if elnumber == 0:
            dpg.configure_item('drums_error2', show=True)
            return    

    # actualizo numero de elementos
    if datalist[31] == '05':
        elnumber = 1
    if datalist[31] == '06':
        elnumber= 2
    if datalist[31] == '07':
        elnumber = 4
    if datalist[4] == '64':
        elnumber = 0
        
    # set elements number
    if elnumber == 0:
        pastedrumpatch()

    else:
        if elnumber == 1:
            VALUE = '05'
            dpg.configure_item(item='el2_tab', show = False)
            dpg.configure_item(item='el3_tab', show = False)
            dpg.configure_item(item='el4_tab', show = False)
        if elnumber == 2:
            VALUE = '06'
            dpg.configure_item(item='el2_tab', show = True)
            dpg.configure_item(item='el3_tab', show = False)
            dpg.configure_item(item='el4_tab', show = False)
        if elnumber == 4:
            VALUE = '07'
            dpg.configure_item(item='el2_tab', show = True)
            dpg.configure_item(item='el3_tab', show = True)
            dpg.configure_item(item='el4_tab', show = True)
            
        PARAM = '02 00 00 00 00 '
        MESSAGE = INI + PARAM + VALUE + END
        sendmessage(MESSAGE)

        # PASTE
        pastepatch()

def savepatch():
    global datalist
    # update midi prefs
    checkmidiprefs()
    requestvoice()

    file = filedialpy.saveFile(title="Save patch file")
    if file == '':
        return
    file = file
    f = open(file, 'w')
    json.dump(datalist, f)
    f.close()

def exitprogram():
    try:
        inport.close()
    except:
        pass
    try:
        outport.close()
    except:
        pass    
    os._exit(0)

############################ VOICE #############################
def requestvoice():
    global inport, outport, datalist, NoWriteRequest, elnumber
    found = 0
    ################### PUT THE SYNTH IN EDIT MODE #################
    PARAM = '02 00 00 22 00 '
    VALUE = (hex(127)[2:].zfill(2)).upper() # 00 TO 7F (0 TO 127)
    MESSAGE = INI + PARAM + VALUE + END
    sendmessage(MESSAGE)

    INI1 = 'F0 ' # Status
    M1 = '43 ' # Identification
    M2 = '2F ' # Device number 16
    M3 = '7A ' # Format number
    M4 = '4C 4D 20 20 ' # Classification Name LM__
    M5 = '38 31 30 33 ' # Data format Name 8103
    M6 = '56 43 '# VOICE (VC in ascii to hex: 56 43)
    M7 = '00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' # Additional header, ignored.
    M8 = '7F ' # Memory type: Edit buffer (current patch)
    M9 = '00 ' # Memory number (Ignored)
    END1 = 'F7' # End message
    MESSAGE = INI1+M1+M2+M3+M4+M5+M6+M7+M8+M9+END1
    msg1 = mido.Message.from_hex(MESSAGE)
    # Request patch
    start = time.time()
    outport.send(msg1)
    while True:  # empiezo a leer inmediatamente despues de mandar el menasje
        msg = inport.poll() # Poll es como recive, pero no se cuelga cuando no hay mensaje.
        try:
            if msg.type == 'sysex': # if we get a message that is sysex
                if len(msg)>50: # En Drums manda primero un mensaje corto con el ultimo parametro tocado.
                    found = 1
                    break
        except:
            pass
        # if after one second is not receiving, break the loop.
        end = time.time()
        if end - start > .6:
            break
    if found == 0:
        return
    else:
        # Quito parentesis al principio y al final
        try: 
            data = str(msg.data)[1:-1]
        except AttributeError:
            dpg.configure_item('midi_error', show=True)
            return

        # creo una lista separando por comas
        datalist = str(data).split(',')
        # convierto a hex de 2 decimales
        for i in range(len(datalist)):
            datalist[i] = hex(int(datalist[i]))[2:].zfill(2).upper()
    # detecto drums
    if datalist[4] == '64':
        elnumber = 0
    else:
        # actualizo numero de elementos
        if datalist[31] == '05':
            elnumber = 1
        if datalist[31] == '06':
            elnumber= 2
        if datalist[31] == '07':
            elnumber = 4

    if NoWriteRequest == 0:
        if elnumber == 0:
            drawdrumcontrols()
        else:
            drawvoicecontrols()
    else:
        NoWriteRequest = 0
    changemode()

def drawvoicecontrols():
    global requestok, NoWriteRequest, EL, ELFILTER12, datalist, nosend, elnumber

    if len(datalist) not in (190,311,553): #190:1el / 311:2el / 553:4el
        dpg.configure_item('midi_error', show=True)
        return

    try:
        requestok = 1
        nosend = 1
        if datalist[31] == '05':
            elnum = 1
        if datalist[31] == '06':
            elnum= 2
        if datalist[31] == '07':
            elnum = 4
        ############################## COMMON
        #Voice Mode (elements)
        if elnum == 1:
            dpg.configure_item(item='voice_mode', default_value = '1 Element')
            dpg.configure_item(item='el2_tab', show = False)
            dpg.configure_item(item='el3_tab', show = False)
            dpg.configure_item(item='el4_tab', show = False)
            elnumber = 1
        if elnum == 2:
            dpg.configure_item(item='voice_mode', default_value = '2 Elements')
            dpg.configure_item(item='el2_tab', show = True)
            dpg.configure_item(item='el3_tab', show = False)
            dpg.configure_item(item='el4_tab', show = False)
            elnumber = 2
        if elnum == 4:
            dpg.configure_item(item='voice_mode', default_value = '4 Elements')
            dpg.configure_item(item='el2_tab', show = True)
            dpg.configure_item(item='el3_tab', show = True)
            dpg.configure_item(item='el4_tab', show = True)
            elnumber = 4

        # Voice Name
        name = ''
        for i in range(32,42):
            name = name+(bytearray.fromhex(datalist[i]).decode())
        dpg.configure_item(item='voice_name', default_value = name)

        # Efx Type + params 1,2,3
        dpg.configure_item(item='effect_type', default_value = effectslist[int(datalist[42],16)-1])
        effecttype('effect_type')

        # Efx output level
        dpg.configure_item(item='effect_level', default_value = int(datalist[43],16))

        # Pitch Bend Range
        dpg.configure_item(item='pitch_bend_range', default_value = int(datalist[47],16))

        # Aftertouch pitch bias
        decvalue = int(datalist[48],16)
        if decvalue > 16:
            decvalue = -(decvalue - 16)
        dpg.configure_item(item='aftertouch_pitch_bias', default_value = decvalue)

        # random pitch range
        dpg.configure_item(item='random_pitch_range', default_value = int(datalist[63],16)) 

        # Voice Volume
        dpg.configure_item(item='voice_volume', default_value = int(datalist[65],16)) 

        ############################## CONTROLLERS
        # pitch mod
        dpg.configure_item(item='pitch_mod_cc', default_value = controllerlist[int(datalist[49],16)])
        dpg.configure_item(item='pitch_mod_rng', default_value = int(datalist[50],16))
        # amp mod
        dpg.configure_item(item='amp_mod_cc', default_value = controllerlist[int(datalist[51],16)])
        dpg.configure_item(item='amp_mod_rng', default_value = int(datalist[52],16))  
        # cutoff mod
        dpg.configure_item(item='cutoff_mod_cc', default_value = controllerlist[int(datalist[53],16)])
        dpg.configure_item(item='cutoff_mod_rng', default_value = int(datalist[54],16))  
        # cutoff freq
        dpg.configure_item(item='cutoff_freq_cc', default_value = controllerlist[int(datalist[55],16)])
        dpg.configure_item(item='cutoff_freq_rng', default_value = int(datalist[56],16)) 
        # Env gen bias
        dpg.configure_item(item='env_gen_bias_cc', default_value =  controllerlist[int(datalist[59],16)]) 
        dpg.configure_item(item='env_gen_rng', default_value = int(datalist[60],16)) 
        # Voice Volume
        dpg.configure_item(item='volume_cc', default_value =  controllerlist[int(datalist[61],16)]) 
        dpg.configure_item(item='vol_min_rng', default_value = int(datalist[62],16)) 

        ############################## ELEMENTS

        ######## COMMON
        e = {}
        #EL1
        e['P_el1_volume'] = 68
        e['P_el1_detune'] = 69
        e['P_el1_noteshift'] = 70
        e['P_el1_notelimL'] = 71
        e['P_el1_notelimH'] = 72
        e['P_el1_vellimL'] = 73
        e['P_el1_vellimH'] = 74
        e['P_el1_pan'] = 75
        e['P_el1_efxbal'] = 76
        #EL2
        e['P_el2_volume'] = 77
        e['P_el2_detune'] = 78
        e['P_el2_noteshift'] = 79
        e['P_el2_notelimL'] = 80
        e['P_el2_notelimH'] = 81
        e['P_el2_vellimL'] = 82
        e['P_el2_vellimH'] = 83
        e['P_el2_pan'] = 84
        e['P_el2_efxbal'] = 85
        #EL3
        e['P_el3_volume'] = 86
        e['P_el3_detune'] = 87
        e['P_el3_noteshift'] = 88
        e['P_el3_notelimL'] = 89
        e['P_el3_notelimH'] = 90
        e['P_el3_vellimL'] = 91
        e['P_el3_vellimH'] = 92
        e['P_el3_pan'] = 93
        e['P_el3_efxbal'] = 94
        #EL4
        e['P_el4_volume'] = 95
        e['P_el4_detune'] = 96
        e['P_el4_noteshift'] = 97
        e['P_el4_notelimL'] = 98
        e['P_el4_notelimH'] = 99
        e['P_el4_vellimL'] = 100
        e['P_el4_vellimH'] = 101
        e['P_el4_pan'] = 102
        e['P_el4_efxbal'] = 103

        # 1 ELEMENT
        if elnum == 1:
            e['P_el1_voice'] = 79
            e['P_el1_oscfreqmode'] = 80
            e['P_el1_oscfreqnote'] = 81
            e['P_el1_oscfreqtune'] = 82
            e['P_el1_pitchmodsens'] = 83
            e['P_el1_pitchenvR1'] = 84
            e['P_el1_pitchenvR2'] = 85
            e['P_el1_pitchenvR3'] = 86
            e['P_el1_pitchenvRR'] = 87
            e['P_el1_pitchenvL0'] = 88
            e['P_el1_pitchenvL1'] = 89
            e['P_el1_pitchenvL2'] = 90
            e['P_el1_pitchenvL3'] = 91
            e['P_el1_pitchenvRL'] = 92
            e['P_el1_pitchenvrng'] = 93
            e['P_el1_pitchenvratescl'] = 94
            e['P_el1_pitchenvvelsw'] = 95
            e['P_el1_lfospd'] = 96
            e['P_el1_lfodly'] = 97
            e['P_el1_lfopitchmod'] = 98
            e['P_el1_lfoampmod'] = 99
            e['P_el1_lfocutoffmod'] = 100
            e['P_el1_lfowave'] = 101
            e['P_el1_lfophase'] = 102
            e['P_el1_fl1type'] = 104
            e['P_el1_fl1cutoff'] = 105
            e['P_el1_fl1mode'] = 106
            e['P_el1_fl1envR1'] = 107
            e['P_el1_fl1envR2'] = 108
            e['P_el1_fl1envR3'] = 109
            e['P_el1_fl1envR4'] = 110
            e['P_el1_fl1envRR1'] = 111
            e['P_el1_fl1envRR2'] = 112
            e['P_el1_fl1envL0'] = 113
            e['P_el1_fl1envL1'] = 114
            e['P_el1_fl1envL2'] = 115
            e['P_el1_fl1envL3'] = 116
            e['P_el1_fl1envL4'] = 117
            e['P_el1_fl1envRL1'] = 118
            e['P_el1_fl1envRL2'] = 119
            e['P_el1_fl1envertscl'] = 120
            e['P_el1_fl1envBP1'] = 121
            e['P_el1_fl1envBP2'] = 122
            e['P_el1_fl1envBP3'] = 123
            e['P_el1_fl1envBP4'] = 124
            e['P_el1_fl1envOff1b1'] = 125
            e['P_el1_fl1envOff1b2'] = 126
            e['P_el1_fl1envOff2b1'] = 127
            e['P_el1_fl1envOff2b2'] = 128
            e['P_el1_fl1envOff3b1'] = 129
            e['P_el1_fl1envOff3b2'] = 130
            e['P_el1_fl1envOff4b1'] = 131
            e['P_el1_fl1envOff4b2'] = 132
            e['P_el1_fl2type'] = 133
            e['P_el1_fl2cutoff'] = 134
            e['P_el1_fl2mode'] = 135
            e['P_el1_fl2envR1'] = 136
            e['P_el1_fl2envR2'] = 137
            e['P_el1_fl2envR3'] = 138
            e['P_el1_fl2envR4'] = 139
            e['P_el1_fl2envRR1'] = 140
            e['P_el1_fl2envRR2'] = 141
            e['P_el1_fl2envL0'] = 142
            e['P_el1_fl2envL1'] = 143
            e['P_el1_fl2envL2'] = 144
            e['P_el1_fl2envL3'] = 145
            e['P_el1_fl2envL4'] = 146
            e['P_el1_fl2envRL1'] = 147
            e['P_el1_fl2envRL2'] = 148
            e['P_el1_fl2envertscl'] = 149
            e['P_el1_fl2envBP1'] = 150
            e['P_el1_fl2envBP2'] = 151
            e['P_el1_fl2envBP3'] = 152
            e['P_el1_fl2envBP4'] = 153
            e['P_el1_fl2envOff1b1'] = 154
            e['P_el1_fl2envOff1b2'] = 155
            e['P_el1_fl2envOff2b1'] = 156
            e['P_el1_fl2envOff2b2'] = 157
            e['P_el1_fl2envOff3b1'] = 158
            e['P_el1_fl2envOff3b2'] = 159
            e['P_el1_fl2envOff4b1'] = 160
            e['P_el1_fl2envOff4b2'] = 161
            e['P_el1flres'] = 162
            e['P_el1flvelsens'] = 163
            e['P_el1flmodsens'] = 164
            e['P_el1ampenvmode'] = 165
            e['P_el1ampenvR1'] = 166
            e['P_el1ampenvR2'] = 167
            e['P_el1ampenvR3'] = 168
            e['P_el1ampenvR4'] = 169
            e['P_el1ampenvRR'] = 170
            e['P_el1ampenvL2'] = 171
            e['P_el1ampenvL3'] = 172
            e['P_el1ampenvrtscl'] = 173
            e['P_el1ampenvBP1'] = 174
            e['P_el1ampenvBP2'] = 175
            e['P_el1ampenvBP3'] = 176
            e['P_el1ampenvBP4'] = 177
            e['P_el1ampenvOff1b1'] = 178
            e['P_el1ampenvOff1b2'] = 179
            e['P_el1ampenvOff2b1'] = 180
            e['P_el1ampenvOff2b2'] = 181
            e['P_el1ampenvOff3b1'] = 182
            e['P_el1ampenvOff3b2'] = 183
            e['P_el1ampenvOff4b1'] = 184
            e['P_el1ampenvOff4b2'] = 185
            e['P_el1velsens'] = 186
            e['P_el1velratesens'] = 187
            e['P_el1ampmodsens'] = 188
        
        # 2 ELEMENTS
        if elnum == 2:
            ##### ELEMENT 1
            e['P_el1_voice'] = 88
            e['P_el1_oscfreqmode'] = 89
            e['P_el1_oscfreqnote'] = 90
            e['P_el1_oscfreqtune'] = 91
            e['P_el1_pitchmodsens'] = 92
            e['P_el1_pitchenvR1'] = 93
            e['P_el1_pitchenvR2'] = 94
            e['P_el1_pitchenvR3'] = 95
            e['P_el1_pitchenvRR'] = 96
            e['P_el1_pitchenvL0'] = 97
            e['P_el1_pitchenvL1'] = 98
            e['P_el1_pitchenvL2'] = 99
            e['P_el1_pitchenvL3'] = 100
            e['P_el1_pitchenvRL'] = 101
            e['P_el1_pitchenvrng'] = 102
            e['P_el1_pitchenvratescl'] = 103
            e['P_el1_pitchenvvelsw'] = 104
            e['P_el1_lfospd'] = 105
            e['P_el1_lfodly'] = 106
            e['P_el1_lfopitchmod'] = 107
            e['P_el1_lfoampmod'] = 108
            e['P_el1_lfocutoffmod'] = 109
            e['P_el1_lfowave'] = 110
            e['P_el1_lfophase'] = 111
            e['P_el1_fl1type'] = 113
            e['P_el1_fl1cutoff'] = 114
            e['P_el1_fl1mode'] = 115
            e['P_el1_fl1envR1'] = 116
            e['P_el1_fl1envR2'] = 117
            e['P_el1_fl1envR3'] = 118
            e['P_el1_fl1envR4'] = 119
            e['P_el1_fl1envRR1'] = 120
            e['P_el1_fl1envRR2'] = 121
            e['P_el1_fl1envL0'] = 122
            e['P_el1_fl1envL1'] = 123
            e['P_el1_fl1envL2'] = 124
            e['P_el1_fl1envL3'] = 125
            e['P_el1_fl1envL4'] = 126
            e['P_el1_fl1envRL1'] = 127
            e['P_el1_fl1envRL2'] = 128
            e['P_el1_fl1envertscl'] = 129
            e['P_el1_fl1envBP1'] = 130
            e['P_el1_fl1envBP2'] = 131
            e['P_el1_fl1envBP3'] = 132
            e['P_el1_fl1envBP4'] = 133
            e['P_el1_fl1envOff1b1'] = 134
            e['P_el1_fl1envOff1b2'] = 135
            e['P_el1_fl1envOff2b1'] = 136
            e['P_el1_fl1envOff2b2'] = 137
            e['P_el1_fl1envOff3b1'] = 138
            e['P_el1_fl1envOff3b2'] = 139
            e['P_el1_fl1envOff4b1'] = 140
            e['P_el1_fl1envOff4b2'] = 141
            e['P_el1_fl2type'] = 142
            e['P_el1_fl2cutoff'] = 143
            e['P_el1_fl2mode'] = 144
            e['P_el1_fl2envR1'] = 145
            e['P_el1_fl2envR2'] = 146
            e['P_el1_fl2envR3'] = 147
            e['P_el1_fl2envR4'] = 148
            e['P_el1_fl2envRR1'] = 149
            e['P_el1_fl2envRR2'] = 150
            e['P_el1_fl2envL0'] = 151
            e['P_el1_fl2envL1'] = 152
            e['P_el1_fl2envL2'] = 153
            e['P_el1_fl2envL3'] = 154
            e['P_el1_fl2envL4'] = 155
            e['P_el1_fl2envRL1'] = 156
            e['P_el1_fl2envRL2'] = 157
            e['P_el1_fl2envertscl'] = 158
            e['P_el1_fl2envBP1'] = 159
            e['P_el1_fl2envBP2'] = 160
            e['P_el1_fl2envBP3'] = 161
            e['P_el1_fl2envBP4'] = 162
            e['P_el1_fl2envOff1b1'] = 163
            e['P_el1_fl2envOff1b2'] = 164
            e['P_el1_fl2envOff2b1'] = 165
            e['P_el1_fl2envOff2b2'] = 166
            e['P_el1_fl2envOff3b1'] = 167
            e['P_el1_fl2envOff3b2'] = 168
            e['P_el1_fl2envOff4b1'] = 169
            e['P_el1_fl2envOff4b2'] = 170
            e['P_el1flres'] = 171
            e['P_el1flvelsens'] = 172
            e['P_el1flmodsens'] = 173
            e['P_el1ampenvmode'] = 174
            e['P_el1ampenvR1'] = 175
            e['P_el1ampenvR2'] = 176
            e['P_el1ampenvR3'] = 177
            e['P_el1ampenvR4'] = 178
            e['P_el1ampenvRR'] = 179
            e['P_el1ampenvL2'] = 180
            e['P_el1ampenvL3'] = 181
            e['P_el1ampenvrtscl'] = 182
            e['P_el1ampenvBP1'] = 183
            e['P_el1ampenvBP2'] = 184
            e['P_el1ampenvBP3'] = 185
            e['P_el1ampenvBP4'] = 186
            e['P_el1ampenvOff1b1'] = 187
            e['P_el1ampenvOff1b2'] = 188
            e['P_el1ampenvOff2b1'] = 189
            e['P_el1ampenvOff2b2'] = 190
            e['P_el1ampenvOff3b1'] = 191
            e['P_el1ampenvOff3b2'] = 192
            e['P_el1ampenvOff4b1'] = 193
            e['P_el1ampenvOff4b2'] = 194
            e['P_el1velsens'] = 195
            e['P_el1velratesens'] = 196
            e['P_el1ampmodsens'] = 197
            
            ##### ELEMENT 2
            e['P_el2_voice'] = 200
            e['P_el2_oscfreqmode'] = 201
            e['P_el2_oscfreqnote'] = 202
            e['P_el2_oscfreqtune'] = 203
            e['P_el2_pitchmodsens'] = 204
            e['P_el2_pitchenvR1'] = 205
            e['P_el2_pitchenvR2'] = 206
            e['P_el2_pitchenvR3'] = 207
            e['P_el2_pitchenvRR'] = 208
            e['P_el2_pitchenvL0'] = 209
            e['P_el2_pitchenvL1'] = 210
            e['P_el2_pitchenvL2'] = 211
            e['P_el2_pitchenvL3'] = 212
            e['P_el2_pitchenvRL'] = 213
            e['P_el2_pitchenvrng'] = 214
            e['P_el2_pitchenvratescl'] = 215
            e['P_el2_pitchenvvelsw'] = 216
            e['P_el2_lfospd'] = 217
            e['P_el2_lfodly'] = 218
            e['P_el2_lfopitchmod'] = 219
            e['P_el2_lfoampmod'] = 220
            e['P_el2_lfocutoffmod'] = 221
            e['P_el2_lfowave'] = 222
            e['P_el2_lfophase'] = 223
            e['P_el2_fl1type'] = 225
            e['P_el2_fl1cutoff'] = 226
            e['P_el2_fl1mode'] = 227
            e['P_el2_fl1envR1'] = 228
            e['P_el2_fl1envR2'] = 229
            e['P_el2_fl1envR3'] = 230
            e['P_el2_fl1envR4'] = 231
            e['P_el2_fl1envRR1'] = 232
            e['P_el2_fl1envRR2'] = 233
            e['P_el2_fl1envL0'] = 234
            e['P_el2_fl1envL1'] = 235
            e['P_el2_fl1envL2'] = 236
            e['P_el2_fl1envL3'] = 237
            e['P_el2_fl1envL4'] = 238
            e['P_el2_fl1envRL1'] = 239
            e['P_el2_fl1envRL2'] = 240
            e['P_el2_fl1envertscl'] = 241
            e['P_el2_fl1envBP1'] = 242
            e['P_el2_fl1envBP2'] = 243
            e['P_el2_fl1envBP3'] = 244
            e['P_el2_fl1envBP4'] = 245
            e['P_el2_fl1envOff1b1'] = 246
            e['P_el2_fl1envOff1b2'] = 247
            e['P_el2_fl1envOff2b1'] = 248
            e['P_el2_fl1envOff2b2'] = 249
            e['P_el2_fl1envOff3b1'] = 250
            e['P_el2_fl1envOff3b2'] = 251
            e['P_el2_fl1envOff4b1'] = 252
            e['P_el2_fl1envOff4b2'] = 253
            e['P_el2_fl2type'] = 254
            e['P_el2_fl2cutoff'] = 255
            e['P_el2_fl2mode'] = 256
            e['P_el2_fl2envR1'] = 257
            e['P_el2_fl2envR2'] = 258
            e['P_el2_fl2envR3'] = 259
            e['P_el2_fl2envR4'] = 260
            e['P_el2_fl2envRR1'] = 261
            e['P_el2_fl2envRR2'] = 262
            e['P_el2_fl2envL0'] = 263
            e['P_el2_fl2envL1'] = 264
            e['P_el2_fl2envL2'] = 265
            e['P_el2_fl2envL3'] = 266
            e['P_el2_fl2envL4'] = 267
            e['P_el2_fl2envRL1'] = 268
            e['P_el2_fl2envRL2'] = 269
            e['P_el2_fl2envertscl'] = 270
            e['P_el2_fl2envBP1'] = 271
            e['P_el2_fl2envBP2'] = 272
            e['P_el2_fl2envBP3'] = 273
            e['P_el2_fl2envBP4'] = 274
            e['P_el2_fl2envOff1b1'] = 275
            e['P_el2_fl2envOff1b2'] = 276
            e['P_el2_fl2envOff2b1'] = 277
            e['P_el2_fl2envOff2b2'] = 278
            e['P_el2_fl2envOff3b1'] = 279
            e['P_el2_fl2envOff3b2'] = 280
            e['P_el2_fl2envOff4b1'] = 281
            e['P_el2_fl2envOff4b2'] = 282
            e['P_el2flres'] = 283
            e['P_el2flvelsens'] = 284
            e['P_el2flmodsens'] = 285
            e['P_el2ampenvmode'] = 286
            e['P_el2ampenvR1'] = 287
            e['P_el2ampenvR2'] = 288
            e['P_el2ampenvR3'] = 289
            e['P_el2ampenvR4'] = 290
            e['P_el2ampenvRR'] = 291
            e['P_el2ampenvL2'] = 292
            e['P_el2ampenvL3'] = 293
            e['P_el2ampenvrtscl'] = 294
            e['P_el2ampenvBP1'] = 295
            e['P_el2ampenvBP2'] = 296
            e['P_el2ampenvBP3'] = 297
            e['P_el2ampenvBP4'] = 298
            e['P_el2ampenvOff1b1'] = 299
            e['P_el2ampenvOff1b2'] = 300
            e['P_el2ampenvOff2b1'] = 301
            e['P_el2ampenvOff2b2'] = 302
            e['P_el2ampenvOff3b1'] = 303
            e['P_el2ampenvOff3b2'] = 304
            e['P_el2ampenvOff4b1'] = 305
            e['P_el2ampenvOff4b2'] = 306
            e['P_el2velsens'] = 307
            e['P_el2velratesens'] = 308
            e['P_el2ampmodsens'] = 309

        # 4 ELEMENTS
        if elnum == 4:
            ##### ELEMENT 1
            e['P_el1_voice'] = 106
            e['P_el1_oscfreqmode'] = 107
            e['P_el1_oscfreqnote'] = 108
            e['P_el1_oscfreqtune'] = 109
            e['P_el1_pitchmodsens'] = 110
            e['P_el1_pitchenvR1'] = 111
            e['P_el1_pitchenvR2'] = 112
            e['P_el1_pitchenvR3'] = 113
            e['P_el1_pitchenvRR'] = 114
            e['P_el1_pitchenvL0'] = 115
            e['P_el1_pitchenvL1'] = 116
            e['P_el1_pitchenvL2'] = 117
            e['P_el1_pitchenvL3'] = 118
            e['P_el1_pitchenvRL'] = 119
            e['P_el1_pitchenvrng'] = 120
            e['P_el1_pitchenvratescl'] = 121
            e['P_el1_pitchenvvelsw'] = 122
            e['P_el1_lfospd'] = 123
            e['P_el1_lfodly'] = 124
            e['P_el1_lfopitchmod'] = 125
            e['P_el1_lfoampmod'] = 126
            e['P_el1_lfocutoffmod'] = 127
            e['P_el1_lfowave'] = 128
            e['P_el1_lfophase'] = 129
            e['P_el1_fl1type'] = 131
            e['P_el1_fl1cutoff'] = 132
            e['P_el1_fl1mode'] = 133
            e['P_el1_fl1envR1'] = 134
            e['P_el1_fl1envR2'] = 135
            e['P_el1_fl1envR3'] = 136
            e['P_el1_fl1envR4'] = 137
            e['P_el1_fl1envRR1'] = 138
            e['P_el1_fl1envRR2'] = 139
            e['P_el1_fl1envL0'] = 140
            e['P_el1_fl1envL1'] = 141
            e['P_el1_fl1envL2'] = 142
            e['P_el1_fl1envL3'] = 143
            e['P_el1_fl1envL4'] = 144
            e['P_el1_fl1envRL1'] = 145
            e['P_el1_fl1envRL2'] = 146
            e['P_el1_fl1envertscl'] = 147
            e['P_el1_fl1envBP1'] = 148
            e['P_el1_fl1envBP2'] = 149
            e['P_el1_fl1envBP3'] = 150
            e['P_el1_fl1envBP4'] = 151
            e['P_el1_fl1envOff1b1'] = 152
            e['P_el1_fl1envOff1b2'] = 153
            e['P_el1_fl1envOff2b1'] = 154
            e['P_el1_fl1envOff2b2'] = 155
            e['P_el1_fl1envOff3b1'] = 156
            e['P_el1_fl1envOff3b2'] = 157
            e['P_el1_fl1envOff4b1'] = 158
            e['P_el1_fl1envOff4b2'] = 159
            e['P_el1_fl2type'] = 160
            e['P_el1_fl2cutoff'] = 161
            e['P_el1_fl2mode'] = 162
            e['P_el1_fl2envR1'] = 163
            e['P_el1_fl2envR2'] = 164
            e['P_el1_fl2envR3'] = 165
            e['P_el1_fl2envR4'] = 166
            e['P_el1_fl2envRR1'] = 167
            e['P_el1_fl2envRR2'] = 168
            e['P_el1_fl2envL0'] = 169
            e['P_el1_fl2envL1'] = 170
            e['P_el1_fl2envL2'] = 171
            e['P_el1_fl2envL3'] = 172
            e['P_el1_fl2envL4'] = 173
            e['P_el1_fl2envRL1'] = 174
            e['P_el1_fl2envRL2'] = 175
            e['P_el1_fl2envertscl'] = 176
            e['P_el1_fl2envBP1'] = 177
            e['P_el1_fl2envBP2'] = 178
            e['P_el1_fl2envBP3'] = 179
            e['P_el1_fl2envBP4'] = 180
            e['P_el1_fl2envOff1b1'] = 181
            e['P_el1_fl2envOff1b2'] = 182
            e['P_el1_fl2envOff2b1'] = 183
            e['P_el1_fl2envOff2b2'] = 184
            e['P_el1_fl2envOff3b1'] = 185
            e['P_el1_fl2envOff3b2'] = 186
            e['P_el1_fl2envOff4b1'] = 187
            e['P_el1_fl2envOff4b2'] = 188
            e['P_el1flres'] = 189
            e['P_el1flvelsens'] = 190
            e['P_el1flmodsens'] = 191
            e['P_el1ampenvmode'] = 192
            e['P_el1ampenvR1'] = 193
            e['P_el1ampenvR2'] = 194
            e['P_el1ampenvR3'] = 195
            e['P_el1ampenvR4'] = 196
            e['P_el1ampenvRR'] = 197
            e['P_el1ampenvL2'] = 198
            e['P_el1ampenvL3'] = 199
            e['P_el1ampenvrtscl'] = 200
            e['P_el1ampenvBP1'] = 201
            e['P_el1ampenvBP2'] = 202
            e['P_el1ampenvBP3'] = 203
            e['P_el1ampenvBP4'] = 204
            e['P_el1ampenvOff1b1'] = 205
            e['P_el1ampenvOff1b2'] = 206
            e['P_el1ampenvOff2b1'] = 207
            e['P_el1ampenvOff2b2'] = 208
            e['P_el1ampenvOff3b1'] = 209
            e['P_el1ampenvOff3b2'] = 210
            e['P_el1ampenvOff4b1'] = 211
            e['P_el1ampenvOff4b2'] = 212
            e['P_el1velsens'] = 213
            e['P_el1velratesens'] = 214
            e['P_el1ampmodsens'] = 215

            ##### ELEMENT 2
            e['P_el2_voice'] = 218
            e['P_el2_oscfreqmode'] = 219
            e['P_el2_oscfreqnote'] = 220
            e['P_el2_oscfreqtune'] = 221
            e['P_el2_pitchmodsens'] = 222
            e['P_el2_pitchenvR1'] = 223
            e['P_el2_pitchenvR2'] = 224
            e['P_el2_pitchenvR3'] = 225
            e['P_el2_pitchenvRR'] = 226
            e['P_el2_pitchenvL0'] = 227
            e['P_el2_pitchenvL1'] = 228
            e['P_el2_pitchenvL2'] = 229
            e['P_el2_pitchenvL3'] = 230
            e['P_el2_pitchenvRL'] = 231
            e['P_el2_pitchenvrng'] = 232
            e['P_el2_pitchenvratescl'] = 233
            e['P_el2_pitchenvvelsw'] = 234
            e['P_el2_lfospd'] = 235
            e['P_el2_lfodly'] = 236
            e['P_el2_lfopitchmod'] = 237
            e['P_el2_lfoampmod'] = 238
            e['P_el2_lfocutoffmod'] = 239
            e['P_el2_lfowave'] = 240
            e['P_el2_lfophase'] = 241
            e['P_el2_fl1type'] = 243
            e['P_el2_fl1cutoff'] = 244
            e['P_el2_fl1mode'] = 245
            e['P_el2_fl1envR1'] = 246
            e['P_el2_fl1envR2'] = 247
            e['P_el2_fl1envR3'] = 248
            e['P_el2_fl1envR4'] = 249
            e['P_el2_fl1envRR1'] = 250
            e['P_el2_fl1envRR2'] = 251
            e['P_el2_fl1envL0'] = 252
            e['P_el2_fl1envL1'] = 253
            e['P_el2_fl1envL2'] = 254
            e['P_el2_fl1envL3'] = 255
            e['P_el2_fl1envL4'] = 256
            e['P_el2_fl1envRL1'] = 257
            e['P_el2_fl1envRL2'] = 258
            e['P_el2_fl1envertscl'] = 259
            e['P_el2_fl1envBP1'] = 260
            e['P_el2_fl1envBP2'] = 261
            e['P_el2_fl1envBP3'] = 262
            e['P_el2_fl1envBP4'] = 263
            e['P_el2_fl1envOff1b1'] = 264
            e['P_el2_fl1envOff1b2'] = 265
            e['P_el2_fl1envOff2b1'] = 266
            e['P_el2_fl1envOff2b2'] = 267
            e['P_el2_fl1envOff3b1'] = 268
            e['P_el2_fl1envOff3b2'] = 269
            e['P_el2_fl1envOff4b1'] = 270
            e['P_el2_fl1envOff4b2'] = 271
            e['P_el2_fl2type'] = 272
            e['P_el2_fl2cutoff'] = 273
            e['P_el2_fl2mode'] = 274
            e['P_el2_fl2envR1'] = 275
            e['P_el2_fl2envR2'] = 276
            e['P_el2_fl2envR3'] = 277
            e['P_el2_fl2envR4'] = 278
            e['P_el2_fl2envRR1'] = 279
            e['P_el2_fl2envRR2'] = 280
            e['P_el2_fl2envL0'] = 281
            e['P_el2_fl2envL1'] = 282
            e['P_el2_fl2envL2'] = 283
            e['P_el2_fl2envL3'] = 284
            e['P_el2_fl2envL4'] = 285
            e['P_el2_fl2envRL1'] = 286
            e['P_el2_fl2envRL2'] = 287
            e['P_el2_fl2envertscl'] = 288
            e['P_el2_fl2envBP1'] = 289
            e['P_el2_fl2envBP2'] = 290
            e['P_el2_fl2envBP3'] = 291
            e['P_el2_fl2envBP4'] = 292
            e['P_el2_fl2envOff1b1'] = 293
            e['P_el2_fl2envOff1b2'] = 294
            e['P_el2_fl2envOff2b1'] = 295
            e['P_el2_fl2envOff2b2'] = 296
            e['P_el2_fl2envOff3b1'] = 297
            e['P_el2_fl2envOff3b2'] = 298
            e['P_el2_fl2envOff4b1'] = 299
            e['P_el2_fl2envOff4b2'] = 300
            e['P_el2flres'] = 301
            e['P_el2flvelsens'] = 302
            e['P_el2flmodsens'] = 303
            e['P_el2ampenvmode'] = 304
            e['P_el2ampenvR1'] = 305
            e['P_el2ampenvR2'] = 306
            e['P_el2ampenvR3'] = 307
            e['P_el2ampenvR4'] = 308
            e['P_el2ampenvRR'] = 309
            e['P_el2ampenvL2'] = 310
            e['P_el2ampenvL3'] = 311
            e['P_el2ampenvrtscl'] = 312
            e['P_el2ampenvBP1'] = 313
            e['P_el2ampenvBP2'] = 314
            e['P_el2ampenvBP3'] = 315
            e['P_el2ampenvBP4'] = 316
            e['P_el2ampenvOff1b1'] = 317
            e['P_el2ampenvOff1b2'] = 318
            e['P_el2ampenvOff2b1'] = 319
            e['P_el2ampenvOff2b2'] = 320
            e['P_el2ampenvOff3b1'] = 321
            e['P_el2ampenvOff3b2'] = 322
            e['P_el2ampenvOff4b1'] = 323
            e['P_el2ampenvOff4b2'] = 324
            e['P_el2velsens'] = 325
            e['P_el2velratesens'] = 326
            e['P_el2ampmodsens'] = 327

    ##### ELEMENT 3
            e['P_el3_voice'] = 330
            e['P_el3_oscfreqmode'] = 331
            e['P_el3_oscfreqnote'] = 332
            e['P_el3_oscfreqtune'] = 333
            e['P_el3_pitchmodsens'] = 334
            e['P_el3_pitchenvR1'] = 335
            e['P_el3_pitchenvR2'] = 336
            e['P_el3_pitchenvR3'] = 337
            e['P_el3_pitchenvRR'] = 338
            e['P_el3_pitchenvL0'] = 339
            e['P_el3_pitchenvL1'] = 340
            e['P_el3_pitchenvL2'] = 341
            e['P_el3_pitchenvL3'] = 342
            e['P_el3_pitchenvRL'] = 343
            e['P_el3_pitchenvrng'] = 344
            e['P_el3_pitchenvratescl'] = 345
            e['P_el3_pitchenvvelsw'] = 346
            e['P_el3_lfospd'] = 347
            e['P_el3_lfodly'] = 348
            e['P_el3_lfopitchmod'] = 349
            e['P_el3_lfoampmod'] = 350
            e['P_el3_lfocutoffmod'] = 351
            e['P_el3_lfowave'] = 352
            e['P_el3_lfophase'] = 353
            e['P_el3_fl1type'] = 355
            e['P_el3_fl1cutoff'] = 356
            e['P_el3_fl1mode'] = 357
            e['P_el3_fl1envR1'] = 358
            e['P_el3_fl1envR2'] = 359
            e['P_el3_fl1envR3'] = 360
            e['P_el3_fl1envR4'] = 361
            e['P_el3_fl1envRR1'] = 362
            e['P_el3_fl1envRR2'] = 363
            e['P_el3_fl1envL0'] = 364
            e['P_el3_fl1envL1'] = 365
            e['P_el3_fl1envL2'] = 366
            e['P_el3_fl1envL3'] = 367
            e['P_el3_fl1envL4'] = 368
            e['P_el3_fl1envRL1'] = 369
            e['P_el3_fl1envRL2'] = 370
            e['P_el3_fl1envertscl'] = 371
            e['P_el3_fl1envBP1'] = 372
            e['P_el3_fl1envBP2'] = 373
            e['P_el3_fl1envBP3'] = 374
            e['P_el3_fl1envBP4'] = 375
            e['P_el3_fl1envOff1b1'] = 376
            e['P_el3_fl1envOff1b2'] = 377
            e['P_el3_fl1envOff2b1'] = 378
            e['P_el3_fl1envOff2b2'] = 379
            e['P_el3_fl1envOff3b1'] = 380
            e['P_el3_fl1envOff3b2'] = 381
            e['P_el3_fl1envOff4b1'] = 382
            e['P_el3_fl1envOff4b2'] = 383
            e['P_el3_fl2type'] = 384
            e['P_el3_fl2cutoff'] = 385
            e['P_el3_fl2mode'] = 386
            e['P_el3_fl2envR1'] = 387
            e['P_el3_fl2envR2'] = 388
            e['P_el3_fl2envR3'] = 389
            e['P_el3_fl2envR4'] = 390
            e['P_el3_fl2envRR1'] = 391
            e['P_el3_fl2envRR2'] = 392
            e['P_el3_fl2envL0'] = 393
            e['P_el3_fl2envL1'] = 394
            e['P_el3_fl2envL2'] = 395
            e['P_el3_fl2envL3'] = 396
            e['P_el3_fl2envL4'] = 397
            e['P_el3_fl2envRL1'] = 398
            e['P_el3_fl2envRL2'] = 399
            e['P_el3_fl2envertscl'] = 400
            e['P_el3_fl2envBP1'] = 401
            e['P_el3_fl2envBP2'] = 402
            e['P_el3_fl2envBP3'] = 403
            e['P_el3_fl2envBP4'] = 404
            e['P_el3_fl2envOff1b1'] = 405
            e['P_el3_fl2envOff1b2'] = 406
            e['P_el3_fl2envOff2b1'] = 407
            e['P_el3_fl2envOff2b2'] = 408
            e['P_el3_fl2envOff3b1'] = 409
            e['P_el3_fl2envOff3b2'] = 410
            e['P_el3_fl2envOff4b1'] = 411
            e['P_el3_fl2envOff4b2'] = 412
            e['P_el3flres'] = 413
            e['P_el3flvelsens'] = 414
            e['P_el3flmodsens'] = 415
            e['P_el3ampenvmode'] = 416
            e['P_el3ampenvR1'] = 417
            e['P_el3ampenvR2'] = 418
            e['P_el3ampenvR3'] = 419
            e['P_el3ampenvR4'] = 420
            e['P_el3ampenvRR'] = 421
            e['P_el3ampenvL2'] = 422
            e['P_el3ampenvL3'] = 423
            e['P_el3ampenvrtscl'] = 424
            e['P_el3ampenvBP1'] = 425
            e['P_el3ampenvBP2'] = 426
            e['P_el3ampenvBP3'] = 427
            e['P_el3ampenvBP4'] = 428
            e['P_el3ampenvOff1b1'] = 429
            e['P_el3ampenvOff1b2'] = 430
            e['P_el3ampenvOff2b1'] = 431
            e['P_el3ampenvOff2b2'] = 432
            e['P_el3ampenvOff3b1'] = 433
            e['P_el3ampenvOff3b2'] = 434
            e['P_el3ampenvOff4b1'] = 435
            e['P_el3ampenvOff4b2'] = 436
            e['P_el3velsens'] = 437
            e['P_el3velratesens'] = 438
            e['P_el3ampmodsens'] = 439
    ##### ELEMENT 4
            e['P_el4_voice'] = 442
            e['P_el4_oscfreqmode'] = 443
            e['P_el4_oscfreqnote'] = 444
            e['P_el4_oscfreqtune'] = 445
            e['P_el4_pitchmodsens'] = 446
            e['P_el4_pitchenvR1'] = 447
            e['P_el4_pitchenvR2'] = 448
            e['P_el4_pitchenvR3'] = 449
            e['P_el4_pitchenvRR'] = 450
            e['P_el4_pitchenvL0'] = 451
            e['P_el4_pitchenvL1'] = 452
            e['P_el4_pitchenvL2'] = 453
            e['P_el4_pitchenvL3'] = 454
            e['P_el4_pitchenvRL'] = 455
            e['P_el4_pitchenvrng'] = 456
            e['P_el4_pitchenvratescl'] = 457
            e['P_el4_pitchenvvelsw'] = 458
            e['P_el4_lfospd'] = 459
            e['P_el4_lfodly'] = 460
            e['P_el4_lfopitchmod'] = 461
            e['P_el4_lfoampmod'] = 462
            e['P_el4_lfocutoffmod'] = 463
            e['P_el4_lfowave'] = 464
            e['P_el4_lfophase'] = 465
            e['P_el4_fl1type'] = 467
            e['P_el4_fl1cutoff'] = 468
            e['P_el4_fl1mode'] = 469
            e['P_el4_fl1envR1'] = 470
            e['P_el4_fl1envR2'] = 471
            e['P_el4_fl1envR3'] = 472
            e['P_el4_fl1envR4'] = 473
            e['P_el4_fl1envRR1'] = 474
            e['P_el4_fl1envRR2'] = 475
            e['P_el4_fl1envL0'] = 476
            e['P_el4_fl1envL1'] = 477
            e['P_el4_fl1envL2'] = 478
            e['P_el4_fl1envL3'] = 479
            e['P_el4_fl1envL4'] = 480
            e['P_el4_fl1envRL1'] = 481
            e['P_el4_fl1envRL2'] = 482
            e['P_el4_fl1envertscl'] = 483
            e['P_el4_fl1envBP1'] = 484
            e['P_el4_fl1envBP2'] = 485
            e['P_el4_fl1envBP3'] = 486
            e['P_el4_fl1envBP4'] = 487
            e['P_el4_fl1envOff1b1'] = 488
            e['P_el4_fl1envOff1b2'] = 489
            e['P_el4_fl1envOff2b1'] = 490
            e['P_el4_fl1envOff2b2'] = 491
            e['P_el4_fl1envOff3b1'] = 492
            e['P_el4_fl1envOff3b2'] = 493
            e['P_el4_fl1envOff4b1'] = 494
            e['P_el4_fl1envOff4b2'] = 495
            e['P_el4_fl2type'] = 496
            e['P_el4_fl2cutoff'] = 497
            e['P_el4_fl2mode'] = 498
            e['P_el4_fl2envR1'] = 499
            e['P_el4_fl2envR2'] = 500
            e['P_el4_fl2envR3'] = 501
            e['P_el4_fl2envR4'] = 502
            e['P_el4_fl2envRR1'] = 503
            e['P_el4_fl2envRR2'] = 504
            e['P_el4_fl2envL0'] = 505
            e['P_el4_fl2envL1'] = 506
            e['P_el4_fl2envL2'] = 507
            e['P_el4_fl2envL3'] = 508
            e['P_el4_fl2envL4'] = 509
            e['P_el4_fl2envRL1'] = 510
            e['P_el4_fl2envRL2'] = 511
            e['P_el4_fl2envertscl'] = 512
            e['P_el4_fl2envBP1'] = 513
            e['P_el4_fl2envBP2'] = 514
            e['P_el4_fl2envBP3'] = 515
            e['P_el4_fl2envBP4'] = 516
            e['P_el4_fl2envOff1b1'] = 517
            e['P_el4_fl2envOff1b2'] = 518
            e['P_el4_fl2envOff2b1'] = 519
            e['P_el4_fl2envOff2b2'] = 520
            e['P_el4_fl2envOff3b1'] = 521
            e['P_el4_fl2envOff3b2'] = 522
            e['P_el4_fl2envOff4b1'] = 523
            e['P_el4_fl2envOff4b2'] = 524
            e['P_el4flres'] = 525
            e['P_el4flvelsens'] = 526
            e['P_el4flmodsens'] = 527
            e['P_el4ampenvmode'] = 528
            e['P_el4ampenvR1'] = 529
            e['P_el4ampenvR2'] = 530
            e['P_el4ampenvR3'] = 531
            e['P_el4ampenvR4'] = 532
            e['P_el4ampenvRR'] = 533
            e['P_el4ampenvL2'] = 534
            e['P_el4ampenvL3'] = 535
            e['P_el4ampenvrtscl'] = 536
            e['P_el4ampenvBP1'] = 537
            e['P_el4ampenvBP2'] = 538
            e['P_el4ampenvBP3'] = 539
            e['P_el4ampenvBP4'] = 540
            e['P_el4ampenvOff1b1'] = 541
            e['P_el4ampenvOff1b2'] = 542
            e['P_el4ampenvOff2b1'] = 543
            e['P_el4ampenvOff2b2'] = 544
            e['P_el4ampenvOff3b1'] = 545
            e['P_el4ampenvOff3b2'] = 546
            e['P_el4ampenvOff4b1'] = 547
            e['P_el4ampenvOff4b2'] = 548
            e['P_el4velsens'] = 549
            e['P_el4velratesens'] = 550
            e['P_el4ampmodsens'] = 551
        
        for i in range(1,elnum+1):
            EL = 'el'+str(i)
            # Vol
            dpg.configure_item(item='el'+str(i)+'_volume', default_value =  int(datalist[e['P_el'+str(i)+'_volume']],16))

            # detune
            decvalue = int(datalist[e['P_el'+str(i)+'_detune']],16)
            eldetune(decvalue)

            # note shift
            decvalue = int(datalist[e['P_el'+str(i)+'_noteshift']],16)
            elnoteshift(decvalue)

            # Note Limit L
            dpg.configure_item(item='el'+str(i)+'_note_limitL', default_value = notelist[int(datalist[e['P_el'+str(i)+'_notelimL']],16)])
            # Note Limit H
            dpg.configure_item(item='el'+str(i)+'_note_limitH', default_value = notelist[int(datalist[e['P_el'+str(i)+'_notelimH']],16)])
            # Vel Limit L
            dpg.configure_item(item='el'+str(i)+'_vel_limitL', default_value = int(datalist[e['P_el'+str(i)+'_vellimL']],16))
            # Vel Limit H
            dpg.configure_item(item='el'+str(i)+'_vel_limitH', default_value = int(datalist[e['P_el'+str(i)+'_vellimH']],16))

            # pan
            decvalue = int(datalist[e['P_el'+str(i)+'_pan']],16) # el1 = 75, el2 = 84
            elpan(decvalue)

            # efx balance
            decvalue = int(datalist[e['P_el'+str(i)+'_efxbal']],16)
            elefxbalance(decvalue)

            # Element AWM Voice
            dpg.configure_item(item='el'+str(i)+'_Waveform', default_value = voicelist[int(datalist[e['P_el'+str(i)+'_voice']],16)])

            # OSC freq mode
            dpg.configure_item(item='el'+str(i)+'_osc_freq_mode', default_value = int(datalist[e['P_el'+str(i)+'_oscfreqmode']],16))
            if int(datalist[e['P_el'+str(i)+'_oscfreqmode']],16) == 1:
                dpg.configure_item(item='el'+str(i)+'_osc_freq_note', enabled = True)
            else:
                dpg.configure_item(item='el'+str(i)+'_osc_freq_note', default_value = '') 
                dpg.configure_item(item='el'+str(i)+'_osc_freq_note', enabled = False)

            # OSC freq note
            if int(datalist[e['P_el'+str(i)+'_oscfreqmode']],16) == 1:
                dpg.configure_item(item='el'+str(i)+'_osc_freq_note', default_value = notelist[int(datalist[e['P_el'+str(i)+'_oscfreqnote']],16)])

            # OSC freq tune
            decvalue = int(datalist[e['P_el'+str(i)+'_oscfreqtune']],16)
            eloscfreqtune(decvalue)

            # Pitch mod sens
            decvalue = int(datalist[e['P_el'+str(i)+'_pitchmodsens']],16)
            elpitchmodsens(decvalue)

            # Pitch envelope
            for n in pitchenvlist:
                a = 'el'+str(i)+'_pitch_env_'+n
                b = int(datalist[e['P_el'+str(i)+'_pitchenv'+n]],16)
                if 'L' in n:
                    b=b-64
                dpg.configure_item(item=a,default_value = b)
                elpitchenvelope(a)

            # Pitch envelope range
            decvalue = 3-int(datalist[e['P_el'+str(i)+'_pitchenvrng']],16)
            dpg.configure_item(item='el'+str(i)+'_pitch_env_range', default_value = decvalue)
            elpitchenvrange('el'+str(i)+'_pitch_env_range')

            # Pitch env ratescale
            decvalue = int(datalist[e['P_el'+str(i)+'_pitchenvratescl']],16)
            if decvalue>7:
                decvalue = 8 - abs(decvalue)
            dpg.configure_item(item='el'+str(i)+'_pitch_env_rate_scale', default_value = decvalue)

            #Pitch env velocity switch
            decvalue = int(datalist[e['P_el'+str(i)+'_pitchenvvelsw']],16)
            dpg.configure_item(item='el'+str(i)+'_pitch_env_vel_sw', default_value = 1-decvalue)

            # LFO Speed
            decvalue = int(datalist[e['P_el'+str(i)+'_lfospd']],16)
            ellfospeed(decvalue)

            # LFO Delay
            decvalue = int(datalist[e['P_el'+str(i)+'_lfodly']],16)
            ellfodelay(decvalue)

            # LFO Pitchmod
            decvalue = int(datalist[e['P_el'+str(i)+'_lfopitchmod']],16)
            ellfopitchmod(decvalue)

            # LFO Ampmod
            decvalue = int(datalist[e['P_el'+str(i)+'_lfoampmod']],16)
            ellfoampmod(decvalue)

            # LFO Cutoffmod
            decvalue = int(datalist[e['P_el'+str(i)+'_lfocutoffmod']],16)
            ellfocutoffmod(decvalue)

            # LFO Wave
            decvalue = int(datalist[e['P_el'+str(i)+'_lfowave']],16)
            dpg.configure_item(item='el'+str(i)+'_lfo_wave', default_value = decvalue)
            ellfowave(decvalue)

            # LFO Phase
            decvalue = int(datalist[e['P_el'+str(i)+'_lfophase']],16)
            ellfophase(decvalue)

            # Filter1type
            decvalue = int(datalist[e['P_el'+str(i)+'_fl1type']],16)
            ELFILTER12 = str(int(EL[2:3])-1)+'0'
            dpg.configure_item(item='el'+str(i)+'_filter1_type', default_value = decvalue)
            elfilter12type(decvalue)

            # Filter 1 Cutoff
            decvalue = int(datalist[e['P_el'+str(i)+'_fl1cutoff']],16)
            ELFILTER12 = str(int(EL[2:3])-1)+'0'
            dpg.configure_item(item='el'+str(i)+'_filter1_cutoff', default_value = decvalue)
            elfilter12cutoff(decvalue)

            # Filter 1 mode
            decvalue = int(datalist[e['P_el'+str(i)+'_fl1mode']],16)
            ELFILTER12 = str(int(EL[2:3])-1)+'0'
            dpg.configure_item(item='el'+str(i)+'_filter1_mode', default_value = decvalue)
            elfilter12mode(decvalue)

            # Filter 1 env
            ELFILTER12 = str(int(EL[2:3])-1)+'0'
            for n in filterenvlist:
                a = 'el'+str(i)+'_filter1_env_'+n
                b = int(datalist[e['P_el'+str(i)+'_fl1env'+n]],16)
                if 'L' in n:
                    b=b-64
                dpg.configure_item(item=a,default_value = b)
                elfilter12envelope(a)

            # Filter 1 env rate scale
            decvalue = int(datalist[e['P_el'+str(i)+'_fl1envertscl']],16)
            if decvalue>7:
                decvalue = 8-decvalue
            dpg.configure_item(item='el'+str(i)+'_filter1_env_rate_scale', default_value = decvalue)

            # Filter 1 env Breakpoints
            for n in range(1,5):
                param = int(datalist[e['P_el'+str(i)+'_fl1envBP'+str(n)]],16)
                dpg.configure_item(item='el'+str(i)+'_filter1_env_bp'+str(n), default_value = notelist[param])

            # Filter 1 breakpoints scale Offset 
            for n in range(1,5):
                bit1 = int(datalist[e['P_el'+str(i)+'_fl1envOff'+str(n)+'b1']],16)
                bit2 = int(datalist[e['P_el'+str(i)+'_fl1envOff'+str(n)+'b2']],16)
                if bit1 == 0:
                    decvalue = bit2 - 128
                else:
                    decvalue = bit2
                dpg.configure_item(item='el'+str(i)+'_filter1_env_sc_off_'+str(n), default_value = decvalue)

            # Filter2type
            decvalue = int(datalist[e['P_el'+str(i)+'_fl2type']],16)
            ELFILTER12 = str(int(EL[2:3])+3)+'0'
            dpg.configure_item(item='el'+str(i)+'_filter2_type', default_value = decvalue)
            elfilter12type(decvalue)

            # Filter 2 Cutoff
            decvalue = int(datalist[e['P_el'+str(i)+'_fl2cutoff']],16)
            ELFILTER12 = str(int(EL[2:3])+3)+'0'
            dpg.configure_item(item='el'+str(i)+'_filter2_cutoff', default_value = decvalue)
            elfilter12cutoff(decvalue)

            # Filter 2 mode
            decvalue = int(datalist[e['P_el'+str(i)+'_fl2mode']],16)
            ELFILTER12 = str(int(EL[2:3])+3)+'0'
            dpg.configure_item(item='el'+str(i)+'_filter2_mode', default_value = decvalue)
            elfilter12mode(decvalue)

            # Filter 2 env
            ELFILTER12 = str(int(EL[2:3])+3)+'0'
            for n in filterenvlist:
                a = 'el'+str(i)+'_filter2_env_'+n
                b = int(datalist[e['P_el'+str(i)+'_fl2env'+n]],16)
                if 'L' in n:
                    b=b-64
                dpg.configure_item(item=a,default_value = b)
                elfilter12envelope(a)

            # Filter 2 env rate scale
            decvalue = int(datalist[e['P_el'+str(i)+'_fl2envertscl']],16)
            if decvalue>7:
                decvalue = 8-decvalue
            dpg.configure_item(item='el'+str(i)+'_filter2_env_rate_scale', default_value = decvalue)

            # Filter 2 env Breakpoints
            for n in range(1,5):
                param = int(datalist[e['P_el'+str(i)+'_fl2envBP'+str(n)]],16)
                dpg.configure_item(item='el'+str(i)+'_filter2_env_bp'+str(n), default_value = notelist[param])

            # Filter 2 breakpoints scale Offset 
            for n in range(1,5):
                bit1 = int(datalist[e['P_el'+str(i)+'_fl2envOff'+str(n)+'b1']],16)
                bit2 = int(datalist[e['P_el'+str(i)+'_fl2envOff'+str(n)+'b2']],16)
                if bit1 == 0:
                    decvalue = bit2 - 128
                else:
                    decvalue = bit2
                dpg.configure_item(item='el'+str(i)+'_filter2_env_sc_off_'+str(n), default_value = decvalue)

            # Filter resonance:
            decvalue = int(datalist[e['P_el'+str(i)+'flres']],16)
            dpg.configure_item(item='el'+str(i)+'_filter1_reso', default_value = decvalue)

            # Filter vel sens:
            decvalue = int(datalist[e['P_el'+str(i)+'flvelsens']],16)
            elfiltervelsens(decvalue)

            # Filter mod sens:
            decvalue = int(datalist[e['P_el'+str(i)+'flmodsens']],16)
            elfiltermodsens(decvalue)

            # Amp Env mode:
            decvalue = int(datalist[e['P_el'+str(i)+'ampenvmode']],16)
            dpg.configure_item(item='el'+str(i)+'_amp_env_mode', default_value = decvalue)
            # elampenvmode(decvalue)

            # Amp Envelope:
            for n in ampenvlist:
                a = 'el'+str(i)+'_amp_env_'+n
                b = int(datalist[e['P_el'+str(i)+'ampenv'+n]],16)
                dpg.configure_item(item=a,default_value = b)
                elampenvelope(a)

            # Amp env rate scale
            decvalue = int(datalist[e['P_el'+str(i)+'ampenvrtscl']],16)
            if decvalue>7:
                decvalue = 8-decvalue
            dpg.configure_item(item='el'+str(i)+'_amp_env_rate_scale', default_value = decvalue)

            # Amp env Breakpoints
            for n in range(1,5):
                param = int(datalist[e['P_el'+str(i)+'ampenvBP'+str(n)]],16)
                dpg.configure_item(item='el'+str(i)+'_amp_env_bp'+str(n), default_value = notelist[param])

            # Amp breakpoints scale Offset 
            for n in range(1,5):
                bit1 = int(datalist[e['P_el'+str(i)+'ampenvOff'+str(n)+'b1']],16)
                bit2 = int(datalist[e['P_el'+str(i)+'ampenvOff'+str(n)+'b2']],16)
                if bit1 == 0:
                    decvalue = bit2 - 128
                else:
                    decvalue = bit2
                dpg.configure_item(item='el'+str(i)+'_amp_env_sc_off_'+str(n), default_value = decvalue)

            # Amp vel sens:
            decvalue = int(datalist[e['P_el'+str(i)+'velsens']],16)
            elampvelsens(decvalue)

            # Amp vel rate sens:
            decvalue = int(datalist[e['P_el'+str(i)+'velratesens']],16)
            dpg.configure_item(item='el'+str(i)+'_amp_sens_vel_rate', default_value = 1-decvalue)               

            # Amp mod sens:
            decvalue = int(datalist[e['P_el'+str(i)+'ampmodsens']],16)
            elampmodsens(decvalue)

        requestok = 0
        NoWriteRequest = 0
        nosend = 0
        # devolvemos elemento al del TAB seleccionado
        for i in range(4):
            if dpg.get_value(item='el'+str(i+1)+'_tab') == True:
                EL = 'el'+str(i+1)
    except:
        dpg.configure_item('load_error', show=True)
        datalist = []
        requestok = 0
        NoWriteRequest = 0
        nosend = 0

def drawdrumcontrols():
    global nosend, requestok, NoWriteRequest
    if len(datalist) != 618:
        dpg.configure_item('midi_error', show=True)
        return
    requestok = 1
    nosend = 1
    ############################## COMMON
    # Voice Name
    name = ''
    for i in range(32,42):
        name = name+(bytearray.fromhex(datalist[i]).decode())
    dpg.configure_item(item='voice_name', default_value = name)

    # Efx Type + params 1,2,3
    dpg.configure_item(item='effect_type', default_value = effectslist[int(datalist[42],16)-1])
    effecttype('effect_type')

    # Efx output level
    dpg.configure_item(item='effect_level', default_value = int(datalist[43],16))

    # Voice Volume
    dpg.configure_item(item='voice_volume', default_value = int(datalist[65],16)) 

    ############################## CONTROLLERS
    # Voice Volume
    dpg.configure_item(item='volume_cc', default_value =  controllerlist[int(datalist[61],16)]) 
    dpg.configure_item(item='vol_min_rng', default_value = int(datalist[62],16)) 

    ############################## ELEMENTS
    notewave = [71,80,89,98,107,116,125,134,143,152,161,170,179,188,197,206,215,224,233,242,251,260,269,278,287,296,305,314,323,332,341,350,359,368,377,386,395,404,413,422,431,440,449,458,467,476,485,494,503,512,521,530,539,548,557,566,575,584,593,602,611]
    notevol = [72,81,90,99,108,117,126,135,144,153,162,171,180,189,198,207,216,225,234,243,252,261,270,279,288,297,306,315,324,333,342,351,360,369,378,387,396,405,414,423,432,441,450,459,468,477,486,495,504,513,522,531,540,549,558,567,576,585,594,603,612]
    noteshift = [74,83,92,101,110,119,128,137,146,155,164,173,182,191,200,209,218,227,236,245,254,263,272,281,290,299,308,317,326,335,344,353,362,371,380,389,398,407,416,425,434,443,452,461,470,479,488,497,506,515,524,533,542,551,560,569,578,587,596,605,614]
    notetune = [73,82,91,100,109,118,127,136,145,154,163,172,181,190,199,208,217,226,235,244,253,262,271,280,289,298,307,316,325,334,343,352,361,370,379,388,397,406,415,424,433,442,451,460,469,478,487,496,505,514,523,532,541,550,559,568,577,586,595,604,613]
    notealtgr = [68,77,86,95,104,113,122,131,140,149,158,167,176,185,194,203,212,221,230,239,248,257,266,275,284,293,302,311,320,329,338,347,356,365,374,383,392,401,410,419,428,437,446,455,464,473,482,491,500,509,518,527,536,545,554,563,572,581,590,599,608]
    notepan = [75,84,93,102,111,120,129,138,147,156,165,174,183,192,201,210,219,228,237,246,255,264,273,282,291,300,309,318,327,336,345,354,363,372,381,390,399,408,417,426,435,444,453,462,471,480,489,498,507,516,525,534,543,552,561,570,579,588,597,606,615]
    noteefxbal = [76,85,94,103,112,121,130,139,148,157,166,175,184,193,202,211,220,229,238,247,256,265,274 ,283,292,301,310,319,328,337,346,355,364,373,382,391,400,409,418,427,436,445,454,463,472,481,490,499,508,517,526,535,544,553,562,571,580,589,598,607,616]
    
    # Note waveform
    for i in range(61):
        dpg.configure_item(item='drums_Waveform'+str(i), default_value = drumvoicelist[int(datalist[notewave[i]],16)+1])
    # Note volume
    for i in range(61):
        dpg.configure_item(item='drums_Volume'+str(i), default_value = int(datalist[notevol[i]],16))
    # Note Shift
    for i in range(61):
        dpg.configure_item(item='drums_Noteshift'+str(i), default_value = int(datalist[noteshift[i]],16)-64)
    # Note tune
    for i in range(61):
        dpg.configure_item(item='drums_Tune'+str(i), default_value = int(datalist[notetune[i]],16)-64)
    # Note Alt Group
    for i in range(61):
        dpg.configure_item(item='drums_Alt_Group'+str(i), default_value = int((int(datalist[notealtgr[i]],16)-32)/64))
    # Note pan
    for i in range(61):
        dpg.configure_item(item='drums_Pan'+str(i), default_value = int(datalist[notepan[i]],16)-32)    
    # Note efx balance
    for i in range(61):
        dpg.configure_item(item='drums_Efx_Balance'+str(i), default_value = int(datalist[noteefxbal[i]],16))    

    requestok = 0
    NoWriteRequest = 0
    nosend = 0

def initializepatch():
    requestvoice()
    # detecto drums
    if datalist[4] == '64':
        elnumber = 0
    else:
        if datalist[31] == '05':
            elnumber = 1
        if datalist[31] == '06':
            elnumber = 2
        if datalist[31] == '07':
            elnumber = 4

    dpg.configure_item('confirminitialize', show=True) 

def initializepatchok():
    global datalist, ELCOPY, ELPASTE, elnumber, copyel, EL, NoWriteRequest
    if elnumber == 0:
        initializedrums()
        return    
    copyel = 0
    ELCOPY = 1
    # update midi prefs
    checkmidiprefs()

    # SET 4 ELEMENTS
    PARAM = '02 00 00 00 00 '
    VALUE = '07' # 4 el
    MESSAGE = INI + PARAM + VALUE + END
    sendmessage(MESSAGE)

    # LOAD DATALIST
    datalist = []
    dpg.configure_item('confirminitialize', show=False) 
    f = open('files/initvoice', 'r')
    datalist = json.load(f)
    f.close()

    # PASTE
    for i in range(4):
        ELPASTE = i+1
        EL = 'el'+str(ELPASTE)
        pasteelement()

    # SET 1 ELEMENTS
    PARAM = '02 00 00 00 00 '
    VALUE = '05' # 4 el
    MESSAGE = INI + PARAM + VALUE + END
    sendmessage(MESSAGE)
    dpg.configure_item(item='voice_mode', default_value = '1 Element')
    dpg.configure_item(item='el2_tab', show = False)
    dpg.configure_item(item='el3_tab', show = False)
    dpg.configure_item(item='el4_tab', show = False)
    elnumber = 1
    NoWriteRequest = 0
    # Voice Name
    name = ''
    for i in range(32,42):
        name = name+(bytearray.fromhex(datalist[i]).decode())
    dpg.configure_item(item='voice_name', default_value = name)
    voicename('voice_name')

def initializedrums():
    global datalist, NoWriteRequest, loading
    loading = 1
    NoWriteRequest == 0
    # LOAD DATALIST
    datalist = []
    dpg.configure_item('confirminitialize', show=False) 
    f = open('files/initdrum', 'r')
    datalist = json.load(f)
    f.close()
    pastedrumpatch()
    pass
    
########################### ELEMENT ############################
def copyelement():
    global ELCOPY, copyel, NoWriteRequest, datalist
    # update midi prefs
    checkmidiprefs()
    # Request data
    NoWriteRequest = 1
    requestvoice()
    NoWriteRequest = 0
    # SET 4 ELEMENTS
    PARAM = '02 00 00 00 00 '
    VALUE = '07' # 4 el
    MESSAGE = INI + PARAM + VALUE + END
    sendmessage(MESSAGE)
    # GUARDAMOS EN DISCO EL PATCH ACTUAL PERO CON 4 ELEMENTOS
    f = open('files/currentvoice', 'w')
    json.dump(datalist, f)
    f.close()
    # GUARDAMOS EL NUMERO DE ELEMENTO DE DONDE COPIAR EN ELCOPY
    for i in range(5):
        if dpg.get_value(item='el'+str(i+1)+'_tab') == True:
            ELCOPY = i+1
    # ANOTAMOS EN copyel QUE ESTAMOS COPIANDO ELEMENTO
    copyel = 1

def pasteelement():
    global copyel, requestok, NoWriteRequest, EL, ELFILTER12, datalist, ELPASTE, nosend, ELBP, datalist
    if ELCOPY ==-1:
        return
    requestok = 1   
    nosend = 0
    NoWriteRequest = 1
    if copyel == 1:
        # CARGAMOS DATALIST DE DISCO
        f = open('files/currentvoice', 'r')
        datalist = json.load(f)
        f.close()
        # ELCOPY =  numero de elemento del que vamos a copiar
        # GUARDAMOS EN ELPASTE EL ELEMENTO AL QUE VAMOS A COPIAR
        for i in range(4):
            if dpg.get_value(item='el'+str(i+1)+'_tab') == True:
                ELPASTE = i+1
                EL = 'el'+str(ELPASTE)

    # DEFINIMOS VARIABLES PARA TODOS LOS PARAMETROS EN 4 ELEMENTOS
    e = {}
    if 0==0:
        ##### ELEMENT 1
        e['P_el1_volume'] = 68
        e['P_el1_detune'] = 69
        e['P_el1_noteshift'] = 70
        e['P_el1_notelimL'] = 71
        e['P_el1_notelimH'] = 72
        e['P_el1_vellimL'] = 73
        e['P_el1_vellimH'] = 74
        e['P_el1_pan'] = 75
        e['P_el1_efxbal'] = 76
        e['P_el1_voice'] = 106
        e['P_el1_oscfreqmode'] = 107
        e['P_el1_oscfreqnote'] = 108
        e['P_el1_oscfreqtune'] = 109
        e['P_el1_pitchmodsens'] = 110
        e['P_el1_pitchenvR1'] = 111
        e['P_el1_pitchenvR2'] = 112
        e['P_el1_pitchenvR3'] = 113
        e['P_el1_pitchenvRR'] = 114
        e['P_el1_pitchenvL0'] = 115
        e['P_el1_pitchenvL1'] = 116
        e['P_el1_pitchenvL2'] = 117
        e['P_el1_pitchenvL3'] = 118
        e['P_el1_pitchenvRL'] = 119
        e['P_el1_pitchenvrng'] = 120
        e['P_el1_pitchenvratescl'] = 121
        e['P_el1_pitchenvvelsw'] = 122
        e['P_el1_lfospd'] = 123
        e['P_el1_lfodly'] = 124
        e['P_el1_lfopitchmod'] = 125
        e['P_el1_lfoampmod'] = 126
        e['P_el1_lfocutoffmod'] = 127
        e['P_el1_lfowave'] = 128
        e['P_el1_lfophase'] = 129
        e['P_el1_fl1type'] = 131
        e['P_el1_fl1cutoff'] = 132
        e['P_el1_fl1mode'] = 133
        e['P_el1_fl1envR1'] = 134
        e['P_el1_fl1envR2'] = 135
        e['P_el1_fl1envR3'] = 136
        e['P_el1_fl1envR4'] = 137
        e['P_el1_fl1envRR1'] = 138
        e['P_el1_fl1envRR2'] = 139
        e['P_el1_fl1envL0'] = 140
        e['P_el1_fl1envL1'] = 141
        e['P_el1_fl1envL2'] = 142
        e['P_el1_fl1envL3'] = 143
        e['P_el1_fl1envL4'] = 144
        e['P_el1_fl1envRL1'] = 145
        e['P_el1_fl1envRL2'] = 146
        e['P_el1_fl1envertscl'] = 147
        e['P_el1_fl1envBP1'] = 148
        e['P_el1_fl1envBP2'] = 149
        e['P_el1_fl1envBP3'] = 150
        e['P_el1_fl1envBP4'] = 151
        e['P_el1_fl1envOff1b1'] = 152
        e['P_el1_fl1envOff1b2'] = 153
        e['P_el1_fl1envOff2b1'] = 154
        e['P_el1_fl1envOff2b2'] = 155
        e['P_el1_fl1envOff3b1'] = 156
        e['P_el1_fl1envOff3b2'] = 157
        e['P_el1_fl1envOff4b1'] = 158
        e['P_el1_fl1envOff4b2'] = 159
        e['P_el1_fl2type'] = 160
        e['P_el1_fl2cutoff'] = 161
        e['P_el1_fl2mode'] = 162
        e['P_el1_fl2envR1'] = 163
        e['P_el1_fl2envR2'] = 164
        e['P_el1_fl2envR3'] = 165
        e['P_el1_fl2envR4'] = 166
        e['P_el1_fl2envRR1'] = 167
        e['P_el1_fl2envRR2'] = 168
        e['P_el1_fl2envL0'] = 169
        e['P_el1_fl2envL1'] = 170
        e['P_el1_fl2envL2'] = 171
        e['P_el1_fl2envL3'] = 172
        e['P_el1_fl2envL4'] = 173
        e['P_el1_fl2envRL1'] = 174
        e['P_el1_fl2envRL2'] = 175
        e['P_el1_fl2envertscl'] = 176
        e['P_el1_fl2envBP1'] = 177
        e['P_el1_fl2envBP2'] = 178
        e['P_el1_fl2envBP3'] = 179
        e['P_el1_fl2envBP4'] = 180
        e['P_el1_fl2envOff1b1'] = 181
        e['P_el1_fl2envOff1b2'] = 182
        e['P_el1_fl2envOff2b1'] = 183
        e['P_el1_fl2envOff2b2'] = 184
        e['P_el1_fl2envOff3b1'] = 185
        e['P_el1_fl2envOff3b2'] = 186
        e['P_el1_fl2envOff4b1'] = 187
        e['P_el1_fl2envOff4b2'] = 188
        e['P_el1flres'] = 189
        e['P_el1flvelsens'] = 190
        e['P_el1flmodsens'] = 191
        e['P_el1ampenvmode'] = 192
        e['P_el1ampenvR1'] = 193
        e['P_el1ampenvR2'] = 194
        e['P_el1ampenvR3'] = 195
        e['P_el1ampenvR4'] = 196
        e['P_el1ampenvRR'] = 197
        e['P_el1ampenvL2'] = 198
        e['P_el1ampenvL3'] = 199
        e['P_el1ampenvrtscl'] = 200
        e['P_el1ampenvBP1'] = 201
        e['P_el1ampenvBP2'] = 202
        e['P_el1ampenvBP3'] = 203
        e['P_el1ampenvBP4'] = 204
        e['P_el1ampenvOff1b1'] = 205
        e['P_el1ampenvOff1b2'] = 206
        e['P_el1ampenvOff2b1'] = 207
        e['P_el1ampenvOff2b2'] = 208
        e['P_el1ampenvOff3b1'] = 209
        e['P_el1ampenvOff3b2'] = 210
        e['P_el1ampenvOff4b1'] = 211
        e['P_el1ampenvOff4b2'] = 212
        e['P_el1velsens'] = 213
        e['P_el1velratesens'] = 214
        e['P_el1ampmodsens'] = 215

        ##### ELEMENT 2
        e['P_el2_volume'] = 77
        e['P_el2_detune'] = 78
        e['P_el2_noteshift'] = 79
        e['P_el2_notelimL'] = 80
        e['P_el2_notelimH'] = 81
        e['P_el2_vellimL'] = 82
        e['P_el2_vellimH'] = 83
        e['P_el2_pan'] = 84
        e['P_el2_efxbal'] = 85
        e['P_el2_voice'] = 218
        e['P_el2_oscfreqmode'] = 219
        e['P_el2_oscfreqnote'] = 220
        e['P_el2_oscfreqtune'] = 221
        e['P_el2_pitchmodsens'] = 222
        e['P_el2_pitchenvR1'] = 223
        e['P_el2_pitchenvR2'] = 224
        e['P_el2_pitchenvR3'] = 225
        e['P_el2_pitchenvRR'] = 226
        e['P_el2_pitchenvL0'] = 227
        e['P_el2_pitchenvL1'] = 228
        e['P_el2_pitchenvL2'] = 229
        e['P_el2_pitchenvL3'] = 230
        e['P_el2_pitchenvRL'] = 231
        e['P_el2_pitchenvrng'] = 232
        e['P_el2_pitchenvratescl'] = 233
        e['P_el2_pitchenvvelsw'] = 234
        e['P_el2_lfospd'] = 235
        e['P_el2_lfodly'] = 236
        e['P_el2_lfopitchmod'] = 237
        e['P_el2_lfoampmod'] = 238
        e['P_el2_lfocutoffmod'] = 239
        e['P_el2_lfowave'] = 240
        e['P_el2_lfophase'] = 241
        e['P_el2_fl1type'] = 243
        e['P_el2_fl1cutoff'] = 244
        e['P_el2_fl1mode'] = 245
        e['P_el2_fl1envR1'] = 246
        e['P_el2_fl1envR2'] = 247
        e['P_el2_fl1envR3'] = 248
        e['P_el2_fl1envR4'] = 249
        e['P_el2_fl1envRR1'] = 250
        e['P_el2_fl1envRR2'] = 251
        e['P_el2_fl1envL0'] = 252
        e['P_el2_fl1envL1'] = 253
        e['P_el2_fl1envL2'] = 254
        e['P_el2_fl1envL3'] = 255
        e['P_el2_fl1envL4'] = 256
        e['P_el2_fl1envRL1'] = 257
        e['P_el2_fl1envRL2'] = 258
        e['P_el2_fl1envertscl'] = 259
        e['P_el2_fl1envBP1'] = 260
        e['P_el2_fl1envBP2'] = 261
        e['P_el2_fl1envBP3'] = 262
        e['P_el2_fl1envBP4'] = 263
        e['P_el2_fl1envOff1b1'] = 264
        e['P_el2_fl1envOff1b2'] = 265
        e['P_el2_fl1envOff2b1'] = 266
        e['P_el2_fl1envOff2b2'] = 267
        e['P_el2_fl1envOff3b1'] = 268
        e['P_el2_fl1envOff3b2'] = 269
        e['P_el2_fl1envOff4b1'] = 270
        e['P_el2_fl1envOff4b2'] = 271
        e['P_el2_fl2type'] = 272
        e['P_el2_fl2cutoff'] = 273
        e['P_el2_fl2mode'] = 274
        e['P_el2_fl2envR1'] = 275
        e['P_el2_fl2envR2'] = 276
        e['P_el2_fl2envR3'] = 277
        e['P_el2_fl2envR4'] = 278
        e['P_el2_fl2envRR1'] = 279
        e['P_el2_fl2envRR2'] = 280
        e['P_el2_fl2envL0'] = 281
        e['P_el2_fl2envL1'] = 282
        e['P_el2_fl2envL2'] = 283
        e['P_el2_fl2envL3'] = 284
        e['P_el2_fl2envL4'] = 285
        e['P_el2_fl2envRL1'] = 286
        e['P_el2_fl2envRL2'] = 287
        e['P_el2_fl2envertscl'] = 288
        e['P_el2_fl2envBP1'] = 289
        e['P_el2_fl2envBP2'] = 290
        e['P_el2_fl2envBP3'] = 291
        e['P_el2_fl2envBP4'] = 292
        e['P_el2_fl2envOff1b1'] = 293
        e['P_el2_fl2envOff1b2'] = 294
        e['P_el2_fl2envOff2b1'] = 295
        e['P_el2_fl2envOff2b2'] = 296
        e['P_el2_fl2envOff3b1'] = 297
        e['P_el2_fl2envOff3b2'] = 298
        e['P_el2_fl2envOff4b1'] = 299
        e['P_el2_fl2envOff4b2'] = 300
        e['P_el2flres'] = 301
        e['P_el2flvelsens'] = 302
        e['P_el2flmodsens'] = 303
        e['P_el2ampenvmode'] = 304
        e['P_el2ampenvR1'] = 305
        e['P_el2ampenvR2'] = 306
        e['P_el2ampenvR3'] = 307
        e['P_el2ampenvR4'] = 308
        e['P_el2ampenvRR'] = 309
        e['P_el2ampenvL2'] = 310
        e['P_el2ampenvL3'] = 311
        e['P_el2ampenvrtscl'] = 312
        e['P_el2ampenvBP1'] = 313
        e['P_el2ampenvBP2'] = 314
        e['P_el2ampenvBP3'] = 315
        e['P_el2ampenvBP4'] = 316
        e['P_el2ampenvOff1b1'] = 317
        e['P_el2ampenvOff1b2'] = 318
        e['P_el2ampenvOff2b1'] = 319
        e['P_el2ampenvOff2b2'] = 320
        e['P_el2ampenvOff3b1'] = 321
        e['P_el2ampenvOff3b2'] = 322
        e['P_el2ampenvOff4b1'] = 323
        e['P_el2ampenvOff4b2'] = 324
        e['P_el2velsens'] = 325
        e['P_el2velratesens'] = 326
        e['P_el2ampmodsens'] = 327

        ##### ELEMENT 3
        e['P_el3_volume'] = 86
        e['P_el3_detune'] = 87
        e['P_el3_noteshift'] = 88
        e['P_el3_notelimL'] = 89
        e['P_el3_notelimH'] = 90
        e['P_el3_vellimL'] = 91
        e['P_el3_vellimH'] = 92
        e['P_el3_pan'] = 93
        e['P_el3_efxbal'] = 94
        e['P_el3_voice'] = 330
        e['P_el3_oscfreqmode'] = 331
        e['P_el3_oscfreqnote'] = 332
        e['P_el3_oscfreqtune'] = 333
        e['P_el3_pitchmodsens'] = 334
        e['P_el3_pitchenvR1'] = 335
        e['P_el3_pitchenvR2'] = 336
        e['P_el3_pitchenvR3'] = 337
        e['P_el3_pitchenvRR'] = 338
        e['P_el3_pitchenvL0'] = 339
        e['P_el3_pitchenvL1'] = 340
        e['P_el3_pitchenvL2'] = 341
        e['P_el3_pitchenvL3'] = 342
        e['P_el3_pitchenvRL'] = 343
        e['P_el3_pitchenvrng'] = 344
        e['P_el3_pitchenvratescl'] = 345
        e['P_el3_pitchenvvelsw'] = 346
        e['P_el3_lfospd'] = 347
        e['P_el3_lfodly'] = 348
        e['P_el3_lfopitchmod'] = 349
        e['P_el3_lfoampmod'] = 350
        e['P_el3_lfocutoffmod'] = 351
        e['P_el3_lfowave'] = 352
        e['P_el3_lfophase'] = 353
        e['P_el3_fl1type'] = 355
        e['P_el3_fl1cutoff'] = 356
        e['P_el3_fl1mode'] = 357
        e['P_el3_fl1envR1'] = 358
        e['P_el3_fl1envR2'] = 359
        e['P_el3_fl1envR3'] = 360
        e['P_el3_fl1envR4'] = 361
        e['P_el3_fl1envRR1'] = 362
        e['P_el3_fl1envRR2'] = 363
        e['P_el3_fl1envL0'] = 364
        e['P_el3_fl1envL1'] = 365
        e['P_el3_fl1envL2'] = 366
        e['P_el3_fl1envL3'] = 367
        e['P_el3_fl1envL4'] = 368
        e['P_el3_fl1envRL1'] = 369
        e['P_el3_fl1envRL2'] = 370
        e['P_el3_fl1envertscl'] = 371
        e['P_el3_fl1envBP1'] = 372
        e['P_el3_fl1envBP2'] = 373
        e['P_el3_fl1envBP3'] = 374
        e['P_el3_fl1envBP4'] = 375
        e['P_el3_fl1envOff1b1'] = 376
        e['P_el3_fl1envOff1b2'] = 377
        e['P_el3_fl1envOff2b1'] = 378
        e['P_el3_fl1envOff2b2'] = 379
        e['P_el3_fl1envOff3b1'] = 380
        e['P_el3_fl1envOff3b2'] = 381
        e['P_el3_fl1envOff4b1'] = 382
        e['P_el3_fl1envOff4b2'] = 383
        e['P_el3_fl2type'] = 384
        e['P_el3_fl2cutoff'] = 385
        e['P_el3_fl2mode'] = 386
        e['P_el3_fl2envR1'] = 387
        e['P_el3_fl2envR2'] = 388
        e['P_el3_fl2envR3'] = 389
        e['P_el3_fl2envR4'] = 390
        e['P_el3_fl2envRR1'] = 391
        e['P_el3_fl2envRR2'] = 392
        e['P_el3_fl2envL0'] = 393
        e['P_el3_fl2envL1'] = 394
        e['P_el3_fl2envL2'] = 395
        e['P_el3_fl2envL3'] = 396
        e['P_el3_fl2envL4'] = 397
        e['P_el3_fl2envRL1'] = 398
        e['P_el3_fl2envRL2'] = 399
        e['P_el3_fl2envertscl'] = 400
        e['P_el3_fl2envBP1'] = 401
        e['P_el3_fl2envBP2'] = 402
        e['P_el3_fl2envBP3'] = 403
        e['P_el3_fl2envBP4'] = 404
        e['P_el3_fl2envOff1b1'] = 405
        e['P_el3_fl2envOff1b2'] = 406
        e['P_el3_fl2envOff2b1'] = 407
        e['P_el3_fl2envOff2b2'] = 408
        e['P_el3_fl2envOff3b1'] = 409
        e['P_el3_fl2envOff3b2'] = 410
        e['P_el3_fl2envOff4b1'] = 411
        e['P_el3_fl2envOff4b2'] = 412
        e['P_el3flres'] = 413
        e['P_el3flvelsens'] = 414
        e['P_el3flmodsens'] = 415
        e['P_el3ampenvmode'] = 416
        e['P_el3ampenvR1'] = 417
        e['P_el3ampenvR2'] = 418
        e['P_el3ampenvR3'] = 419
        e['P_el3ampenvR4'] = 420
        e['P_el3ampenvRR'] = 421
        e['P_el3ampenvL2'] = 422
        e['P_el3ampenvL3'] = 423
        e['P_el3ampenvrtscl'] = 424
        e['P_el3ampenvBP1'] = 425
        e['P_el3ampenvBP2'] = 426
        e['P_el3ampenvBP3'] = 427
        e['P_el3ampenvBP4'] = 428
        e['P_el3ampenvOff1b1'] = 429
        e['P_el3ampenvOff1b2'] = 430
        e['P_el3ampenvOff2b1'] = 431
        e['P_el3ampenvOff2b2'] = 432
        e['P_el3ampenvOff3b1'] = 433
        e['P_el3ampenvOff3b2'] = 434
        e['P_el3ampenvOff4b1'] = 435
        e['P_el3ampenvOff4b2'] = 436
        e['P_el3velsens'] = 437
        e['P_el3velratesens'] = 438
        e['P_el3ampmodsens'] = 439
        ##### ELEMENT 4
        e['P_el4_volume'] = 95
        e['P_el4_detune'] = 96
        e['P_el4_noteshift'] = 97
        e['P_el4_notelimL'] = 98
        e['P_el4_notelimH'] = 99
        e['P_el4_vellimL'] = 100
        e['P_el4_vellimH'] = 101
        e['P_el4_pan'] = 102
        e['P_el4_efxbal'] = 103
        e['P_el4_voice'] = 442
        e['P_el4_oscfreqmode'] = 443
        e['P_el4_oscfreqnote'] = 444
        e['P_el4_oscfreqtune'] = 445
        e['P_el4_pitchmodsens'] = 446
        e['P_el4_pitchenvR1'] = 447
        e['P_el4_pitchenvR2'] = 448
        e['P_el4_pitchenvR3'] = 449
        e['P_el4_pitchenvRR'] = 450
        e['P_el4_pitchenvL0'] = 451
        e['P_el4_pitchenvL1'] = 452
        e['P_el4_pitchenvL2'] = 453
        e['P_el4_pitchenvL3'] = 454
        e['P_el4_pitchenvRL'] = 455
        e['P_el4_pitchenvrng'] = 456
        e['P_el4_pitchenvratescl'] = 457
        e['P_el4_pitchenvvelsw'] = 458
        e['P_el4_lfospd'] = 459
        e['P_el4_lfodly'] = 460
        e['P_el4_lfopitchmod'] = 461
        e['P_el4_lfoampmod'] = 462
        e['P_el4_lfocutoffmod'] = 463
        e['P_el4_lfowave'] = 464
        e['P_el4_lfophase'] = 465
        e['P_el4_fl1type'] = 467
        e['P_el4_fl1cutoff'] = 468
        e['P_el4_fl1mode'] = 469
        e['P_el4_fl1envR1'] = 470
        e['P_el4_fl1envR2'] = 471
        e['P_el4_fl1envR3'] = 472
        e['P_el4_fl1envR4'] = 473
        e['P_el4_fl1envRR1'] = 474
        e['P_el4_fl1envRR2'] = 475
        e['P_el4_fl1envL0'] = 476
        e['P_el4_fl1envL1'] = 477
        e['P_el4_fl1envL2'] = 478
        e['P_el4_fl1envL3'] = 479
        e['P_el4_fl1envL4'] = 480
        e['P_el4_fl1envRL1'] = 481
        e['P_el4_fl1envRL2'] = 482
        e['P_el4_fl1envertscl'] = 483
        e['P_el4_fl1envBP1'] = 484
        e['P_el4_fl1envBP2'] = 485
        e['P_el4_fl1envBP3'] = 486
        e['P_el4_fl1envBP4'] = 487
        e['P_el4_fl1envOff1b1'] = 488
        e['P_el4_fl1envOff1b2'] = 489
        e['P_el4_fl1envOff2b1'] = 490
        e['P_el4_fl1envOff2b2'] = 491
        e['P_el4_fl1envOff3b1'] = 492
        e['P_el4_fl1envOff3b2'] = 493
        e['P_el4_fl1envOff4b1'] = 494
        e['P_el4_fl1envOff4b2'] = 495
        e['P_el4_fl2type'] = 496
        e['P_el4_fl2cutoff'] = 497
        e['P_el4_fl2mode'] = 498
        e['P_el4_fl2envR1'] = 499
        e['P_el4_fl2envR2'] = 500
        e['P_el4_fl2envR3'] = 501
        e['P_el4_fl2envR4'] = 502
        e['P_el4_fl2envRR1'] = 503
        e['P_el4_fl2envRR2'] = 504
        e['P_el4_fl2envL0'] = 505
        e['P_el4_fl2envL1'] = 506
        e['P_el4_fl2envL2'] = 507
        e['P_el4_fl2envL3'] = 508
        e['P_el4_fl2envL4'] = 509
        e['P_el4_fl2envRL1'] = 510
        e['P_el4_fl2envRL2'] = 511
        e['P_el4_fl2envertscl'] = 512
        e['P_el4_fl2envBP1'] = 513
        e['P_el4_fl2envBP2'] = 514
        e['P_el4_fl2envBP3'] = 515
        e['P_el4_fl2envBP4'] = 516
        e['P_el4_fl2envOff1b1'] = 517
        e['P_el4_fl2envOff1b2'] = 518
        e['P_el4_fl2envOff2b1'] = 519
        e['P_el4_fl2envOff2b2'] = 520
        e['P_el4_fl2envOff3b1'] = 521
        e['P_el4_fl2envOff3b2'] = 522
        e['P_el4_fl2envOff4b1'] = 523
        e['P_el4_fl2envOff4b2'] = 524
        e['P_el4flres'] = 525
        e['P_el4flvelsens'] = 526
        e['P_el4flmodsens'] = 527
        e['P_el4ampenvmode'] = 528
        e['P_el4ampenvR1'] = 529
        e['P_el4ampenvR2'] = 530
        e['P_el4ampenvR3'] = 531
        e['P_el4ampenvR4'] = 532
        e['P_el4ampenvRR'] = 533
        e['P_el4ampenvL2'] = 534
        e['P_el4ampenvL3'] = 535
        e['P_el4ampenvrtscl'] = 536
        e['P_el4ampenvBP1'] = 537
        e['P_el4ampenvBP2'] = 538
        e['P_el4ampenvBP3'] = 539
        e['P_el4ampenvBP4'] = 540
        e['P_el4ampenvOff1b1'] = 541
        e['P_el4ampenvOff1b2'] = 542
        e['P_el4ampenvOff2b1'] = 543
        e['P_el4ampenvOff2b2'] = 544
        e['P_el4ampenvOff3b1'] = 545
        e['P_el4ampenvOff3b2'] = 546
        e['P_el4ampenvOff4b1'] = 547
        e['P_el4ampenvOff4b2'] = 548
        e['P_el4velsens'] = 549
        e['P_el4velratesens'] = 550
        e['P_el4ampmodsens'] = 551
    # "PEGAMOS" LOS PARAMETROS
    # Vol
    try:
        dpg.configure_item(item='el'+str(ELPASTE)+'_volume', default_value =  int(datalist[e['P_el'+str(ELCOPY)+'_volume']],16))
        elementvol('el'+str(ELPASTE)+'_volume')

        # detune - KNOB
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_detune']],16)
        eldetune(decvalue)

        # # Note shift - KONB
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_noteshift']],16)
        elnoteshift(decvalue)

        # Note Limit L
        dpg.configure_item(item='el'+str(ELPASTE)+'_note_limitL', default_value = notelist[int(datalist[e['P_el'+str(ELCOPY)+'_notelimL']],16)])
        elnotelimitL('el'+str(ELPASTE)+'_note_limitL')
        # Note Limit H
        dpg.configure_item(item='el'+str(ELPASTE)+'_note_limitH', default_value = notelist[int(datalist[e['P_el'+str(ELCOPY)+'_notelimH']],16)])
        elnotelimitH('el'+str(ELPASTE)+'_note_limitH')
        # Vel Limit L
        dpg.configure_item(item='el'+str(ELPASTE)+'_vel_limitL', default_value = int(datalist[e['P_el'+str(ELCOPY)+'_vellimL']],16))
        elvellimitL('el'+str(ELPASTE)+'_vel_limitL')
        # Vel Limit H
        dpg.configure_item(item='el'+str(ELPASTE)+'_vel_limitH', default_value = int(datalist[e['P_el'+str(ELCOPY)+'_vellimH']],16))
        elvellimitH('el'+str(ELPASTE)+'_vel_limitH')

        # pan - KNOB
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_pan']],16) # el1 = 75, el2 = 84
        elpan(decvalue)

        # efx balance - KNOB
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_efxbal']],16)
        elefxbalance(decvalue)

        # Element AWM Voice
        decvalue = voicelist[int(datalist[e['P_el'+str(ELCOPY)+'_voice']],16)]
        dpg.configure_item(item='el'+str(ELPASTE)+'_Waveform', default_value = decvalue)
        AWMwaveform('el'+str(ELPASTE)+'_Waveform')

        # OSC freq mode
        dpg.configure_item(item='el'+str(ELPASTE)+'_osc_freq_mode', default_value = int(datalist[e['P_el'+str(ELCOPY)+'_oscfreqmode']],16))
        eloscfreqmode('el'+str(ELPASTE)+'_osc_freq_mode')

        # OSC freq note 
        if int(datalist[e['P_el'+str(ELCOPY)+'_oscfreqmode']],16) == 1:
            decvalue = notelist[int(datalist[e['P_el'+str(ELCOPY)+'_oscfreqnote']],16)]
            dpg.configure_item(item='el'+str(ELPASTE)+'_osc_freq_note', default_value = decvalue)
            eloscfreqnote('el'+str(ELPASTE)+'_osc_freq_note')

        # OSC freq tune - KNOB
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_oscfreqtune']],16)
        eloscfreqtune(decvalue)

        # Pitch mod sens - KNOB
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_pitchmodsens']],16)
        elpitchmodsens(decvalue)

        # Pitch envelope
        for n in pitchenvlist:
            a = 'el'+str(ELPASTE)+'_pitch_env_'+n
            b = int(datalist[e['P_el'+str(ELCOPY)+'_pitchenv'+n]],16)
            if 'L' in n:
                b=b-64
            dpg.configure_item(item=a,default_value = b)
            elpitchenvelope(a)

        # Pitch envelope range
        decvalue = 3-int(datalist[e['P_el'+str(ELCOPY)+'_pitchenvrng']],16)
        dpg.configure_item(item='el'+str(ELPASTE)+'_pitch_env_range', default_value = decvalue)
        elpitchenvrange('el'+str(ELPASTE)+'_pitch_env_range')

        # Pitch env ratescale
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_pitchenvratescl']],16)
        if decvalue>7:
            decvalue = 8 - abs(decvalue)
        dpg.configure_item(item='el'+str(ELPASTE)+'_pitch_env_rate_scale', default_value = decvalue)
        elpitchenvratescale(decvalue)

        #Pitch env velocity switch
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_pitchenvvelsw']],16)
        dpg.configure_item(item='el'+str(ELPASTE)+'_pitch_env_vel_sw', default_value = 1-decvalue)
        elpitchenvvelsw('el'+str(ELPASTE)+'_pitch_env_vel_sw')

        # LFO Speed - KNOB
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_lfospd']],16)
        ellfospeed(decvalue)

        # LFO Delay - KNOB
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_lfodly']],16)
        ellfodelay(decvalue)

        # LFO Pitchmod - KNOB
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_lfopitchmod']],16)
        ellfopitchmod(decvalue)

        # LFO Ampmod - KNOB
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_lfoampmod']],16)
        ellfoampmod(decvalue)

        # LFO Cutoffmod - KNOB
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_lfocutoffmod']],16)
        ellfocutoffmod(decvalue)

        # LFO Wave
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_lfowave']],16)
        dpg.configure_item(item='el'+str(ELPASTE)+'_lfo_wave', default_value = decvalue)
        ellfowave(decvalue)

        # LFO Phase - KNOB
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_lfophase']],16)
        ellfophase(decvalue)

        # Filter1type
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_fl1type']],16)
        ELFILTER12 = str(int(ELPASTE)-1)+'0'
        dpg.configure_item(item='el'+str(ELPASTE)+'_filter1_type', default_value = decvalue)
        elfilter12type(decvalue)

        # Filter 1 Cutoff
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_fl1cutoff']],16)
        ELFILTER12 = str(int(ELPASTE)-1)+'0'
        dpg.configure_item(item='el'+str(ELPASTE)+'_filter1_cutoff', default_value = decvalue)
        elfilter12cutoff(decvalue)

        # Filter 1 mode
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_fl1mode']],16)
        ELFILTER12 = str(int(ELPASTE)-1)+'0'
        dpg.configure_item(item='el'+str(ELPASTE)+'_filter1_mode', default_value = decvalue)
        elfilter12mode(decvalue)

        # Filter 1 env
        ELFILTER12 = str(int(ELPASTE)-1)+'0'
        for n in filterenvlist:
            a = 'el'+str(ELPASTE)+'_filter1_env_'+n
            b = int(datalist[e['P_el'+str(ELCOPY)+'_fl1env'+n]],16)
            if 'L' in n:
                b=b-64
            dpg.configure_item(item=a,default_value = b)
            elfilter12envelope(a)

        # Filter 1 env rate scale
        ELFILTER12 = str(int(ELPASTE)-1)+'0'
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_fl1envertscl']],16)
        if decvalue>7:
            decvalue = 8-decvalue
        dpg.configure_item(item='el'+str(ELPASTE)+'_filter1_env_rate_scale', default_value = decvalue)
        elfilter12envratescale(decvalue)

        # Filter 1 env Breakpoints
        ELFILTER12 = str(int(ELPASTE)-1)+'0'
        for n in range(4,0,-1):
            ELBP = n
            param = int(datalist[e['P_el'+str(ELCOPY)+'_fl1envBP'+str(n)]],16)
            dpg.configure_item(item='el'+str(ELPASTE)+'_filter1_env_bp'+str(n), default_value = notelist[param])
            elfilter12envbp(param)

        # Filter 1 breakpoints scale Offset 
        ELFILTER12 = str(int(ELPASTE)-1)+'0'
        for n in range(1,5):
            bit1 = int(datalist[e['P_el'+str(ELCOPY)+'_fl1envOff'+str(n)+'b1']],16)
            bit2 = int(datalist[e['P_el'+str(ELCOPY)+'_fl1envOff'+str(n)+'b2']],16)
            if bit1 == 0:
                decvalue = bit2 - 128
            else:
                decvalue = bit2
            dpg.configure_item(item='el'+str(ELPASTE)+'_filter1_env_sc_off_'+str(n), default_value = decvalue)
            elfilter12envscoff('el'+str(ELPASTE)+'_filter1_env_sc_off_'+str(n))

        # Filter2type
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_fl2type']],16)
        ELFILTER12 = str(int(ELPASTE)+3)+'0'
        dpg.configure_item(item='el'+str(ELPASTE)+'_filter2_type', default_value = decvalue)
        elfilter12type(decvalue)

        # Filter 2 Cutoff
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_fl2cutoff']],16)
        ELFILTER12 = str(int(ELPASTE)+3)+'0'
        dpg.configure_item(item='el'+str(ELPASTE)+'_filter2_cutoff', default_value = decvalue)
        elfilter12cutoff(decvalue)

        # Filter 2 mode
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_fl2mode']],16)
        ELFILTER12 = str(int(ELPASTE)+3)+'0'
        dpg.configure_item(item='el'+str(ELPASTE)+'_filter2_mode', default_value = decvalue)
        elfilter12mode(decvalue)

        # Filter 2 env
        ELFILTER12 = str(int(ELPASTE)+3)+'0'
        for n in filterenvlist:
            a = 'el'+str(ELPASTE)+'_filter2_env_'+n
            b = int(datalist[e['P_el'+str(ELCOPY)+'_fl2env'+n]],16)
            if 'L' in n:
                b=b-64
            dpg.configure_item(item=a,default_value = b)
            elfilter12envelope(a)

        # Filter 2 env rate scale
        ELFILTER12 = str(int(ELPASTE)+3)+'0'
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_fl2envertscl']],16)
        if decvalue>7:
            decvalue = 8-decvalue
        dpg.configure_item(item='el'+str(ELPASTE)+'_filter2_env_rate_scale', default_value = decvalue)
        elfilter12envratescale(decvalue)

        # Filter 2 env Breakpoints
        ELFILTER12 = str(int(ELPASTE)+3)+'0'
        for n in range(4,0,-1):
            ELBP = n
            param = int(datalist[e['P_el'+str(ELCOPY)+'_fl2envBP'+str(n)]],16)
            dpg.configure_item(item='el'+str(ELPASTE)+'_filter2_env_bp'+str(n), default_value = notelist[param])
            elfilter12envbp(param)

        # Filter 1 breakpoints scale Offset 
        ELFILTER12 = str(int(ELPASTE)+3)+'0'
        for n in range(1,5):
            bit1 = int(datalist[e['P_el'+str(ELCOPY)+'_fl2envOff'+str(n)+'b1']],16)
            bit2 = int(datalist[e['P_el'+str(ELCOPY)+'_fl2envOff'+str(n)+'b2']],16)
            if bit1 == 0:
                decvalue = bit2 - 128
            else:
                decvalue = bit2
            dpg.configure_item(item='el'+str(ELPASTE)+'_filter2_env_sc_off_'+str(n), default_value = decvalue)
            elfilter12envscoff('el'+str(ELPASTE)+'_filter2_env_sc_off_'+str(n))

        # Filter resonance:
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'flres']],16)
        dpg.configure_item(item='el'+str(ELPASTE)+'_filter1_reso', default_value = decvalue)
        elfilter12reso('el'+str(ELPASTE)+'_filter1_reso')

        # Filter vel sens: - KNOB
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'flvelsens']],16)
        elfiltervelsens(decvalue)

        # Filter mod sens: - KNOB 
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'flmodsens']],16)
        elfiltermodsens(decvalue)

        # Amp Env mode:
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'ampenvmode']],16)
        dpg.configure_item(item='el'+str(ELPASTE)+'_amp_env_mode', default_value = decvalue)
        elampenvmode('el'+str(ELPASTE)+'_amp_env_mode')

        # Amp Envelope:
        for n in ampenvlist:
            a = 'el'+str(ELPASTE)+'_amp_env_'+n
            b = int(datalist[e['P_el'+str(ELCOPY)+'ampenv'+n]],16)
            dpg.configure_item(item=a,default_value = b)
            elampenvelope(a)

        # Amp env rate scale
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'ampenvrtscl']],16)
        if decvalue>7:
            decvalue = 8-decvalue
        dpg.configure_item(item='el'+str(ELPASTE)+'_amp_env_rate_scale', default_value = decvalue)
        ampenvratescale('el'+str(ELPASTE)+'_amp_env_rate_scale')

        # Amp env Breakpoints
        for n in range(4,0,-1):
            ELBP = n
            param = int(datalist[e['P_el'+str(ELCOPY)+'ampenvBP'+str(n)]],16)
            dpg.configure_item(item='el'+str(ELPASTE)+'_amp_env_bp'+str(n), default_value = notelist[param])
            elampenvbp(param)

        # Amp breakpoints scale Offset 
        for n in range(1,5):
            bit1 = int(datalist[e['P_el'+str(ELCOPY)+'ampenvOff'+str(n)+'b1']],16)
            bit2 = int(datalist[e['P_el'+str(ELCOPY)+'ampenvOff'+str(n)+'b2']],16)
            if bit1 == 0:
                decvalue = bit2 - 128
            else:
                decvalue = bit2
            dpg.configure_item(item='el'+str(ELPASTE)+'_amp_env_sc_off_'+str(n), default_value = decvalue)
            elampenvscoff('el'+str(ELPASTE)+'_amp_env_sc_off_'+str(n))

        # Amp vel sens: - KNOB
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'velsens']],16)
        elampvelsens(decvalue)

        # Amp vel rate sens: 
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'velratesens']],16)
        dpg.configure_item(item='el'+str(ELPASTE)+'_amp_sens_vel_rate', default_value = 1-decvalue)       
        elsensvelrate('el'+str(ELPASTE)+'_amp_sens_vel_rate')


        # Amp mod sens: - KNOB
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'ampmodsens']],16)
        elampmodsens(decvalue)

        # DEVOLVEMOS EL NUMERO DE ELEMENTOS ORIGINAL
        if elnumber == 1:
            VALUE = '05'
            dpg.configure_item(item='el2_tab', show = False)
            dpg.configure_item(item='el3_tab', show = False)
            dpg.configure_item(item='el4_tab', show = False)
        if elnumber == 2:
            VALUE = '06'
            dpg.configure_item(item='el2_tab', show = True)
            dpg.configure_item(item='el3_tab', show = False)
            dpg.configure_item(item='el4_tab', show = False)
        if elnumber == 4:
            VALUE = '07'
            dpg.configure_item(item='el2_tab', show = True)
            dpg.configure_item(item='el3_tab', show = True)
            dpg.configure_item(item='el4_tab', show = True)
            
        PARAM = '02 00 00 00 00 '
        MESSAGE = INI + PARAM + VALUE + END
        sendmessage(MESSAGE)
    except:
        dpg.configure_item('load_error', show=True)
    requestok = 0
    NoWriteRequest = 0

def pastepatch():
    global copyel, requestok, NoWriteRequest, EL, ELFILTER12, datalist, ELPASTE, nosend, ELBP, elnumber, loading
    requestok = 1   
    nosend = 0
    ############################## ELEMENTS

    ######## COMMON
    e = {}
    #EL1
    e['P_el1_volume'] = 68
    e['P_el1_detune'] = 69
    e['P_el1_noteshift'] = 70
    e['P_el1_notelimL'] = 71
    e['P_el1_notelimH'] = 72
    e['P_el1_vellimL'] = 73
    e['P_el1_vellimH'] = 74
    e['P_el1_pan'] = 75
    e['P_el1_efxbal'] = 76
    #EL2
    e['P_el2_volume'] = 77
    e['P_el2_detune'] = 78
    e['P_el2_noteshift'] = 79
    e['P_el2_notelimL'] = 80
    e['P_el2_notelimH'] = 81
    e['P_el2_vellimL'] = 82
    e['P_el2_vellimH'] = 83
    e['P_el2_pan'] = 84
    e['P_el2_efxbal'] = 85
    #EL3
    e['P_el3_volume'] = 86
    e['P_el3_detune'] = 87
    e['P_el3_noteshift'] = 88
    e['P_el3_notelimL'] = 89
    e['P_el3_notelimH'] = 90
    e['P_el3_vellimL'] = 91
    e['P_el3_vellimH'] = 92
    e['P_el3_pan'] = 93
    e['P_el3_efxbal'] = 94
    #EL4
    e['P_el4_volume'] = 95
    e['P_el4_detune'] = 96
    e['P_el4_noteshift'] = 97
    e['P_el4_notelimL'] = 98
    e['P_el4_notelimH'] = 99
    e['P_el4_vellimL'] = 100
    e['P_el4_vellimH'] = 101
    e['P_el4_pan'] = 102
    e['P_el4_efxbal'] = 103

    # 1 ELEMENT
    if elnumber == 1:
        e['P_el1_voice'] = 79
        e['P_el1_oscfreqmode'] = 80
        e['P_el1_oscfreqnote'] = 81
        e['P_el1_oscfreqtune'] = 82
        e['P_el1_pitchmodsens'] = 83
        e['P_el1_pitchenvR1'] = 84
        e['P_el1_pitchenvR2'] = 85
        e['P_el1_pitchenvR3'] = 86
        e['P_el1_pitchenvRR'] = 87
        e['P_el1_pitchenvL0'] = 88
        e['P_el1_pitchenvL1'] = 89
        e['P_el1_pitchenvL2'] = 90
        e['P_el1_pitchenvL3'] = 91
        e['P_el1_pitchenvRL'] = 92
        e['P_el1_pitchenvrng'] = 93
        e['P_el1_pitchenvratescl'] = 94
        e['P_el1_pitchenvvelsw'] = 95
        e['P_el1_lfospd'] = 96
        e['P_el1_lfodly'] = 97
        e['P_el1_lfopitchmod'] = 98
        e['P_el1_lfoampmod'] = 99
        e['P_el1_lfocutoffmod'] = 100
        e['P_el1_lfowave'] = 101
        e['P_el1_lfophase'] = 102
        e['P_el1_fl1type'] = 104
        e['P_el1_fl1cutoff'] = 105
        e['P_el1_fl1mode'] = 106
        e['P_el1_fl1envR1'] = 107
        e['P_el1_fl1envR2'] = 108
        e['P_el1_fl1envR3'] = 109
        e['P_el1_fl1envR4'] = 110
        e['P_el1_fl1envRR1'] = 111
        e['P_el1_fl1envRR2'] = 112
        e['P_el1_fl1envL0'] = 113
        e['P_el1_fl1envL1'] = 114
        e['P_el1_fl1envL2'] = 115
        e['P_el1_fl1envL3'] = 116
        e['P_el1_fl1envL4'] = 117
        e['P_el1_fl1envRL1'] = 118
        e['P_el1_fl1envRL2'] = 119
        e['P_el1_fl1envertscl'] = 120
        e['P_el1_fl1envBP1'] = 121
        e['P_el1_fl1envBP2'] = 122
        e['P_el1_fl1envBP3'] = 123
        e['P_el1_fl1envBP4'] = 124
        e['P_el1_fl1envOff1b1'] = 125
        e['P_el1_fl1envOff1b2'] = 126
        e['P_el1_fl1envOff2b1'] = 127
        e['P_el1_fl1envOff2b2'] = 128
        e['P_el1_fl1envOff3b1'] = 129
        e['P_el1_fl1envOff3b2'] = 130
        e['P_el1_fl1envOff4b1'] = 131
        e['P_el1_fl1envOff4b2'] = 132
        e['P_el1_fl2type'] = 133
        e['P_el1_fl2cutoff'] = 134
        e['P_el1_fl2mode'] = 135
        e['P_el1_fl2envR1'] = 136
        e['P_el1_fl2envR2'] = 137
        e['P_el1_fl2envR3'] = 138
        e['P_el1_fl2envR4'] = 139
        e['P_el1_fl2envRR1'] = 140
        e['P_el1_fl2envRR2'] = 141
        e['P_el1_fl2envL0'] = 142
        e['P_el1_fl2envL1'] = 143
        e['P_el1_fl2envL2'] = 144
        e['P_el1_fl2envL3'] = 145
        e['P_el1_fl2envL4'] = 146
        e['P_el1_fl2envRL1'] = 147
        e['P_el1_fl2envRL2'] = 148
        e['P_el1_fl2envertscl'] = 149
        e['P_el1_fl2envBP1'] = 150
        e['P_el1_fl2envBP2'] = 151
        e['P_el1_fl2envBP3'] = 152
        e['P_el1_fl2envBP4'] = 153
        e['P_el1_fl2envOff1b1'] = 154
        e['P_el1_fl2envOff1b2'] = 155
        e['P_el1_fl2envOff2b1'] = 156
        e['P_el1_fl2envOff2b2'] = 157
        e['P_el1_fl2envOff3b1'] = 158
        e['P_el1_fl2envOff3b2'] = 159
        e['P_el1_fl2envOff4b1'] = 160
        e['P_el1_fl2envOff4b2'] = 161
        e['P_el1flres'] = 162
        e['P_el1flvelsens'] = 163
        e['P_el1flmodsens'] = 164
        e['P_el1ampenvmode'] = 165
        e['P_el1ampenvR1'] = 166
        e['P_el1ampenvR2'] = 167
        e['P_el1ampenvR3'] = 168
        e['P_el1ampenvR4'] = 169
        e['P_el1ampenvRR'] = 170
        e['P_el1ampenvL2'] = 171
        e['P_el1ampenvL3'] = 172
        e['P_el1ampenvrtscl'] = 173
        e['P_el1ampenvBP1'] = 174
        e['P_el1ampenvBP2'] = 175
        e['P_el1ampenvBP3'] = 176
        e['P_el1ampenvBP4'] = 177
        e['P_el1ampenvOff1b1'] = 178
        e['P_el1ampenvOff1b2'] = 179
        e['P_el1ampenvOff2b1'] = 180
        e['P_el1ampenvOff2b2'] = 181
        e['P_el1ampenvOff3b1'] = 182
        e['P_el1ampenvOff3b2'] = 183
        e['P_el1ampenvOff4b1'] = 184
        e['P_el1ampenvOff4b2'] = 185
        e['P_el1velsens'] = 186
        e['P_el1velratesens'] = 187
        e['P_el1ampmodsens'] = 188
    
    # 2 ELEMENTS
    if elnumber == 2:
        ##### ELEMENT 1
        e['P_el1_voice'] = 88
        e['P_el1_oscfreqmode'] = 89
        e['P_el1_oscfreqnote'] = 90
        e['P_el1_oscfreqtune'] = 91
        e['P_el1_pitchmodsens'] = 92
        e['P_el1_pitchenvR1'] = 93
        e['P_el1_pitchenvR2'] = 94
        e['P_el1_pitchenvR3'] = 95
        e['P_el1_pitchenvRR'] = 96
        e['P_el1_pitchenvL0'] = 97
        e['P_el1_pitchenvL1'] = 98
        e['P_el1_pitchenvL2'] = 99
        e['P_el1_pitchenvL3'] = 100
        e['P_el1_pitchenvRL'] = 101
        e['P_el1_pitchenvrng'] = 102
        e['P_el1_pitchenvratescl'] = 103
        e['P_el1_pitchenvvelsw'] = 104
        e['P_el1_lfospd'] = 105
        e['P_el1_lfodly'] = 106
        e['P_el1_lfopitchmod'] = 107
        e['P_el1_lfoampmod'] = 108
        e['P_el1_lfocutoffmod'] = 109
        e['P_el1_lfowave'] = 110
        e['P_el1_lfophase'] = 111
        e['P_el1_fl1type'] = 113
        e['P_el1_fl1cutoff'] = 114
        e['P_el1_fl1mode'] = 115
        e['P_el1_fl1envR1'] = 116
        e['P_el1_fl1envR2'] = 117
        e['P_el1_fl1envR3'] = 118
        e['P_el1_fl1envR4'] = 119
        e['P_el1_fl1envRR1'] = 120
        e['P_el1_fl1envRR2'] = 121
        e['P_el1_fl1envL0'] = 122
        e['P_el1_fl1envL1'] = 123
        e['P_el1_fl1envL2'] = 124
        e['P_el1_fl1envL3'] = 125
        e['P_el1_fl1envL4'] = 126
        e['P_el1_fl1envRL1'] = 127
        e['P_el1_fl1envRL2'] = 128
        e['P_el1_fl1envertscl'] = 129
        e['P_el1_fl1envBP1'] = 130
        e['P_el1_fl1envBP2'] = 131
        e['P_el1_fl1envBP3'] = 132
        e['P_el1_fl1envBP4'] = 133
        e['P_el1_fl1envOff1b1'] = 134
        e['P_el1_fl1envOff1b2'] = 135
        e['P_el1_fl1envOff2b1'] = 136
        e['P_el1_fl1envOff2b2'] = 137
        e['P_el1_fl1envOff3b1'] = 138
        e['P_el1_fl1envOff3b2'] = 139
        e['P_el1_fl1envOff4b1'] = 140
        e['P_el1_fl1envOff4b2'] = 141
        e['P_el1_fl2type'] = 142
        e['P_el1_fl2cutoff'] = 143
        e['P_el1_fl2mode'] = 144
        e['P_el1_fl2envR1'] = 145
        e['P_el1_fl2envR2'] = 146
        e['P_el1_fl2envR3'] = 147
        e['P_el1_fl2envR4'] = 148
        e['P_el1_fl2envRR1'] = 149
        e['P_el1_fl2envRR2'] = 150
        e['P_el1_fl2envL0'] = 151
        e['P_el1_fl2envL1'] = 152
        e['P_el1_fl2envL2'] = 153
        e['P_el1_fl2envL3'] = 154
        e['P_el1_fl2envL4'] = 155
        e['P_el1_fl2envRL1'] = 156
        e['P_el1_fl2envRL2'] = 157
        e['P_el1_fl2envertscl'] = 158
        e['P_el1_fl2envBP1'] = 159
        e['P_el1_fl2envBP2'] = 160
        e['P_el1_fl2envBP3'] = 161
        e['P_el1_fl2envBP4'] = 162
        e['P_el1_fl2envOff1b1'] = 163
        e['P_el1_fl2envOff1b2'] = 164
        e['P_el1_fl2envOff2b1'] = 165
        e['P_el1_fl2envOff2b2'] = 166
        e['P_el1_fl2envOff3b1'] = 167
        e['P_el1_fl2envOff3b2'] = 168
        e['P_el1_fl2envOff4b1'] = 169
        e['P_el1_fl2envOff4b2'] = 170
        e['P_el1flres'] = 171
        e['P_el1flvelsens'] = 172
        e['P_el1flmodsens'] = 173
        e['P_el1ampenvmode'] = 174
        e['P_el1ampenvR1'] = 175
        e['P_el1ampenvR2'] = 176
        e['P_el1ampenvR3'] = 177
        e['P_el1ampenvR4'] = 178
        e['P_el1ampenvRR'] = 179
        e['P_el1ampenvL2'] = 180
        e['P_el1ampenvL3'] = 181
        e['P_el1ampenvrtscl'] = 182
        e['P_el1ampenvBP1'] = 183
        e['P_el1ampenvBP2'] = 184
        e['P_el1ampenvBP3'] = 185
        e['P_el1ampenvBP4'] = 186
        e['P_el1ampenvOff1b1'] = 187
        e['P_el1ampenvOff1b2'] = 188
        e['P_el1ampenvOff2b1'] = 189
        e['P_el1ampenvOff2b2'] = 190
        e['P_el1ampenvOff3b1'] = 191
        e['P_el1ampenvOff3b2'] = 192
        e['P_el1ampenvOff4b1'] = 193
        e['P_el1ampenvOff4b2'] = 194
        e['P_el1velsens'] = 195
        e['P_el1velratesens'] = 196
        e['P_el1ampmodsens'] = 197
        
        ##### ELEMENT 2
        e['P_el2_voice'] = 200
        e['P_el2_oscfreqmode'] = 201
        e['P_el2_oscfreqnote'] = 202
        e['P_el2_oscfreqtune'] = 203
        e['P_el2_pitchmodsens'] = 204
        e['P_el2_pitchenvR1'] = 205
        e['P_el2_pitchenvR2'] = 206
        e['P_el2_pitchenvR3'] = 207
        e['P_el2_pitchenvRR'] = 208
        e['P_el2_pitchenvL0'] = 209
        e['P_el2_pitchenvL1'] = 210
        e['P_el2_pitchenvL2'] = 211
        e['P_el2_pitchenvL3'] = 212
        e['P_el2_pitchenvRL'] = 213
        e['P_el2_pitchenvrng'] = 214
        e['P_el2_pitchenvratescl'] = 215
        e['P_el2_pitchenvvelsw'] = 216
        e['P_el2_lfospd'] = 217
        e['P_el2_lfodly'] = 218
        e['P_el2_lfopitchmod'] = 219
        e['P_el2_lfoampmod'] = 220
        e['P_el2_lfocutoffmod'] = 221
        e['P_el2_lfowave'] = 222
        e['P_el2_lfophase'] = 223
        e['P_el2_fl1type'] = 225
        e['P_el2_fl1cutoff'] = 226
        e['P_el2_fl1mode'] = 227
        e['P_el2_fl1envR1'] = 228
        e['P_el2_fl1envR2'] = 229
        e['P_el2_fl1envR3'] = 230
        e['P_el2_fl1envR4'] = 231
        e['P_el2_fl1envRR1'] = 232
        e['P_el2_fl1envRR2'] = 233
        e['P_el2_fl1envL0'] = 234
        e['P_el2_fl1envL1'] = 235
        e['P_el2_fl1envL2'] = 236
        e['P_el2_fl1envL3'] = 237
        e['P_el2_fl1envL4'] = 238
        e['P_el2_fl1envRL1'] = 239
        e['P_el2_fl1envRL2'] = 240
        e['P_el2_fl1envertscl'] = 241
        e['P_el2_fl1envBP1'] = 242
        e['P_el2_fl1envBP2'] = 243
        e['P_el2_fl1envBP3'] = 244
        e['P_el2_fl1envBP4'] = 245
        e['P_el2_fl1envOff1b1'] = 246
        e['P_el2_fl1envOff1b2'] = 247
        e['P_el2_fl1envOff2b1'] = 248
        e['P_el2_fl1envOff2b2'] = 249
        e['P_el2_fl1envOff3b1'] = 250
        e['P_el2_fl1envOff3b2'] = 251
        e['P_el2_fl1envOff4b1'] = 252
        e['P_el2_fl1envOff4b2'] = 253
        e['P_el2_fl2type'] = 254
        e['P_el2_fl2cutoff'] = 255
        e['P_el2_fl2mode'] = 256
        e['P_el2_fl2envR1'] = 257
        e['P_el2_fl2envR2'] = 258
        e['P_el2_fl2envR3'] = 259
        e['P_el2_fl2envR4'] = 260
        e['P_el2_fl2envRR1'] = 261
        e['P_el2_fl2envRR2'] = 262
        e['P_el2_fl2envL0'] = 263
        e['P_el2_fl2envL1'] = 264
        e['P_el2_fl2envL2'] = 265
        e['P_el2_fl2envL3'] = 266
        e['P_el2_fl2envL4'] = 267
        e['P_el2_fl2envRL1'] = 268
        e['P_el2_fl2envRL2'] = 269
        e['P_el2_fl2envertscl'] = 270
        e['P_el2_fl2envBP1'] = 271
        e['P_el2_fl2envBP2'] = 272
        e['P_el2_fl2envBP3'] = 273
        e['P_el2_fl2envBP4'] = 274
        e['P_el2_fl2envOff1b1'] = 275
        e['P_el2_fl2envOff1b2'] = 276
        e['P_el2_fl2envOff2b1'] = 277
        e['P_el2_fl2envOff2b2'] = 278
        e['P_el2_fl2envOff3b1'] = 279
        e['P_el2_fl2envOff3b2'] = 280
        e['P_el2_fl2envOff4b1'] = 281
        e['P_el2_fl2envOff4b2'] = 282
        e['P_el2flres'] = 283
        e['P_el2flvelsens'] = 284
        e['P_el2flmodsens'] = 285
        e['P_el2ampenvmode'] = 286
        e['P_el2ampenvR1'] = 287
        e['P_el2ampenvR2'] = 288
        e['P_el2ampenvR3'] = 289
        e['P_el2ampenvR4'] = 290
        e['P_el2ampenvRR'] = 291
        e['P_el2ampenvL2'] = 292
        e['P_el2ampenvL3'] = 293
        e['P_el2ampenvrtscl'] = 294
        e['P_el2ampenvBP1'] = 295
        e['P_el2ampenvBP2'] = 296
        e['P_el2ampenvBP3'] = 297
        e['P_el2ampenvBP4'] = 298
        e['P_el2ampenvOff1b1'] = 299
        e['P_el2ampenvOff1b2'] = 300
        e['P_el2ampenvOff2b1'] = 301
        e['P_el2ampenvOff2b2'] = 302
        e['P_el2ampenvOff3b1'] = 303
        e['P_el2ampenvOff3b2'] = 304
        e['P_el2ampenvOff4b1'] = 305
        e['P_el2ampenvOff4b2'] = 306
        e['P_el2velsens'] = 307
        e['P_el2velratesens'] = 308
        e['P_el2ampmodsens'] = 309

    # 4 ELEMENTS
    if elnumber == 4:
        ##### ELEMENT 1
        e['P_el1_voice'] = 106
        e['P_el1_oscfreqmode'] = 107
        e['P_el1_oscfreqnote'] = 108
        e['P_el1_oscfreqtune'] = 109
        e['P_el1_pitchmodsens'] = 110
        e['P_el1_pitchenvR1'] = 111
        e['P_el1_pitchenvR2'] = 112
        e['P_el1_pitchenvR3'] = 113
        e['P_el1_pitchenvRR'] = 114
        e['P_el1_pitchenvL0'] = 115
        e['P_el1_pitchenvL1'] = 116
        e['P_el1_pitchenvL2'] = 117
        e['P_el1_pitchenvL3'] = 118
        e['P_el1_pitchenvRL'] = 119
        e['P_el1_pitchenvrng'] = 120
        e['P_el1_pitchenvratescl'] = 121
        e['P_el1_pitchenvvelsw'] = 122
        e['P_el1_lfospd'] = 123
        e['P_el1_lfodly'] = 124
        e['P_el1_lfopitchmod'] = 125
        e['P_el1_lfoampmod'] = 126
        e['P_el1_lfocutoffmod'] = 127
        e['P_el1_lfowave'] = 128
        e['P_el1_lfophase'] = 129
        e['P_el1_fl1type'] = 131
        e['P_el1_fl1cutoff'] = 132
        e['P_el1_fl1mode'] = 133
        e['P_el1_fl1envR1'] = 134
        e['P_el1_fl1envR2'] = 135
        e['P_el1_fl1envR3'] = 136
        e['P_el1_fl1envR4'] = 137
        e['P_el1_fl1envRR1'] = 138
        e['P_el1_fl1envRR2'] = 139
        e['P_el1_fl1envL0'] = 140
        e['P_el1_fl1envL1'] = 141
        e['P_el1_fl1envL2'] = 142
        e['P_el1_fl1envL3'] = 143
        e['P_el1_fl1envL4'] = 144
        e['P_el1_fl1envRL1'] = 145
        e['P_el1_fl1envRL2'] = 146
        e['P_el1_fl1envertscl'] = 147
        e['P_el1_fl1envBP1'] = 148
        e['P_el1_fl1envBP2'] = 149
        e['P_el1_fl1envBP3'] = 150
        e['P_el1_fl1envBP4'] = 151
        e['P_el1_fl1envOff1b1'] = 152
        e['P_el1_fl1envOff1b2'] = 153
        e['P_el1_fl1envOff2b1'] = 154
        e['P_el1_fl1envOff2b2'] = 155
        e['P_el1_fl1envOff3b1'] = 156
        e['P_el1_fl1envOff3b2'] = 157
        e['P_el1_fl1envOff4b1'] = 158
        e['P_el1_fl1envOff4b2'] = 159
        e['P_el1_fl2type'] = 160
        e['P_el1_fl2cutoff'] = 161
        e['P_el1_fl2mode'] = 162
        e['P_el1_fl2envR1'] = 163
        e['P_el1_fl2envR2'] = 164
        e['P_el1_fl2envR3'] = 165
        e['P_el1_fl2envR4'] = 166
        e['P_el1_fl2envRR1'] = 167
        e['P_el1_fl2envRR2'] = 168
        e['P_el1_fl2envL0'] = 169
        e['P_el1_fl2envL1'] = 170
        e['P_el1_fl2envL2'] = 171
        e['P_el1_fl2envL3'] = 172
        e['P_el1_fl2envL4'] = 173
        e['P_el1_fl2envRL1'] = 174
        e['P_el1_fl2envRL2'] = 175
        e['P_el1_fl2envertscl'] = 176
        e['P_el1_fl2envBP1'] = 177
        e['P_el1_fl2envBP2'] = 178
        e['P_el1_fl2envBP3'] = 179
        e['P_el1_fl2envBP4'] = 180
        e['P_el1_fl2envOff1b1'] = 181
        e['P_el1_fl2envOff1b2'] = 182
        e['P_el1_fl2envOff2b1'] = 183
        e['P_el1_fl2envOff2b2'] = 184
        e['P_el1_fl2envOff3b1'] = 185
        e['P_el1_fl2envOff3b2'] = 186
        e['P_el1_fl2envOff4b1'] = 187
        e['P_el1_fl2envOff4b2'] = 188
        e['P_el1flres'] = 189
        e['P_el1flvelsens'] = 190
        e['P_el1flmodsens'] = 191
        e['P_el1ampenvmode'] = 192
        e['P_el1ampenvR1'] = 193
        e['P_el1ampenvR2'] = 194
        e['P_el1ampenvR3'] = 195
        e['P_el1ampenvR4'] = 196
        e['P_el1ampenvRR'] = 197
        e['P_el1ampenvL2'] = 198
        e['P_el1ampenvL3'] = 199
        e['P_el1ampenvrtscl'] = 200
        e['P_el1ampenvBP1'] = 201
        e['P_el1ampenvBP2'] = 202
        e['P_el1ampenvBP3'] = 203
        e['P_el1ampenvBP4'] = 204
        e['P_el1ampenvOff1b1'] = 205
        e['P_el1ampenvOff1b2'] = 206
        e['P_el1ampenvOff2b1'] = 207
        e['P_el1ampenvOff2b2'] = 208
        e['P_el1ampenvOff3b1'] = 209
        e['P_el1ampenvOff3b2'] = 210
        e['P_el1ampenvOff4b1'] = 211
        e['P_el1ampenvOff4b2'] = 212
        e['P_el1velsens'] = 213
        e['P_el1velratesens'] = 214
        e['P_el1ampmodsens'] = 215

        ##### ELEMENT 2
        e['P_el2_voice'] = 218
        e['P_el2_oscfreqmode'] = 219
        e['P_el2_oscfreqnote'] = 220
        e['P_el2_oscfreqtune'] = 221
        e['P_el2_pitchmodsens'] = 222
        e['P_el2_pitchenvR1'] = 223
        e['P_el2_pitchenvR2'] = 224
        e['P_el2_pitchenvR3'] = 225
        e['P_el2_pitchenvRR'] = 226
        e['P_el2_pitchenvL0'] = 227
        e['P_el2_pitchenvL1'] = 228
        e['P_el2_pitchenvL2'] = 229
        e['P_el2_pitchenvL3'] = 230
        e['P_el2_pitchenvRL'] = 231
        e['P_el2_pitchenvrng'] = 232
        e['P_el2_pitchenvratescl'] = 233
        e['P_el2_pitchenvvelsw'] = 234
        e['P_el2_lfospd'] = 235
        e['P_el2_lfodly'] = 236
        e['P_el2_lfopitchmod'] = 237
        e['P_el2_lfoampmod'] = 238
        e['P_el2_lfocutoffmod'] = 239
        e['P_el2_lfowave'] = 240
        e['P_el2_lfophase'] = 241
        e['P_el2_fl1type'] = 243
        e['P_el2_fl1cutoff'] = 244
        e['P_el2_fl1mode'] = 245
        e['P_el2_fl1envR1'] = 246
        e['P_el2_fl1envR2'] = 247
        e['P_el2_fl1envR3'] = 248
        e['P_el2_fl1envR4'] = 249
        e['P_el2_fl1envRR1'] = 250
        e['P_el2_fl1envRR2'] = 251
        e['P_el2_fl1envL0'] = 252
        e['P_el2_fl1envL1'] = 253
        e['P_el2_fl1envL2'] = 254
        e['P_el2_fl1envL3'] = 255
        e['P_el2_fl1envL4'] = 256
        e['P_el2_fl1envRL1'] = 257
        e['P_el2_fl1envRL2'] = 258
        e['P_el2_fl1envertscl'] = 259
        e['P_el2_fl1envBP1'] = 260
        e['P_el2_fl1envBP2'] = 261
        e['P_el2_fl1envBP3'] = 262
        e['P_el2_fl1envBP4'] = 263
        e['P_el2_fl1envOff1b1'] = 264
        e['P_el2_fl1envOff1b2'] = 265
        e['P_el2_fl1envOff2b1'] = 266
        e['P_el2_fl1envOff2b2'] = 267
        e['P_el2_fl1envOff3b1'] = 268
        e['P_el2_fl1envOff3b2'] = 269
        e['P_el2_fl1envOff4b1'] = 270
        e['P_el2_fl1envOff4b2'] = 271
        e['P_el2_fl2type'] = 272
        e['P_el2_fl2cutoff'] = 273
        e['P_el2_fl2mode'] = 274
        e['P_el2_fl2envR1'] = 275
        e['P_el2_fl2envR2'] = 276
        e['P_el2_fl2envR3'] = 277
        e['P_el2_fl2envR4'] = 278
        e['P_el2_fl2envRR1'] = 279
        e['P_el2_fl2envRR2'] = 280
        e['P_el2_fl2envL0'] = 281
        e['P_el2_fl2envL1'] = 282
        e['P_el2_fl2envL2'] = 283
        e['P_el2_fl2envL3'] = 284
        e['P_el2_fl2envL4'] = 285
        e['P_el2_fl2envRL1'] = 286
        e['P_el2_fl2envRL2'] = 287
        e['P_el2_fl2envertscl'] = 288
        e['P_el2_fl2envBP1'] = 289
        e['P_el2_fl2envBP2'] = 290
        e['P_el2_fl2envBP3'] = 291
        e['P_el2_fl2envBP4'] = 292
        e['P_el2_fl2envOff1b1'] = 293
        e['P_el2_fl2envOff1b2'] = 294
        e['P_el2_fl2envOff2b1'] = 295
        e['P_el2_fl2envOff2b2'] = 296
        e['P_el2_fl2envOff3b1'] = 297
        e['P_el2_fl2envOff3b2'] = 298
        e['P_el2_fl2envOff4b1'] = 299
        e['P_el2_fl2envOff4b2'] = 300
        e['P_el2flres'] = 301
        e['P_el2flvelsens'] = 302
        e['P_el2flmodsens'] = 303
        e['P_el2ampenvmode'] = 304
        e['P_el2ampenvR1'] = 305
        e['P_el2ampenvR2'] = 306
        e['P_el2ampenvR3'] = 307
        e['P_el2ampenvR4'] = 308
        e['P_el2ampenvRR'] = 309
        e['P_el2ampenvL2'] = 310
        e['P_el2ampenvL3'] = 311
        e['P_el2ampenvrtscl'] = 312
        e['P_el2ampenvBP1'] = 313
        e['P_el2ampenvBP2'] = 314
        e['P_el2ampenvBP3'] = 315
        e['P_el2ampenvBP4'] = 316
        e['P_el2ampenvOff1b1'] = 317
        e['P_el2ampenvOff1b2'] = 318
        e['P_el2ampenvOff2b1'] = 319
        e['P_el2ampenvOff2b2'] = 320
        e['P_el2ampenvOff3b1'] = 321
        e['P_el2ampenvOff3b2'] = 322
        e['P_el2ampenvOff4b1'] = 323
        e['P_el2ampenvOff4b2'] = 324
        e['P_el2velsens'] = 325
        e['P_el2velratesens'] = 326
        e['P_el2ampmodsens'] = 327

##### ELEMENT 3
        e['P_el3_voice'] = 330
        e['P_el3_oscfreqmode'] = 331
        e['P_el3_oscfreqnote'] = 332
        e['P_el3_oscfreqtune'] = 333
        e['P_el3_pitchmodsens'] = 334
        e['P_el3_pitchenvR1'] = 335
        e['P_el3_pitchenvR2'] = 336
        e['P_el3_pitchenvR3'] = 337
        e['P_el3_pitchenvRR'] = 338
        e['P_el3_pitchenvL0'] = 339
        e['P_el3_pitchenvL1'] = 340
        e['P_el3_pitchenvL2'] = 341
        e['P_el3_pitchenvL3'] = 342
        e['P_el3_pitchenvRL'] = 343
        e['P_el3_pitchenvrng'] = 344
        e['P_el3_pitchenvratescl'] = 345
        e['P_el3_pitchenvvelsw'] = 346
        e['P_el3_lfospd'] = 347
        e['P_el3_lfodly'] = 348
        e['P_el3_lfopitchmod'] = 349
        e['P_el3_lfoampmod'] = 350
        e['P_el3_lfocutoffmod'] = 351
        e['P_el3_lfowave'] = 352
        e['P_el3_lfophase'] = 353
        e['P_el3_fl1type'] = 355
        e['P_el3_fl1cutoff'] = 356
        e['P_el3_fl1mode'] = 357
        e['P_el3_fl1envR1'] = 358
        e['P_el3_fl1envR2'] = 359
        e['P_el3_fl1envR3'] = 360
        e['P_el3_fl1envR4'] = 361
        e['P_el3_fl1envRR1'] = 362
        e['P_el3_fl1envRR2'] = 363
        e['P_el3_fl1envL0'] = 364
        e['P_el3_fl1envL1'] = 365
        e['P_el3_fl1envL2'] = 366
        e['P_el3_fl1envL3'] = 367
        e['P_el3_fl1envL4'] = 368
        e['P_el3_fl1envRL1'] = 369
        e['P_el3_fl1envRL2'] = 370
        e['P_el3_fl1envertscl'] = 371
        e['P_el3_fl1envBP1'] = 372
        e['P_el3_fl1envBP2'] = 373
        e['P_el3_fl1envBP3'] = 374
        e['P_el3_fl1envBP4'] = 375
        e['P_el3_fl1envOff1b1'] = 376
        e['P_el3_fl1envOff1b2'] = 377
        e['P_el3_fl1envOff2b1'] = 378
        e['P_el3_fl1envOff2b2'] = 379
        e['P_el3_fl1envOff3b1'] = 380
        e['P_el3_fl1envOff3b2'] = 381
        e['P_el3_fl1envOff4b1'] = 382
        e['P_el3_fl1envOff4b2'] = 383
        e['P_el3_fl2type'] = 384
        e['P_el3_fl2cutoff'] = 385
        e['P_el3_fl2mode'] = 386
        e['P_el3_fl2envR1'] = 387
        e['P_el3_fl2envR2'] = 388
        e['P_el3_fl2envR3'] = 389
        e['P_el3_fl2envR4'] = 390
        e['P_el3_fl2envRR1'] = 391
        e['P_el3_fl2envRR2'] = 392
        e['P_el3_fl2envL0'] = 393
        e['P_el3_fl2envL1'] = 394
        e['P_el3_fl2envL2'] = 395
        e['P_el3_fl2envL3'] = 396
        e['P_el3_fl2envL4'] = 397
        e['P_el3_fl2envRL1'] = 398
        e['P_el3_fl2envRL2'] = 399
        e['P_el3_fl2envertscl'] = 400
        e['P_el3_fl2envBP1'] = 401
        e['P_el3_fl2envBP2'] = 402
        e['P_el3_fl2envBP3'] = 403
        e['P_el3_fl2envBP4'] = 404
        e['P_el3_fl2envOff1b1'] = 405
        e['P_el3_fl2envOff1b2'] = 406
        e['P_el3_fl2envOff2b1'] = 407
        e['P_el3_fl2envOff2b2'] = 408
        e['P_el3_fl2envOff3b1'] = 409
        e['P_el3_fl2envOff3b2'] = 410
        e['P_el3_fl2envOff4b1'] = 411
        e['P_el3_fl2envOff4b2'] = 412
        e['P_el3flres'] = 413
        e['P_el3flvelsens'] = 414
        e['P_el3flmodsens'] = 415
        e['P_el3ampenvmode'] = 416
        e['P_el3ampenvR1'] = 417
        e['P_el3ampenvR2'] = 418
        e['P_el3ampenvR3'] = 419
        e['P_el3ampenvR4'] = 420
        e['P_el3ampenvRR'] = 421
        e['P_el3ampenvL2'] = 422
        e['P_el3ampenvL3'] = 423
        e['P_el3ampenvrtscl'] = 424
        e['P_el3ampenvBP1'] = 425
        e['P_el3ampenvBP2'] = 426
        e['P_el3ampenvBP3'] = 427
        e['P_el3ampenvBP4'] = 428
        e['P_el3ampenvOff1b1'] = 429
        e['P_el3ampenvOff1b2'] = 430
        e['P_el3ampenvOff2b1'] = 431
        e['P_el3ampenvOff2b2'] = 432
        e['P_el3ampenvOff3b1'] = 433
        e['P_el3ampenvOff3b2'] = 434
        e['P_el3ampenvOff4b1'] = 435
        e['P_el3ampenvOff4b2'] = 436
        e['P_el3velsens'] = 437
        e['P_el3velratesens'] = 438
        e['P_el3ampmodsens'] = 439
##### ELEMENT 4
        e['P_el4_voice'] = 442
        e['P_el4_oscfreqmode'] = 443
        e['P_el4_oscfreqnote'] = 444
        e['P_el4_oscfreqtune'] = 445
        e['P_el4_pitchmodsens'] = 446
        e['P_el4_pitchenvR1'] = 447
        e['P_el4_pitchenvR2'] = 448
        e['P_el4_pitchenvR3'] = 449
        e['P_el4_pitchenvRR'] = 450
        e['P_el4_pitchenvL0'] = 451
        e['P_el4_pitchenvL1'] = 452
        e['P_el4_pitchenvL2'] = 453
        e['P_el4_pitchenvL3'] = 454
        e['P_el4_pitchenvRL'] = 455
        e['P_el4_pitchenvrng'] = 456
        e['P_el4_pitchenvratescl'] = 457
        e['P_el4_pitchenvvelsw'] = 458
        e['P_el4_lfospd'] = 459
        e['P_el4_lfodly'] = 460
        e['P_el4_lfopitchmod'] = 461
        e['P_el4_lfoampmod'] = 462
        e['P_el4_lfocutoffmod'] = 463
        e['P_el4_lfowave'] = 464
        e['P_el4_lfophase'] = 465
        e['P_el4_fl1type'] = 467
        e['P_el4_fl1cutoff'] = 468
        e['P_el4_fl1mode'] = 469
        e['P_el4_fl1envR1'] = 470
        e['P_el4_fl1envR2'] = 471
        e['P_el4_fl1envR3'] = 472
        e['P_el4_fl1envR4'] = 473
        e['P_el4_fl1envRR1'] = 474
        e['P_el4_fl1envRR2'] = 475
        e['P_el4_fl1envL0'] = 476
        e['P_el4_fl1envL1'] = 477
        e['P_el4_fl1envL2'] = 478
        e['P_el4_fl1envL3'] = 479
        e['P_el4_fl1envL4'] = 480
        e['P_el4_fl1envRL1'] = 481
        e['P_el4_fl1envRL2'] = 482
        e['P_el4_fl1envertscl'] = 483
        e['P_el4_fl1envBP1'] = 484
        e['P_el4_fl1envBP2'] = 485
        e['P_el4_fl1envBP3'] = 486
        e['P_el4_fl1envBP4'] = 487
        e['P_el4_fl1envOff1b1'] = 488
        e['P_el4_fl1envOff1b2'] = 489
        e['P_el4_fl1envOff2b1'] = 490
        e['P_el4_fl1envOff2b2'] = 491
        e['P_el4_fl1envOff3b1'] = 492
        e['P_el4_fl1envOff3b2'] = 493
        e['P_el4_fl1envOff4b1'] = 494
        e['P_el4_fl1envOff4b2'] = 495
        e['P_el4_fl2type'] = 496
        e['P_el4_fl2cutoff'] = 497
        e['P_el4_fl2mode'] = 498
        e['P_el4_fl2envR1'] = 499
        e['P_el4_fl2envR2'] = 500
        e['P_el4_fl2envR3'] = 501
        e['P_el4_fl2envR4'] = 502
        e['P_el4_fl2envRR1'] = 503
        e['P_el4_fl2envRR2'] = 504
        e['P_el4_fl2envL0'] = 505
        e['P_el4_fl2envL1'] = 506
        e['P_el4_fl2envL2'] = 507
        e['P_el4_fl2envL3'] = 508
        e['P_el4_fl2envL4'] = 509
        e['P_el4_fl2envRL1'] = 510
        e['P_el4_fl2envRL2'] = 511
        e['P_el4_fl2envertscl'] = 512
        e['P_el4_fl2envBP1'] = 513
        e['P_el4_fl2envBP2'] = 514
        e['P_el4_fl2envBP3'] = 515
        e['P_el4_fl2envBP4'] = 516
        e['P_el4_fl2envOff1b1'] = 517
        e['P_el4_fl2envOff1b2'] = 518
        e['P_el4_fl2envOff2b1'] = 519
        e['P_el4_fl2envOff2b2'] = 520
        e['P_el4_fl2envOff3b1'] = 521
        e['P_el4_fl2envOff3b2'] = 522
        e['P_el4_fl2envOff4b1'] = 523
        e['P_el4_fl2envOff4b2'] = 524
        e['P_el4flres'] = 525
        e['P_el4flvelsens'] = 526
        e['P_el4flmodsens'] = 527
        e['P_el4ampenvmode'] = 528
        e['P_el4ampenvR1'] = 529
        e['P_el4ampenvR2'] = 530
        e['P_el4ampenvR3'] = 531
        e['P_el4ampenvR4'] = 532
        e['P_el4ampenvRR'] = 533
        e['P_el4ampenvL2'] = 534
        e['P_el4ampenvL3'] = 535
        e['P_el4ampenvrtscl'] = 536
        e['P_el4ampenvBP1'] = 537
        e['P_el4ampenvBP2'] = 538
        e['P_el4ampenvBP3'] = 539
        e['P_el4ampenvBP4'] = 540
        e['P_el4ampenvOff1b1'] = 541
        e['P_el4ampenvOff1b2'] = 542
        e['P_el4ampenvOff2b1'] = 543
        e['P_el4ampenvOff2b2'] = 544
        e['P_el4ampenvOff3b1'] = 545
        e['P_el4ampenvOff3b2'] = 546
        e['P_el4ampenvOff4b1'] = 547
        e['P_el4ampenvOff4b2'] = 548
        e['P_el4velsens'] = 549
        e['P_el4velratesens'] = 550
        e['P_el4ampmodsens'] = 551
    
    # "PEGAMOS" LOS PARAMETROS
    # Voice Name
    name = ''
    for i in range(32,42):
        name = name+(bytearray.fromhex(datalist[i]).decode())
    dpg.configure_item(item='voice_name', default_value = name)
    voicename('voice_name')

    # Efx Type 
    dpg.configure_item(item='effect_type', default_value = effectslist[int(datalist[42],16)-1])
    effecttype('effect_type')

    # Efx Param 1,2,3 
    dpg.configure_item(item='param1_slider', default_value = int(datalist[44],16))
    dpg.configure_item(item='param2_slider', default_value = int(datalist[45],16))
    dpg.configure_item(item='param3_slider', default_value = int(datalist[46],16))
    effectparam1('param1_slider')
    effectparam2('param2_slider')
    effectparam3('param3_slider')

    # Efx output level
    dpg.configure_item(item='effect_level', default_value = int(datalist[43],16))
    effectlevel('effect_level')

    # Pitch Bend Range
    dpg.configure_item(item='pitch_bend_range', default_value = int(datalist[47],16))
    pitchbendrange('pitch_bend_range')

    # Aftertouch pitch bias
    decvalue = int(datalist[48],16)
    if decvalue > 16:
        decvalue = -(decvalue - 16)
    dpg.configure_item(item='aftertouch_pitch_bias', default_value = decvalue)
    aftertouchpitchbias('aftertouch_pitch_bias')

    # random pitch range
    dpg.configure_item(item='random_pitch_range', default_value = int(datalist[63],16)) 
    randompitchrange('random_pitch_range')

    # Voice Volume
    dpg.configure_item(item='voice_volume', default_value = int(datalist[65],16)) 
    voicevolume('voice_volume')

    ############################## CONTROLLERS
    # pitch mod
    dpg.configure_item(item='pitch_mod_cc', default_value = controllerlist[int(datalist[49],16)])
    pitchmodcc('pitch_mod_cc')
    dpg.configure_item(item='pitch_mod_rng', default_value = int(datalist[50],16))
    pitchmodrng('pitch_mod_rng')
    # amp mod
    dpg.configure_item(item='amp_mod_cc', default_value = controllerlist[int(datalist[51],16)])
    ampmodcc('amp_mod_cc')
    dpg.configure_item(item='amp_mod_rng', default_value = int(datalist[52],16))  
    ampmodrng('amp_mod_rng')
    # cutoff mod
    dpg.configure_item(item='cutoff_mod_cc', default_value = controllerlist[int(datalist[53],16)])
    cutoffmodcc('cutoff_mod_cc')
    dpg.configure_item(item='cutoff_mod_rng', default_value = int(datalist[54],16))  
    cutoffmodrng('cutoff_mod_rng')
    # cutoff freq
    dpg.configure_item(item='cutoff_freq_cc', default_value = controllerlist[int(datalist[55],16)])
    cutofffreqcc('cutoff_freq_cc')
    dpg.configure_item(item='cutoff_freq_rng', default_value = int(datalist[56],16)) 
    cutofffreqrng('cutoff_freq_rng')
    # Env gen bias
    dpg.configure_item(item='env_gen_bias_cc', default_value =  controllerlist[int(datalist[59],16)]) 
    envgenbiascc('env_gen_bias_cc')
    dpg.configure_item(item='env_gen_rng', default_value = int(datalist[60],16)) 
    envgenrng('env_gen_rng')
    # Voice Volume
    dpg.configure_item(item='volume_cc', default_value =  controllerlist[int(datalist[61],16)]) 
    volumecc('volume_cc')
    dpg.configure_item(item='vol_min_rng', default_value = int(datalist[62],16)) 
    volumerngmin('vol_min_rng')

    # elements
    for i in range(1,elnumber+1):
        EL = 'el'+str(i)
        ELCOPY = i
        ELPASTE = i
        dpg.configure_item(item='el'+str(ELPASTE)+'_volume', default_value =  int(datalist[e['P_el'+str(ELCOPY)+'_volume']],16))
        elementvol('el'+str(ELPASTE)+'_volume')

        # detune - KNOB
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_detune']],16)
        eldetune(decvalue)

        # # Note shift - KONB
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_noteshift']],16)
        elnoteshift(decvalue)

        # Note Limit L
        dpg.configure_item(item='el'+str(ELPASTE)+'_note_limitL', default_value = notelist[int(datalist[e['P_el'+str(ELCOPY)+'_notelimL']],16)])
        elnotelimitL('el'+str(ELPASTE)+'_note_limitL')
        # Note Limit H
        dpg.configure_item(item='el'+str(ELPASTE)+'_note_limitH', default_value = notelist[int(datalist[e['P_el'+str(ELCOPY)+'_notelimH']],16)])
        elnotelimitH('el'+str(ELPASTE)+'_note_limitH')
        # Vel Limit L
        dpg.configure_item(item='el'+str(ELPASTE)+'_vel_limitL', default_value = int(datalist[e['P_el'+str(ELCOPY)+'_vellimL']],16))
        elvellimitL('el'+str(ELPASTE)+'_vel_limitL')
        # Vel Limit H
        dpg.configure_item(item='el'+str(ELPASTE)+'_vel_limitH', default_value = int(datalist[e['P_el'+str(ELCOPY)+'_vellimH']],16))
        elvellimitH('el'+str(ELPASTE)+'_vel_limitH')

        # pan - KNOB
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_pan']],16) # el1 = 75, el2 = 84
        elpan(decvalue)

        # efx balance - KNOB
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_efxbal']],16)
        elefxbalance(decvalue)

        # Element AWM Voice
        decvalue = voicelist[int(datalist[e['P_el'+str(ELCOPY)+'_voice']],16)]
        dpg.configure_item(item='el'+str(ELPASTE)+'_Waveform', default_value = decvalue)
        AWMwaveform('el'+str(ELPASTE)+'_Waveform')

        # OSC freq mode
        dpg.configure_item(item='el'+str(ELPASTE)+'_osc_freq_mode', default_value = int(datalist[e['P_el'+str(ELCOPY)+'_oscfreqmode']],16))
        eloscfreqmode('el'+str(ELPASTE)+'_osc_freq_mode')

        # OSC freq note 
        if int(datalist[e['P_el'+str(ELCOPY)+'_oscfreqmode']],16) == 1:
            decvalue = notelist[int(datalist[e['P_el'+str(ELCOPY)+'_oscfreqnote']],16)]
            dpg.configure_item(item='el'+str(ELPASTE)+'_osc_freq_note', default_value = decvalue)
            eloscfreqnote('el'+str(ELPASTE)+'_osc_freq_note')

        # OSC freq tune - KNOB
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_oscfreqtune']],16)
        eloscfreqtune(decvalue)

        # Pitch mod sens - KNOB
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_pitchmodsens']],16)
        elpitchmodsens(decvalue)

        # Pitch envelope
        for n in pitchenvlist:
            a = 'el'+str(ELPASTE)+'_pitch_env_'+n
            b = int(datalist[e['P_el'+str(ELCOPY)+'_pitchenv'+n]],16)
            if 'L' in n:
                b=b-64
            dpg.configure_item(item=a,default_value = b)
            elpitchenvelope(a)

        # Pitch envelope range
        decvalue = 3-int(datalist[e['P_el'+str(ELCOPY)+'_pitchenvrng']],16)
        dpg.configure_item(item='el'+str(ELPASTE)+'_pitch_env_range', default_value = decvalue)
        elpitchenvrange('el'+str(ELPASTE)+'_pitch_env_range')

        # Pitch env ratescale
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_pitchenvratescl']],16)
        if decvalue>7:
            decvalue = 8 - abs(decvalue)
        dpg.configure_item(item='el'+str(ELPASTE)+'_pitch_env_rate_scale', default_value = decvalue)
        elpitchenvratescale(decvalue)

        #Pitch env velocity switch
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_pitchenvvelsw']],16)
        dpg.configure_item(item='el'+str(ELPASTE)+'_pitch_env_vel_sw', default_value = 1-decvalue)
        elpitchenvvelsw('el'+str(ELPASTE)+'_pitch_env_vel_sw')

        # LFO Speed - KNOB
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_lfospd']],16)
        ellfospeed(decvalue)

        # LFO Delay - KNOB
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_lfodly']],16)
        ellfodelay(decvalue)

        # LFO Pitchmod - KNOB
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_lfopitchmod']],16)
        ellfopitchmod(decvalue)

        # LFO Ampmod - KNOB
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_lfoampmod']],16)
        ellfoampmod(decvalue)

        # LFO Cutoffmod - KNOB
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_lfocutoffmod']],16)
        ellfocutoffmod(decvalue)

        # LFO Wave
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_lfowave']],16)
        dpg.configure_item(item='el'+str(ELPASTE)+'_lfo_wave', default_value = decvalue)
        ellfowave(decvalue)

        # LFO Phase - KNOB
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_lfophase']],16)
        ellfophase(decvalue)

        # Filter1type
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_fl1type']],16)
        ELFILTER12 = str(int(ELPASTE)-1)+'0'
        dpg.configure_item(item='el'+str(ELPASTE)+'_filter1_type', default_value = decvalue)
        elfilter12type(decvalue)

        # Filter 1 Cutoff
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_fl1cutoff']],16)
        ELFILTER12 = str(int(ELPASTE)-1)+'0'
        dpg.configure_item(item='el'+str(ELPASTE)+'_filter1_cutoff', default_value = decvalue)
        elfilter12cutoff(decvalue)

        # Filter 1 mode
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_fl1mode']],16)
        ELFILTER12 = str(int(ELPASTE)-1)+'0'
        dpg.configure_item(item='el'+str(ELPASTE)+'_filter1_mode', default_value = decvalue)
        elfilter12mode(decvalue)

        # Filter 1 env
        ELFILTER12 = str(int(ELPASTE)-1)+'0'
        for n in filterenvlist:
            a = 'el'+str(ELPASTE)+'_filter1_env_'+n
            b = int(datalist[e['P_el'+str(ELCOPY)+'_fl1env'+n]],16)
            if 'L' in n:
                b=b-64
            dpg.configure_item(item=a,default_value = b)
            elfilter12envelope(a)

        # Filter 1 env rate scale
        ELFILTER12 = str(int(ELPASTE)-1)+'0'
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_fl1envertscl']],16)
        if decvalue>7:
            decvalue = 8-decvalue
        dpg.configure_item(item='el'+str(ELPASTE)+'_filter1_env_rate_scale', default_value = decvalue)
        elfilter12envratescale(decvalue)

        # Filter 1 env Breakpoints
        ELFILTER12 = str(int(ELPASTE)-1)+'0'
        for n in range(4,0,-1):
            ELBP = n
            param = int(datalist[e['P_el'+str(ELCOPY)+'_fl1envBP'+str(n)]],16)
            dpg.configure_item(item='el'+str(ELPASTE)+'_filter1_env_bp'+str(n), default_value = notelist[param])
            elfilter12envbp(param)

        # Filter 1 breakpoints scale Offset 
        ELFILTER12 = str(int(ELPASTE)-1)+'0'
        for n in range(1,5):
            bit1 = int(datalist[e['P_el'+str(ELCOPY)+'_fl1envOff'+str(n)+'b1']],16)
            bit2 = int(datalist[e['P_el'+str(ELCOPY)+'_fl1envOff'+str(n)+'b2']],16)
            if bit1 == 0:
                decvalue = bit2 - 128
            else:
                decvalue = bit2
            dpg.configure_item(item='el'+str(ELPASTE)+'_filter1_env_sc_off_'+str(n), default_value = decvalue)
            elfilter12envscoff('el'+str(ELPASTE)+'_filter1_env_sc_off_'+str(n))

        # Filter2type
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_fl2type']],16)
        ELFILTER12 = str(int(ELPASTE)+3)+'0'
        dpg.configure_item(item='el'+str(ELPASTE)+'_filter2_type', default_value = decvalue)
        elfilter12type(decvalue)

        # Filter 2 Cutoff
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_fl2cutoff']],16)
        ELFILTER12 = str(int(ELPASTE)+3)+'0'
        dpg.configure_item(item='el'+str(ELPASTE)+'_filter2_cutoff', default_value = decvalue)
        elfilter12cutoff(decvalue)

        # Filter 2 mode
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_fl2mode']],16)
        ELFILTER12 = str(int(ELPASTE)+3)+'0'
        dpg.configure_item(item='el'+str(ELPASTE)+'_filter2_mode', default_value = decvalue)
        elfilter12mode(decvalue)

        # Filter 2 env
        ELFILTER12 = str(int(ELPASTE)+3)+'0'
        for n in filterenvlist:
            a = 'el'+str(ELPASTE)+'_filter2_env_'+n
            b = int(datalist[e['P_el'+str(ELCOPY)+'_fl2env'+n]],16)
            if 'L' in n:
                b=b-64
            dpg.configure_item(item=a,default_value = b)
            elfilter12envelope(a)

        # Filter 2 env rate scale
        ELFILTER12 = str(int(ELPASTE)+3)+'0'
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'_fl2envertscl']],16)
        if decvalue>7:
            decvalue = 8-decvalue
        dpg.configure_item(item='el'+str(ELPASTE)+'_filter2_env_rate_scale', default_value = decvalue)
        elfilter12envratescale(decvalue)

        # Filter 2 env Breakpoints
        ELFILTER12 = str(int(ELPASTE)+3)+'0'
        for n in range(4,0,-1):
            ELBP = n
            param = int(datalist[e['P_el'+str(ELCOPY)+'_fl2envBP'+str(n)]],16)
            dpg.configure_item(item='el'+str(ELPASTE)+'_filter2_env_bp'+str(n), default_value = notelist[param])
            elfilter12envbp(param)

        # Filter 1 breakpoints scale Offset 
        ELFILTER12 = str(int(ELPASTE)+3)+'0'
        for n in range(1,5):
            bit1 = int(datalist[e['P_el'+str(ELCOPY)+'_fl2envOff'+str(n)+'b1']],16)
            bit2 = int(datalist[e['P_el'+str(ELCOPY)+'_fl2envOff'+str(n)+'b2']],16)
            if bit1 == 0:
                decvalue = bit2 - 128
            else:
                decvalue = bit2
            dpg.configure_item(item='el'+str(ELPASTE)+'_filter2_env_sc_off_'+str(n), default_value = decvalue)
            elfilter12envscoff('el'+str(ELPASTE)+'_filter2_env_sc_off_'+str(n))

        # Filter resonance:
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'flres']],16)
        dpg.configure_item(item='el'+str(ELPASTE)+'_filter1_reso', default_value = decvalue)
        elfilter12reso('el'+str(ELPASTE)+'_filter1_reso')

        # Filter vel sens: - KNOB
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'flvelsens']],16)
        elfiltervelsens(decvalue)

        # Filter mod sens: - KNOB 
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'flmodsens']],16)
        elfiltermodsens(decvalue)

        # Amp Env mode:
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'ampenvmode']],16)
        dpg.configure_item(item='el'+str(ELPASTE)+'_amp_env_mode', default_value = decvalue)
        elampenvmode('el'+str(ELPASTE)+'_amp_env_mode')

        # Amp Envelope:
        for n in ampenvlist:
            a = 'el'+str(ELPASTE)+'_amp_env_'+n
            b = int(datalist[e['P_el'+str(ELCOPY)+'ampenv'+n]],16)
            dpg.configure_item(item=a,default_value = b)
            elampenvelope(a)

        # Amp env rate scale
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'ampenvrtscl']],16)
        if decvalue>7:
            decvalue = 8-decvalue
        dpg.configure_item(item='el'+str(ELPASTE)+'_amp_env_rate_scale', default_value = decvalue)
        ampenvratescale('el'+str(ELPASTE)+'_amp_env_rate_scale')

        # Amp env Breakpoints
        for n in range(4,0,-1):
            ELBP = n
            param = int(datalist[e['P_el'+str(ELCOPY)+'ampenvBP'+str(n)]],16)
            dpg.configure_item(item='el'+str(ELPASTE)+'_amp_env_bp'+str(n), default_value = notelist[param])
            elampenvbp(param)

        # Amp breakpoints scale Offset 
        for n in range(1,5):
            bit1 = int(datalist[e['P_el'+str(ELCOPY)+'ampenvOff'+str(n)+'b1']],16)
            bit2 = int(datalist[e['P_el'+str(ELCOPY)+'ampenvOff'+str(n)+'b2']],16)
            if bit1 == 0:
                decvalue = bit2 - 128
            else:
                decvalue = bit2
            dpg.configure_item(item='el'+str(ELPASTE)+'_amp_env_sc_off_'+str(n), default_value = decvalue)
            elampenvscoff('el'+str(ELPASTE)+'_amp_env_sc_off_'+str(n))

        # Amp vel sens: - KNOB
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'velsens']],16)
        elampvelsens(decvalue)

        # Amp vel rate sens: 
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'velratesens']],16)
        dpg.configure_item(item='el'+str(ELPASTE)+'_amp_sens_vel_rate', default_value = 1-decvalue)       
        elsensvelrate('el'+str(ELPASTE)+'_amp_sens_vel_rate')

        # Amp mod sens: - KNOB
        decvalue = int(datalist[e['P_el'+str(ELCOPY)+'ampmodsens']],16)
        elampmodsens(decvalue)

    requestok = 0
    NoWriteRequest = 0
    loading = 0

def pastedrumpatch():
    global requestok, NoWriteRequest,datalist, nosend, loading
    requestok = 1   
    nosend = 0   
    ############################## COMMON
    # Voice Name
    name = ''
    for i in range(32,42):
        name = name+(bytearray.fromhex(datalist[i]).decode())
    dpg.configure_item(item='voice_name', default_value = name)
    voicename('voice_name')

    nosend =1
    # Efx Type 
    dpg.configure_item(item='effect_type', default_value = effectslist[int(datalist[42],16)-1])
    effecttype('effect_type')
    nosend =0

    # Efx Param 1,2,3
    dpg.configure_item(item='param1_value', default_value = int(datalist[44],16))
    dpg.configure_item(item='param2_value', default_value = int(datalist[45],16))
    dpg.configure_item(item='param3_value', default_value = int(datalist[46],16))
    effectparam1('param1_value')
    effectparam2('param2_value')
    effectparam3('param3_value')

    # Efx output level
    dpg.configure_item(item='effect_level', default_value = int(datalist[43],16))
    effectlevel('effect_level')

    # Voice Volume
    dpg.configure_item(item='voice_volume', default_value = int(datalist[65],16)) 
    voicevolume('voice_volume')

    ############################## CONTROLLERS
    # Voice Volume
    dpg.configure_item(item='volume_cc', default_value =  controllerlist[int(datalist[61],16)]) 
    volumecc('volume_cc')
    dpg.configure_item(item='vol_min_rng', default_value = int(datalist[62],16)) 
    volumerngmin('vol_min_rng')

    ############################## ELEMENTS
    notewave = [71,80,89,98,107,116,125,134,143,152,161,170,179,188,197,206,215,224,233,242,251,260,269,278,287,296,305,314,323,332,341,350,359,368,377,386,395,404,413,422,431,440,449,458,467,476,485,494,503,512,521,530,539,548,557,566,575,584,593,602,611]
    notevol = [72,81,90,99,108,117,126,135,144,153,162,171,180,189,198,207,216,225,234,243,252,261,270,279,288,297,306,315,324,333,342,351,360,369,378,387,396,405,414,423,432,441,450,459,468,477,486,495,504,513,522,531,540,549,558,567,576,585,594,603,612]
    noteshift = [74,83,92,101,110,119,128,137,146,155,164,173,182,191,200,209,218,227,236,245,254,263,272,281,290,299,308,317,326,335,344,353,362,371,380,389,398,407,416,425,434,443,452,461,470,479,488,497,506,515,524,533,542,551,560,569,578,587,596,605,614]
    notetune = [73,82,91,100,109,118,127,136,145,154,163,172,181,190,199,208,217,226,235,244,253,262,271,280,289,298,307,316,325,334,343,352,361,370,379,388,397,406,415,424,433,442,451,460,469,478,487,496,505,514,523,532,541,550,559,568,577,586,595,604,613]
    notealtgr = [68,77,86,95,104,113,122,131,140,149,158,167,176,185,194,203,212,221,230,239,248,257,266,275,284,293,302,311,320,329,338,347,356,365,374,383,392,401,410,419,428,437,446,455,464,473,482,491,500,509,518,527,536,545,554,563,572,581,590,599,608]
    notepan = [75,84,93,102,111,120,129,138,147,156,165,174,183,192,201,210,219,228,237,246,255,264,273,282,291,300,309,318,327,336,345,354,363,372,381,390,399,408,417,426,435,444,453,462,471,480,489,498,507,516,525,534,543,552,561,570,579,588,597,606,615]
    noteefxbal = [76,85,94,103,112,121,130,139,148,157,166,175,184,193,202,211,220,229,238,247,256,265,274 ,283,292,301,310,319,328,337,346,355,364,373,382,391,400,409,418,427,436,445,454,463,472,481,490,499,508,517,526,535,544,553,562,571,580,589,598,607,616]
    
    # Note waveform
    for i in range(61):
        dpg.configure_item(item='drums_Waveform'+str(i), default_value = drumvoicelist[int(datalist[notewave[i]],16)+1])
        drumwave('drums_Waveform'+str(i))

    # Note volume
    for i in range(61):
        dpg.configure_item(item='drums_Volume'+str(i), default_value = int(datalist[notevol[i]],16))
        drumvolume('drums_Volume'+str(i))

    # Note Shift
    for i in range(61):
        dpg.configure_item(item='drums_Noteshift'+str(i), default_value = int(datalist[noteshift[i]],16)-64)
        drumnoteshift('drums_Noteshift'+str(i))

    # Note tune
    for i in range(61):
        dpg.configure_item(item='drums_Tune'+str(i), default_value = int(datalist[notetune[i]],16)-64)
        drumtune('drums_Tune'+str(i))

    # Note Alt Group
    for i in range(61):
        dpg.configure_item(item='drums_Alt_Group'+str(i), default_value = int((int(datalist[notealtgr[i]],16)-32)/64))
        drumaltgroup('drums_Alt_Group'+str(i))

    # Note pan
    for i in range(61):
        dpg.configure_item(item='drums_Pan'+str(i), default_value = int(datalist[notepan[i]],16)-32)    
        drumpan('drums_Pan'+str(i))

    # Note efx balance
    for i in range(61):
        dpg.configure_item(item='drums_Efx_Balance'+str(i), default_value = int(datalist[noteefxbal[i]],16))  
        drumfxbal('drums_Efx_Balance'+str(i))
    
    loading = 0
    requestok = 0

def initializeelement():
    dpg.configure_item('elconfirminitialize', show=True) 
    
def initializeelementok():
    global datalist, ELCOPY, ELPASTE, elnumber, copyel, EL
    copyel = 0
    # update midi prefs
    checkmidiprefs()
    # UPDATE DATALIST
    requestvoice()
    # detecto drums
    if datalist[4] == '64':
        elnumber = 0
    else:
    # SALVO NUMERO DE ELEMENTOS
        if datalist[31] == '05':
            elnumber = 1
        if datalist[31] == '06':
            elnumber = 2
        if datalist[31] == '07':
            elnumber = 4
    # SAVE ELEMENT PASTE
    for i in range(4):
        if dpg.get_value(item='el'+str(i+1)+'_tab') == True:
            ELPASTE = i+1
            EL = 'el'+str(ELPASTE)
            break
    # SET 4 ELEMENTS
    PARAM = '02 00 00 00 00 '
    VALUE = '07' # 4 el
    MESSAGE = INI + PARAM + VALUE + END
    sendmessage(MESSAGE)
    # LOAD DATALIST
    datalist = []
    dpg.configure_item('elconfirminitialize', show=False) 
    f = open('files/initvoice', 'r')
    datalist = json.load(f)
    f.close()
    # PASTE
    ELCOPY = 1
    pasteelement()

############################# MIDI #############################
def selectmidiin(sender):
    global inport, indevicelist
    try:
        inport.close()
    except:
        pass
    for i in indevicelist:
        dpg.set_item_label('i'+i, i)
    for i in indevicelist:
        if i == sender[1:]:
            dpg.set_item_label(sender, '*** ' + i + ' ***')
            inport = mido.open_input(i)
            break
    f = open(prefdir, 'r')
    data = f.readlines()
    f = open(prefdir, 'w')
    data[0] = i+'\n'
    f.writelines(data)
    f.close()
    
def selectmidiout(sender):
    global outport
    try:
        outport.close()
    except:
        pass
    for i in outdevicelist:
        dpg.set_item_label('o'+i, i)
    for i in outdevicelist:
        if i == sender[1:]:
            dpg.set_item_label(sender, '*** ' + i + ' ***')
            outport = mido.open_output(i)
            break
    f = open(prefdir, 'r')
    data = f.readlines()
    f = open(prefdir, 'w')
    data[1] = i+'\n'
    f.writelines(data)
    f.close()

def setrequestonstart(sender):
    a = dpg.get_item_label(sender)
    if a == '  Request on start':
        dpg.set_item_label(sender,'* Request on start')
        f = open(prefdir, 'r')
        data = f.readlines()
        f = open(prefdir, 'w')
        data[2] = 'request on start\n'
        f.writelines(data)
        f.close()

    else:
        dpg.set_item_label(sender,'  Request on start')
        f = open(prefdir, 'r')
        data = f.readlines()
        f = open(prefdir, 'w')
        data[2] = 'NO request on start\n'
        f.writelines(data)
        f.close()

def resetmidiconfig():
    global indevicelist, outdevicelist
    # borro menus
    for i in indevicelist:
        dpg.delete_item('i'+i)
    for i in outdevicelist:
        dpg.delete_item('o'+i)

    # creo nueva lista
    indevicelist = mido.get_input_names()
    outdevicelist = mido.get_output_names()

    #Creo menus de nuevo
    for i in indevicelist:
        dpg.add_menu_item(tag = 'i'+i, label=i , callback= selectmidiin, parent = 'midi_in_menu')
    for i in outdevicelist:
        dpg.add_menu_item(tag = 'o'+i, label=i , callback= selectmidiout, parent = 'midi_out_menu')

def resetmididevice():
    try:
        # Leo el interface de nuevo, por si se ha encendido el sinte despues de seleccionar el midi.
        checkmidiprefs()
    except:
        # Si no lo detecta, reseteo la config midi.
        dpg.configure_item('prefsio_error', show=True)
        resetmidiconfig()

######################################################### OTHER ACTIONS ########################################################
def changemode(): # 1,2,4 elements / drums
    if elnumber == 0:
        dpg.configure_item('drums_tab', show=True)
        dpg.configure_item('el1_tab', show=False)
        dpg.configure_item('el2_tab', show=False)
        dpg.configure_item('el3_tab', show=False)
        dpg.configure_item('el4_tab', show=False)

        dpg.configure_item('elementcopymenu',enabled = False)
        dpg.configure_item('elementpastemenu',enabled = False)
        dpg.configure_item('elementinimenu',enabled = False)

        #common
        dpg.configure_item('voicemodetext', color = (50,50,50))
        dpg.configure_item('voice_mode',enabled = False)
        dpg.configure_item('pitchbendrangetext', color = (50,50,50))
        dpg.configure_item('pitch_bend_range',enabled = False)
        dpg.configure_item('aftertouchpitchbiastext', color = (50,50,50))
        dpg.configure_item('aftertouch_pitch_bias',enabled = False)
        dpg.configure_item('randompitchrangetext', color = (50,50,50))
        dpg.configure_item('random_pitch_range',enabled = False)

        #controllers
        dpg.configure_item('pitchmodcctext', color = (50,50,50))
        dpg.configure_item('pitch_mod_cc',enabled = False)
        dpg.configure_item('pitchmodrngtext', color = (50,50,50))
        dpg.configure_item('pitch_mod_rng',enabled = False)
        dpg.configure_item('cutoffmodcctext', color = (50,50,50))
        dpg.configure_item('cutoff_mod_cc',enabled = False)
        dpg.configure_item('cutoffmodrngtext', color = (50,50,50))
        dpg.configure_item('cutoff_mod_rng',enabled = False)
        dpg.configure_item('cutofffreqcctext', color = (50,50,50))
        dpg.configure_item('cutoff_freq_cc',enabled = False)
        dpg.configure_item('cutofffreqrngtext', color = (50,50,50))
        dpg.configure_item('cutoff_freq_rng',enabled = False)  
        dpg.configure_item('envgenbiascctext', color = (50,50,50))
        dpg.configure_item('env_gen_bias_cc',enabled = False)
        dpg.configure_item('envgenbiasrngtext', color = (50,50,50))
        dpg.configure_item('env_gen_rng',enabled = False)
        dpg.configure_item('ampmodcctext', color = (50,50,50))
        dpg.configure_item('amp_mod_cc',enabled = False)
        dpg.configure_item('ampmodrngtext', color = (50,50,50))
        dpg.configure_item('amp_mod_rng',enabled = False)


    else:          
        dpg.configure_item(item='el1_tab', show = True)      
        if elnumber == 1:
            dpg.configure_item(item='el2_tab', show = False)
            dpg.configure_item(item='el3_tab', show = False)
            dpg.configure_item(item='el4_tab', show = False)
        if elnumber == 2:
            dpg.configure_item(item='el2_tab', show = True)
            dpg.configure_item(item='el3_tab', show = False)
            dpg.configure_item(item='el4_tab', show = False)
        if elnumber == 4:
            dpg.configure_item(item='el2_tab', show = True)
            dpg.configure_item(item='el3_tab', show = True)
            dpg.configure_item(item='el4_tab', show = True)

        dpg.configure_item('drums_tab', show=False)
        dpg.configure_item('elementcopymenu',enabled = True)
        dpg.configure_item('elementpastemenu',enabled = True)
        dpg.configure_item('elementinimenu',enabled = True)

        #common
        dpg.configure_item('voicemodetext', color = (255,255,255))
        dpg.configure_item('voice_mode',enabled = True)
        dpg.configure_item('pitchbendrangetext', color = (255,255,255))
        dpg.configure_item('pitch_bend_range',enabled = True)
        dpg.configure_item('aftertouchpitchbiastext', color = (255,255,255))
        dpg.configure_item('aftertouch_pitch_bias',enabled = True)
        dpg.configure_item('randompitchrangetext', color = (255,255,255))
        dpg.configure_item('random_pitch_range',enabled = True)

        #controllers
        dpg.configure_item('pitchmodcctext', color = (255,255,255))
        dpg.configure_item('pitch_mod_cc',enabled = True)
        dpg.configure_item('pitchmodrngtext', color = (255,255,255))
        dpg.configure_item('pitch_mod_rng',enabled = True)
        dpg.configure_item('cutoffmodcctext', color = (255,255,255))
        dpg.configure_item('cutoff_mod_cc',enabled = True)
        dpg.configure_item('cutoffmodrngtext', color = (255,255,255))
        dpg.configure_item('cutoff_mod_rng',enabled = True)
        dpg.configure_item('cutofffreqcctext', color = (255,255,255))
        dpg.configure_item('cutoff_freq_cc',enabled = True)
        dpg.configure_item('cutofffreqrngtext', color = (255,255,255))
        dpg.configure_item('cutoff_freq_rng',enabled = True)  
        dpg.configure_item('envgenbiascctext', color = (255,255,255))
        dpg.configure_item('env_gen_bias_cc',enabled = True)
        dpg.configure_item('envgenbiasrngtext', color = (255,255,255))
        dpg.configure_item('env_gen_rng',enabled = True)
        dpg.configure_item('ampmodcctext', color = (255,255,255))
        dpg.configure_item('amp_mod_cc',enabled = True)
        dpg.configure_item('ampmodrngtext', color = (255,255,255))
        dpg.configure_item('amp_mod_rng',enabled = True)

def sendmessage(MESSAGE):
    if outport == '':
            dpg.configure_item('interface_error', show=True)
            return
    msg1 = mido.Message.from_hex(MESSAGE)
    outport.send(msg1)

####################################################### CREATE INTERFACE #######################################################
dpg.create_context()
dpg.create_viewport(title='SY-55 Editor',x_pos = (150), width=1200, height=830, disable_close = True, resizable = False)
dpg.set_exit_callback(exitprogram)

########################################################## CREATE IMAGES #######################################################
for i in imageslist:
    width, height, channels, data = dpg.load_image('files/'+i+'.png')
    with dpg.texture_registry(show=False):
        dpg.add_static_texture(width=width, height=height, default_value=data, tag=i)

############################################################-------------#######################################################
############################################################ MAIN WINDOW #######################################################
############################################################-------------#######################################################
with dpg.window(tag='Primary Window', on_close = exitprogram):   
    dpg.draw_image('LOGO', (810, 14), (810 + 320, 14 + 106))
    ###################################################### ITEM HANDLERS ########################################################
    with dpg.handler_registry():
        dpg.add_mouse_click_handler(callback=mouseclickCallback)
        dpg.add_mouse_down_handler(callback=mousedownCallback)
        dpg.add_mouse_release_handler(callback=mousereleaseCallback)
        dpg.add_key_down_handler(callback=keydownCallback)
        dpg.add_key_release_handler(callback=keyreleaseCallback)
        
    ########################################################## MENU BAR #########################################################
    with dpg.menu_bar():
        with dpg.menu(label='File'):
            dpg.add_menu_item(label = 'Load', callback= loadpatch)
            dpg.add_menu_item(label = 'Save', callback= savepatch,)
            dpg.add_menu_item(label = 'Quit', callback= exitprogram)
        with dpg.menu(label = 'Patch'):
            dpg.add_menu_item(label='Request current patch', callback = requestvoice)
            dpg.add_menu_item(label='  Request on start', tag = 'reqonstart',callback = setrequestonstart)
            dpg.add_menu_item(label='Initialize Patch', tag = 'inipatchmenu', callback = initializepatch)
        with dpg.menu(label = 'Element'):
            dpg.add_menu_item(label='Copy', tag = 'elementcopymenu', callback = copyelement, )
            dpg.add_menu_item(label='Paste', tag = 'elementpastemenu', callback = pasteelement)
            dpg.add_menu_item(label='Initialize', tag = 'elementinimenu',callback = initializeelement)
        with dpg.menu(label='Midi'):
            dpg.add_menu_item(label='Reset Midi Configuration', callback = resetmidiconfig)
            dpg.add_menu_item(label='Reset Midi Device', callback = resetmididevice)
            with dpg.menu(label='Midi Input Device', tag = 'midi_in_menu'):
                for i in indevicelist:
                    dpg.add_menu_item(tag = 'i'+i, label=i , callback= selectmidiin)
            with dpg.menu(label='Midi Output Device', tag = 'midi_out_menu'):
                for i in outdevicelist:
                    dpg.add_menu_item(tag = 'o'+i, label=i , callback= selectmidiout)
        with dpg.menu(label='Help'):
            dpg.add_menu_item(label='Manual', callback = lambda: dpg.configure_item('manual', show=True))
            
    
    ################################################## VOICE COMMON CONTROL ####################################################
    with dpg.window(label = 'common window',no_title_bar = True,no_resize = True, no_move = True, pos = (0,20), height = 130, width = 800,no_background=True,no_scrollbar = True):
        dpg.add_text('Voice Name:', pos = (12,9))
        dpg.add_input_text(label='', tag = 'voice_name', width = 130,callback = voicename, on_enter = True, pos = (12,29))
        dpg.add_text('Voice Volume:', pos = (12,59))
        dpg.add_slider_int(no_input = True,tag = 'voice_volume', label='', width=130, max_value=127, callback= voicevolume, pos = (12,79),)
        dpg.add_text('Voice Mode:', tag='voicemodetext', pos = (170,9))
        dpg.add_combo(tag = 'voice_mode', label = '', width = 130, items = ('1 Element','2 Elements','4 Elements'),callback= voicemode, pos = (170,29))
        dpg.add_text('Pitch Bend Range:', tag = 'pitchbendrangetext', pos = (170,59))
        dpg.add_slider_int(no_input = True,tag = 'pitch_bend_range', label='', width=130, max_value=12, callback= pitchbendrange, pos = (170,79))
        dpg.add_text('Aftertouch Pitch Bias:', tag = 'aftertouchpitchbiastext', pos = (328,9))
        dpg.add_slider_int(no_input = True,tag = 'aftertouch_pitch_bias', label='', width=130, min_value=-12, max_value=12, callback= aftertouchpitchbias, pos = (328,29))
        dpg.add_text('Random Pitch Range:', tag = 'randompitchrangetext', pos = (328,59))
        dpg.add_slider_int(no_input = True,tag = 'random_pitch_range', label='', width=130, max_value=7, callback= randompitchrange, pos = (328,79))
        dpg.add_text('Effect Type:', pos = (486,9))
        dpg.add_combo(tag = 'effect_type', label = '', width = 130, items = effectslist,callback= effecttype, pos = (486,29), height_mode = 2,)
        dpg.add_text('Effect Level', pos = (486,59) )
        dpg.add_slider_int(no_input = True,tag = 'effect_level', label='', width=130, max_value=100, pos = (486,79), callback= effectlevel)

        dpg.add_text('Effect Param. 1:',tag = 'Param1_title',  pos = (644,9))
        dpg.add_slider_int(no_input = True,tag = 'param1_slider',  label='', width=130, pos = (644,29), height = 90,callback = effectparam1,format= f'')
        dpg.add_text('0', tag = 'param1_value',  pos = (707,29))

        dpg.add_text('Effect Param. 2:',tag = 'Param2_title',  pos = (644,49))
        dpg.add_slider_int(no_input = True,tag = 'param2_slider',  label='', width=130, pos = (644,69), height = 90,callback = effectparam2,format= f'')
        dpg.add_text('0', tag = 'param2_value',  pos = (707,69))

        dpg.add_text('Effect Param. 3:',tag = 'Param3_title',  pos = (644,89))
        dpg.add_slider_int(no_input = True,tag = 'param3_slider',  label='', width=130, pos = (644,109), height = 90,callback = effectparam3,format= f'')
        dpg.add_text('0', tag = 'param3_value',  pos = (707,109))   

    ############################################################ TABS ###########################################################
    with dpg.window(label = 'tabs window',no_title_bar = True,no_resize = True, no_move = True, pos = (0,140), height = 1000, width = 1200 ,no_background=True,no_scrollbar = True):
        with dpg.tab_bar(tag = 'tabs', show = True):

            ################################################### ELEMENT 1 #######################################################
            with dpg.tab(label=' ELEMENT 1 ',tag = 'el1_tab'):
                dpg.add_slider_int(no_input = True,tag = 'el1_volume', label='', vertical = True, height=130, max_value=127, callback= elementvol, pos = (24,45))
                dpg.add_text('Vol', pos = (24,175))
                dpg.add_text('Element 1\nEnable', pos = (63,43))
                dpg.add_checkbox(tag = 'el1_enable', label = '', callback = elementenable, pos = (63,78))
                dpg.set_value('el1_enable', True)
                dpg.add_text('On | Off', pos = (89,78), color =(0,150,0))
                dpg.add_image('REDLIGHT', pos = (66,81), width = 14,height = 14, tag = 'el1_enabled', show = True)
                dpg.add_text('Pan', pos = (panknobx+13,panknoby+47))
                dpg.add_image_button('KNOB',tag = 'el1_pan_knob',pos = (panknobx,panknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el1_pan_dot',pos = (panknobx+20,panknoby+5),width = 8, height = 8)
                dpg.add_text('0', tag = 'el1_pan_value',  pos = (panknobx+20,panknoby-20))  
                dpg.add_text('Wave Select:', pos = (153,50))
                dpg.add_combo(tag = 'el1_Waveform', label = '', width = 107, items = voicelist,callback= AWMwaveform, pos = (152,70), height_mode = 2)
                dpg.add_text('EF Balance', pos = (efbalknobx-10,efbalknoby+47))
                dpg.add_image_button('KNOB', tag = 'el1_efbal_knob',pos = (efbalknobx,efbalknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el1_efbal_dot',pos = (efbalknobx+13.3,efbalknoby+33.3),width = 8, height = 8)
                dpg.add_text('0', tag = 'el1_efbal_value',  pos = (efbalknobx+20,efbalknoby-20))  
                dpg.add_text('AEG\nRate Sens', pos = (281,43))
                dpg.add_slider_int(no_input = True,tag = 'el1_amp_sens_vel_rate', width=40, max_value=1, callback= elsensvelrate, pos = (281,78),format= f'') 
                dpg.add_text('On | Off', pos = (281+47, 78), color =(0,150,0))
                dpg.add_text('Amp Vel Sens', pos = (ampvelsensknobx-16,ampvelsensknoby+47))
                dpg.add_image_button('KNOB', tag = 'el1_ampvelsens_knob',pos = (ampvelsensknobx,ampvelsensknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el1_ampvelsens_dot',pos = (ampvelsensknobx+20,ampvelsensknoby+5),width = 8, height = 8)
                dpg.add_text('0', tag = 'el1_ampvelsens_value',  pos = (ampvelsensknobx+20,ampvelsensknoby-20))  
                dpg.add_text('Amp Mod Sens', pos = (ampmodsensknobx-16,ampmodsensknoby+47))
                dpg.add_image_button('KNOB', tag = 'el1_ampmodsens_knob',pos = (ampmodsensknobx,ampmodsensknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el1_ampmodsens_dot',pos = (ampmodsensknobx+20,ampmodsensknoby+5),width = 8, height = 8)
                dpg.add_text('0', tag = 'el1_ampmodsens_value',  pos = (ampmodsensknobx+20,ampmodsensknoby-20))  
                dpg.add_text('Amp Envelope',  pos = (700,175))  
                for i in range(len(ampenvlist)):
                    dpg.add_slider_int(no_input = True,tag = 'el1_amp_env_'+ampenvlist[i], vertical = True, height=130, max_value=63, default_value=0,callback= elampenvelope, pos = (390+i*25,45))
                    dpg.add_text(ampenvlist[i],tag = 'el1_ampenv'+str(i), pos = (393+i*25,178))
                dpg.add_text('AEG Rate Scale', pos = (582,43))
                dpg.add_slider_int(no_input = True,tag = 'el1_amp_env_rate_scale', label='', width=120, max_value=7, min_value = -7, callback= ampenvratescale, pos = (581,63))
                dpg.add_text('AEG mode', pos = (780,43))
                dpg.add_slider_int(no_input = True,tag = 'el1_amp_env_mode', width=40, max_value=1, default_value=0,callback= elampenvmode, pos = (780,63),format= f'')
                dpg.add_text('Norm | Hold', tag = 'el1_amp_env_mode_value',  pos = (780+47,63), color =(0,150,0))
                dpg.add_text('Amp Env Breakpoints', pos = (1000,43))
                dpg.add_text('Note', pos = (975,70), color =(0,150,0))
                dpg.add_text('Scale Offset', pos = (1070,70), color =(0,150,0))
                dpg.add_text('BP 1', pos = (924,88))
                dpg.add_combo(tag = 'el1_amp_env_bp1', width=60, items = notelist, callback= elampenvbp, pos = (960,88), height_mode = 2) 
                dpg.add_slider_int(no_input = True,tag = 'el1_amp_env_sc_off_1', label='', width=144, max_value=127, min_value=-127, callback= elampenvscoff, pos = (1036,88))
                dpg.add_text('BP 2', pos = (924,113))
                dpg.add_combo(tag = 'el1_amp_env_bp2', width=60, items = notelist, callback= elampenvbp, pos = (960,113), height_mode = 2) 
                dpg.add_slider_int(no_input = True,tag = 'el1_amp_env_sc_off_2', label='', width=144, max_value=127, min_value=-127, callback= elampenvscoff, pos = (1036,113))
                dpg.add_text('BP 3', pos = (924,138))
                dpg.add_combo(tag = 'el1_amp_env_bp3', width=60, items = notelist, callback= elampenvbp, pos = (960,138), height_mode = 2) 
                dpg.add_slider_int(no_input = True,tag = 'el1_amp_env_sc_off_3', label='', width=144, max_value=127, min_value=-127, callback= elampenvscoff, pos = (1036,138))
                dpg.add_text('BP 4', pos = (924,163))
                dpg.add_combo(tag = 'el1_amp_env_bp4', width=60, items = notelist, callback= elampenvbp, pos = (960,163), height_mode = 2) 
                dpg.add_slider_int(no_input = True,tag = 'el1_amp_env_sc_off_4', label='', width=144, max_value=127, min_value=-127, callback= elampenvscoff, pos = (1036,163))
                dpg.add_text('Note shift', pos = (noteshiftknobx-2,noteshiftknoby+46))
                dpg.add_image_button('KNOB', tag = 'el1_noteshift_knob',pos = (noteshiftknobx,noteshiftknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el1_noteshift_dot',pos = (noteshiftknobx+20,noteshiftknoby+5),width = 8, height = 8)
                dpg.add_text('0', tag = 'el1_noteshift_value',  pos = (noteshiftknobx+20,noteshiftknoby-20))  
                dpg.add_text('Detune', pos = (detuneknobx+4,detuneknoby+46))
                dpg.add_image_button('KNOB', tag = 'el1_detune_knob',pos = (detuneknobx,detuneknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el1_detune_dot',pos = (detuneknobx+20,detuneknoby+5),width = 8, height = 8)
                dpg.add_text('0', tag = 'el1_detune_value',  pos = (detuneknobx+20,detuneknoby-20))
                dpg.add_text('OSC Frq Mode', pos = (20,228))
                dpg.add_slider_int(no_input = True,tag = 'el1_osc_freq_mode', width=40, max_value=1, callback= eloscfreqmode, pos = (20,248),format= f'') 
                dpg.add_text('Norm | Fix', pos = (20+47, 248), color =(0,150,0))
                dpg.add_text('OSC Frq Note', pos = (20,310))
                dpg.add_combo(tag = 'el1_osc_freq_note', label='', width=105, items = notelist, callback= eloscfreqnote, pos = (20,330), height_mode = 2, enabled = False) 
                dpg.add_text('OSC Frq Tune', pos = (oscfreqtuneknobx-16,oscfreqtuneknoby+46))
                dpg.add_image_button('KNOB', tag = 'el1_oscfreqtune_knob',pos = (oscfreqtuneknobx,oscfreqtuneknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el1_oscfreqtune_dot',pos = (oscfreqtuneknobx+20,oscfreqtuneknoby+5),width = 8, height = 8)
                dpg.add_text('0', tag = 'el1_oscfreqtune_value',  pos = (oscfreqtuneknobx+20,oscfreqtuneknoby-20))
                dpg.add_text('Pitch Mod Sens', pos = (pitchmodsensknobx-19,pitchmodsensknoby+46))
                dpg.add_image_button('KNOB', tag = 'el1_pitchmodsens_knob',pos = (pitchmodsensknobx,pitchmodsensknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el1_pitchmodsens_dot',pos = (pitchmodsensknobx+13.3,pitchmodsensknoby+33.3),width = 8, height = 8)
                dpg.add_text('0', tag = 'el1_pitchmodsens_value',  pos = (pitchmodsensknobx+20,pitchmodsensknoby-20), color =(0,0,0,0))
                dpg.add_text('0', tag = 'el1_pitchmodsens_valuex',  pos = (pitchmodsensknobx+20,pitchmodsensknoby-20))
                dpg.add_text('Pitch Envelope',  pos = (700,356))  
                for i in range(len(pitchenvlist)):
                    if 'L' in pitchenvlist[i]:
                        dpg.add_slider_int(no_input = True,tag = 'el1_pitch_env_'+pitchenvlist[i], vertical = True, height=130, max_value=63, min_value =-64, default_value=0,callback= elpitchenvelope, pos = (339+i*25,226))
                    else:
                        dpg.add_slider_int(no_input = True,tag = 'el1_pitch_env_'+pitchenvlist[i], vertical = True, height=130, max_value=63, default_value=0,callback= elpitchenvelope, pos = (339+i*25,226))
                    dpg.add_text(pitchenvlist[i],tag = 'el1_pitchenv'+str(i), pos = (343+i*25,359))
                dpg.add_text('PEG Range', pos = (582,224))
                dpg.add_slider_int(no_input = True,tag = 'el1_pitch_env_range', label='', width=60, max_value=2, callback= elpitchenvrange, pos = (581,244),format= f'')
                dpg.add_text('1/2oct', tag = 'el1_pitch_env_range_value', pos = (646,244), color =(0,150,0))
                dpg.add_text('PEG Rate Scale', pos = (693,224))
                dpg.add_slider_int(no_input = True,tag = 'el1_pitch_env_rate_scale', label='', width=110, max_value=7, min_value = -7, callback= elpitchenvratescale, pos = (692,244))
                dpg.add_text('PEG Vel SW', pos = (816,224))
                dpg.add_slider_int(no_input = True,tag = 'el1_pitch_env_vel_sw', width=40, max_value=1, default_value=0,callback= elpitchenvvelsw, pos = (816,244),format= f'')
                dpg.add_text('On | Off', tag = 'el1_pitch_env_vel_sw_value',  pos = (816+47,244), color =(0,150,0))

                ######### DRAWING
                with dpg.drawlist(width=1600, height=342):
                    linecolor = (60,70,65)

                    #### AMP ENVELOPE LINES
                    dpg.draw_rectangle((AmpHini-5,AmpVini-5),(AmpHini+(5*VHSum)+5,AmpVini+VHSum+5), color=(50,50,50,255), thickness=2, fill = (100,120,0,255))
                    dpg.draw_line((AmpHini,AmpVini+VHSum),(AmpHini+VHSum,AmpVini),tag = 'el1_amp_R1', color=linecolor, thickness=2)
                    dpg.draw_line((AmpHini+VHSum,AmpVini),(AmpHini+(2*VHSum),AmpVini+VHSum),tag = 'el1_amp_R2', color=linecolor, thickness=2)
                    dpg.draw_line((AmpHini+(2*VHSum),AmpVini+VHSum),(AmpHini+(3*VHSum),AmpVini+VHSum),tag = 'el1_amp_R3', color=linecolor, thickness=2)
                    dpg.draw_line((AmpHini+(3*VHSum),AmpVini+VHSum),(AmpHini+(4*VHSum),AmpVini+VHSum),tag = 'el1_amp_R4', color=linecolor, thickness=2)
                    dpg.draw_line((AmpHini+(4*VHSum),AmpVini+VHSum),(AmpHini+(5*VHSum),AmpVini+VHSum),tag = 'el1_amp_RR', color=linecolor, thickness=2)
                    for i in range(AmpVini,AmpVini+VHSum,8):
                        dpg.draw_line((AmpHini+(4*VHSum),i),(AmpHini+(4*VHSum),i+4),tag = 'el1_amp_RE'+str(i), color=(80,80,80), thickness=1)

                    #### PITCH ENVELOPE LINES
                    dpg.draw_rectangle((PitchHini-5,PitchVini-5),(PitchHini+(5*VHSum)+5,PitchVini+VHSum+5), color=(50,50,50,255), thickness=2, fill = (100,120,0,255))
                    dpg.draw_line((PitchHini,PitchVini+VHSum/2),(PitchHini+VHSum,PitchVini+VHSum/2),tag = 'el1_pitch_R1', color=linecolor, thickness=2)
                    dpg.draw_line((PitchHini+VHSum,PitchVini+VHSum/2),(PitchHini+(2*VHSum),PitchVini+VHSum/2),tag = 'el1_pitch_R2', color=linecolor, thickness=2)
                    dpg.draw_line((PitchHini+(2*VHSum),PitchVini+VHSum/2),(PitchHini+(3*VHSum),PitchVini+VHSum/2),tag = 'el1_pitch_R3', color=linecolor, thickness=2)
                    dpg.draw_line((PitchHini+(3*VHSum),PitchVini+VHSum/2),(PitchHini+(4*VHSum),PitchVini+VHSum/2),tag = 'el1_pitch_RR', color=linecolor, thickness=2)
                    for i in range(PitchVini,PitchVini+VHSum,8):
                        dpg.draw_line((PitchHini+(3*VHSum),i),(PitchHini+(3*VHSum),i+4),tag = 'el1_pitch_RE'+str(i), color=(80,80,80), thickness=1)

                    #### ELEMENT LINES
                    dpg.draw_line((0,170),(1600,170), thickness=1, color = (60,60,60,255))

                    ########## FILTER TABS
                with dpg.tab_bar(show = True):
                    with dpg.tab(label='FILTER 1', tag = 'el1_FILTER1',show = True):
                        dpg.add_text('Cutoff', pos = (24-8,419+131))
                        dpg.add_slider_int(no_input = True,tag = 'el1_filter1_cutoff', height=130, vertical = True, max_value=127, default_value=0,callback= elfilter12cutoff, pos = (24,419))
                        dpg.add_text('Filter type', pos = (77,415))
                        dpg.add_slider_int(no_input = True,tag = 'el1_filter1_type', width=60, max_value=2, default_value=1,callback= elfilter12type, pos = (77,415+20),format= f'') 
                        dpg.add_text('LPF', tag = 'el1_filter1_type_value',  pos = (77,435+20), color =(0,150,0))   
                        dpg.add_image('LPF', pos = (77+30,435+23), width = 30,height = 13, tag = 'el1_LPF1_img', show = True)
                        dpg.add_image('HPF', pos = (77+30,435+23), width = 30,height = 13, tag = 'el1_HPF1_img', show = False)
                        dpg.add_image('NOFILTER', pos = (77+30,435+23), width = 30,height = 13, tag = 'el1_NOFILTER1_img', show = False)
                        dpg.add_text('Filter mode', pos = (77,35+460))
                        dpg.add_slider_int(no_input = True,tag = 'el1_filter1_mode', width=60, max_value=2, default_value=0,callback= elfilter12mode, pos = (77,35+480),format= f'')
                        dpg.add_text('  EG', tag = 'el1_filter1_mode_value',  pos = (77+13,35+500), color =(0,150,0)) 
                        dpg.add_text('FEG Rate Scale', pos = (520,418))
                        dpg.add_slider_int(no_input = True,tag = 'el1_filter1_env_rate_scale', label='', width=110, max_value=7, min_value = -7, callback= elfilter12envratescale, pos = (519,438))
                        dpg.add_text('Filter Envelope',  pos = (670,550))  
                        for i in range(len(filterenvlist)):
                            if 'L' in filterenvlist[i]:
                                dpg.add_slider_int(no_input = True,tag = 'el1_filter1_env_'+filterenvlist[i], vertical = True, height=130, max_value=63, min_value =-64, default_value=0,callback= elfilter12envelope, pos = (170+i*25,420))
                            else:
                                dpg.add_slider_int(no_input = True,tag = 'el1_filter1_env_'+filterenvlist[i], vertical = True, height=130, max_value=63, default_value=0,callback= elfilter12envelope, pos = (170+i*25,420))
                            dpg.add_text(filterenvlist[i],tag = 'el1_filter1env'+str(i),pos = ((183+i*25)-int(4*len(filterenvlist[i])),420+134))
                        dpg.add_text('Filter Env Breakpoints', pos = (996,410))

                        #### FILTER ENVELOPE LINES
                        with dpg.drawlist(width=1000, height=150):
                            linecolor = (60,70,65)
                            dpg.draw_rectangle((FilterHini-5,FilterVini-5),(FilterHini+(6*VHSum)+5,FilterVini+VHSum+5), color=(50,50,50,255), thickness=2, fill = (100,120,0,255))
                            dpg.draw_line((FilterHini,FilterVini+VHSum/2),(FilterHini+VHSum,FilterVini+VHSum/2),tag = 'el1_filter1_R1', color=linecolor, thickness=2)
                            dpg.draw_line((FilterHini+VHSum,FilterVini+VHSum/2),(FilterHini+(2*VHSum),FilterVini+VHSum/2),tag = 'el1_filter1_R2', color=linecolor, thickness=2)
                            dpg.draw_line((FilterHini+(2*VHSum),FilterVini+VHSum/2),(FilterHini+(3*VHSum),FilterVini+VHSum/2),tag = 'el1_filter1_R3', color=linecolor, thickness=2)
                            dpg.draw_line((FilterHini+(3*VHSum),FilterVini+VHSum/2),(FilterHini+(4*VHSum),FilterVini+VHSum/2),tag = 'el1_filter1_R4', color=linecolor, thickness=2)
                            dpg.draw_line((FilterHini+(4*VHSum),FilterVini+VHSum/2),(FilterHini+(5*VHSum),FilterVini+VHSum/2),tag = 'el1_filter1_RR1', color=linecolor, thickness=2)
                            dpg.draw_line((FilterHini+(5*VHSum),FilterVini+VHSum/2),(FilterHini+(6*VHSum),FilterVini+VHSum/2),tag = 'el1_filter1_RR2', color=linecolor, thickness=2)
                            for i in range(FilterVini,FilterVini+VHSum,8):
                                dpg.draw_line((FilterHini+(4*VHSum),i),(FilterHini+(4*VHSum),i+4),tag = 'el1_filter1_RE'+str(i), color=(80,80,80), thickness=1)
            
                        dpg.add_text('Note', pos = (975,444), color =(0,150,0))
                        dpg.add_text('Scale Offset', pos = (1070,440), color =(0,150,0))
                        dpg.add_text('BP 1', pos = (924,462))
                        dpg.add_combo(tag = 'el1_filter1_env_bp1', width=60, items = notelist, callback= elfilter12envbp, pos = (960,462), height_mode = 2) 
                        dpg.add_slider_int(no_input = True,tag = 'el1_filter1_env_sc_off_1', label='', width=144, max_value=127, min_value=-127, callback= elfilter12envscoff, pos = (1036,462))
                        dpg.add_text('BP 2', pos = (924,487))
                        dpg.add_combo(tag = 'el1_filter1_env_bp2', width=60, items = notelist, callback= elfilter12envbp, pos = (960,487), height_mode = 2) 
                        dpg.add_slider_int(no_input = True,tag = 'el1_filter1_env_sc_off_2', label='', width=144, max_value=127, min_value=-127, callback= elfilter12envscoff, pos = (1036,487))
                        dpg.add_text('BP 3', pos = (924,512))
                        dpg.add_combo(tag = 'el1_filter1_env_bp3', width=60, items = notelist, callback= elfilter12envbp, pos = (960,512), height_mode = 2) 
                        dpg.add_slider_int(no_input = True,tag = 'el1_filter1_env_sc_off_3', label='', width=144, max_value=127, min_value=-127, callback= elfilter12envscoff, pos = (1036,512))
                        dpg.add_text('BP 4', pos = (924,537))
                        dpg.add_combo(tag = 'el1_filter1_env_bp4', width=60, items = notelist, callback= elfilter12envbp, pos = (960,537), height_mode = 2) 
                        dpg.add_slider_int(no_input = True,tag = 'el1_filter1_env_sc_off_4', label='', width=144, max_value=127, min_value=-127, callback= elfilter12envscoff, pos = (1036,537))

                    with dpg.tab(label='FILTER 2', tag = 'el1_FILTER2',show = True):
                        dpg.add_text('Cutoff', pos = (24-8,419+131))
                        dpg.add_slider_int(no_input = True,tag = 'el1_filter2_cutoff', height=130, vertical = True, max_value=127, default_value=0,callback= elfilter12cutoff, pos = (24,419))
                        dpg.add_text('Filter type', pos = (77,415))
                        dpg.add_slider_int(no_input = True,tag = 'el1_filter2_type', width=40, max_value=1, default_value=1,callback= elfilter12type, pos = (77,415+20),format= f'') 
                        dpg.add_text('LPF', tag = 'el1_filter2_type_value',  pos = (77,435+20), color =(0,150,0))   
                        dpg.add_image('LPF', pos = (77+30,435+23), width = 30,height = 13, tag = 'el1_LPF2_img', show = True)
                        dpg.add_image('NOFILTER', pos = (77+30,435+23), width = 30,height = 13, tag = 'el1_NOFILTER2_img', show = False)
                        dpg.add_text('Filter mode', pos = (77,35+460))
                        dpg.add_slider_int(no_input = True,tag = 'el1_filter2_mode', width=60, max_value=2, default_value=0,callback= elfilter12mode, pos = (77,35+480),format= f'')
                        dpg.add_text('  EG', tag = 'el1_filter2_mode_value',  pos = (77+13,35+500), color =(0,150,0)) 
                        dpg.add_text('FEG Rate Scale', pos = (520,418))
                        dpg.add_slider_int(no_input = True,tag = 'el1_filter2_env_rate_scale', label='', width=110, max_value=7, min_value = -7, callback= elfilter12envratescale, pos = (519,438))
                        dpg.add_text('Filter Envelope',  pos = (670,550))  
                        for i in range(len(filterenvlist)):
                            if 'L' in filterenvlist[i]:
                                dpg.add_slider_int(no_input = True,tag = 'el1_filter2_env_'+filterenvlist[i], vertical = True, height=130, max_value=63, min_value =-64, default_value=0,callback= elfilter12envelope, pos = (170+i*25,420))
                            else:
                                dpg.add_slider_int(no_input = True,tag = 'el1_filter2_env_'+filterenvlist[i], vertical = True, height=130, max_value=63, default_value=0,callback= elfilter12envelope, pos = (170+i*25,420))
                            dpg.add_text(filterenvlist[i],tag = 'el1_filter2env'+str(i),pos = ((183+i*25)-int(4*len(filterenvlist[i])),420+134))

                        dpg.add_text('Filter Env Breakpoints', pos = (996,410))
                        with dpg.drawlist(width=1000, height=150):
                            linecolor = (60,70,65)
                            #### FILTER ENVELOPE LINES
                            dpg.draw_rectangle((FilterHini-5,FilterVini-5),(FilterHini+(6*VHSum)+5,FilterVini+VHSum+5), color=(50,50,50,255), thickness=2, fill = (100,120,0,255))
                            dpg.draw_line((FilterHini,FilterVini+VHSum/2),(FilterHini+VHSum,FilterVini+VHSum/2),tag = 'el1_filter2_R1', color=linecolor, thickness=2)
                            dpg.draw_line((FilterHini+VHSum,FilterVini+VHSum/2),(FilterHini+(2*VHSum),FilterVini+VHSum/2),tag = 'el1_filter2_R2', color=linecolor, thickness=2)
                            dpg.draw_line((FilterHini+(2*VHSum),FilterVini+VHSum/2),(FilterHini+(3*VHSum),FilterVini+VHSum/2),tag = 'el1_filter2_R3', color=linecolor, thickness=2)
                            dpg.draw_line((FilterHini+(3*VHSum),FilterVini+VHSum/2),(FilterHini+(4*VHSum),FilterVini+VHSum/2),tag = 'el1_filter2_R4', color=linecolor, thickness=2)
                            dpg.draw_line((FilterHini+(4*VHSum),FilterVini+VHSum/2),(FilterHini+(5*VHSum),FilterVini+VHSum/2),tag = 'el1_filter2_RR1', color=linecolor, thickness=2)
                            dpg.draw_line((FilterHini+(5*VHSum),FilterVini+VHSum/2),(FilterHini+(6*VHSum),FilterVini+VHSum/2),tag = 'el1_filter2_RR2', color=linecolor, thickness=2)
                            for i in range(FilterVini,FilterVini+VHSum,8):
                                dpg.draw_line((FilterHini+(4*VHSum),i),(FilterHini+(4*VHSum),i+4),tag = 'el1_filter2_RE'+str(i), color=(80,80,80), thickness=1)
                        dpg.add_text('Note', pos = (975,444), color =(0,150,0))
                        dpg.add_text('Scale Offset', pos = (1070,440), color =(0,150,0))
                        dpg.add_text('BP 1', pos = (924,462))
                        dpg.add_combo(tag = 'el1_filter2_env_bp1', width=60, items = notelist, callback= elfilter12envbp, pos = (960,462), height_mode = 2) 
                        dpg.add_slider_int(no_input = True,tag = 'el1_filter2_env_sc_off_1', label='', width=144, max_value=127, min_value=-127, callback= elfilter12envscoff, pos = (1036,462))
                        dpg.add_text('BP 2', pos = (924,487))
                        dpg.add_combo(tag = 'el1_filter2_env_bp2', width=60, items = notelist, callback= elfilter12envbp, pos = (960,487), height_mode = 2) 
                        dpg.add_slider_int(no_input = True,tag = 'el1_filter2_env_sc_off_2', label='', width=144, max_value=127, min_value=-127, callback= elfilter12envscoff, pos = (1036,487))
                        dpg.add_text('BP 3', pos = (924,512))
                        dpg.add_combo(tag = 'el1_filter2_env_bp3', width=60, items = notelist, callback= elfilter12envbp, pos = (960,512), height_mode = 2) 
                        dpg.add_slider_int(no_input = True,tag = 'el1_filter2_env_sc_off_3', label='', width=144, max_value=127, min_value=-127, callback= elfilter12envscoff, pos = (1036,512))
                        dpg.add_text('BP 4', pos = (924,537))
                        dpg.add_combo(tag = 'el1_filter2_env_bp4', width=60, items = notelist, callback= elfilter12envbp, pos = (960,537), height_mode = 2) 
                        dpg.add_slider_int(no_input = True,tag = 'el1_filter2_env_sc_off_4', label='', width=144, max_value=127, min_value=-127, callback= elfilter12envscoff, pos = (1036,537))

                    with dpg.tab(label='FILTER 1+2', tag = 'el1_FILTER12',show = True):
                        dpg.add_text('Reso', pos = (24-4,419+131))
                        dpg.add_slider_int(no_input = True,tag = 'el1_filter1_reso', height=130, vertical = True, max_value=99, default_value=0,callback= elfilter12reso, pos = (24,419))
                        dpg.add_text('Filter Vel Sens', pos = (filtervelsensknobx-10,filtervelsensknoby+46))
                        dpg.add_image_button('KNOB', tag = 'el1_filtervelsens_knob',pos = (filtervelsensknobx,filtervelsensknoby), width = 48, height = 48)
                        dpg.add_image('DOT', tag = 'el1_filtervelsens_dot',pos = (filtervelsensknobx+20,filtervelsensknoby+5),width = 8, height = 8)
                        dpg.add_text('0', tag = 'el1_filtervelsens_value',  pos = (filtervelsensknobx+20,filtervelsensknoby-20))
                        dpg.add_text('Filter Mod Sens', pos = (filtermodsensknobx-16,filtermodsensknoby+46))
                        dpg.add_image_button('KNOB', tag = 'el1_filtermodsens_knob',pos = (filtermodsensknobx,filtermodsensknoby), width = 48, height = 48)
                        dpg.add_image('DOT', tag = 'el1_filtermodsens_dot',pos = (filtermodsensknobx+20,filtermodsensknoby+5),width = 8, height = 8)
                        dpg.add_text('0', tag = 'el1_filtermodsens_value',  pos = (filtermodsensknobx+20,filtermodsensknoby-20))

                dpg.add_text('Note Limit/L:', pos = (20,604))
                dpg.add_combo(tag = 'el1_note_limitL', label='', width=100, items = notelist, callback= elnotelimitL, pos = (20,624), height_mode = 2 ) 
                dpg.add_text('Note Limit/H:', pos = (140,604))
                dpg.add_combo(tag = 'el1_note_limitH', label='', width=100, items = notelist, callback= elnotelimitH, pos = (140,624), height_mode = 2 ) 

                dpg.add_text('Vel. Limit/L:', pos = (260,604))
                dpg.add_slider_int(no_input = True,tag = 'el1_vel_limitL', label='', width=100, max_value=127, min_value=1, callback= elvellimitL, pos = (260,624)) 
                dpg.add_text('Vel. Limit/H:', pos = (380,604))
                dpg.add_slider_int(no_input = True,tag = 'el1_vel_limitH', label='', width=100, max_value=127, min_value=1, callback= elvellimitH, pos = (380,624)) 

                dpg.add_text('LFO Wave:', pos = (514,604))
                dpg.add_slider_int(no_input = True,tag = 'el1_lfo_wave', width=100, max_value=5, default_value=0,callback= ellfowave, pos = (514,624),format= f'')
                dpg.add_text('TRI', tag = 'el1_lfo_wave_value',  pos = (514,646), color =(0,150,0)) 
                dpg.add_image('TRI', pos = (543,648), width = 40,height = 14, tag = 'el1_TRI_img', show = True)
                for i in range(6,11):
                    dpg.add_image(imageslist[i], pos = (543,648), width = 40,height = 14, tag = 'el1_'+imageslist[i]+'_img', show = False)
                dpg.add_text('LFO Speed', pos = (lfospeedknobx-8,lfospeedknoby+46))
                dpg.add_image_button('KNOB', tag = 'el1_lfospeed_knob',pos = (lfospeedknobx,lfospeedknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el1_lfospeed_dot',pos = (lfospeedknobx+13.3,lfospeedknoby+33.3),width = 8, height = 8)
                dpg.add_text('0', tag = 'el1_lfospeed_value',  pos = (lfospeedknobx+20,lfospeedknoby-20))
                dpg.add_text('LFO Delay', pos = (lfodelayknobx-8,lfodelayknoby+46))
                dpg.add_image_button('KNOB', tag = 'el1_lfodelay_knob',pos = (lfodelayknobx,lfodelayknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el1_lfodelay_dot',pos = (lfodelayknobx+13.3,lfodelayknoby+33.3),width = 8, height = 8)
                dpg.add_text('0', tag = 'el1_lfodelay_value',  pos = (lfodelayknobx+20,lfodelayknoby-20))
                dpg.add_text('LFO Phase', pos = (lfophaseknobx-8,lfophaseknoby+46))
                dpg.add_image_button('KNOB', tag = 'el1_lfophase_knob',pos = (lfophaseknobx,lfophaseknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el1_lfophase_dot',pos = (lfophaseknobx+13.3,lfophaseknoby+33.3),width = 8, height = 8)
                dpg.add_text('0', tag = 'el1_lfophase_value',  pos = (lfophaseknobx+20,lfophaseknoby-20))
                dpg.add_text('LFO Amp Mod', pos = (lfoampmodknobx-17,lfoampmodknoby+46))
                dpg.add_image_button('KNOB', tag = 'el1_lfoampmod_knob',pos = (lfoampmodknobx,lfoampmodknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el1_lfoampmod_dot',pos = (lfoampmodknobx+13.3,lfoampmodknoby+33.3),width = 8, height = 8)
                dpg.add_text('0', tag = 'el1_lfoampmod_value',  pos = (lfoampmodknobx+20,lfoampmodknoby-20))
                dpg.add_text('LFO Pitch Mod', pos = (lfopitchmodknobx-17,lfopitchmodknoby+46))
                dpg.add_image_button('KNOB', tag = 'el1_lfopitchmod_knob',pos = (lfopitchmodknobx,lfopitchmodknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el1_lfopitchmod_dot',pos = (lfopitchmodknobx+13.3,lfopitchmodknoby+33.3),width = 8, height = 8)
                dpg.add_text('0', tag = 'el1_lfopitchmod_value',  pos = (lfopitchmodknobx+20,lfopitchmodknoby-20))
                dpg.add_text('LFO Cutoff Mod', pos = (lfocutoffmodknobx-17,lfocutoffmodknoby+46))
                dpg.add_image_button('KNOB', tag = 'el1_lfocutoffmod_knob',pos = (lfocutoffmodknobx,lfocutoffmodknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el1_lfocutoffmod_dot',pos = (lfocutoffmodknobx+13.3,lfocutoffmodknoby+33.3),width = 8, height = 8)
                dpg.add_text('0', tag = 'el1_lfocutoffmod_value',  pos = (lfocutoffmodknobx+20,lfocutoffmodknoby-20))

                #### SEPARATORS BOTTOM
                with dpg.drawlist(width=1600, height=311):    
                    dpg.draw_line((0,10),(1600,10), color=(60,60,60,255), thickness=1)
                    dpg.draw_line((490,10),(490,128), color=(60,60,60,255), thickness=1)

            ################################################### ELEMENT 2 #######################################################
            with dpg.tab(label=' ELEMENT 2 ',tag = 'el2_tab'):
                dpg.add_slider_int(no_input = True,tag = 'el2_volume', label='', vertical = True, height=130, max_value=127, callback= elementvol, pos = (24,45))
                dpg.add_text('Vol', pos = (24,175))
                dpg.add_text('Element 1\nEnable', pos = (63,43))
                dpg.add_checkbox(tag = 'el2_enable', label = '', callback = elementenable, pos = (63,78))
                dpg.set_value('el2_enable', True)
                dpg.add_text('On | Off', pos = (89,78), color =(0,150,0))
                dpg.add_image('REDLIGHT', pos = (66,81), width = 14,height = 14, tag = 'el2_enabled', show = True)
                dpg.add_text('Pan', pos = (panknobx+13,panknoby+47))
                dpg.add_image_button('KNOB', tag = 'el2_pan_knob',pos = (panknobx,panknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el2_pan_dot',pos = (panknobx+20,panknoby+5),width = 8, height = 8)
                dpg.add_text('0', tag = 'el2_pan_value',  pos = (panknobx+20,panknoby-20))  
                dpg.add_text('Wave Select:', pos = (153,50))
                dpg.add_combo(tag = 'el2_Waveform', label = '', width = 107, items = voicelist,callback= AWMwaveform, pos = (152,70), height_mode = 2)
                dpg.add_text('EF Balance', pos = (efbalknobx-10,efbalknoby+47))
                dpg.add_image_button('KNOB', tag = 'el2_efbal_knob',pos = (efbalknobx,efbalknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el2_efbal_dot',pos = (efbalknobx+13.3,efbalknoby+33.3),width = 8, height = 8)
                dpg.add_text('0', tag = 'el2_efbal_value',  pos = (efbalknobx+20,efbalknoby-20))  
                dpg.add_text('AEG\nRate Sens', pos = (281,43))
                dpg.add_slider_int(no_input = True,tag = 'el2_amp_sens_vel_rate', width=40, max_value=1, callback= elsensvelrate, pos = (281,78),format= f'') 
                dpg.add_text('On | Off', pos = (281+47, 78), color =(0,150,0))
                dpg.add_text('Amp Vel Sens', pos = (ampvelsensknobx-16,ampvelsensknoby+47))
                dpg.add_image_button('KNOB', tag = 'el2_ampvelsens_knob',pos = (ampvelsensknobx,ampvelsensknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el2_ampvelsens_dot',pos = (ampvelsensknobx+20,ampvelsensknoby+5),width = 8, height = 8)
                dpg.add_text('0', tag = 'el2_ampvelsens_value',  pos = (ampvelsensknobx+20,ampvelsensknoby-20))  
                dpg.add_text('Amp Mod Sens', pos = (ampmodsensknobx-16,ampmodsensknoby+47))
                dpg.add_image_button('KNOB', tag = 'el2_ampmodsens_knob',pos = (ampmodsensknobx,ampmodsensknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el2_ampmodsens_dot',pos = (ampmodsensknobx+20,ampmodsensknoby+5),width = 8, height = 8)
                dpg.add_text('0', tag = 'el2_ampmodsens_value',  pos = (ampmodsensknobx+20,ampmodsensknoby-20))  
                dpg.add_text('Amp Envelope',  pos = (700,175))  
                for i in range(len(ampenvlist)):
                    dpg.add_slider_int(no_input = True,tag = 'el2_amp_env_'+ampenvlist[i], vertical = True, height=130, max_value=63, default_value=0,callback= elampenvelope, pos = (390+i*25,45))
                    dpg.add_text(ampenvlist[i],tag = 'el2_ampenv'+str(i), pos = (393+i*25,178))
                dpg.add_text('AEG Rate Scale', pos = (582,43))
                dpg.add_slider_int(no_input = True,tag = 'el2_amp_env_rate_scale', label='', width=120, max_value=7, min_value = -7, callback= ampenvratescale, pos = (581,63))
                dpg.add_text('AEG mode', pos = (780,43))
                dpg.add_slider_int(no_input = True,tag = 'el2_amp_env_mode', width=40, max_value=1, default_value=0,callback= elampenvmode, pos = (780,63),format= f'')
                dpg.add_text('Norm | Hold', tag = 'el2_amp_env_mode_value',  pos = (780+47,63), color =(0,150,0))
                dpg.add_text('Amp Env Breakpoints', pos = (1000,43))
                dpg.add_text('Note', pos = (975,70), color =(0,150,0))
                dpg.add_text('Scale Offset', pos = (1070,70), color =(0,150,0))
                dpg.add_text('BP 1', pos = (924,88))
                dpg.add_combo(tag = 'el2_amp_env_bp1', width=60, items = notelist, callback= elampenvbp, pos = (960,88), height_mode = 2) 
                dpg.add_slider_int(no_input = True,tag = 'el2_amp_env_sc_off_1', label='', width=144, max_value=127, min_value=-127, callback= elampenvscoff, pos = (1036,88))
                dpg.add_text('BP 2', pos = (924,113))
                dpg.add_combo(tag = 'el2_amp_env_bp2', width=60, items = notelist, callback= elampenvbp, pos = (960,113), height_mode = 2) 
                dpg.add_slider_int(no_input = True,tag = 'el2_amp_env_sc_off_2', label='', width=144, max_value=127, min_value=-127, callback= elampenvscoff, pos = (1036,113))
                dpg.add_text('BP 3', pos = (924,138))
                dpg.add_combo(tag = 'el2_amp_env_bp3', width=60, items = notelist, callback= elampenvbp, pos = (960,138), height_mode = 2) 
                dpg.add_slider_int(no_input = True,tag = 'el2_amp_env_sc_off_3', label='', width=144, max_value=127, min_value=-127, callback= elampenvscoff, pos = (1036,138))
                dpg.add_text('BP 4', pos = (924,163))
                dpg.add_combo(tag = 'el2_amp_env_bp4', width=60, items = notelist, callback= elampenvbp, pos = (960,163), height_mode = 2) 
                dpg.add_slider_int(no_input = True,tag = 'el2_amp_env_sc_off_4', label='', width=144, max_value=127, min_value=-127, callback= elampenvscoff, pos = (1036,163))
                dpg.add_text('Note shift', pos = (noteshiftknobx-2,noteshiftknoby+46))
                dpg.add_image_button('KNOB', tag = 'el2_noteshift_knob',pos = (noteshiftknobx,noteshiftknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el2_noteshift_dot',pos = (noteshiftknobx+20,noteshiftknoby+5),width = 8, height = 8)
                dpg.add_text('0', tag = 'el2_noteshift_value',  pos = (noteshiftknobx+20,noteshiftknoby-20))  
                dpg.add_text('Detune', pos = (detuneknobx+4,detuneknoby+46))
                dpg.add_image_button('KNOB', tag = 'el2_detune_knob',pos = (detuneknobx,detuneknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el2_detune_dot',pos = (detuneknobx+20,detuneknoby+5),width = 8, height = 8)
                dpg.add_text('0', tag = 'el2_detune_value',  pos = (detuneknobx+20,detuneknoby-20))
                dpg.add_text('OSC Frq Mode', pos = (20,228))
                dpg.add_slider_int(no_input = True,tag = 'el2_osc_freq_mode', width=40, max_value=1, callback= eloscfreqmode, pos = (20,248),format= f'') 
                dpg.add_text('Norm | Fix', pos = (20+47, 248), color =(0,150,0))
                dpg.add_text('OSC Frq Note', pos = (20,310))
                dpg.add_combo(tag = 'el2_osc_freq_note', label='', width=105, items = notelist, callback= eloscfreqnote, pos = (20,330), height_mode = 2, enabled = False) 
                dpg.add_text('OSC Frq Tune', pos = (oscfreqtuneknobx-16,oscfreqtuneknoby+46))
                dpg.add_image_button('KNOB', tag = 'el2_oscfreqtune_knob',pos = (oscfreqtuneknobx,oscfreqtuneknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el2_oscfreqtune_dot',pos = (oscfreqtuneknobx+20,oscfreqtuneknoby+5),width = 8, height = 8)
                dpg.add_text('0', tag = 'el2_oscfreqtune_value',  pos = (oscfreqtuneknobx+20,oscfreqtuneknoby-20))
                dpg.add_text('Pitch Mod Sens', pos = (pitchmodsensknobx-19,pitchmodsensknoby+46))
                dpg.add_image_button('KNOB', tag = 'el2_pitchmodsens_knob',pos = (pitchmodsensknobx,pitchmodsensknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el2_pitchmodsens_dot',pos = (pitchmodsensknobx+13.3,pitchmodsensknoby+33.3),width = 8, height = 8)
                dpg.add_text('0', tag = 'el2_pitchmodsens_value',  pos = (pitchmodsensknobx+20,pitchmodsensknoby-20), color =(0,0,0,0))
                dpg.add_text('0', tag = 'el2_pitchmodsens_valuex',  pos = (pitchmodsensknobx+20,pitchmodsensknoby-20))
                dpg.add_text('Pitch Envelope',  pos = (700,356))  
                for i in range(len(pitchenvlist)):
                    if 'L' in pitchenvlist[i]:
                        dpg.add_slider_int(no_input = True,tag = 'el2_pitch_env_'+pitchenvlist[i], vertical = True, height=130, max_value=63, min_value =-64, default_value=0,callback= elpitchenvelope, pos = (339+i*25,226))
                    else:
                        dpg.add_slider_int(no_input = True,tag = 'el2_pitch_env_'+pitchenvlist[i], vertical = True, height=130, max_value=63, default_value=0,callback= elpitchenvelope, pos = (339+i*25,226))
                    dpg.add_text(pitchenvlist[i],tag = 'el2_pitchenv'+str(i), pos = (343+i*25,359))
                dpg.add_text('PEG Range', pos = (582,224))
                dpg.add_slider_int(no_input = True,tag = 'el2_pitch_env_range', label='', width=60, max_value=2, callback= elpitchenvrange, pos = (581,244),format= f'')
                dpg.add_text('1/2oct', tag = 'el2_pitch_env_range_value', pos = (646,244), color =(0,150,0))
                dpg.add_text('PEG Rate Scale', pos = (693,224))
                dpg.add_slider_int(no_input = True,tag = 'el2_pitch_env_rate_scale', label='', width=110, max_value=7, min_value = -7, callback= elpitchenvratescale, pos = (692,244))
                dpg.add_text('PEG Vel SW', pos = (816,224))
                dpg.add_slider_int(no_input = True,tag = 'el2_pitch_env_vel_sw', width=40, max_value=1, default_value=0,callback= elpitchenvvelsw, pos = (816,244),format= f'')
                dpg.add_text('On | Off', tag = 'el2_pitch_env_vel_sw_value',  pos = (816+47,244), color =(0,150,0))

                ######### DRAWING
                with dpg.drawlist(width=1600, height=342):
                    linecolor = (60,70,65)

                    #### AMP ENVELOPE LINES
                    dpg.draw_rectangle((AmpHini-5,AmpVini-5),(AmpHini+(5*VHSum)+5,AmpVini+VHSum+5), color=(50,50,50,255), thickness=2, fill = (100,120,0,255))
                    dpg.draw_line((AmpHini,AmpVini+VHSum),(AmpHini+VHSum,AmpVini),tag = 'el2_amp_R1', color=linecolor, thickness=2)
                    dpg.draw_line((AmpHini+VHSum,AmpVini),(AmpHini+(2*VHSum),AmpVini+VHSum),tag = 'el2_amp_R2', color=linecolor, thickness=2)
                    dpg.draw_line((AmpHini+(2*VHSum),AmpVini+VHSum),(AmpHini+(3*VHSum),AmpVini+VHSum),tag = 'el2_amp_R3', color=linecolor, thickness=2)
                    dpg.draw_line((AmpHini+(3*VHSum),AmpVini+VHSum),(AmpHini+(4*VHSum),AmpVini+VHSum),tag = 'el2_amp_R4', color=linecolor, thickness=2)
                    dpg.draw_line((AmpHini+(4*VHSum),AmpVini+VHSum),(AmpHini+(5*VHSum),AmpVini+VHSum),tag = 'el2_amp_RR', color=linecolor, thickness=2)
                    for i in range(AmpVini,AmpVini+VHSum,8):
                        dpg.draw_line((AmpHini+(4*VHSum),i),(AmpHini+(4*VHSum),i+4),tag = 'el2_amp_RE'+str(i), color=(80,80,80), thickness=1)

                    #### PITCH ENVELOPE LINES
                    dpg.draw_rectangle((PitchHini-5,PitchVini-5),(PitchHini+(5*VHSum)+5,PitchVini+VHSum+5), color=(50,50,50,255), thickness=2, fill = (100,120,0,255))
                    dpg.draw_line((PitchHini,PitchVini+VHSum/2),(PitchHini+VHSum,PitchVini+VHSum/2),tag = 'el2_pitch_R1', color=linecolor, thickness=2)
                    dpg.draw_line((PitchHini+VHSum,PitchVini+VHSum/2),(PitchHini+(2*VHSum),PitchVini+VHSum/2),tag = 'el2_pitch_R2', color=linecolor, thickness=2)
                    dpg.draw_line((PitchHini+(2*VHSum),PitchVini+VHSum/2),(PitchHini+(3*VHSum),PitchVini+VHSum/2),tag = 'el2_pitch_R3', color=linecolor, thickness=2)
                    dpg.draw_line((PitchHini+(3*VHSum),PitchVini+VHSum/2),(PitchHini+(4*VHSum),PitchVini+VHSum/2),tag = 'el2_pitch_RR', color=linecolor, thickness=2)
                    for i in range(PitchVini,PitchVini+VHSum,8):
                        dpg.draw_line((PitchHini+(3*VHSum),i),(PitchHini+(3*VHSum),i+4),tag = 'el2_pitch_RE'+str(i), color=(80,80,80), thickness=1)

                    #### ELEMENT LINES
                    dpg.draw_line((0,170),(1600,170), thickness=1, color = (60,60,60,255))

                    ########## FILTER TABS
                with dpg.tab_bar(show = True):
                    with dpg.tab(label='FILTER 1', tag = 'el2_FILTER1',show = True):
                        dpg.add_text('Cutoff', pos = (24-8,419+131))
                        dpg.add_slider_int(no_input = True,tag = 'el2_filter1_cutoff', height=130, vertical = True, max_value=127, default_value=0,callback= elfilter12cutoff, pos = (24,419))
                        dpg.add_text('Filter type', pos = (77,415))
                        dpg.add_slider_int(no_input = True,tag = 'el2_filter1_type', width=60, max_value=2, default_value=1,callback= elfilter12type, pos = (77,415+20),format= f'') 
                        dpg.add_text('LPF', tag = 'el2_filter1_type_value',  pos = (77,435+20), color =(0,150,0))   
                        dpg.add_image('LPF', pos = (77+30,435+23), width = 30,height = 13, tag = 'el2_LPF1_img', show = True)
                        dpg.add_image('HPF', pos = (77+30,435+23), width = 30,height = 13, tag = 'el2_HPF1_img', show = False)
                        dpg.add_image('NOFILTER', pos = (77+30,435+23), width = 30,height = 13, tag = 'el2_NOFILTER1_img', show = False)
                        dpg.add_text('Filter mode', pos = (77,35+460))
                        dpg.add_slider_int(no_input = True,tag = 'el2_filter1_mode', width=60, max_value=2, default_value=0,callback= elfilter12mode, pos = (77,35+480),format= f'')
                        dpg.add_text('  EG', tag = 'el2_filter1_mode_value',  pos = (77+13,35+500), color =(0,150,0)) 
                        dpg.add_text('FEG Rate Scale', pos = (520,418))
                        dpg.add_slider_int(no_input = True,tag = 'el2_filter1_env_rate_scale', label='', width=110, max_value=7, min_value = -7, callback= elfilter12envratescale, pos = (519,438))
                        dpg.add_text('Filter Envelope',  pos = (670,550))  
                        for i in range(len(filterenvlist)):
                            if 'L' in filterenvlist[i]:
                                dpg.add_slider_int(no_input = True,tag = 'el2_filter1_env_'+filterenvlist[i], vertical = True, height=130, max_value=63, min_value =-64, default_value=0,callback= elfilter12envelope, pos = (170+i*25,420))
                            else:
                                dpg.add_slider_int(no_input = True,tag = 'el2_filter1_env_'+filterenvlist[i], vertical = True, height=130, max_value=63, default_value=0,callback= elfilter12envelope, pos = (170+i*25,420))
                            dpg.add_text(filterenvlist[i],tag = 'el2_filter1env'+str(i),pos = ((183+i*25)-int(4*len(filterenvlist[i])),420+134))
                        dpg.add_text('Filter Env Breakpoints', pos = (996,410))

                        #### FILTER ENVELOPE LINES
                        with dpg.drawlist(width=1000, height=150):
                            linecolor = (60,70,65)
                            dpg.draw_rectangle((FilterHini-5,FilterVini-5),(FilterHini+(6*VHSum)+5,FilterVini+VHSum+5), color=(50,50,50,255), thickness=2, fill = (100,120,0,255))
                            dpg.draw_line((FilterHini,FilterVini+VHSum/2),(FilterHini+VHSum,FilterVini+VHSum/2),tag = 'el2_filter1_R1', color=linecolor, thickness=2)
                            dpg.draw_line((FilterHini+VHSum,FilterVini+VHSum/2),(FilterHini+(2*VHSum),FilterVini+VHSum/2),tag = 'el2_filter1_R2', color=linecolor, thickness=2)
                            dpg.draw_line((FilterHini+(2*VHSum),FilterVini+VHSum/2),(FilterHini+(3*VHSum),FilterVini+VHSum/2),tag = 'el2_filter1_R3', color=linecolor, thickness=2)
                            dpg.draw_line((FilterHini+(3*VHSum),FilterVini+VHSum/2),(FilterHini+(4*VHSum),FilterVini+VHSum/2),tag = 'el2_filter1_R4', color=linecolor, thickness=2)
                            dpg.draw_line((FilterHini+(4*VHSum),FilterVini+VHSum/2),(FilterHini+(5*VHSum),FilterVini+VHSum/2),tag = 'el2_filter1_RR1', color=linecolor, thickness=2)
                            dpg.draw_line((FilterHini+(5*VHSum),FilterVini+VHSum/2),(FilterHini+(6*VHSum),FilterVini+VHSum/2),tag = 'el2_filter1_RR2', color=linecolor, thickness=2)
                            for i in range(FilterVini,FilterVini+VHSum,8):
                                dpg.draw_line((FilterHini+(4*VHSum),i),(FilterHini+(4*VHSum),i+4),tag = 'el2_filter1_RE'+str(i), color=(80,80,80), thickness=1)
            
                        dpg.add_text('Note', pos = (975,444), color =(0,150,0))
                        dpg.add_text('Scale Offset', pos = (1070,440), color =(0,150,0))
                        dpg.add_text('BP 1', pos = (924,462))
                        dpg.add_combo(tag = 'el2_filter1_env_bp1', width=60, items = notelist, callback= elfilter12envbp, pos = (960,462), height_mode = 2) 
                        dpg.add_slider_int(no_input = True,tag = 'el2_filter1_env_sc_off_1', label='', width=144, max_value=127, min_value=-127, callback= elfilter12envscoff, pos = (1036,462))
                        dpg.add_text('BP 2', pos = (924,487))
                        dpg.add_combo(tag = 'el2_filter1_env_bp2', width=60, items = notelist, callback= elfilter12envbp, pos = (960,487), height_mode = 2) 
                        dpg.add_slider_int(no_input = True,tag = 'el2_filter1_env_sc_off_2', label='', width=144, max_value=127, min_value=-127, callback= elfilter12envscoff, pos = (1036,487))
                        dpg.add_text('BP 3', pos = (924,512))
                        dpg.add_combo(tag = 'el2_filter1_env_bp3', width=60, items = notelist, callback= elfilter12envbp, pos = (960,512), height_mode = 2) 
                        dpg.add_slider_int(no_input = True,tag = 'el2_filter1_env_sc_off_3', label='', width=144, max_value=127, min_value=-127, callback= elfilter12envscoff, pos = (1036,512))
                        dpg.add_text('BP 4', pos = (924,537))
                        dpg.add_combo(tag = 'el2_filter1_env_bp4', width=60, items = notelist, callback= elfilter12envbp, pos = (960,537), height_mode = 2) 
                        dpg.add_slider_int(no_input = True,tag = 'el2_filter1_env_sc_off_4', label='', width=144, max_value=127, min_value=-127, callback= elfilter12envscoff, pos = (1036,537))

                    with dpg.tab(label='FILTER 2', tag = 'el2_FILTER2',show = True):
                        dpg.add_text('Cutoff', pos = (24-8,419+131))
                        dpg.add_slider_int(no_input = True,tag = 'el2_filter2_cutoff', height=130, vertical = True, max_value=127, default_value=0,callback= elfilter12cutoff, pos = (24,419))
                        dpg.add_text('Filter type', pos = (77,415))
                        dpg.add_slider_int(no_input = True,tag = 'el2_filter2_type', width=40, max_value=1, default_value=1,callback= elfilter12type, pos = (77,415+20),format= f'') 
                        dpg.add_text('LPF', tag = 'el2_filter2_type_value',  pos = (77,435+20), color =(0,150,0))   
                        dpg.add_image('LPF', pos = (77+30,435+23), width = 30,height = 13, tag = 'el2_LPF2_img', show = True)
                        dpg.add_image('NOFILTER', pos = (77+30,435+23), width = 30,height = 13, tag = 'el2_NOFILTER2_img', show = False)
                        dpg.add_text('Filter mode', pos = (77,35+460))
                        dpg.add_slider_int(no_input = True,tag = 'el2_filter2_mode', width=60, max_value=2, default_value=0,callback= elfilter12mode, pos = (77,35+480),format= f'')
                        dpg.add_text('  EG', tag = 'el2_filter2_mode_value',  pos = (77+13,35+500), color =(0,150,0)) 
                        dpg.add_text('FEG Rate Scale', pos = (520,418))
                        dpg.add_slider_int(no_input = True,tag = 'el2_filter2_env_rate_scale', label='', width=110, max_value=7, min_value = -7, callback= elfilter12envratescale, pos = (519,438))
                        dpg.add_text('Filter Envelope',  pos = (670,550))  
                        for i in range(len(filterenvlist)):
                            if 'L' in filterenvlist[i]:
                                dpg.add_slider_int(no_input = True,tag = 'el2_filter2_env_'+filterenvlist[i], vertical = True, height=130, max_value=63, min_value =-64, default_value=0,callback= elfilter12envelope, pos = (170+i*25,420))
                            else:
                                dpg.add_slider_int(no_input = True,tag = 'el2_filter2_env_'+filterenvlist[i], vertical = True, height=130, max_value=63, default_value=0,callback= elfilter12envelope, pos = (170+i*25,420))
                            dpg.add_text(filterenvlist[i],tag = 'el2_filter2env'+str(i),pos = ((183+i*25)-int(4*len(filterenvlist[i])),420+134))

                        dpg.add_text('Filter Env Breakpoints', pos = (996,410))
                        with dpg.drawlist(width=1000, height=150):
                            linecolor = (60,70,65)
                            #### FILTER ENVELOPE LINES
                            dpg.draw_rectangle((FilterHini-5,FilterVini-5),(FilterHini+(6*VHSum)+5,FilterVini+VHSum+5), color=(50,50,50,255), thickness=2, fill = (100,120,0,255))
                            dpg.draw_line((FilterHini,FilterVini+VHSum/2),(FilterHini+VHSum,FilterVini+VHSum/2),tag = 'el2_filter2_R1', color=linecolor, thickness=2)
                            dpg.draw_line((FilterHini+VHSum,FilterVini+VHSum/2),(FilterHini+(2*VHSum),FilterVini+VHSum/2),tag = 'el2_filter2_R2', color=linecolor, thickness=2)
                            dpg.draw_line((FilterHini+(2*VHSum),FilterVini+VHSum/2),(FilterHini+(3*VHSum),FilterVini+VHSum/2),tag = 'el2_filter2_R3', color=linecolor, thickness=2)
                            dpg.draw_line((FilterHini+(3*VHSum),FilterVini+VHSum/2),(FilterHini+(4*VHSum),FilterVini+VHSum/2),tag = 'el2_filter2_R4', color=linecolor, thickness=2)
                            dpg.draw_line((FilterHini+(4*VHSum),FilterVini+VHSum/2),(FilterHini+(5*VHSum),FilterVini+VHSum/2),tag = 'el2_filter2_RR1', color=linecolor, thickness=2)
                            dpg.draw_line((FilterHini+(5*VHSum),FilterVini+VHSum/2),(FilterHini+(6*VHSum),FilterVini+VHSum/2),tag = 'el2_filter2_RR2', color=linecolor, thickness=2)
                            for i in range(FilterVini,FilterVini+VHSum,8):
                                dpg.draw_line((FilterHini+(4*VHSum),i),(FilterHini+(4*VHSum),i+4),tag = 'el2_filter2_RE'+str(i), color=(80,80,80), thickness=1)
                        dpg.add_text('Note', pos = (975,444), color =(0,150,0))
                        dpg.add_text('Scale Offset', pos = (1070,440), color =(0,150,0))
                        dpg.add_text('BP 1', pos = (924,462))
                        dpg.add_combo(tag = 'el2_filter2_env_bp1', width=60, items = notelist, callback= elfilter12envbp, pos = (960,462), height_mode = 2) 
                        dpg.add_slider_int(no_input = True,tag = 'el2_filter2_env_sc_off_1', label='', width=144, max_value=127, min_value=-127, callback= elfilter12envscoff, pos = (1036,462))
                        dpg.add_text('BP 2', pos = (924,487))
                        dpg.add_combo(tag = 'el2_filter2_env_bp2', width=60, items = notelist, callback= elfilter12envbp, pos = (960,487), height_mode = 2) 
                        dpg.add_slider_int(no_input = True,tag = 'el2_filter2_env_sc_off_2', label='', width=144, max_value=127, min_value=-127, callback= elfilter12envscoff, pos = (1036,487))
                        dpg.add_text('BP 3', pos = (924,512))
                        dpg.add_combo(tag = 'el2_filter2_env_bp3', width=60, items = notelist, callback= elfilter12envbp, pos = (960,512), height_mode = 2) 
                        dpg.add_slider_int(no_input = True,tag = 'el2_filter2_env_sc_off_3', label='', width=144, max_value=127, min_value=-127, callback= elfilter12envscoff, pos = (1036,512))
                        dpg.add_text('BP 4', pos = (924,537))
                        dpg.add_combo(tag = 'el2_filter2_env_bp4', width=60, items = notelist, callback= elfilter12envbp, pos = (960,537), height_mode = 2) 
                        dpg.add_slider_int(no_input = True,tag = 'el2_filter2_env_sc_off_4', label='', width=144, max_value=127, min_value=-127, callback= elfilter12envscoff, pos = (1036,537))

                    with dpg.tab(label='FILTER 1+2', tag = 'el2_FILTER12',show = True):
                        dpg.add_text('Reso', pos = (24-4,419+131))
                        dpg.add_slider_int(no_input = True,tag = 'el2_filter1_reso', height=130, vertical = True, max_value=99, default_value=0,callback= elfilter12reso, pos = (24,419))
                        dpg.add_text('Filter Vel Sens', pos = (filtervelsensknobx-10,filtervelsensknoby+46))
                        dpg.add_image_button('KNOB', tag = 'el2_filtervelsens_knob',pos = (filtervelsensknobx,filtervelsensknoby), width = 48, height = 48)
                        dpg.add_image('DOT', tag = 'el2_filtervelsens_dot',pos = (filtervelsensknobx+20,filtervelsensknoby+5),width = 8, height = 8)
                        dpg.add_text('0', tag = 'el2_filtervelsens_value',  pos = (filtervelsensknobx+20,filtervelsensknoby-20))
                        dpg.add_text('Filter Mod Sens', pos = (filtermodsensknobx-16,filtermodsensknoby+46))
                        dpg.add_image_button('KNOB', tag = 'el2_filtermodsens_knob',pos = (filtermodsensknobx,filtermodsensknoby), width = 48, height = 48)
                        dpg.add_image('DOT', tag = 'el2_filtermodsens_dot',pos = (filtermodsensknobx+20,filtermodsensknoby+5),width = 8, height = 8)
                        dpg.add_text('0', tag = 'el2_filtermodsens_value',  pos = (filtermodsensknobx+20,filtermodsensknoby-20))

                dpg.add_text('Note Limit/L:', pos = (20,604))
                dpg.add_combo(tag = 'el2_note_limitL', label='', width=100, items = notelist, callback= elnotelimitL, pos = (20,624), height_mode = 2 ) 
                dpg.add_text('Note Limit/H:', pos = (140,604))
                dpg.add_combo(tag = 'el2_note_limitH', label='', width=100, items = notelist, callback= elnotelimitH, pos = (140,624), height_mode = 2 ) 
                dpg.add_text('Vel. Limit/L:', pos = (260,604))
                dpg.add_slider_int(no_input = True,tag = 'el2_vel_limitL', label='', width=100, max_value=127, min_value=1, callback= elvellimitL, pos = (260,624)) 
                dpg.add_text('Vel. Limit/H:', pos = (380,604))
                dpg.add_slider_int(no_input = True,tag = 'el2_vel_limitH', label='', width=100, max_value=127, min_value=1, callback= elvellimitH, pos = (380,624)) 
                dpg.add_text('LFO Wave:', pos = (514,604))
                dpg.add_slider_int(no_input = True,tag = 'el2_lfo_wave', width=100, max_value=5, default_value=0,callback= ellfowave, pos = (514,624),format= f'')
                dpg.add_text('TRI', tag = 'el2_lfo_wave_value',  pos = (514,646), color =(0,150,0)) 
                dpg.add_image('TRI', pos = (543,648), width = 40,height = 14, tag = 'el2_TRI_img', show = True)
                for i in range(6,11):
                    dpg.add_image(imageslist[i], pos = (543,648), width = 40,height = 14, tag = 'el2_'+imageslist[i]+'_img', show = False)
                dpg.add_text('LFO Speed', pos = (lfospeedknobx-8,lfospeedknoby+46))
                dpg.add_image_button('KNOB', tag = 'el2_lfospeed_knob',pos = (lfospeedknobx,lfospeedknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el2_lfospeed_dot',pos = (lfospeedknobx+13.3,lfospeedknoby+33.3),width = 8, height = 8)
                dpg.add_text('0', tag = 'el2_lfospeed_value',  pos = (lfospeedknobx+20,lfospeedknoby-20))
                dpg.add_text('LFO Delay', pos = (lfodelayknobx-8,lfodelayknoby+46))
                dpg.add_image_button('KNOB', tag = 'el2_lfodelay_knob',pos = (lfodelayknobx,lfodelayknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el2_lfodelay_dot',pos = (lfodelayknobx+13.3,lfodelayknoby+33.3),width = 8, height = 8)
                dpg.add_text('0', tag = 'el2_lfodelay_value',  pos = (lfodelayknobx+20,lfodelayknoby-20))
                dpg.add_text('LFO Phase', pos = (lfophaseknobx-8,lfophaseknoby+46))
                dpg.add_image_button('KNOB', tag = 'el2_lfophase_knob',pos = (lfophaseknobx,lfophaseknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el2_lfophase_dot',pos = (lfophaseknobx+13.3,lfophaseknoby+33.3),width = 8, height = 8)
                dpg.add_text('0', tag = 'el2_lfophase_value',  pos = (lfophaseknobx+20,lfophaseknoby-20))
                dpg.add_text('LFO Amp Mod', pos = (lfoampmodknobx-17,lfoampmodknoby+46))
                dpg.add_image_button('KNOB', tag = 'el2_lfoampmod_knob',pos = (lfoampmodknobx,lfoampmodknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el2_lfoampmod_dot',pos = (lfoampmodknobx+13.3,lfoampmodknoby+33.3),width = 8, height = 8)
                dpg.add_text('0', tag = 'el2_lfoampmod_value',  pos = (lfoampmodknobx+20,lfoampmodknoby-20))
                dpg.add_text('LFO Pitch Mod', pos = (lfopitchmodknobx-17,lfopitchmodknoby+46))
                dpg.add_image_button('KNOB', tag = 'el2_lfopitchmod_knob',pos = (lfopitchmodknobx,lfopitchmodknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el2_lfopitchmod_dot',pos = (lfopitchmodknobx+13.3,lfopitchmodknoby+33.3),width = 8, height = 8)
                dpg.add_text('0', tag = 'el2_lfopitchmod_value',  pos = (lfopitchmodknobx+20,lfopitchmodknoby-20))
                dpg.add_text('LFO Cutoff Mod', pos = (lfocutoffmodknobx-17,lfocutoffmodknoby+46))
                dpg.add_image_button('KNOB', tag = 'el2_lfocutoffmod_knob',pos = (lfocutoffmodknobx,lfocutoffmodknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el2_lfocutoffmod_dot',pos = (lfocutoffmodknobx+13.3,lfocutoffmodknoby+33.3),width = 8, height = 8)
                dpg.add_text('0', tag = 'el2_lfocutoffmod_value',  pos = (lfocutoffmodknobx+20,lfocutoffmodknoby-20))

                #### SEPARATORS BOTTOM
                with dpg.drawlist(width=1600, height=311):    
                    dpg.draw_line((0,10),(1600,10), color=(60,60,60,255), thickness=1)
                    dpg.draw_line((490,10),(490,128), color=(60,60,60,255), thickness=1)

            ################################################### ELEMENT 3 #######################################################
            with dpg.tab(label=' ELEMENT 3 ',tag = 'el3_tab'):
                dpg.add_slider_int(no_input = True,tag = 'el3_volume', label='', vertical = True, height=130, max_value=127, callback= elementvol, pos = (24,45))
                dpg.add_text('Vol', pos = (24,175))
                dpg.add_text('Element 1\nEnable', pos = (63,43))
                dpg.add_checkbox(tag = 'el3_enable', label = '', callback = elementenable, pos = (63,78))
                dpg.set_value('el3_enable', True)
                dpg.add_text('On | Off', pos = (89,78), color =(0,150,0))
                dpg.add_image('REDLIGHT', pos = (66,81), width = 14,height = 14, tag = 'el3_enabled', show = True)
                dpg.add_text('Pan', pos = (panknobx+13,panknoby+47))
                dpg.add_image_button('KNOB', tag = 'el3_pan_knob',pos = (panknobx,panknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el3_pan_dot',pos = (panknobx+20,panknoby+5),width = 8, height = 8)
                dpg.add_text('0', tag = 'el3_pan_value',  pos = (panknobx+20,panknoby-20))  
                dpg.add_text('Wave Select:', pos = (153,50))
                dpg.add_combo(tag = 'el3_Waveform', label = '', width = 107, items = voicelist,callback= AWMwaveform, pos = (152,70), height_mode = 2)
                dpg.add_text('EF Balance', pos = (efbalknobx-10,efbalknoby+47))
                dpg.add_image_button('KNOB', tag = 'el3_efbal_knob',pos = (efbalknobx,efbalknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el3_efbal_dot',pos = (efbalknobx+13.3,efbalknoby+33.3),width = 8, height = 8)
                dpg.add_text('0', tag = 'el3_efbal_value',  pos = (efbalknobx+20,efbalknoby-20))  
                dpg.add_text('AEG\nRate Sens', pos = (281,43))
                dpg.add_slider_int(no_input = True,tag = 'el3_amp_sens_vel_rate', width=40, max_value=1, callback= elsensvelrate, pos = (281,78),format= f'') 
                dpg.add_text('On | Off', pos = (281+47, 78), color =(0,150,0))
                dpg.add_text('Amp Vel Sens', pos = (ampvelsensknobx-16,ampvelsensknoby+47))
                dpg.add_image_button('KNOB', tag = 'el3_ampvelsens_knob',pos = (ampvelsensknobx,ampvelsensknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el3_ampvelsens_dot',pos = (ampvelsensknobx+20,ampvelsensknoby+5),width = 8, height = 8)
                dpg.add_text('0', tag = 'el3_ampvelsens_value',  pos = (ampvelsensknobx+20,ampvelsensknoby-20))  
                dpg.add_text('Amp Mod Sens', pos = (ampmodsensknobx-16,ampmodsensknoby+47))
                dpg.add_image_button('KNOB', tag = 'el3_ampmodsens_knob',pos = (ampmodsensknobx,ampmodsensknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el3_ampmodsens_dot',pos = (ampmodsensknobx+20,ampmodsensknoby+5),width = 8, height = 8)
                dpg.add_text('0', tag = 'el3_ampmodsens_value',  pos = (ampmodsensknobx+20,ampmodsensknoby-20))  
                dpg.add_text('Amp Envelope',  pos = (700,175))  
                for i in range(len(ampenvlist)):
                    dpg.add_slider_int(no_input = True,tag = 'el3_amp_env_'+ampenvlist[i], vertical = True, height=130, max_value=63, default_value=0,callback= elampenvelope, pos = (390+i*25,45))
                    dpg.add_text(ampenvlist[i],tag = 'el3_ampenv'+str(i), pos = (393+i*25,178))
                dpg.add_text('AEG Rate Scale', pos = (582,43))
                dpg.add_slider_int(no_input = True,tag = 'el3_amp_env_rate_scale', label='', width=120, max_value=7, min_value = -7, callback= ampenvratescale, pos = (581,63))
                dpg.add_text('AEG mode', pos = (780,43))
                dpg.add_slider_int(no_input = True,tag = 'el3_amp_env_mode', width=40, max_value=1, default_value=0,callback= elampenvmode, pos = (780,63),format= f'')
                dpg.add_text('Norm | Hold', tag = 'el3_amp_env_mode_value',  pos = (780+47,63), color =(0,150,0))
                dpg.add_text('Amp Env Breakpoints', pos = (1000,43))
                dpg.add_text('Note', pos = (975,70), color =(0,150,0))
                dpg.add_text('Scale Offset', pos = (1070,70), color =(0,150,0))
                dpg.add_text('BP 1', pos = (924,88))
                dpg.add_combo(tag = 'el3_amp_env_bp1', width=60, items = notelist, callback= elampenvbp, pos = (960,88), height_mode = 2) 
                dpg.add_slider_int(no_input = True,tag = 'el3_amp_env_sc_off_1', label='', width=144, max_value=127, min_value=-127, callback= elampenvscoff, pos = (1036,88))
                dpg.add_text('BP 2', pos = (924,113))
                dpg.add_combo(tag = 'el3_amp_env_bp2', width=60, items = notelist, callback= elampenvbp, pos = (960,113), height_mode = 2) 
                dpg.add_slider_int(no_input = True,tag = 'el3_amp_env_sc_off_2', label='', width=144, max_value=127, min_value=-127, callback= elampenvscoff, pos = (1036,113))
                dpg.add_text('BP 3', pos = (924,138))
                dpg.add_combo(tag = 'el3_amp_env_bp3', width=60, items = notelist, callback= elampenvbp, pos = (960,138), height_mode = 2) 
                dpg.add_slider_int(no_input = True,tag = 'el3_amp_env_sc_off_3', label='', width=144, max_value=127, min_value=-127, callback= elampenvscoff, pos = (1036,138))
                dpg.add_text('BP 4', pos = (924,163))
                dpg.add_combo(tag = 'el3_amp_env_bp4', width=60, items = notelist, callback= elampenvbp, pos = (960,163), height_mode = 2) 
                dpg.add_slider_int(no_input = True,tag = 'el3_amp_env_sc_off_4', label='', width=144, max_value=127, min_value=-127, callback= elampenvscoff, pos = (1036,163))
                dpg.add_text('Note shift', pos = (noteshiftknobx-2,noteshiftknoby+46))
                dpg.add_image_button('KNOB', tag = 'el3_noteshift_knob',pos = (noteshiftknobx,noteshiftknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el3_noteshift_dot',pos = (noteshiftknobx+20,noteshiftknoby+5),width = 8, height = 8)
                dpg.add_text('0', tag = 'el3_noteshift_value',  pos = (noteshiftknobx+20,noteshiftknoby-20))  
                dpg.add_text('Detune', pos = (detuneknobx+4,detuneknoby+46))
                dpg.add_image_button('KNOB', tag = 'el3_detune_knob',pos = (detuneknobx,detuneknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el3_detune_dot',pos = (detuneknobx+20,detuneknoby+5),width = 8, height = 8)
                dpg.add_text('0', tag = 'el3_detune_value',  pos = (detuneknobx+20,detuneknoby-20))
                dpg.add_text('OSC Frq Mode', pos = (20,228))
                dpg.add_slider_int(no_input = True,tag = 'el3_osc_freq_mode', width=40, max_value=1, callback= eloscfreqmode, pos = (20,248),format= f'') 
                dpg.add_text('Norm | Fix', pos = (20+47, 248), color =(0,150,0))
                dpg.add_text('OSC Frq Note', pos = (20,310))
                dpg.add_combo(tag = 'el3_osc_freq_note', label='', width=105, items = notelist, callback= eloscfreqnote, pos = (20,330), height_mode = 2, enabled = False) 
                dpg.add_text('OSC Frq Tune', pos = (oscfreqtuneknobx-16,oscfreqtuneknoby+46))
                dpg.add_image_button('KNOB', tag = 'el3_oscfreqtune_knob',pos = (oscfreqtuneknobx,oscfreqtuneknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el3_oscfreqtune_dot',pos = (oscfreqtuneknobx+20,oscfreqtuneknoby+5),width = 8, height = 8)
                dpg.add_text('0', tag = 'el3_oscfreqtune_value',  pos = (oscfreqtuneknobx+20,oscfreqtuneknoby-20))
                dpg.add_text('Pitch Mod Sens', pos = (pitchmodsensknobx-19,pitchmodsensknoby+46))
                dpg.add_image_button('KNOB', tag = 'el3_pitchmodsens_knob',pos = (pitchmodsensknobx,pitchmodsensknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el3_pitchmodsens_dot',pos = (pitchmodsensknobx+13.3,pitchmodsensknoby+33.3),width = 8, height = 8)
                dpg.add_text('0', tag = 'el3_pitchmodsens_value',  pos = (pitchmodsensknobx+20,pitchmodsensknoby-20), color =(0,0,0,0))
                dpg.add_text('0', tag = 'el3_pitchmodsens_valuex',  pos = (pitchmodsensknobx+20,pitchmodsensknoby-20))
                dpg.add_text('Pitch Envelope',  pos = (700,356))  
                for i in range(len(pitchenvlist)):
                    if 'L' in pitchenvlist[i]:
                        dpg.add_slider_int(no_input = True,tag = 'el3_pitch_env_'+pitchenvlist[i], vertical = True, height=130, max_value=63, min_value =-64, default_value=0,callback= elpitchenvelope, pos = (339+i*25,226))
                    else:
                        dpg.add_slider_int(no_input = True,tag = 'el3_pitch_env_'+pitchenvlist[i], vertical = True, height=130, max_value=63, default_value=0,callback= elpitchenvelope, pos = (339+i*25,226))
                    dpg.add_text(pitchenvlist[i],tag = 'el3_pitchenv'+str(i), pos = (343+i*25,359))
                dpg.add_text('PEG Range', pos = (582,224))
                dpg.add_slider_int(no_input = True,tag = 'el3_pitch_env_range', label='', width=60, max_value=2, callback= elpitchenvrange, pos = (581,244),format= f'')
                dpg.add_text('1/2oct', tag = 'el3_pitch_env_range_value', pos = (646,244), color =(0,150,0))
                dpg.add_text('PEG Rate Scale', pos = (693,224))
                dpg.add_slider_int(no_input = True,tag = 'el3_pitch_env_rate_scale', label='', width=110, max_value=7, min_value = -7, callback= elpitchenvratescale, pos = (692,244))
                dpg.add_text('PEG Vel SW', pos = (816,224))
                dpg.add_slider_int(no_input = True,tag = 'el3_pitch_env_vel_sw', width=40, max_value=1, default_value=0,callback= elpitchenvvelsw, pos = (816,244),format= f'')
                dpg.add_text('On | Off', tag = 'el3_pitch_env_vel_sw_value',  pos = (816+47,244), color =(0,150,0))

                ######### DRAWING
                with dpg.drawlist(width=1600, height=342):
                    linecolor = (60,70,65)

                    #### AMP ENVELOPE LINES
                    dpg.draw_rectangle((AmpHini-5,AmpVini-5),(AmpHini+(5*VHSum)+5,AmpVini+VHSum+5), color=(50,50,50,255), thickness=2, fill = (100,120,0,255))
                    dpg.draw_line((AmpHini,AmpVini+VHSum),(AmpHini+VHSum,AmpVini),tag = 'el3_amp_R1', color=linecolor, thickness=2)
                    dpg.draw_line((AmpHini+VHSum,AmpVini),(AmpHini+(2*VHSum),AmpVini+VHSum),tag = 'el3_amp_R2', color=linecolor, thickness=2)
                    dpg.draw_line((AmpHini+(2*VHSum),AmpVini+VHSum),(AmpHini+(3*VHSum),AmpVini+VHSum),tag = 'el3_amp_R3', color=linecolor, thickness=2)
                    dpg.draw_line((AmpHini+(3*VHSum),AmpVini+VHSum),(AmpHini+(4*VHSum),AmpVini+VHSum),tag = 'el3_amp_R4', color=linecolor, thickness=2)
                    dpg.draw_line((AmpHini+(4*VHSum),AmpVini+VHSum),(AmpHini+(5*VHSum),AmpVini+VHSum),tag = 'el3_amp_RR', color=linecolor, thickness=2)
                    for i in range(AmpVini,AmpVini+VHSum,8):
                        dpg.draw_line((AmpHini+(4*VHSum),i),(AmpHini+(4*VHSum),i+4),tag = 'el3_amp_RE'+str(i), color=(80,80,80), thickness=1)

                    #### PITCH ENVELOPE LINES
                    dpg.draw_rectangle((PitchHini-5,PitchVini-5),(PitchHini+(5*VHSum)+5,PitchVini+VHSum+5), color=(50,50,50,255), thickness=2, fill = (100,120,0,255))
                    dpg.draw_line((PitchHini,PitchVini+VHSum/2),(PitchHini+VHSum,PitchVini+VHSum/2),tag = 'el3_pitch_R1', color=linecolor, thickness=2)
                    dpg.draw_line((PitchHini+VHSum,PitchVini+VHSum/2),(PitchHini+(2*VHSum),PitchVini+VHSum/2),tag = 'el3_pitch_R2', color=linecolor, thickness=2)
                    dpg.draw_line((PitchHini+(2*VHSum),PitchVini+VHSum/2),(PitchHini+(3*VHSum),PitchVini+VHSum/2),tag = 'el3_pitch_R3', color=linecolor, thickness=2)
                    dpg.draw_line((PitchHini+(3*VHSum),PitchVini+VHSum/2),(PitchHini+(4*VHSum),PitchVini+VHSum/2),tag = 'el3_pitch_RR', color=linecolor, thickness=2)
                    for i in range(PitchVini,PitchVini+VHSum,8):
                        dpg.draw_line((PitchHini+(3*VHSum),i),(PitchHini+(3*VHSum),i+4),tag = 'el3_pitch_RE'+str(i), color=(80,80,80), thickness=1)

                    #### ELEMENT LINES
                    dpg.draw_line((0,170),(1600,170), thickness=1, color = (60,60,60,255))

                    ########## FILTER TABS
                with dpg.tab_bar(show = True):
                    with dpg.tab(label='FILTER 1', tag = 'el3_FILTER1',show = True):
                        dpg.add_text('Cutoff', pos = (24-8,419+131))
                        dpg.add_slider_int(no_input = True,tag = 'el3_filter1_cutoff', height=130, vertical = True, max_value=127, default_value=0,callback= elfilter12cutoff, pos = (24,419))
                        dpg.add_text('Filter type', pos = (77,415))
                        dpg.add_slider_int(no_input = True,tag = 'el3_filter1_type', width=60, max_value=2, default_value=1,callback= elfilter12type, pos = (77,415+20),format= f'') 
                        dpg.add_text('LPF', tag = 'el3_filter1_type_value',  pos = (77,435+20), color =(0,150,0))   
                        dpg.add_image('LPF', pos = (77+30,435+23), width = 30,height = 13, tag = 'el3_LPF1_img', show = True)
                        dpg.add_image('HPF', pos = (77+30,435+23), width = 30,height = 13, tag = 'el3_HPF1_img', show = False)
                        dpg.add_image('NOFILTER', pos = (77+30,435+23), width = 30,height = 13, tag = 'el3_NOFILTER1_img', show = False)
                        dpg.add_text('Filter mode', pos = (77,35+460))
                        dpg.add_slider_int(no_input = True,tag = 'el3_filter1_mode', width=60, max_value=2, default_value=0,callback= elfilter12mode, pos = (77,35+480),format= f'')
                        dpg.add_text('  EG', tag = 'el3_filter1_mode_value',  pos = (77+13,35+500), color =(0,150,0)) 
                        dpg.add_text('FEG Rate Scale', pos = (520,418))
                        dpg.add_slider_int(no_input = True,tag = 'el3_filter1_env_rate_scale', label='', width=110, max_value=7, min_value = -7, callback= elfilter12envratescale, pos = (519,438))
                        dpg.add_text('Filter Envelope',  pos = (670,550))  
                        for i in range(len(filterenvlist)):
                            if 'L' in filterenvlist[i]:
                                dpg.add_slider_int(no_input = True,tag = 'el3_filter1_env_'+filterenvlist[i], vertical = True, height=130, max_value=63, min_value =-64, default_value=0,callback= elfilter12envelope, pos = (170+i*25,420))
                            else:
                                dpg.add_slider_int(no_input = True,tag = 'el3_filter1_env_'+filterenvlist[i], vertical = True, height=130, max_value=63, default_value=0,callback= elfilter12envelope, pos = (170+i*25,420))
                            dpg.add_text(filterenvlist[i],tag = 'el3_filter1env'+str(i),pos = ((183+i*25)-int(4*len(filterenvlist[i])),420+134))
                        dpg.add_text('Filter Env Breakpoints', pos = (996,410))

                        #### FILTER ENVELOPE LINES
                        with dpg.drawlist(width=1000, height=150):
                            linecolor = (60,70,65)
                            dpg.draw_rectangle((FilterHini-5,FilterVini-5),(FilterHini+(6*VHSum)+5,FilterVini+VHSum+5), color=(50,50,50,255), thickness=2, fill = (100,120,0,255))
                            dpg.draw_line((FilterHini,FilterVini+VHSum/2),(FilterHini+VHSum,FilterVini+VHSum/2),tag = 'el3_filter1_R1', color=linecolor, thickness=2)
                            dpg.draw_line((FilterHini+VHSum,FilterVini+VHSum/2),(FilterHini+(2*VHSum),FilterVini+VHSum/2),tag = 'el3_filter1_R2', color=linecolor, thickness=2)
                            dpg.draw_line((FilterHini+(2*VHSum),FilterVini+VHSum/2),(FilterHini+(3*VHSum),FilterVini+VHSum/2),tag = 'el3_filter1_R3', color=linecolor, thickness=2)
                            dpg.draw_line((FilterHini+(3*VHSum),FilterVini+VHSum/2),(FilterHini+(4*VHSum),FilterVini+VHSum/2),tag = 'el3_filter1_R4', color=linecolor, thickness=2)
                            dpg.draw_line((FilterHini+(4*VHSum),FilterVini+VHSum/2),(FilterHini+(5*VHSum),FilterVini+VHSum/2),tag = 'el3_filter1_RR1', color=linecolor, thickness=2)
                            dpg.draw_line((FilterHini+(5*VHSum),FilterVini+VHSum/2),(FilterHini+(6*VHSum),FilterVini+VHSum/2),tag = 'el3_filter1_RR2', color=linecolor, thickness=2)
                            for i in range(FilterVini,FilterVini+VHSum,8):
                                dpg.draw_line((FilterHini+(4*VHSum),i),(FilterHini+(4*VHSum),i+4),tag = 'el3_filter1_RE'+str(i), color=(80,80,80), thickness=1)
            
                        dpg.add_text('Note', pos = (975,444), color =(0,150,0))
                        dpg.add_text('Scale Offset', pos = (1070,440), color =(0,150,0))
                        dpg.add_text('BP 1', pos = (924,462))
                        dpg.add_combo(tag = 'el3_filter1_env_bp1', width=60, items = notelist, callback= elfilter12envbp, pos = (960,462), height_mode = 2) 
                        dpg.add_slider_int(no_input = True,tag = 'el3_filter1_env_sc_off_1', label='', width=144, max_value=127, min_value=-127, callback= elfilter12envscoff, pos = (1036,462))
                        dpg.add_text('BP 2', pos = (924,487))
                        dpg.add_combo(tag = 'el3_filter1_env_bp2', width=60, items = notelist, callback= elfilter12envbp, pos = (960,487), height_mode = 2) 
                        dpg.add_slider_int(no_input = True,tag = 'el3_filter1_env_sc_off_2', label='', width=144, max_value=127, min_value=-127, callback= elfilter12envscoff, pos = (1036,487))
                        dpg.add_text('BP 3', pos = (924,512))
                        dpg.add_combo(tag = 'el3_filter1_env_bp3', width=60, items = notelist, callback= elfilter12envbp, pos = (960,512), height_mode = 2) 
                        dpg.add_slider_int(no_input = True,tag = 'el3_filter1_env_sc_off_3', label='', width=144, max_value=127, min_value=-127, callback= elfilter12envscoff, pos = (1036,512))
                        dpg.add_text('BP 4', pos = (924,537))
                        dpg.add_combo(tag = 'el3_filter1_env_bp4', width=60, items = notelist, callback= elfilter12envbp, pos = (960,537), height_mode = 2) 
                        dpg.add_slider_int(no_input = True,tag = 'el3_filter1_env_sc_off_4', label='', width=144, max_value=127, min_value=-127, callback= elfilter12envscoff, pos = (1036,537))

                    with dpg.tab(label='FILTER 2', tag = 'el3_FILTER2',show = True):
                        dpg.add_text('Cutoff', pos = (24-8,419+131))
                        dpg.add_slider_int(no_input = True,tag = 'el3_filter2_cutoff', height=130, vertical = True, max_value=127, default_value=0,callback= elfilter12cutoff, pos = (24,419))
                        dpg.add_text('Filter type', pos = (77,415))
                        dpg.add_slider_int(no_input = True,tag = 'el3_filter2_type', width=40, max_value=1, default_value=1,callback= elfilter12type, pos = (77,415+20),format= f'') 
                        dpg.add_text('LPF', tag = 'el3_filter2_type_value',  pos = (77,435+20), color =(0,150,0))   
                        dpg.add_image('LPF', pos = (77+30,435+23), width = 30,height = 13, tag = 'el3_LPF2_img', show = True)
                        dpg.add_image('NOFILTER', pos = (77+30,435+23), width = 30,height = 13, tag = 'el3_NOFILTER2_img', show = False)
                        dpg.add_text('Filter mode', pos = (77,35+460))
                        dpg.add_slider_int(no_input = True,tag = 'el3_filter2_mode', width=60, max_value=2, default_value=0,callback= elfilter12mode, pos = (77,35+480),format= f'')
                        dpg.add_text('  EG', tag = 'el3_filter2_mode_value',  pos = (77+13,35+500), color =(0,150,0)) 
                        dpg.add_text('FEG Rate Scale', pos = (520,418))
                        dpg.add_slider_int(no_input = True,tag = 'el3_filter2_env_rate_scale', label='', width=110, max_value=7, min_value = -7, callback= elfilter12envratescale, pos = (519,438))
                        dpg.add_text('Filter Envelope',  pos = (670,550))  
                        for i in range(len(filterenvlist)):
                            if 'L' in filterenvlist[i]:
                                dpg.add_slider_int(no_input = True,tag = 'el3_filter2_env_'+filterenvlist[i], vertical = True, height=130, max_value=63, min_value =-64, default_value=0,callback= elfilter12envelope, pos = (170+i*25,420))
                            else:
                                dpg.add_slider_int(no_input = True,tag = 'el3_filter2_env_'+filterenvlist[i], vertical = True, height=130, max_value=63, default_value=0,callback= elfilter12envelope, pos = (170+i*25,420))
                            dpg.add_text(filterenvlist[i],tag = 'el3_filter2env'+str(i),pos = ((183+i*25)-int(4*len(filterenvlist[i])),420+134))

                        dpg.add_text('Filter Env Breakpoints', pos = (996,410))
                        with dpg.drawlist(width=1000, height=150):
                            linecolor = (60,70,65)
                            #### FILTER ENVELOPE LINES
                            dpg.draw_rectangle((FilterHini-5,FilterVini-5),(FilterHini+(6*VHSum)+5,FilterVini+VHSum+5), color=(50,50,50,255), thickness=2, fill = (100,120,0,255))
                            dpg.draw_line((FilterHini,FilterVini+VHSum/2),(FilterHini+VHSum,FilterVini+VHSum/2),tag = 'el3_filter2_R1', color=linecolor, thickness=2)
                            dpg.draw_line((FilterHini+VHSum,FilterVini+VHSum/2),(FilterHini+(2*VHSum),FilterVini+VHSum/2),tag = 'el3_filter2_R2', color=linecolor, thickness=2)
                            dpg.draw_line((FilterHini+(2*VHSum),FilterVini+VHSum/2),(FilterHini+(3*VHSum),FilterVini+VHSum/2),tag = 'el3_filter2_R3', color=linecolor, thickness=2)
                            dpg.draw_line((FilterHini+(3*VHSum),FilterVini+VHSum/2),(FilterHini+(4*VHSum),FilterVini+VHSum/2),tag = 'el3_filter2_R4', color=linecolor, thickness=2)
                            dpg.draw_line((FilterHini+(4*VHSum),FilterVini+VHSum/2),(FilterHini+(5*VHSum),FilterVini+VHSum/2),tag = 'el3_filter2_RR1', color=linecolor, thickness=2)
                            dpg.draw_line((FilterHini+(5*VHSum),FilterVini+VHSum/2),(FilterHini+(6*VHSum),FilterVini+VHSum/2),tag = 'el3_filter2_RR2', color=linecolor, thickness=2)
                            for i in range(FilterVini,FilterVini+VHSum,8):
                                dpg.draw_line((FilterHini+(4*VHSum),i),(FilterHini+(4*VHSum),i+4),tag = 'el3_filter2_RE'+str(i), color=(80,80,80), thickness=1)
                        dpg.add_text('Note', pos = (975,444), color =(0,150,0))
                        dpg.add_text('Scale Offset', pos = (1070,440), color =(0,150,0))
                        dpg.add_text('BP 1', pos = (924,462))
                        dpg.add_combo(tag = 'el3_filter2_env_bp1', width=60, items = notelist, callback= elfilter12envbp, pos = (960,462), height_mode = 2) 
                        dpg.add_slider_int(no_input = True,tag = 'el3_filter2_env_sc_off_1', label='', width=144, max_value=127, min_value=-127, callback= elfilter12envscoff, pos = (1036,462))
                        dpg.add_text('BP 2', pos = (924,487))
                        dpg.add_combo(tag = 'el3_filter2_env_bp2', width=60, items = notelist, callback= elfilter12envbp, pos = (960,487), height_mode = 2) 
                        dpg.add_slider_int(no_input = True,tag = 'el3_filter2_env_sc_off_2', label='', width=144, max_value=127, min_value=-127, callback= elfilter12envscoff, pos = (1036,487))
                        dpg.add_text('BP 3', pos = (924,512))
                        dpg.add_combo(tag = 'el3_filter2_env_bp3', width=60, items = notelist, callback= elfilter12envbp, pos = (960,512), height_mode = 2) 
                        dpg.add_slider_int(no_input = True,tag = 'el3_filter2_env_sc_off_3', label='', width=144, max_value=127, min_value=-127, callback= elfilter12envscoff, pos = (1036,512))
                        dpg.add_text('BP 4', pos = (924,537))
                        dpg.add_combo(tag = 'el3_filter2_env_bp4', width=60, items = notelist, callback= elfilter12envbp, pos = (960,537), height_mode = 2) 
                        dpg.add_slider_int(no_input = True,tag = 'el3_filter2_env_sc_off_4', label='', width=144, max_value=127, min_value=-127, callback= elfilter12envscoff, pos = (1036,537))

                    with dpg.tab(label='FILTER 1+2', tag = 'el3_FILTER12',show = True):
                        dpg.add_text('Reso', pos = (24-4,419+131))
                        dpg.add_slider_int(no_input = True,tag = 'el3_filter1_reso', height=130, vertical = True, max_value=99, default_value=0,callback= elfilter12reso, pos = (24,419))
                        dpg.add_text('Filter Vel Sens', pos = (filtervelsensknobx-10,filtervelsensknoby+46))
                        dpg.add_image_button('KNOB', tag = 'el3_filtervelsens_knob',pos = (filtervelsensknobx,filtervelsensknoby), width = 48, height = 48)
                        dpg.add_image('DOT', tag = 'el3_filtervelsens_dot',pos = (filtervelsensknobx+20,filtervelsensknoby+5),width = 8, height = 8)
                        dpg.add_text('0', tag = 'el3_filtervelsens_value',  pos = (filtervelsensknobx+20,filtervelsensknoby-20))
                        dpg.add_text('Filter Mod Sens', pos = (filtermodsensknobx-16,filtermodsensknoby+46))
                        dpg.add_image_button('KNOB', tag = 'el3_filtermodsens_knob',pos = (filtermodsensknobx,filtermodsensknoby), width = 48, height = 48)
                        dpg.add_image('DOT', tag = 'el3_filtermodsens_dot',pos = (filtermodsensknobx+20,filtermodsensknoby+5),width = 8, height = 8)
                        dpg.add_text('0', tag = 'el3_filtermodsens_value',  pos = (filtermodsensknobx+20,filtermodsensknoby-20))

                dpg.add_text('Note Limit/L:', pos = (20,604))
                dpg.add_combo(tag = 'el3_note_limitL', label='', width=100, items = notelist, callback= elnotelimitL, pos = (20,624), height_mode = 2 ) 
                dpg.add_text('Note Limit/H:', pos = (140,604))
                dpg.add_combo(tag = 'el3_note_limitH', label='', width=100, items = notelist, callback= elnotelimitH, pos = (140,624), height_mode = 2 ) 
                dpg.add_text('Vel. Limit/L:', pos = (260,604))
                dpg.add_slider_int(no_input = True,tag = 'el3_vel_limitL', label='', width=100, max_value=127, min_value=1, callback= elvellimitL, pos = (260,624)) 
                dpg.add_text('Vel. Limit/H:', pos = (380,604))
                dpg.add_slider_int(no_input = True,tag = 'el3_vel_limitH', label='', width=100, max_value=127, min_value=1, callback= elvellimitH, pos = (380,624)) 
                dpg.add_text('LFO Wave:', pos = (514,604))
                dpg.add_slider_int(no_input = True,tag = 'el3_lfo_wave', width=100, max_value=5, default_value=0,callback= ellfowave, pos = (514,624),format= f'')
                dpg.add_text('TRI', tag = 'el3_lfo_wave_value',  pos = (514,646), color =(0,150,0)) 
                dpg.add_image('TRI', pos = (543,648), width = 40,height = 14, tag = 'el3_TRI_img', show = True)
                for i in range(6,11):
                    dpg.add_image(imageslist[i], pos = (543,648), width = 40,height = 14, tag = 'el3_'+imageslist[i]+'_img', show = False)
                dpg.add_text('LFO Speed', pos = (lfospeedknobx-8,lfospeedknoby+46))
                dpg.add_image_button('KNOB', tag = 'el3_lfospeed_knob',pos = (lfospeedknobx,lfospeedknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el3_lfospeed_dot',pos = (lfospeedknobx+13.3,lfospeedknoby+33.3),width = 8, height = 8)
                dpg.add_text('0', tag = 'el3_lfospeed_value',  pos = (lfospeedknobx+20,lfospeedknoby-20))
                dpg.add_text('LFO Delay', pos = (lfodelayknobx-8,lfodelayknoby+46))
                dpg.add_image_button('KNOB', tag = 'el3_lfodelay_knob',pos = (lfodelayknobx,lfodelayknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el3_lfodelay_dot',pos = (lfodelayknobx+13.3,lfodelayknoby+33.3),width = 8, height = 8)
                dpg.add_text('0', tag = 'el3_lfodelay_value',  pos = (lfodelayknobx+20,lfodelayknoby-20))
                dpg.add_text('LFO Phase', pos = (lfophaseknobx-8,lfophaseknoby+46))
                dpg.add_image_button('KNOB', tag = 'el3_lfophase_knob',pos = (lfophaseknobx,lfophaseknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el3_lfophase_dot',pos = (lfophaseknobx+13.3,lfophaseknoby+33.3),width = 8, height = 8)
                dpg.add_text('0', tag = 'el3_lfophase_value',  pos = (lfophaseknobx+20,lfophaseknoby-20))
                dpg.add_text('LFO Amp Mod', pos = (lfoampmodknobx-17,lfoampmodknoby+46))
                dpg.add_image_button('KNOB', tag = 'el3_lfoampmod_knob',pos = (lfoampmodknobx,lfoampmodknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el3_lfoampmod_dot',pos = (lfoampmodknobx+13.3,lfoampmodknoby+33.3),width = 8, height = 8)
                dpg.add_text('0', tag = 'el3_lfoampmod_value',  pos = (lfoampmodknobx+20,lfoampmodknoby-20))
                dpg.add_text('LFO Pitch Mod', pos = (lfopitchmodknobx-17,lfopitchmodknoby+46))
                dpg.add_image_button('KNOB', tag = 'el3_lfopitchmod_knob',pos = (lfopitchmodknobx,lfopitchmodknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el3_lfopitchmod_dot',pos = (lfopitchmodknobx+13.3,lfopitchmodknoby+33.3),width = 8, height = 8)
                dpg.add_text('0', tag = 'el3_lfopitchmod_value',  pos = (lfopitchmodknobx+20,lfopitchmodknoby-20))
                dpg.add_text('LFO Cutoff Mod', pos = (lfocutoffmodknobx-17,lfocutoffmodknoby+46))
                dpg.add_image_button('KNOB', tag = 'el3_lfocutoffmod_knob',pos = (lfocutoffmodknobx,lfocutoffmodknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el3_lfocutoffmod_dot',pos = (lfocutoffmodknobx+13.3,lfocutoffmodknoby+33.3),width = 8, height = 8)
                dpg.add_text('0', tag = 'el3_lfocutoffmod_value',  pos = (lfocutoffmodknobx+20,lfocutoffmodknoby-20))

                #### SEPARATORS BOTTOM
                with dpg.drawlist(width=1600, height=311):    
                    dpg.draw_line((0,10),(1600,10), color=(60,60,60,255), thickness=1)
                    dpg.draw_line((490,10),(490,128), color=(60,60,60,255), thickness=1)

            ################################################### ELEMENT 4 #######################################################
            with dpg.tab(label=' ELEMENT 4 ',tag = 'el4_tab'):
                dpg.add_slider_int(no_input = True,tag = 'el4_volume', label='', vertical = True, height=130, max_value=127, callback= elementvol, pos = (24,45))
                dpg.add_text('Vol', pos = (24,175))
                dpg.add_text('Element 1\nEnable', pos = (63,43))
                dpg.add_checkbox(tag = 'el4_enable', label = '', callback = elementenable, pos = (63,78))
                dpg.set_value('el4_enable', True)
                dpg.add_text('On | Off', pos = (89,78), color =(0,150,0))
                dpg.add_image('REDLIGHT', pos = (66,81), width = 14,height = 14, tag = 'el4_enabled', show = True)
                dpg.add_text('Pan', pos = (panknobx+13,panknoby+47))
                dpg.add_image_button('KNOB', tag = 'el4_pan_knob',pos = (panknobx,panknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el4_pan_dot',pos = (panknobx+20,panknoby+5),width = 8, height = 8)
                dpg.add_text('0', tag = 'el4_pan_value',  pos = (panknobx+20,panknoby-20))  
                dpg.add_text('Wave Select:', pos = (153,50))
                dpg.add_combo(tag = 'el4_Waveform', label = '', width = 107, items = voicelist,callback= AWMwaveform, pos = (152,70), height_mode = 2)
                dpg.add_text('EF Balance', pos = (efbalknobx-10,efbalknoby+47))
                dpg.add_image_button('KNOB', tag = 'el4_efbal_knob',pos = (efbalknobx,efbalknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el4_efbal_dot',pos = (efbalknobx+13.3,efbalknoby+33.3),width = 8, height = 8)
                dpg.add_text('0', tag = 'el4_efbal_value',  pos = (efbalknobx+20,efbalknoby-20))  
                dpg.add_text('AEG\nRate Sens', pos = (281,43))
                dpg.add_slider_int(no_input = True,tag = 'el4_amp_sens_vel_rate', width=40, max_value=1, callback= elsensvelrate, pos = (281,78),format= f'') 
                dpg.add_text('On | Off', pos = (281+47, 78), color =(0,150,0))
                dpg.add_text('Amp Vel Sens', pos = (ampvelsensknobx-16,ampvelsensknoby+47))
                dpg.add_image_button('KNOB', tag = 'el4_ampvelsens_knob',pos = (ampvelsensknobx,ampvelsensknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el4_ampvelsens_dot',pos = (ampvelsensknobx+20,ampvelsensknoby+5),width = 8, height = 8)
                dpg.add_text('0', tag = 'el4_ampvelsens_value',  pos = (ampvelsensknobx+20,ampvelsensknoby-20))  
                dpg.add_text('Amp Mod Sens', pos = (ampmodsensknobx-16,ampmodsensknoby+47))
                dpg.add_image_button('KNOB', tag = 'el4_ampmodsens_knob',pos = (ampmodsensknobx,ampmodsensknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el4_ampmodsens_dot',pos = (ampmodsensknobx+20,ampmodsensknoby+5),width = 8, height = 8)
                dpg.add_text('0', tag = 'el4_ampmodsens_value',  pos = (ampmodsensknobx+20,ampmodsensknoby-20))  
                dpg.add_text('Amp Envelope',  pos = (700,175))  
                for i in range(len(ampenvlist)):
                    dpg.add_slider_int(no_input = True,tag = 'el4_amp_env_'+ampenvlist[i], vertical = True, height=130, max_value=63, default_value=0,callback= elampenvelope, pos = (390+i*25,45))
                    dpg.add_text(ampenvlist[i],tag = 'el4_ampenv'+str(i), pos = (393+i*25,178))
                dpg.add_text('AEG Rate Scale', pos = (582,43))
                dpg.add_slider_int(no_input = True,tag = 'el4_amp_env_rate_scale', label='', width=120, max_value=7, min_value = -7, callback= ampenvratescale, pos = (581,63))
                dpg.add_text('AEG mode', pos = (780,43))
                dpg.add_slider_int(no_input = True,tag = 'el4_amp_env_mode', width=40, max_value=1, default_value=0,callback= elampenvmode, pos = (780,63),format= f'')
                dpg.add_text('Norm | Hold', tag = 'el4_amp_env_mode_value',  pos = (780+47,63), color =(0,150,0))
                dpg.add_text('Amp Env Breakpoints', pos = (1000,43))
                dpg.add_text('Note', pos = (975,70), color =(0,150,0))
                dpg.add_text('Scale Offset', pos = (1070,70), color =(0,150,0))
                dpg.add_text('BP 1', pos = (924,88))
                dpg.add_combo(tag = 'el4_amp_env_bp1', width=60, items = notelist, callback= elampenvbp, pos = (960,88), height_mode = 2) 
                dpg.add_slider_int(no_input = True,tag = 'el4_amp_env_sc_off_1', label='', width=144, max_value=127, min_value=-127, callback= elampenvscoff, pos = (1036,88))
                dpg.add_text('BP 2', pos = (924,113))
                dpg.add_combo(tag = 'el4_amp_env_bp2', width=60, items = notelist, callback= elampenvbp, pos = (960,113), height_mode = 2) 
                dpg.add_slider_int(no_input = True,tag = 'el4_amp_env_sc_off_2', label='', width=144, max_value=127, min_value=-127, callback= elampenvscoff, pos = (1036,113))
                dpg.add_text('BP 3', pos = (924,138))
                dpg.add_combo(tag = 'el4_amp_env_bp3', width=60, items = notelist, callback= elampenvbp, pos = (960,138), height_mode = 2) 
                dpg.add_slider_int(no_input = True,tag = 'el4_amp_env_sc_off_3', label='', width=144, max_value=127, min_value=-127, callback= elampenvscoff, pos = (1036,138))
                dpg.add_text('BP 4', pos = (924,163))
                dpg.add_combo(tag = 'el4_amp_env_bp4', width=60, items = notelist, callback= elampenvbp, pos = (960,163), height_mode = 2) 
                dpg.add_slider_int(no_input = True,tag = 'el4_amp_env_sc_off_4', label='', width=144, max_value=127, min_value=-127, callback= elampenvscoff, pos = (1036,163))
                dpg.add_text('Note shift', pos = (noteshiftknobx-2,noteshiftknoby+46))
                dpg.add_image_button('KNOB', tag = 'el4_noteshift_knob',pos = (noteshiftknobx,noteshiftknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el4_noteshift_dot',pos = (noteshiftknobx+20,noteshiftknoby+5),width = 8, height = 8)
                dpg.add_text('0', tag = 'el4_noteshift_value',  pos = (noteshiftknobx+20,noteshiftknoby-20))  
                dpg.add_text('Detune', pos = (detuneknobx+4,detuneknoby+46))
                dpg.add_image_button('KNOB', tag = 'el4_detune_knob',pos = (detuneknobx,detuneknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el4_detune_dot',pos = (detuneknobx+20,detuneknoby+5),width = 8, height = 8)
                dpg.add_text('0', tag = 'el4_detune_value',  pos = (detuneknobx+20,detuneknoby-20))
                dpg.add_text('OSC Frq Mode', pos = (20,228))
                dpg.add_slider_int(no_input = True,tag = 'el4_osc_freq_mode', width=40, max_value=1, callback= eloscfreqmode, pos = (20,248),format= f'') 
                dpg.add_text('Norm | Fix', pos = (20+47, 248), color =(0,150,0))
                dpg.add_text('OSC Frq Note', pos = (20,310))
                dpg.add_combo(tag = 'el4_osc_freq_note', label='', width=105, items = notelist, callback= eloscfreqnote, pos = (20,330), height_mode = 2, enabled = False) 
                dpg.add_text('OSC Frq Tune', pos = (oscfreqtuneknobx-16,oscfreqtuneknoby+46))
                dpg.add_image_button('KNOB', tag = 'el4_oscfreqtune_knob',pos = (oscfreqtuneknobx,oscfreqtuneknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el4_oscfreqtune_dot',pos = (oscfreqtuneknobx+20,oscfreqtuneknoby+5),width = 8, height = 8)
                dpg.add_text('0', tag = 'el4_oscfreqtune_value',  pos = (oscfreqtuneknobx+20,oscfreqtuneknoby-20))
                dpg.add_text('Pitch Mod Sens', pos = (pitchmodsensknobx-19,pitchmodsensknoby+46))
                dpg.add_image_button('KNOB', tag = 'el4_pitchmodsens_knob',pos = (pitchmodsensknobx,pitchmodsensknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el4_pitchmodsens_dot',pos = (pitchmodsensknobx+13.3,pitchmodsensknoby+33.3),width = 8, height = 8)
                dpg.add_text('0', tag = 'el4_pitchmodsens_value',  pos = (pitchmodsensknobx+20,pitchmodsensknoby-20), color =(0,0,0,0))
                dpg.add_text('0', tag = 'el4_pitchmodsens_valuex',  pos = (pitchmodsensknobx+20,pitchmodsensknoby-20))
                dpg.add_text('Pitch Envelope',  pos = (700,356))  
                for i in range(len(pitchenvlist)):
                    if 'L' in pitchenvlist[i]:
                        dpg.add_slider_int(no_input = True,tag = 'el4_pitch_env_'+pitchenvlist[i], vertical = True, height=130, max_value=63, min_value =-64, default_value=0,callback= elpitchenvelope, pos = (339+i*25,226))
                    else:
                        dpg.add_slider_int(no_input = True,tag = 'el4_pitch_env_'+pitchenvlist[i], vertical = True, height=130, max_value=63, default_value=0,callback= elpitchenvelope, pos = (339+i*25,226))
                    dpg.add_text(pitchenvlist[i],tag = 'el4_pitchenv'+str(i), pos = (343+i*25,359))
                dpg.add_text('PEG Range', pos = (582,224))
                dpg.add_slider_int(no_input = True,tag = 'el4_pitch_env_range', label='', width=60, max_value=2, callback= elpitchenvrange, pos = (581,244),format= f'')
                dpg.add_text('1/2oct', tag = 'el4_pitch_env_range_value', pos = (646,244), color =(0,150,0))
                dpg.add_text('PEG Rate Scale', pos = (693,224))
                dpg.add_slider_int(no_input = True,tag = 'el4_pitch_env_rate_scale', label='', width=110, max_value=7, min_value = -7, callback= elpitchenvratescale, pos = (692,244))
                dpg.add_text('PEG Vel SW', pos = (816,224))
                dpg.add_slider_int(no_input = True,tag = 'el4_pitch_env_vel_sw', width=40, max_value=1, default_value=0,callback= elpitchenvvelsw, pos = (816,244),format= f'')
                dpg.add_text('On | Off', tag = 'el4_pitch_env_vel_sw_value',  pos = (816+47,244), color =(0,150,0))

                ######### DRAWING
                with dpg.drawlist(width=1600, height=342):
                    linecolor = (60,70,65)

                    #### AMP ENVELOPE LINES
                    dpg.draw_rectangle((AmpHini-5,AmpVini-5),(AmpHini+(5*VHSum)+5,AmpVini+VHSum+5), color=(50,50,50,255), thickness=2, fill = (100,120,0,255))
                    dpg.draw_line((AmpHini,AmpVini+VHSum),(AmpHini+VHSum,AmpVini),tag = 'el4_amp_R1', color=linecolor, thickness=2)
                    dpg.draw_line((AmpHini+VHSum,AmpVini),(AmpHini+(2*VHSum),AmpVini+VHSum),tag = 'el4_amp_R2', color=linecolor, thickness=2)
                    dpg.draw_line((AmpHini+(2*VHSum),AmpVini+VHSum),(AmpHini+(3*VHSum),AmpVini+VHSum),tag = 'el4_amp_R3', color=linecolor, thickness=2)
                    dpg.draw_line((AmpHini+(3*VHSum),AmpVini+VHSum),(AmpHini+(4*VHSum),AmpVini+VHSum),tag = 'el4_amp_R4', color=linecolor, thickness=2)
                    dpg.draw_line((AmpHini+(4*VHSum),AmpVini+VHSum),(AmpHini+(5*VHSum),AmpVini+VHSum),tag = 'el4_amp_RR', color=linecolor, thickness=2)
                    for i in range(AmpVini,AmpVini+VHSum,8):
                        dpg.draw_line((AmpHini+(4*VHSum),i),(AmpHini+(4*VHSum),i+4),tag = 'el4_amp_RE'+str(i), color=(80,80,80), thickness=1)

                    #### PITCH ENVELOPE LINES
                    dpg.draw_rectangle((PitchHini-5,PitchVini-5),(PitchHini+(5*VHSum)+5,PitchVini+VHSum+5), color=(50,50,50,255), thickness=2, fill = (100,120,0,255))
                    dpg.draw_line((PitchHini,PitchVini+VHSum/2),(PitchHini+VHSum,PitchVini+VHSum/2),tag = 'el4_pitch_R1', color=linecolor, thickness=2)
                    dpg.draw_line((PitchHini+VHSum,PitchVini+VHSum/2),(PitchHini+(2*VHSum),PitchVini+VHSum/2),tag = 'el4_pitch_R2', color=linecolor, thickness=2)
                    dpg.draw_line((PitchHini+(2*VHSum),PitchVini+VHSum/2),(PitchHini+(3*VHSum),PitchVini+VHSum/2),tag = 'el4_pitch_R3', color=linecolor, thickness=2)
                    dpg.draw_line((PitchHini+(3*VHSum),PitchVini+VHSum/2),(PitchHini+(4*VHSum),PitchVini+VHSum/2),tag = 'el4_pitch_RR', color=linecolor, thickness=2)
                    for i in range(PitchVini,PitchVini+VHSum,8):
                        dpg.draw_line((PitchHini+(3*VHSum),i),(PitchHini+(3*VHSum),i+4),tag = 'el4_pitch_RE'+str(i), color=(80,80,80), thickness=1)

                    #### ELEMENT LINES
                    dpg.draw_line((0,170),(1600,170), thickness=1, color = (60,60,60,255))

                    ########## FILTER TABS
                with dpg.tab_bar(show = True):
                    with dpg.tab(label='FILTER 1', tag = 'el4_FILTER1',show = True):
                        dpg.add_text('Cutoff', pos = (24-8,419+131))
                        dpg.add_slider_int(no_input = True,tag = 'el4_filter1_cutoff', height=130, vertical = True, max_value=127, default_value=0,callback= elfilter12cutoff, pos = (24,419))
                        dpg.add_text('Filter type', pos = (77,415))
                        dpg.add_slider_int(no_input = True,tag = 'el4_filter1_type', width=60, max_value=2, default_value=1,callback= elfilter12type, pos = (77,415+20),format= f'') 
                        dpg.add_text('LPF', tag = 'el4_filter1_type_value',  pos = (77,435+20), color =(0,150,0))   
                        dpg.add_image('LPF', pos = (77+30,435+23), width = 30,height = 13, tag = 'el4_LPF1_img', show = True)
                        dpg.add_image('HPF', pos = (77+30,435+23), width = 30,height = 13, tag = 'el4_HPF1_img', show = False)
                        dpg.add_image('NOFILTER', pos = (77+30,435+23), width = 30,height = 13, tag = 'el4_NOFILTER1_img', show = False)
                        dpg.add_text('Filter mode', pos = (77,35+460))
                        dpg.add_slider_int(no_input = True,tag = 'el4_filter1_mode', width=60, max_value=2, default_value=0,callback= elfilter12mode, pos = (77,35+480),format= f'')
                        dpg.add_text('  EG', tag = 'el4_filter1_mode_value',  pos = (77+13,35+500), color =(0,150,0)) 
                        dpg.add_text('FEG Rate Scale', pos = (520,418))
                        dpg.add_slider_int(no_input = True,tag = 'el4_filter1_env_rate_scale', label='', width=110, max_value=7, min_value = -7, callback= elfilter12envratescale, pos = (519,438))
                        dpg.add_text('Filter Envelope',  pos = (670,550))  
                        for i in range(len(filterenvlist)):
                            if 'L' in filterenvlist[i]:
                                dpg.add_slider_int(no_input = True,tag = 'el4_filter1_env_'+filterenvlist[i], vertical = True, height=130, max_value=63, min_value =-64, default_value=0,callback= elfilter12envelope, pos = (170+i*25,420))
                            else:
                                dpg.add_slider_int(no_input = True,tag = 'el4_filter1_env_'+filterenvlist[i], vertical = True, height=130, max_value=63, default_value=0,callback= elfilter12envelope, pos = (170+i*25,420))
                            dpg.add_text(filterenvlist[i],tag = 'el4_filter1env'+str(i),pos = ((183+i*25)-int(4*len(filterenvlist[i])),420+134))
                        dpg.add_text('Filter Env Breakpoints', pos = (996,410))

                        #### FILTER ENVELOPE LINES
                        with dpg.drawlist(width=1000, height=150):
                            linecolor = (60,70,65)
                            dpg.draw_rectangle((FilterHini-5,FilterVini-5),(FilterHini+(6*VHSum)+5,FilterVini+VHSum+5), color=(50,50,50,255), thickness=2, fill = (100,120,0,255))
                            dpg.draw_line((FilterHini,FilterVini+VHSum/2),(FilterHini+VHSum,FilterVini+VHSum/2),tag = 'el4_filter1_R1', color=linecolor, thickness=2)
                            dpg.draw_line((FilterHini+VHSum,FilterVini+VHSum/2),(FilterHini+(2*VHSum),FilterVini+VHSum/2),tag = 'el4_filter1_R2', color=linecolor, thickness=2)
                            dpg.draw_line((FilterHini+(2*VHSum),FilterVini+VHSum/2),(FilterHini+(3*VHSum),FilterVini+VHSum/2),tag = 'el4_filter1_R3', color=linecolor, thickness=2)
                            dpg.draw_line((FilterHini+(3*VHSum),FilterVini+VHSum/2),(FilterHini+(4*VHSum),FilterVini+VHSum/2),tag = 'el4_filter1_R4', color=linecolor, thickness=2)
                            dpg.draw_line((FilterHini+(4*VHSum),FilterVini+VHSum/2),(FilterHini+(5*VHSum),FilterVini+VHSum/2),tag = 'el4_filter1_RR1', color=linecolor, thickness=2)
                            dpg.draw_line((FilterHini+(5*VHSum),FilterVini+VHSum/2),(FilterHini+(6*VHSum),FilterVini+VHSum/2),tag = 'el4_filter1_RR2', color=linecolor, thickness=2)
                            for i in range(FilterVini,FilterVini+VHSum,8):
                                dpg.draw_line((FilterHini+(4*VHSum),i),(FilterHini+(4*VHSum),i+4),tag = 'el4_filter1_RE'+str(i), color=(80,80,80), thickness=1)
            
                        dpg.add_text('Note', pos = (975,444), color =(0,150,0))
                        dpg.add_text('Scale Offset', pos = (1070,440), color =(0,150,0))
                        dpg.add_text('BP 1', pos = (924,462))
                        dpg.add_combo(tag = 'el4_filter1_env_bp1', width=60, items = notelist, callback= elfilter12envbp, pos = (960,462), height_mode = 2) 
                        dpg.add_slider_int(no_input = True,tag = 'el4_filter1_env_sc_off_1', label='', width=144, max_value=127, min_value=-127, callback= elfilter12envscoff, pos = (1036,462))
                        dpg.add_text('BP 2', pos = (924,487))
                        dpg.add_combo(tag = 'el4_filter1_env_bp2', width=60, items = notelist, callback= elfilter12envbp, pos = (960,487), height_mode = 2) 
                        dpg.add_slider_int(no_input = True,tag = 'el4_filter1_env_sc_off_2', label='', width=144, max_value=127, min_value=-127, callback= elfilter12envscoff, pos = (1036,487))
                        dpg.add_text('BP 3', pos = (924,512))
                        dpg.add_combo(tag = 'el4_filter1_env_bp3', width=60, items = notelist, callback= elfilter12envbp, pos = (960,512), height_mode = 2) 
                        dpg.add_slider_int(no_input = True,tag = 'el4_filter1_env_sc_off_3', label='', width=144, max_value=127, min_value=-127, callback= elfilter12envscoff, pos = (1036,512))
                        dpg.add_text('BP 4', pos = (924,537))
                        dpg.add_combo(tag = 'el4_filter1_env_bp4', width=60, items = notelist, callback= elfilter12envbp, pos = (960,537), height_mode = 2) 
                        dpg.add_slider_int(no_input = True,tag = 'el4_filter1_env_sc_off_4', label='', width=144, max_value=127, min_value=-127, callback= elfilter12envscoff, pos = (1036,537))

                    with dpg.tab(label='FILTER 2', tag = 'el4_FILTER2',show = True):
                        dpg.add_text('Cutoff', pos = (24-8,419+131))
                        dpg.add_slider_int(no_input = True,tag = 'el4_filter2_cutoff', height=130, vertical = True, max_value=127, default_value=0,callback= elfilter12cutoff, pos = (24,419))
                        dpg.add_text('Filter type', pos = (77,415))
                        dpg.add_slider_int(no_input = True,tag = 'el4_filter2_type', width=40, max_value=1, default_value=1,callback= elfilter12type, pos = (77,415+20),format= f'') 
                        dpg.add_text('LPF', tag = 'el4_filter2_type_value',  pos = (77,435+20), color =(0,150,0))   
                        dpg.add_image('LPF', pos = (77+30,435+23), width = 30,height = 13, tag = 'el4_LPF2_img', show = True)
                        dpg.add_image('NOFILTER', pos = (77+30,435+23), width = 30,height = 13, tag = 'el4_NOFILTER2_img', show = False)
                        dpg.add_text('Filter mode', pos = (77,35+460))
                        dpg.add_slider_int(no_input = True,tag = 'el4_filter2_mode', width=60, max_value=2, default_value=0,callback= elfilter12mode, pos = (77,35+480),format= f'')
                        dpg.add_text('  EG', tag = 'el4_filter2_mode_value',  pos = (77+13,35+500), color =(0,150,0)) 
                        dpg.add_text('FEG Rate Scale', pos = (520,418))
                        dpg.add_slider_int(no_input = True,tag = 'el4_filter2_env_rate_scale', label='', width=110, max_value=7, min_value = -7, callback= elfilter12envratescale, pos = (519,438))
                        dpg.add_text('Filter Envelope',  pos = (670,550))  
                        for i in range(len(filterenvlist)):
                            if 'L' in filterenvlist[i]:
                                dpg.add_slider_int(no_input = True,tag = 'el4_filter2_env_'+filterenvlist[i], vertical = True, height=130, max_value=63, min_value =-64, default_value=0,callback= elfilter12envelope, pos = (170+i*25,420))
                            else:
                                dpg.add_slider_int(no_input = True,tag = 'el4_filter2_env_'+filterenvlist[i], vertical = True, height=130, max_value=63, default_value=0,callback= elfilter12envelope, pos = (170+i*25,420))
                            dpg.add_text(filterenvlist[i],tag = 'el4_filter2env'+str(i),pos = ((183+i*25)-int(4*len(filterenvlist[i])),420+134))

                        dpg.add_text('Filter Env Breakpoints', pos = (996,410))
                        with dpg.drawlist(width=1000, height=150):
                            linecolor = (60,70,65)
                            #### FILTER ENVELOPE LINES
                            dpg.draw_rectangle((FilterHini-5,FilterVini-5),(FilterHini+(6*VHSum)+5,FilterVini+VHSum+5), color=(50,50,50,255), thickness=2, fill = (100,120,0,255))
                            dpg.draw_line((FilterHini,FilterVini+VHSum/2),(FilterHini+VHSum,FilterVini+VHSum/2),tag = 'el4_filter2_R1', color=linecolor, thickness=2)
                            dpg.draw_line((FilterHini+VHSum,FilterVini+VHSum/2),(FilterHini+(2*VHSum),FilterVini+VHSum/2),tag = 'el4_filter2_R2', color=linecolor, thickness=2)
                            dpg.draw_line((FilterHini+(2*VHSum),FilterVini+VHSum/2),(FilterHini+(3*VHSum),FilterVini+VHSum/2),tag = 'el4_filter2_R3', color=linecolor, thickness=2)
                            dpg.draw_line((FilterHini+(3*VHSum),FilterVini+VHSum/2),(FilterHini+(4*VHSum),FilterVini+VHSum/2),tag = 'el4_filter2_R4', color=linecolor, thickness=2)
                            dpg.draw_line((FilterHini+(4*VHSum),FilterVini+VHSum/2),(FilterHini+(5*VHSum),FilterVini+VHSum/2),tag = 'el4_filter2_RR1', color=linecolor, thickness=2)
                            dpg.draw_line((FilterHini+(5*VHSum),FilterVini+VHSum/2),(FilterHini+(6*VHSum),FilterVini+VHSum/2),tag = 'el4_filter2_RR2', color=linecolor, thickness=2)
                            for i in range(FilterVini,FilterVini+VHSum,8):
                                dpg.draw_line((FilterHini+(4*VHSum),i),(FilterHini+(4*VHSum),i+4),tag = 'el4_filter2_RE'+str(i), color=(80,80,80), thickness=1)
                        dpg.add_text('Note', pos = (975,444), color =(0,150,0))
                        dpg.add_text('Scale Offset', pos = (1070,440), color =(0,150,0))
                        dpg.add_text('BP 1', pos = (924,462))
                        dpg.add_combo(tag = 'el4_filter2_env_bp1', width=60, items = notelist, callback= elfilter12envbp, pos = (960,462), height_mode = 2) 
                        dpg.add_slider_int(no_input = True,tag = 'el4_filter2_env_sc_off_1', label='', width=144, max_value=127, min_value=-127, callback= elfilter12envscoff, pos = (1036,462))
                        dpg.add_text('BP 2', pos = (924,487))
                        dpg.add_combo(tag = 'el4_filter2_env_bp2', width=60, items = notelist, callback= elfilter12envbp, pos = (960,487), height_mode = 2) 
                        dpg.add_slider_int(no_input = True,tag = 'el4_filter2_env_sc_off_2', label='', width=144, max_value=127, min_value=-127, callback= elfilter12envscoff, pos = (1036,487))
                        dpg.add_text('BP 3', pos = (924,512))
                        dpg.add_combo(tag = 'el4_filter2_env_bp3', width=60, items = notelist, callback= elfilter12envbp, pos = (960,512), height_mode = 2) 
                        dpg.add_slider_int(no_input = True,tag = 'el4_filter2_env_sc_off_3', label='', width=144, max_value=127, min_value=-127, callback= elfilter12envscoff, pos = (1036,512))
                        dpg.add_text('BP 4', pos = (924,537))
                        dpg.add_combo(tag = 'el4_filter2_env_bp4', width=60, items = notelist, callback= elfilter12envbp, pos = (960,537), height_mode = 2) 
                        dpg.add_slider_int(no_input = True,tag = 'el4_filter2_env_sc_off_4', label='', width=144, max_value=127, min_value=-127, callback= elfilter12envscoff, pos = (1036,537))

                    with dpg.tab(label='FILTER 1+2', tag = 'el4_FILTER12',show = True):
                        dpg.add_text('Reso', pos = (24-4,419+131))
                        dpg.add_slider_int(no_input = True,tag = 'el4_filter1_reso', height=130, vertical = True, max_value=99, default_value=0,callback= elfilter12reso, pos = (24,419))
                        dpg.add_text('Filter Vel Sens', pos = (filtervelsensknobx-10,filtervelsensknoby+46))
                        dpg.add_image_button('KNOB', tag = 'el4_filtervelsens_knob',pos = (filtervelsensknobx,filtervelsensknoby), width = 48, height = 48)
                        dpg.add_image('DOT', tag = 'el4_filtervelsens_dot',pos = (filtervelsensknobx+20,filtervelsensknoby+5),width = 8, height = 8)
                        dpg.add_text('0', tag = 'el4_filtervelsens_value',  pos = (filtervelsensknobx+20,filtervelsensknoby-20))
                        dpg.add_text('Filter Mod Sens', pos = (filtermodsensknobx-16,filtermodsensknoby+46))
                        dpg.add_image_button('KNOB', tag = 'el4_filtermodsens_knob',pos = (filtermodsensknobx,filtermodsensknoby), width = 48, height = 48)
                        dpg.add_image('DOT', tag = 'el4_filtermodsens_dot',pos = (filtermodsensknobx+20,filtermodsensknoby+5),width = 8, height = 8)
                        dpg.add_text('0', tag = 'el4_filtermodsens_value',  pos = (filtermodsensknobx+20,filtermodsensknoby-20))

                dpg.add_text('Note Limit/L:', pos = (20,604))
                dpg.add_combo(tag = 'el4_note_limitL', label='', width=100, items = notelist, callback= elnotelimitL, pos = (20,624), height_mode = 2 ) 
                dpg.add_text('Note Limit/H:', pos = (140,604))
                dpg.add_combo(tag = 'el4_note_limitH', label='', width=100, items = notelist, callback= elnotelimitH, pos = (140,624), height_mode = 2 ) 
                dpg.add_text('Vel. Limit/L:', pos = (260,604))
                dpg.add_slider_int(no_input = True,tag = 'el4_vel_limitL', label='', width=100, max_value=127, min_value=1, callback= elvellimitL, pos = (260,624)) 
                dpg.add_text('Vel. Limit/H:', pos = (380,604))
                dpg.add_slider_int(no_input = True,tag = 'el4_vel_limitH', label='', width=100, max_value=127, min_value=1, callback= elvellimitH, pos = (380,624)) 
                dpg.add_text('LFO Wave:', pos = (514,604))
                dpg.add_slider_int(no_input = True,tag = 'el4_lfo_wave', width=100, max_value=5, default_value=0,callback= ellfowave, pos = (514,624),format= f'')
                dpg.add_text('TRI', tag = 'el4_lfo_wave_value',  pos = (514,646), color =(0,150,0)) 
                dpg.add_image('TRI', pos = (543,648), width = 40,height = 14, tag = 'el4_TRI_img', show = True)
                for i in range(6,11):
                    dpg.add_image(imageslist[i], pos = (543,648), width = 40,height = 14, tag = 'el4_'+imageslist[i]+'_img', show = False)
                dpg.add_text('LFO Speed', pos = (lfospeedknobx-8,lfospeedknoby+46))
                dpg.add_image_button('KNOB', tag = 'el4_lfospeed_knob',pos = (lfospeedknobx,lfospeedknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el4_lfospeed_dot',pos = (lfospeedknobx+13.3,lfospeedknoby+33.3),width = 8, height = 8)
                dpg.add_text('0', tag = 'el4_lfospeed_value',  pos = (lfospeedknobx+20,lfospeedknoby-20))
                dpg.add_text('LFO Delay', pos = (lfodelayknobx-8,lfodelayknoby+46))
                dpg.add_image_button('KNOB', tag = 'el4_lfodelay_knob',pos = (lfodelayknobx,lfodelayknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el4_lfodelay_dot',pos = (lfodelayknobx+13.3,lfodelayknoby+33.3),width = 8, height = 8)
                dpg.add_text('0', tag = 'el4_lfodelay_value',  pos = (lfodelayknobx+20,lfodelayknoby-20))
                dpg.add_text('LFO Phase', pos = (lfophaseknobx-8,lfophaseknoby+46))
                dpg.add_image_button('KNOB', tag = 'el4_lfophase_knob',pos = (lfophaseknobx,lfophaseknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el4_lfophase_dot',pos = (lfophaseknobx+13.3,lfophaseknoby+33.3),width = 8, height = 8)
                dpg.add_text('0', tag = 'el4_lfophase_value',  pos = (lfophaseknobx+20,lfophaseknoby-20))
                dpg.add_text('LFO Amp Mod', pos = (lfoampmodknobx-17,lfoampmodknoby+46))
                dpg.add_image_button('KNOB', tag = 'el4_lfoampmod_knob',pos = (lfoampmodknobx,lfoampmodknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el4_lfoampmod_dot',pos = (lfoampmodknobx+13.3,lfoampmodknoby+33.3),width = 8, height = 8)
                dpg.add_text('0', tag = 'el4_lfoampmod_value',  pos = (lfoampmodknobx+20,lfoampmodknoby-20))
                dpg.add_text('LFO Pitch Mod', pos = (lfopitchmodknobx-17,lfopitchmodknoby+46))
                dpg.add_image_button('KNOB', tag = 'el4_lfopitchmod_knob',pos = (lfopitchmodknobx,lfopitchmodknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el4_lfopitchmod_dot',pos = (lfopitchmodknobx+13.3,lfopitchmodknoby+33.3),width = 8, height = 8)
                dpg.add_text('0', tag = 'el4_lfopitchmod_value',  pos = (lfopitchmodknobx+20,lfopitchmodknoby-20))
                dpg.add_text('LFO Cutoff Mod', pos = (lfocutoffmodknobx-17,lfocutoffmodknoby+46))
                dpg.add_image_button('KNOB', tag = 'el4_lfocutoffmod_knob',pos = (lfocutoffmodknobx,lfocutoffmodknoby), width = 48, height = 48)
                dpg.add_image('DOT', tag = 'el4_lfocutoffmod_dot',pos = (lfocutoffmodknobx+13.3,lfocutoffmodknoby+33.3),width = 8, height = 8)
                dpg.add_text('0', tag = 'el4_lfocutoffmod_value',  pos = (lfocutoffmodknobx+20,lfocutoffmodknoby-20))

                #### SEPARATORS BOTTOM
                with dpg.drawlist(width=1600, height=311):    
                    dpg.draw_line((0,10),(1600,10), color=(60,60,60,255), thickness=1)
                    dpg.draw_line((490,10),(490,128), color=(60,60,60,255), thickness=1)

            ##################################################### DRUMS #########################################################
            with dpg.tab(label=' DRUMS ', tag = 'drums_tab'):
                posX = 60
                posX1 = 640
                for i in range(2):
                    pos = posX
                    if i == 1: pos = posX1
                    dpg.add_text('Wave', pos = (pos+20,36))
                    dpg.add_text('Volume', pos = (pos+95,36))
                    dpg.add_text('Note Shift', pos = (pos+170,36))
                    dpg.add_text('Tune', pos = (pos+262,36))
                    dpg.add_text('Alt Grp.', pos = (pos+323,36))
                    dpg.add_text('Pan', pos = (pos+397,36))
                    dpg.add_text('Efx Bal.', pos = (pos+467,36))

                for i in range (61):
                    posY = 55+(20*i)
                    if i > 30:
                        posY = 55+(20*(i-31))
                        posX = posX1
                    dpg.add_text(drumnotelist[i], tag = 'drumtext'+str(i), pos = ((posX-(len(drumnotelist[i])*7)),posY))
                    dpg.add_combo(tag = 'drums_Waveform'+str(i), label = '', width = 70, items = drumvoicelist,callback= drumwave, pos = (posX+3,posY), height_mode = 2)
                    dpg.add_slider_int(no_input = True,tag = 'drums_Volume'+str(i), max_value = 127, width = 70,callback= drumvolume, pos = (posX+83,posY))
                    dpg.add_drag_int(no_input = True, min_value = -48, max_value = 36, tag = 'drums_Noteshift'+str(i), speed = .5,width = 70,callback= drumnoteshift, pos = (posX+163,posY))
                    dpg.add_drag_int(no_input = True, min_value = -64, max_value = 63, tag = 'drums_Tune'+str(i), speed = .5,width = 70,callback= drumtune, pos = (posX+243,posY))
                    dpg.add_slider_int(no_input = True,tag = 'drums_Alt_Group'+str(i), width = 40,max_value = 1, callback= drumaltgroup, pos = (posX+323,posY), format = f'')
                    dpg.add_text('off   on', tag = 'drums_Alt_Group_Text'+str(i), pos = (posX+328,posY),color =(0,0,0))
                    dpg.add_slider_int(no_input = True,tag = 'drums_Pan'+str(i), width = 70,min_value = -31,max_value = 31, callback= drumpan, pos = (posX+373,posY))
                    dpg.add_slider_int(no_input = True,tag = 'drums_Efx_Balance'+str(i), width = 70,min_value = 0,max_value = 100, callback= drumfxbal, pos = (posX+453,posY))

            ################################################## CONTROLLERS ######################################################
            with dpg.tab(label=' CONTROLLERS ', tag = 'controllers'):

                dpg.add_text('Volume CC:', pos = (12,35))
                dpg.add_combo(tag = 'volume_cc', label='', width=130,  items = controllerlist, callback= volumecc, pos = (12,55), height_mode = 2)
                dpg.add_text('Volume Min.:', pos = (12,75))
                dpg.add_slider_int(no_input = True,tag = 'vol_min_rng', label='', width=130, max_value=127, callback= volumerngmin, pos = (12,95),) 

                dpg.add_text('Pitch Mod. CC:', tag = 'pitchmodcctext', pos = (170,35))
                dpg.add_combo(tag = 'pitch_mod_cc', label='', width=130,  items = controllerlist, callback= pitchmodcc, pos = (170,55), height_mode = 2)
                dpg.add_text('Pitch Mod. Range:',tag = 'pitchmodrngtext', pos = (170,75))
                dpg.add_slider_int(no_input = True,tag = 'pitch_mod_rng', label='', width=130, max_value=127, callback= pitchmodrng, pos = (170,95))

                dpg.add_text('Cutoff Mod. CC:', tag = 'cutoffmodcctext',pos = (328,35))
                dpg.add_combo(tag = 'cutoff_mod_cc', label='', width=130,  items = controllerlist, callback= cutoffmodcc, pos = (328,55), height_mode = 2)
                dpg.add_text('Cutoff. Mod. Range:', tag = 'cutoffmodrngtext', pos = (328,75))
                dpg.add_slider_int(no_input = True,tag = 'cutoff_mod_rng', label='', width=130, max_value=127, callback= cutoffmodrng, pos = (328,95))

                dpg.add_text('Cutoff Freq. CC:', tag = 'cutofffreqcctext', pos = (486,35))
                dpg.add_combo(tag = 'cutoff_freq_cc', label='', width=130,  items = controllerlist, callback= cutofffreqcc, pos = (486,55), height_mode = 2)
                dpg.add_text('Cutoff Freq. Range:', tag = 'cutofffreqrngtext', pos = (486,75))
                dpg.add_slider_int(no_input = True,tag = 'cutoff_freq_rng', label='', width=130, max_value=127, callback= cutofffreqrng, pos = (486,95))   

                dpg.add_text('Envelope Gen. Bias CC:', tag = 'envgenbiascctext', pos = (644,35))
                dpg.add_combo(tag = 'env_gen_bias_cc', label='', width=130,  items = controllerlist, callback= envgenbiascc, pos = (644,55), height_mode = 2)
                dpg.add_text('Envelope Gen. Range:', tag = 'envgenbiasrngtext', pos = (644,75))
                dpg.add_slider_int(no_input = True,tag = 'env_gen_rng', label='', width=130, max_value=127, callback= envgenrng, pos = (644,95)) 

                dpg.add_text('Amp. Mod. CC:', tag = 'ampmodcctext', pos = (802,35))
                dpg.add_combo(tag = 'amp_mod_cc', label='', width=130,  items = controllerlist, callback= ampmodcc, pos = (802,55), height_mode = 2)
                dpg.add_text('Amp. Mod. Range:', tag = 'ampmodrngtext' , pos = (802,75))
                dpg.add_slider_int(no_input = True,tag = 'amp_mod_rng', label='', width=130, max_value=127, callback= ampmodrng, pos = (802,95))

############################# POP UPS ##########################
# Errors
with dpg.window(label='Error', modal=True, show=False, tag='interface_error', no_title_bar=False):
    dpg.add_text('Please, select a midi port.')
    dpg.add_text('')
    dpg.add_button(label = 'ok', width = 60, callback = lambda: dpg.configure_item('interface_error', show=False))

with dpg.window(label='Error', modal=True, show=False, tag='midi_error', no_title_bar=False, pos =[500,300],width=(200)):
    dpg.add_text('midi error.')
    dpg.add_text('')
    dpg.add_button(label = 'ok', width = 60, callback = lambda: dpg.configure_item('midi_error', show=False) )

with dpg.window(label='Error', modal=True, show=False, tag='prefsio_error', no_title_bar=False, pos =[500,300],width=(200)):
    dpg.add_text('The lasy midi I/O config is not available.\n Select new midi I/O')
    dpg.add_text('')
    dpg.add_button(label = 'ok', width = 60, callback = lambda: dpg.configure_item('prefsio_error', show=False) )

with dpg.window(label='Error', modal=True, show=False, tag='load_error', no_title_bar=False, pos =[500,300],width=(200)):
    dpg.add_text('Invalid patch.')
    dpg.add_text('')
    dpg.add_button(label = 'ok', width = 60, callback = lambda: dpg.configure_item('load_error', show=False) )

with dpg.window(label='Error', modal=True, show=False, tag='drums_error', no_title_bar=False, pos =[450,300],width=(300)):
    dpg.add_text('Trying to load a drum-set patch in a voice preset.\n\nPlease select a drum-set preset and try again.')
    dpg.add_text('')
    dpg.add_button(label = 'ok', width = 60, callback = lambda: dpg.configure_item('drums_error', show=False) )

with dpg.window(label='Error', modal=True, show=False, tag='drums_error2', no_title_bar=False, pos =[450,300],width=(300)):
    dpg.add_text('Trying to load a voice patch in a drum-set preset.\n\nPlease select a voice preset and try again.')
    dpg.add_text('')
    dpg.add_button(label = 'ok', width = 60, callback = lambda: dpg.configure_item('drums_error2', show=False) )

# Confirmation
with dpg.window(label='Initializing patch', modal=True, show=False, tag='confirminitialize', no_title_bar=False, pos =[500,300],width=(200)):
    dpg.add_text('Do you want to continue?')
    dpg.add_text('')
    with dpg.group(horizontal=True):
        dpg.add_button(label = 'ok', width = 60, callback = initializepatchok)
        dpg.add_button(label = 'Cancel', width = 60, callback = lambda: dpg.configure_item('confirminitialize', show=False))

with dpg.window(label='Initializing element', modal=True, show=False, tag='elconfirminitialize', no_title_bar=False, pos =[500,300],width=(200)):
    dpg.add_text('Do you want to continue?')
    dpg.add_text('')
    with dpg.group(horizontal=True):
        dpg.add_button(label = 'ok', width = 60, callback = initializeelementok)
        dpg.add_button(label = 'Cancel', width = 60, callback = lambda: dpg.configure_item('elconfirminitialize', show=False))

# Manual  
manual = '''SY-55 VOICE EDITOR
-------------------------------

This software is intended to edit the Yamaha SY55 synthesizer voice and drum parameters.
It should work with the TG55, missing some of the features that belongs only to the TG55 as the multiple outputs, but it has been untested.
The multi mode, sequencer and utility controls cannot be accesed by this software.
There is no support for data nor waveform cards, since I don't have any of them to test.

Platform: The software is multi platform, but it has only been tested on intel mac.

--- USING THE SOFTWARE --- 

The software works in two different modes: Voice and drum set, having each of them different parameters to edit.
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
* When a midi input / output is selected, it is saved on the preferences and will be loaded everytime the software starts, unless another input / output is selected.

HELP: This menu.

--- CREDITS ---
Programming and testing: Carlo Bandini, 2024.
carlobandini@gmail.com

'''
with dpg.window(label='Manual', modal=True, show=False, tag='manual', no_title_bar=False, width =900, pos = [150,30]):
     dpg.add_text(manual)
     dpg.add_button(label = 'ok', width = 60, callback = lambda: dpg.configure_item('manual', show=False))

######################### ACTIVATE TAB 1 #######################
dpg.set_value(item='el1_tab', value=True)

######################## READ MIDI PREFS #######################
# check if prefs exist, if not, create one
if os.path.exists(prefdir) is False:
    F = open (prefdir,'w+')
    F.write('Not connected\nNot connected')
    F.close()

def readmidiprefs():
    global inport, outport, checkinport, checkoutport
    try:
        outport.close()
    except AttributeError:
        pass
    time.sleep(0.1)
    try:
        inport.close()
    except AttributeError:
        pass
    time.sleep(0.1)
    F = open(prefdir, 'r')
    data = F.readlines()
    # Read midi input device, if exists, connect it.
    if data[0] !='Not connected':
        for i in indevicelist:
            if i == data[0][:-1]:
                dpg.set_item_label('i'+i, '*** ' + i + ' ***')
                inport = mido.open_input(i)
                break
    # Read midi output device, if exists, connect it.
    if data[1] !='Not connected':
        for i in outdevicelist:
            if i == data[1][:-1]:
                dpg.set_item_label('o'+i, '*** ' + i + ' ***')
                outport = mido.open_output(i)
                break
    F.close()
    checkinport, checkoutport = str(inport), str(outport)
    time.sleep(0.1)

def checkmidiprefs():
    if checkinport != str(inport):
        readmidiprefs()
    elif checkoutport != str(outport):
        readmidiprefs()

readmidiprefs()

########################### READ PREFS #########################
def readprefs():
    F = open(prefdir, 'r')
    data = F.readlines()
    if data[2][:-1] == 'request on start':
        dpg.set_item_label('reqonstart','* Request on start')
        try:    
            # update midi prefs
            checkmidiprefs()
            requestvoice()
        except:
            return
    else:
        dpg.set_item_label('reqonstart','  Request on start')
        initializepatchok()
    F.close()
readprefs()
############################## THEME ###########################
with dpg.theme() as global_theme:
    with dpg.theme_component(dpg.mvAll):
        # Menu bar
        dpg.add_theme_color(dpg.mvThemeCol_MenuBarBg, (40, 40, 40), category=dpg.mvThemeCat_Core)
        # all widgets background
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (10, 10, 10), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (10, 10, 10), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (10, 10, 10), category=dpg.mvThemeCat_Core)
        # all borders
        dpg.add_theme_color(dpg.mvThemeCol_Border, (50, 50, 50), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, (30, 30, 30), category=dpg.mvThemeCat_Core)
        # Text
        dpg.add_theme_color(dpg.mvThemeCol_TextSelectedBg, (96, 110, 0), category=dpg.mvThemeCat_Core)
        # Combo box
        dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (64, 64, 64), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (64, 64, 64), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Header, (64, 64, 64), category=dpg.mvThemeCat_Core)
        # Tabs
        dpg.add_theme_color(dpg.mvThemeCol_TabHovered, (20, 100, 20), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_TabActive, (20, 100, 20), category=dpg.mvThemeCat_Core)
        # buttons and Combo box arrow
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (64, 64, 64), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (74, 74, 74), category=dpg.mvThemeCat_Core)
        # Slider Grab
        dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, (50, 50, 50), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, (50, 50, 50), category=dpg.mvThemeCat_Core)
        # Check mark
        dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (255, 0, 0), category=dpg.mvThemeCat_Core)
        # Window
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (20, 20, 20), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (40, 40, 40), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (20, 20, 20), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_PopupBg, (20, 20, 20), category=dpg.mvThemeCat_Core)

        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 0, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_TabRounding, 0, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 0, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_GrabMinSize, 16, category=dpg.mvThemeCat_Core)
    for comp_type in (dpg.mvMenuItem, dpg.mvButton, dpg.mvText):
        with dpg.theme_component(comp_type, enabled_state=False):
            dpg.add_theme_color(dpg.mvThemeCol_Text, (80,80,80))
        
dpg.bind_theme(global_theme)

with dpg.theme() as knob_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (0,0, 0,0), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (0,0, 0,0), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (0,0, 0,0), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 0, 0,0), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (0, 0, 0,0), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (0, 0, 0,0), category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 0, category=dpg.mvThemeCat_Core)E
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 0, category=dpg.mvThemeCat_Core)
for i in knoblist:
    for el in range(1,5):
        try:
            dpg.bind_item_theme('el'+str(el)+'_'+i+'_knob',knob_theme)
        except:
            pass
with dpg.theme() as drum_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_style(dpg.mvStyleVar_GrabMinSize, 6, category=dpg.mvThemeCat_Core)
for i in range (61):
        dpg.bind_item_theme('drums_Volume'+str(i),drum_theme)
        dpg.bind_item_theme('drums_Noteshift'+str(i),drum_theme)
        dpg.bind_item_theme('drums_Alt_Group'+str(i),drum_theme)
        dpg.bind_item_theme('drums_Alt_Group_Text'+str(i),drum_theme)
        dpg.bind_item_theme('drums_Pan'+str(i),drum_theme)
        dpg.bind_item_theme('drums_Efx_Balance'+str(i),drum_theme)

############################## FONTS ###########################
if sys.platform =='win32':
    fontpath = 'C:/Windows/Fonts/Arial.ttf'
if sys.platform == 'darwin':
    fontpath = '/System/Library/Fonts/Supplemental/Arial.ttf'
with dpg.font_registry():
    default_font = dpg.add_font(fontpath, 14)
    medium_font = dpg.add_font(fontpath, 12)
    small_font = dpg.add_font(fontpath, 11)
dpg.bind_font(default_font)
dpg.bind_item_font('amp_mod_cc', small_font)
dpg.bind_item_font('pitch_mod_cc', small_font)
dpg.bind_item_font('cutoff_mod_cc', small_font)
dpg.bind_item_font('cutoff_freq_cc', small_font)
dpg.bind_item_font('env_gen_bias_cc', small_font)
dpg.bind_item_font('volume_cc', small_font)
for i in range(len(ampenvlist)):
    for a in range(4):
        dpg.bind_item_font('el'+str(a+1)+'_ampenv'+str(i),small_font)
for i in range(len(pitchenvlist)):
    for a in range(4):
        dpg.bind_item_font('el'+str(a+1)+'_pitchenv'+str(i),small_font)
for i in range(len(filterenvlist)):
    for a in range(4):
        dpg.bind_item_font('el'+str(a+1)+'_filter1env'+str(i),small_font)
        dpg.bind_item_font('el'+str(a+1)+'_filter2env'+str(i),small_font)
for i in range (61):
    dpg.bind_item_font('drumtext'+str(i), medium_font)
    dpg.bind_item_font('drums_Waveform'+str(i), medium_font)
    dpg.bind_item_font('drums_Volume'+str(i), medium_font)
    dpg.bind_item_font('drums_Noteshift'+str(i), medium_font)
    dpg.bind_item_font('drums_Tune'+str(i), medium_font)
    dpg.bind_item_font('drums_Alt_Group'+str(i), medium_font)
    dpg.bind_item_font('drums_Alt_Group_Text'+str(i), small_font)
    dpg.bind_item_font('drums_Pan'+str(i), medium_font)
    dpg.bind_item_font('drums_Efx_Balance'+str(i), medium_font)

######################### Start interface ######################
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window('Primary Window', True)
dpg.start_dearpygui()
dpg.destroy_context()

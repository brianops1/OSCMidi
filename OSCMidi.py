
#pip install python-osc
#pip install pygame
#pip install pygame_menu


import math,re,os
from threading import Thread
from time import sleep
#Needs installations
from pythonosc import osc_message_builder
from pythonosc import udp_client
import pygame
import pygame.midi
import pygame_menu

pygame.midi.init()
pygame.init()

# Static variables
floor = math.floor


Dimension = (800,600)


surface = pygame.display.set_mode(Dimension, pygame.RESIZABLE)
PortStyle = 1
ParticleWait = .05
currentPort = None
Debug = False
ParticlesUsed = {"1":False,"2":False,"3":False,"4":False,"5":False,"6":False}
ParticleZone = []
MainLoop = True
CloseThread = False
Out = None
CurrentOutPortNum = None
CurrentPortNum = None
NoteLimiter = False
PressedKeys = {}

client = None

# functions


def simulate_key(t, note, velocity):
    global Out,ParticleZone,PortStyle,client
    if not (-15 <= note-36 <= 88):
        return
    index = note - 20
    if Debug:
        print("PortStyle: "+str(PortStyle))
    if PortStyle == 1:
        if Out and (t == 176 or t == 186):
            Out.write_short(0xb0, 64, velocity)
            return
        elif t > 176:
            return
        if velocity == 0:
            if Out:
                Out.note_off(note, velocity, 0)
            client.send_message('/avatar/parameters/'+str(index),0)
        else:
            if Out:
                Out.note_on(note, velocity, 0)
            ParticleZone.append(index)
            client.send_message('/avatar/parameters/'+str(index),1)
    elif PortStyle == 2:
        if Out and t == 186:
            Out.write_short(0xb0, 64, velocity)
            return
        if not note:
            return
        if velocity == 0:
            if Out:
                Out.note_off(note, velocity, 0)
            client.send_message('/avatar/parameters/'+str(index),0)
        elif velocity >= 1:
            if Out:
                Out.note_on(note, velocity, 0)
            ParticleZone.append(index)
            client.send_message('/avatar/parameters/'+str(index),1)

            


def parse_midi(message):
    global sustainToggle
    if message.type == 'control_change' and SavableSettings["sustainEnabled"]:
        if not sustainToggle and message.value > SavableSettings["sustainCutoff"]:
            sustainToggle = True
            press('space')
        elif sustainToggle and message.value < SavableSettings["sustainCutoff"]:
            sustainToggle = False
            release('space')
    elif (message.type == 'note_on' or message.type == 'note_off'):
        if message.velocity == 0:
            simulate_key('note_off', message.note, message.velocity)
        else:
            simulate_key(message.type, message.note, message.velocity)


def Main():
    global CloseThread,menu
    print("Now listening to note events on "+str(currentPort)+"...")
    while not CloseThread:
        if pygame.midi.Input.poll(currentPort):
            midi_data = pygame.midi.Input.read(currentPort, 1)
            midi_note, timestamp = midi_data[0]
            note_status, keynum, velocity, unused = midi_note
            simulate_key(note_status, keynum, velocity)
            if Debug:
                print(midi_data)
        else:
            sleep(.01)
    print("Closed threads, not listening anymore")

def ParticleSend(Wait,Used):
    global ParticleZone,ParticlesUsed
    Note = float("0."+str(ParticleZone[0]))
    if ParticleZone[0] < 10:
        Note = float("0.0"+str(ParticleZone[0]))
    client.send_message('/avatar/parameters/P'+str(Used),Note)
    print(Used,Note)
    ParticleZone.pop(0)
    sleep(Wait)
    client.send_message('/avatar/parameters/P'+str(Used),0)
    sleep(Wait)
    ParticlesUsed[str(Used)] = False
    

def ParticleBuffer():
    global CloseThread,ParticleWait,UseParticles,ParticleZone,ParticlesUsed,NoteLimiter
    ParticlesUsed = {"1":False,"2":False,"3":False,"4":False,"5":False,"6":False}
    Next = 1
    while not CloseThread:
        if not UseParticles:
            sleep(.1)
            ParticleZone = []
        else:
            sleep(.01)
            if NoteLimiter and len(ParticleZone) >= 16:
                z = {}
                for i in ParticleZone:
                    z[i] = True
                ParticleZone = []
                a = 0
                for i in z:
                    ParticleZone.append(i)
        if len(ParticleZone) >= 1 and not ParticlesUsed[str(Next)]:
            print(ParticlesUsed)
            ParticlesUsed[str(Next)] = True
            Thread(target = ParticleSend, args=(ParticleWait,Next)).start()
            Next += 1
            if Next > 6:
                Next = 1
    print("Buffer closed")

##############################


####

def Clear():
  if os.name == 'nt':
    os.system('cls')
  else:
    os.system('clear')

def IntAsk(text):
    var = None
    while var == None:
        try:
            var = int(input(text))
        except:
            print('\nThere was an issue\n')
            var = None

    return var

########Initalize UI Funcs############

def ResetKeys():
    client.send_message('/avatar/parameters/K1',0)
    for i in range(2,88):
        client.send_message('/avatar/parameters/'+str(i),0)
        sleep(.1)

def InitalizePorts():
    global currentPort,CurrentPortNum,CurrentOutPortNum,Out,CloseThread,Started
    CloseThread = True
    sleep(.02)
    pygame.midi.quit()
    pygame.midi.init()
    if CurrentPortNum:
        currentPort = pygame.midi.Input(CurrentPortNum)
    if CurrentOutPortNum:
        Out = pygame.midi.Output(CurrentOutPortNum)
    Start.set_title("Start")
    Started = False

def SelectPortIn(Val,Num):
    global currentPort,CurrentPortNum,InputPortMenu
    #Label.set_title("Start OSC Client first")
    if Num > 0:
        CurrentPortNum = Num
        if currentPort != None:
            try:
                InitalizePorts()
            except:
                Label.set_title("Device is currently in use, make sure it's not")
                InputPortMenu.reset_value()
                return 
        else:
            try:
                currentPort = pygame.midi.Input(Num)
            except:
                currentPort = None
                Label.set_title("Device is currently in use, make sure it's not")
                InputPortMenu.reset_value()
                return 
        Label.set_title("Device is selected for input")


def SelectPortOut(Val,Num):
    global Out,CurrentOutPortNum
    if Num > 0:
        CurrentOutPortNum = Num
        if Out != None:
            InitalizePorts()
        else:
            Out = pygame.midi.Output(Num)
    else:
        Out = None
        CurrentOutPortNum = None
        InitalizePorts()
    
        
def SetPort(Value):
    global Port
    try:
        Port = int(Value)
    except:
        Port = 9000

def SetIP(Value):
    global IP
    IP = Value

def PortStyleChange(Val,Num):
    global PortStyle
    PortStyle = Num

def Start(Val):
    global Started,client,IP,Port,Label,Start,currentPort,CloseThread
    StartOSC(True)
    if not client:
        Label.set_title("Start OSC Client first")
        return
    elif not currentPort:
        Label.set_title("Select an input port")
        return
    if Started:
        while currentPort.poll():
            b = pygame.midi.Input.read(currentPort, 1)
            pass
        CloseThread = True
        Start.set_title("Start")
    else:
        CloseThread = False
        a = 0
        while currentPort.poll() and a < 50:
            a += 1
            b = pygame.midi.Input.read(currentPort, 1)
            sleep(.01)
            pass
        Start.set_title("Stop")
        Thread(target = ParticleBuffer).start()
        Thread(target = Main).start()
        print('here')
    Started = not Started

def StartOSC(Val):
    global IP,Port,client,Label
    if client == None:
        Label.set_title("Set client")
        client = udp_client.SimpleUDPClient(IP, Port)

def Particles(Val):
    global UseParticles
    UseParticles = not UseParticles

def PBuff(Val):
    global ParticleWait
    try:
        ParticleWait = float(Val)
    except:
        ParticleWait = .1

def BufferLimit(Val):
    global NoteLimiter
    NoteLimiter = not NoteLimiter

def InputRefresh(Val):
    global ListOfInPorts,ListOfOutPorts,InputPortMenu,OutputPortMenu
    Label.set_title("Devices Refreshed")
    ListOfInPorts = []
    ListOfOutPorts = [("None",-1)]
    for i in range(1,pygame.midi.get_count()):
        try:
            if pygame.midi.get_device_info(i)[2] == 1:
                ListOfInPorts.append((str(pygame.midi.get_device_info(i)[1]),i))
            if pygame.midi.get_device_info(i)[2] == 0:
                ListOfOutPorts.append((str(pygame.midi.get_device_info(i)[1]),i))
        except Exception as E:
            pass
    if InputPortMenu and len(ListOfInPorts) > 0:
        InputPortMenu.update_items(items=ListOfInPorts)
        OutputPortMenu.update_items(items=ListOfOutPorts)
        pass

def on_resize():
    """
    Function checked if the window is resized.
    """
    window_size = surface.get_size()
    new_w, new_h = window_size[0], window_size[1]
    menu.resize(new_w, new_h)

def DebugMode(Val):
    global Debug
    Debug = not Debug

def BackgroundChecks():
    global InputPortMenu,OutputPortMenu,ListOfInPorts,ListOfOutPorts
    LastSize = None
    while True:

        #Resizing
        
        if not LastSize:
            LastSize = surface.get_size()
        if LastSize != surface.get_size():
            on_resize()
            LastSize = surface.get_size()


        sleep(.5)
        

#########Initalize Main###########
        

try:
    menu = pygame_menu.Menu('OSC Midi', Dimension[0], Dimension[1],
                       theme=pygame_menu.themes.THEME_DARK)
    Label = menu.add.label('', max_char=-1, font_size=20)
    
    ListOfInPorts = []
    ListOfOutPorts = [("None",-1)]
    InputPortMenu = None
    OutputPortMenu = None
    Port = 9000
    IP = '127.0.0.1'
    Started = False
    UseParticles = False
    CloseThread = False
    InputRefresh(1)
    ParticleWait = .1
    InputPortMenu = menu.add.dropselect(title='Input :', items=ListOfInPorts,
                        selection_box_width=round(Dimension[0]/2),selection_box_height=5, onchange=SelectPortIn)
    OutputPortMenu = menu.add.dropselect(title='Output :', items=ListOfOutPorts,
                        selection_box_width=round(Dimension[0]/2),selection_box_height=5, onchange=SelectPortOut)

#Need to add a settings menu to put port, ip, port style, and particles into
    
    #menu.add.text_input('Set Port: ', default='9000', onreturn=SetPort)
    #menu.add.text_input('Set IP: ', default='127.0.0.1', onreturn=SetIP)
    menu.add.selector('Port Style : ', items=[('1',1),('2',2)], onchange=PortStyleChange)
    menu.add.toggle_switch('Send Particle Paramaters', False, onchange=Particles)
    menu.add.toggle_switch('Toggle Debug Mode', False, onchange=DebugMode)
    menu.add.toggle_switch('Particle Buffer Limit (16)', False, onchange=BufferLimit)
    menu.add.text_input('Particle Buffer: ', default='.1', onreturn=PBuff)
    Start = menu.add.button('Start', Start, 'foo')
    Thread(target = BackgroundChecks).start()
    menu.mainloop(surface)
except Exception as E:
    print('\n\n')
    print('Error detected')
    input(E)
input('\n\nHit enter now to close')

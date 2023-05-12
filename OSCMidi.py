
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


surface = pygame.display.set_mode(Dimension)
PortStyle = 1
ParticleWait = .05
currentPort = None
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
    if PortStyle == 1:
        if Out and t == 176:
            if velocity == 0:
                Out.write_short(0xb0, note, 0)
            else:
                Out.write_short(0xb0, note, 127)
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
        if Out and t == 176:
            if velocity == 0:
                Out.write_short(0xb0, note, 0)
            else:
                Out.write_short(0xb0, note, 127)
            return
        elif t > 176:
            return
        if t == 144:
            if Out:
                Out.note_off(note, velocity, 0)
            client.send_message('/avatar/parameters/'+str(index),0)
        else:
            if Out:
                Out.note_on(note, velocity, 0)
            ParticleZone.append(index)
            client.send_message('/avatar/parameters/'+str(index),1)
    elif PortStyle == 3:
        if Out and t == 176:
            if velocity == 0:
                Out.write_short(0xb0, note, 0)
            else:
                Out.write_short(0xb0, note, 127)
            return
        elif t > 176:
            return
        if t == 144:
            if Out:
                Out.note_off(note, velocity, 0)
            ParticleZone.append(index)
            client.send_message('/avatar/parameters/'+str(index),1)
        elif t == 128:
            if Out:
                Out.note_on(note, velocity, 0)
            client.send_message('/avatar/parameters/'+str(index),0)

            


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
        else:
            sleep(.01)
    print("Closed threads, not listening anymore")

def ParticleSend(Wait,Used):
    global ParticleZone,ParticlesUsed
    client.send_message('/avatar/parameters/P'+str(Used),ParticleZone[0])
    print(Used,ParticleZone)
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
    global currentPort,CurrentPortNum
    if Num > 0:
        CurrentPortNum = Num
        if currentPort != None:
            InitalizePorts()
        else:
            currentPort = pygame.midi.Input(Num)


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
    PortStyle = Num

def Start(Val):
    global Started,client,IP,Port,Label,Start,currentPort,CloseThread
    if not client:
        Label.set_title("Start OSC Client first")
        return
    elif not currentPort:
        Label.set_title("Select an input port")
        return
    if Started:
        while currentPort.poll():
            pass
        CloseThread = True
        Start.set_title("Start")
    else:
        CloseThread = False
        while currentPort.poll():
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
        ParticleWait = int(Val)
    except:
        ParticleWait = .1

def BufferLimit(Val):
    global NoteLimiter
    NoteLimiter = not NoteLimiter
        
#########Initalize Main###########
        

try:
    menu = pygame_menu.Menu('OSC Midi', Dimension[0], Dimension[1],
                       theme=pygame_menu.themes.THEME_DARK)
    ListOfInPorts = []
    ListOfOutPorts = [("None",-1)]
    Port = 9000
    IP = '127.0.0.1'
    PortStyle = 1
    Started = False
    UseParticles = False
    CloseThread = False
    ParticleWait = .1
    for i in range(1,pygame.midi.get_count()):
        try:
            if pygame.midi.get_device_info(i)[2] == 1:
                ListOfInPorts.append((str(pygame.midi.get_device_info(i)[1]),i))
            if pygame.midi.get_device_info(i)[2] == 0:
                ListOfOutPorts.append((str(pygame.midi.get_device_info(i)[1]),i))
        except Exception as E:
            pass
    Label = menu.add.label('', max_char=-1, font_size=20)
    menu.add.dropselect(title='Input :', items=ListOfInPorts,
                        selection_box_width=round(Dimension[0]/2),selection_box_height=5, onchange=SelectPortIn)
    menu.add.dropselect(title='Output :', items=ListOfOutPorts,
                        selection_box_width=round(Dimension[0]/2),selection_box_height=5, onchange=SelectPortOut)
    menu.add.text_input('Set Port: ', default='9000', onreturn=SetPort)
    menu.add.text_input('Set IP: ', default='127.0.0.1', onreturn=SetIP)
    menu.add.selector('Port Style : ', items=[('1',1),('2',2),('3',3)], onchange=PortStyleChange)
    menu.add.toggle_switch('Send Particle Paramaters', False, onchange=Particles)
    menu.add.toggle_switch('Particle Buffer Limit (16)', False, onchange=BufferLimit)
    menu.add.text_input('Particle Buffer: ', default='.1', onreturn=PBuff)
    menu.add.button('Start OSC Connection (Can only do once)', StartOSC, 'foo')
    Start = menu.add.button('Start', Start, 'foo')
    menu.mainloop(surface)
except Exception as E:
    print('\n\n')
    print('Error detected')
    input(E)
input('\n\nHit enter now to close')

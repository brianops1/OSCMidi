# OSCMidi

Currently a semi-placeholder until I can make this stuff pretty.

I AM UNSURE IF THIS WORKS ON MAC :)

The avatars DO NOT MAKE AUDIO, the audio has to come from your mic or through a DAW (Digital Audio Workspace) like FL Studio, Reaper, etc

-----------------------------------

Here are the avatar IDs that you can use with VRCX to import:


avtr_f5648902-719f-4193-80b9-8d1581f076b4 - Fresh Pianist, has lightup keys

avtr_2ed21ba8-f484-4fd0-b251-0e53dfe3c9c9 - OSC Piano, has keydown keys and is properly synced with mic audio

-----------------------------------

Here is everything you will need for this to work:

Python

pip install python-osc

pip install pygame

pip install pygame_menu

And a program called LoopBe1 (LoopBeInternalMidi)
- This you will need to look up online and download

-----------------------------------

Once you have everything all installed, follow these steps

- Read above and make sure everything is installed correctly
- Launch the OSC Midi program
- Set your input to the piano you are using (Will give a message if it didn't work right)
- Set your output to loopbe
- Hit start
- Set your midi input of your DAW to Loopbe
- Hit some keys and it SHOULD be working, if not re read or make a comment
- Launch VR Chat
- Get into the avatar
- Go into setting before the expressions menu and turn on OSC in tools
- Then go into expressions and make sure that you have the piano animation enabled
- Now when you play you should see the animation playing

-----------------------------------

Also I recognize that the code is not great :) I am a amateur not professional programmer, but I know enough to make things work at least, if you can make this better then please do and make a suggestion / comment or whatever you do in github, I'm new. 

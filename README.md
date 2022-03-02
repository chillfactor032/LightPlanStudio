# LightPlanStudio
LightPlan Studio is a Python-based GUI application for creating timed light sequences for Twitch Streams that use LumiaStream.

https://lightplanstudio.com

## Getting Started

To get started, grab the latest [Release](https://github.com/chillfactor032/LightPlanStudio/releases) from the release links on the right this Github repository.

 - Run the exe a explore the GUI.
 - Pick out a song and create a LightPlan.
 - Add your Twitch details to the settings, like user name, OAuth token, and desired channel to connect to.

## What is a LightPlan?

A LightPlan is a collection of Twitch chat messages that are set to fire at very precise intervals. This creates the ability to time light changes from tools like LumiaStream very precisely to music. 

To make sure these chat messages hit exactly when you expect them to, your stream delay must be calculated. The way to do this is to connect to Twitch, Click "Calculate" under the Stream Delay area, and then wait for a moment where you can send a LumiaStream light command. Select the desired message in the Stream Delay dialog and click Send. This will send the command to the stream. When the lights change, click "Stop" and the timer will stop. Click "Save Delay" and your stream delay is set.

When your song starts, wait for the moment in the song you selected as the start point, and click "Start Light Plan".

## Creating a LightPlan

You may create LightPlans manually by inserting events into the Event table and manually setting the offset. Repeat this for all of the desired light events. Be sure to at the very minimum include a song title and artist before you save.

## The Event Wizard

The Event Wizard is there to make it much easier to create LightPlans. This works by specifying a Youtube link (or a local mp4 file), loading it in the event wizard, and then pressing the Play button. The event wizard will play the song and start a timer. You can then press the space bar to add events in time with the music. The slider can be dragged to the desired point in the song if you miss something. If you use the Event Wizard, you will need to specify a starting event (usually the first event). Just right-click the desired event and select "Set Start Event". Remember to start the LightPlan at this point in the song. I usually specify the starting point in the notes of the LightPlan (e.g. "Start on beat 9 after the intro.")

## Full Help Documentation

Full help documentation will be located at https://lightplanstudio.com. Help topics are currently being added so please be patient.

### Donations

LightPlanStudio is provided free and without warranty. If you feel compelled to donated here are my crypto addresses below.

Coin | Address
--- | ---
BTC | 3C7UT1a2Do3LxFvxZt88S7gsNkRyRKXYCw
ETH | 0xc24Fc5E6C2b3E1e1eaE62f59Fab8cFBC87b1FEfc
LTC | MViPMqjn2kdMwbLAbYtgpgnHfzwwpbzUZQ

### Contact

chill@chillaspect.com


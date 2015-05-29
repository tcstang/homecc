#!/bin/bash

play -v 0.5 -q /opt/homecc/sounds/alertPhase.mp3 trim 0 40
sleep 2 
/opt/tims-utils/sendmail.sh "Alarm has been triggered!!!"
sleep 1

# play real alarm
play -v 2.5 -q /opt/homecc/sounds/alarm1.mp3 repeat 99 


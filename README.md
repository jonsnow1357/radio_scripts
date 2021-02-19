## radio_scripts

Collection of scripts to help with programming a radio scanner.

## usage

Get all channels:

    ./bearcat.py BC125AT /dev/tty??? get
  
Channels are exported as .json and .csv in the *read* folder.

Copy any of them to the *write* folder and change. If both files are present in *write* .json has priority.

Set all channels:

    ./bearcat.py BC125AT /dev/tty??? set

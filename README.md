## radio_scripts

Collection of scripts to help with programming a radio scanner.

## usage

Get all channels:

    ./bearcat.py BC125AT /dev/tty??? get
  
Channels are exported as .json and .csv in the *read* folder.

Copy any of them to the *write* folder and change. If both files are present in *write* .json has priority.

Set all channels:

    ./bearcat.py BC125AT /dev/tty??? set

## debug notes

If /dev/ttyACM? does not show up when you plug in a Bearcat scanner try the suggestion [here](https://github.com/rikus--/bc125at-perl/issues/1)

    echo 1965 0017 2 076d 0006 > /sys/bus/usb/drivers/cdc_acm/new_id

# scripts
Various one-off scripts I've put together

# openhab python scripts
These pull credentials from lastpass using an unofficial python api. Either set the environment variables `LPUSERNAME` and `LPPASSWORD` or create the file `lpcreds.py` in the `scripts` folder with `username` and `password` variables

`hydro.py` requires phantomjs somewhere in your `$PATH` and `selenium`'s python package

`teksavvy.py` requires an API key and `requests`. Also requires python3 as python2 has a bug in urllib2's ssl module preventing connection to the api endpoint

Both require `paho-mqtt`.

# tvcontrol
Requires a raspberry pi connected to a TV via HDMI and the TV has to have CEC enabled and the ability to control standby/on via CEC.

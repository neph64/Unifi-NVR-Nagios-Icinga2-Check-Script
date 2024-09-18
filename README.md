# Unifi-NVR-Nagios-Icinga2-Check-Script
A small script that can be used to check the Unifi NVRs for camera connectivity, hard drive status, CPU temp, and camera firmware status. Use at your own risk. The script is provided with no warranty or support. It was just a quick project that I figured I would share.

It works like any other icinga or nagios script. Very lightly tested, feel free to submit issues if you find anything.


# Usage

usage: check_unifi_nvr.py [-h] [-u USERNAME] [-p PASSWORD] [--insecure]
                          [-c CERTIFICATE] [-H HOST] [-P PORT] -t
                          {connection_status,camera_firmware_status,drive_status,cpu_temp}

                          
--insecure will disable certificate verification when the scripts submits POST or GET requests on an https url.
                          

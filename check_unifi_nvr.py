#!/usr/bin/env python3
import argparse
import requests
import json
import urllib3


parser = argparse.ArgumentParser(description="Checks health on UNVR Devices.")


parser.add_argument(
    "-u", "--username",
    dest="username",
    help="Username"
)

parser.add_argument(
    "-p", "--password",
    dest="password",
    help="User Password"
)
parser.add_argument(
    "--insecure",
    dest="insecure",
    action="store_true",
    help="Disable SSL Certificate verification"
)

parser.add_argument(
    "-c", "--certificate",
    dest="certificate",
    help="Specify certificate used to verify requests using SSL",
    required=False
)

parser.add_argument(
    "-H", "--host",
    dest="host",
    help="Specify certificate used to verify requests using SSL",
    required=False
)

parser.add_argument(
    "-P", "--port",
    dest="port",
    help="Specify the port the queries will use",
    required=False
)

parser.add_argument(
    "-t", "--test",
    dest="test",
    help="Which subprogram to run",
    choices=[
        'connection_status', 'camera_firmware_status', 'drive_status', 'cpu_temp', 
        ],
    nargs='+',
    required=True
)

args = parser.parse_args()
if args.insecure:
    import urllib3
    urllib3.disable_warnings()
    requests.packages.urllib3.disable_warnings() # pylint: disable=no-member
    VERIFY_SSL = False
elif args.certificate != "":
    VERIFY_SSL = args.certificate
else:
    VERIFY_SSL = True


## Setup Authentication, get a token.

gateway = {"ip":args.host,"port":args.port}
headers = {"Accept": "application/json","Content-Type": "application/json"}
loginUrl = 'api/auth/login'
authUrl = f"https://{gateway['ip']}:{gateway['port']}/{loginUrl}"
auth = {"username": args.username,"password": args.password}


session = requests.Session()
authResponse = session.post(authUrl,headers=headers,data=json.dumps(auth), verify=VERIFY_SSL)








def handle_html_err(r: requests.Response) -> str|None:
    """
    Handles API request errors.

    Args:
        r (requests.Response): A response from API call

    Returns:
        str|None: str of error output or None if ok.
    """
    if r.ok:
        return None
    try:
        j = json.loads(r.text)
        errmsg = j['message'] if 'message' in j else r.text
    except Exception as e:
        errmsg = r.text
    return f"API call returned non-200 status code {r.status_code} with output: {errmsg}"




def check_connection_status():
    """
    Checks connection status of the cameras to the NVR.

    Returns:
        A check result.
    """
    
    
    result = session.get(
        f"https://{gateway['ip']}:{gateway['port']}"+"/proxy/protect/api/cameras/",
        timeout=15,
        verify=VERIFY_SSL,
        headers=headers,
    )
    if handle_html_err(result) is not None:
        print(str(handle_html_err(result)))
        exit(3)
    data = json.loads(result.content)
    check_status = 0
    for camera in data:
        if camera['state'] != "CONNECTED":
            print(f"Issue detected with {camera['name']}")
            check_status = 2
        else:
            print(f"{camera['name']} is CONNECTED")
    exit(check_status)




def check_camera_firmware_status():
    """
    Checks firmware update status of the cameras.

    Returns:
        A check result.
    """
    
    
    result = session.get(
        f"https://{gateway['ip']}:{gateway['port']}"+"/proxy/protect/api/cameras/",
        timeout=15,
        verify=VERIFY_SSL,
        headers=headers,
    )
    if handle_html_err(result) is not None:
        print(str(handle_html_err(result)))
        exit(3)
    data = json.loads(result.content)
    check_status = 0
    for camera in data:
        if camera['fwUpdateState'] != "upToDate":
            print(f"{camera['name']} needs updates")
            check_status = 2
        else:
            print(f"{camera['name']} is up to date")
            
    exit(check_status)

def check_drive_status():
    """
    Checks the status of the NVR drives.

    Returns:
        A check result.
    """
    
    
    result = session.get(
        f"https://{gateway['ip']}:{gateway['port']}"+"/proxy/protect/api/nvr/",
        timeout=15,
        verify=VERIFY_SSL,
        headers=headers,
    )
    if handle_html_err(result) is not None:
        print(str(handle_html_err(result)))
        exit(3)
    data = json.loads(result.content)

    check_status = 0
    for drive in data['systemInfo']['ustorage']['disks']:
        if drive['state'] == "nodisk": # Checks for a null key in the API
            print(f"Bay {drive['slot']} - Empty")
        elif drive['healthy'] == "good" and drive['temperature'] < 45:
            print(f"Bay {drive['slot']} - Good Health - {drive['temperature']} C")
        else:
            print(f"Bay {drive['slot']} - Issue Detected - {drive['temperature']} C")
            check_status = 2
        
        
    exit(check_status)

def check_cpu_temp():
    """
    Checks the CPU temperature of the NVR

    Returns:
        A check result.
    """
    
    
    result = session.get(
        f"https://{gateway['ip']}:{gateway['port']}"+"/proxy/protect/api/nvr/",
        timeout=15,
        verify=VERIFY_SSL,
        headers=headers,
    )
    if handle_html_err(result) is not None:
        print(str(handle_html_err(result)))
        exit(3)
    data = json.loads(result.content)

    
    bay = 1
    if data['systemInfo']['cpu']['temperature'] > 70:
        print(f"CPU temperature high - {data['systemInfo']['cpu']['temperature']} C")
        check_status = 2
    else:
        print(f"CPU temperature OK - {data['systemInfo']['cpu']['temperature']} C")
        check_status = 0
    exit(check_status)


## Handles arguments and runs the right subprogram
if args.test == ['connection_status']:
    check_connection_status()
elif args.test == ['camera_firmware_status']:
    check_camera_firmware_status()
elif args.test == ['drive_status']:
    check_drive_status()
elif args.test == ['cpu_temp']: 
    check_cpu_temp()

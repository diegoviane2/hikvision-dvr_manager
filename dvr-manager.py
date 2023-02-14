###################################################################
# HIKVISION DVR MANAGER                                           #
# Written by Diego Viane 12-02-2023                               #
# https://github.com/diegoviane2                                  #
# This code generate a text mode menu to operate in 3 functions   #
# 1 - Reboot the device                                           #
# 2 - Sync time with the local machine                            #
# 3 - Show Device Info                                            #
# The IP adresses and ports(optional) must be updated on devices  #
# dictionary.                                                     #
# To operate properly, the default username is admin.             #
# The password must be fulfilled in the option 9 of the main menu #
# The security of the password is poor. Just to avoid typing      #
# passwords on code or command line.                              #
###################################################################

import requests
import datetime
from datetime import time
import os
import time
from cryptography.fernet import Fernet


def password_manager():
    key = Fernet.generate_key()

    with open("key.key", "wb") as key_file:
        key_file.write(key)

    password = input("Enter password: ").encode()

    f = Fernet(key)
    encrypted_password = f.encrypt(password)

    with open("password.bin", "wb") as password_file:
        password_file.write(encrypted_password)


    
def authorization():
    user = "admin" 
    
    with open("password.bin", "rb") as password_file:
        encrypted_password = password_file.read()

    with open("key.key", "rb") as key_file:
        f = Fernet(key_file.read())
        
    pass_ = f.decrypt(encrypted_password)
    
    pass_ = pass_.decode()
    
    return requests.auth.HTTPDigestAuth(user,pass_)
    



def reboot_device(host, auth_data):
    url_reboot = "http://" + host +"/ISAPI/System/reboot"
    
    response = requests.put(url_reboot, auth=auth_data)
    
    if response.status_code == 200:
        print("Reboot operation suceeded ... Please wait!")
        time.sleep(3)
    else:
        print("Reboot operation failed! - [ Error " + str(response.status_code) + "]")       
        time.sleep(3) 

def sync_time(host, auth_data):
    url_syncTime = f"http://{host}/ISAPI/System/Time/"
    
    local_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    
    body = f"<Time xmlns='http://www.hikvision.com/ver20/XMLSchema' version='1.0'><timeMode>manual</timeMode><localTime>{local_time}</localTime><timeZone>CST+3:00:00</timeZone></Time>"

    headers = {'Content-Type': 'text/xml'}
 
    response = requests.put(url_syncTime, auth=auth_data, headers=headers, data=body)
    
    if response.status_code == 200:
        print("Time syncronized sucessfuly. [ " + local_time + " ]")
        time.sleep(3)
    else:
        print("Time syncronization failed! [ Error " + str(response.status_code) + " ]")
        print(response)
        time.sleep(3)

def device_info(host, auth_data):    

    url_info = "http://"+ host +"/ISAPI/System/deviceInfo"

    response = requests.get(url_info, auth=auth_data)

    if response.status_code == 200:
        
        response_content = response.text
        print("Response Content:")
        print(response_content)
        time.sleep(5)
    else:
        
        print("Failed to get device information")
        time.sleep(3)

def handle_device_choice(device, device_ip):
    while True:
        os.system("clear")
        print(f"Select an option for the device {device}:")
        print("1. Reboot device ... [ REBOOT ]")
        print("2. Adjust time ... [ SYNC ]")
        print("3. Device Info ... [ DEVICE INFO ]")
        print("0. Back to main menu")
        choice = int(input("Option: "))
        if choice == 1:
            reboot_device(device_ip, authorization())
        elif choice == 2:
            sync_time(device_ip, authorization())
        elif choice == 3:
            device_info(device_ip, authorization())
        elif choice == 0:
            break

devices = {
           "Device A": "192.168.0.2", 
           "Device B": "192.168.0.3", 
           "Device C": "192.168.0.4",
           "Device D":"192.168.0.5",
           "Device E":"192.168.0.6"
           }



while True:
    os.system("clear")
    #os.system("cls")
    print("Selecione uma opção do menu principal:")
    for i, device in enumerate(devices.keys()):
        print(f"{i+1}. {device}")
    print('9. RESET PASSWORD')    
    print("0. EXIT")
    choice = int(input("OPTION: "))  
    if choice == 9:
        password_manager()
        break
    if choice == 0:
        print('END OF PROGRAM')
        break
    selected_device = list(devices.keys())[choice - 1]
    handle_device_choice(selected_device, devices[selected_device])
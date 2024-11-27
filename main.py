from getpass import getpass
from AddressObjectClass import AddressObjectClass
import time
import SonicAPIClass
import urllib3
urllib3.disable_warnings()

HTTPstatusCodes = {
    "200": "OK",
    "400": "Bad Request",
    "401": "Not Authorized",
    "403": "Forbidden",
    "404": "Not Found",
    "405": "Method Not Allowed",
    "406": "Not Acceptable",
    "413": "Request body too large",
    "414": "Request URL too long",
    "500": "Internal Server Error",
    "503": "No resources"
}

ipAddress = '10.61.12.220'
portNumber = 443
userName = None
userPass = None

def getFirewallParams():
    global userName
    userName = input("Please enter the user name: ")
    global userPass
    userPass = input("Please enter your password: ")

def authentication(firewall):
    authTry = 3

    while authTry > 0:
        authStatus = firewall.authenticate()
        if authStatus != 200:
            print("API authorization failed. Trying again in 5 secs!")
            authTry -= 1
            time.sleep(5)
        else:
            authTry = 0

    print("API authorization:  ", end="")
    print("Status " + str(authStatus) + " " + HTTPstatusCodes[str(authStatus)])
    if authStatus != 200:
        print("Exiting program.")
        exit()

# This is a required step
def startFirewallManagement(firewall):
    startTry = 3
    while startTry > 0:
        mngStatus = firewall.startManagement()
        if mngStatus != 200:
            print("Starting firewall management failed with \"Status " + str(mngStatus) + " " +  HTTPstatusCodes[str(mngStatus)] + "\". Trying again in 5 secs!")
            startTry -= 1
            time.sleep(5)
        else:
            startTry = 0

    print("Starting firewall management: ", end="")
    print("Status " + str(mngStatus) + " " + HTTPstatusCodes[str(mngStatus)])
    if mngStatus != 200:
        print("Exiting program.")
        logoutUser(firewall)
        exit()

# This is required to be able to make changes on the firewall
def changeConfigMode(firewall):
    changeTry = 3
    while changeTry > 0:
        configStatus = firewall.configMode()
        if configStatus != 200:
            print("Changing to Config Mode failed with \"Status " + str(configStatus) + " " + HTTPstatusCodes[str(configStatus)] + "\". Trying again in 5 secs!")
            changeTry -= 1
            time.sleep(5)
        else:
            changeTry = 0

    print("Changing to Config Mode: ", end="")
    print("Status " + str(configStatus) + " " + HTTPstatusCodes[str(configStatus)])
    print(" ")
    if configStatus != 200:
        print("Exiting program.")
        logoutUser(firewall)
        exit()

def commitChanges(firewall):
    print("Commit Changes: ", end="")
    commitStatusJSON = firewall.commitChanges()
    status = commitStatusJSON['status']['success']
    message = commitStatusJSON['status']['info'][0]['message']
    commitStatus = str(status) + ", " + str(message)
    print(commitStatus + "\n")
    if status == False:
        print("Exiting program.")
        exit()

def processIPaddresses(firewall):
    # Read the IP addresses from the file
    with open('ipv4_addresses.txt', 'r') as file:
        addresses = file.readlines()

    # Strip newline characters and print each address
    for i, address in enumerate(addresses):
        print(address.strip())
        postStatus = firewall.postIPv4AddressObjects(AddressObjectClass(aoName=str(address.strip()), aoZone="WAN", aoType="host", aoIPaddress=str(address.strip())).getJSON())
        print("Status " + str(postStatus) + " " + HTTPstatusCodes[str(postStatus)])
        if (i + 1) % 50 == 0:
            commitChanges(firewall)

def logoutUser(firewall):
    print("\nLogging out from the firewall: ", end="")
    logoutStatus = firewall.logoutUser(userName)
    print("Status " + str(logoutStatus) + " " + HTTPstatusCodes[str(logoutStatus)])

def main():

    getFirewallParams()
    firewall = SonicAPIClass.SonicAPIClass(ipAddress, portNumber, userName, userPass)
    authentication(firewall)
    startFirewallManagement(firewall)
    changeConfigMode(firewall)
    processIPaddresses(firewall)
    logoutUser(firewall)

if __name__ == "__main__":
    main()
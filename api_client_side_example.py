########################################################################################################
#
# Code example, showing how to subscribe to a data feed and receive broadcasted data.
#
# Date: Q3, 2020
#
########################################################################################################

# required imports
from os import system, name
import sys
import socketio
import time

# instantiate the client socket
sio = socketio.Client()


# list of available subscriptions.
def init_room_list():
    rooms = ["most_recent_long_alert:btc:5:STREAM",
             "most_recent_short_alert:btc:5:STREAM",
             "most_recent_long_alert:btc:30:STREAM",
             "most_recent_short_alert:btc:30:STREAM",
             "most_recent_long_alert:btc:60:STREAM",
             "most_recent_short_alert:btc:60:STREAM"]
    return rooms


# check that a UUID has been supplied and if it exists then return it
def check_for_auth_token_and_return():
    if len(sys.argv) == 2:
        token = sys.argv[1].strip()
        return token
    else:
        print("No authorization token provided!")
        sys.exit()


# clear the screen (os specific)
def check_os_and_clear_screen():
    # Windows
    if name == 'nt':
        system('cls')
    # Mac / Linux
    elif name == 'posix':
        system('clear')


# get user to specify which feed they wish to subscribe to (using a console based menu)
def menu():
    choice = 0
    check_os_and_clear_screen()

    print("Intelletic(c) 2020")
    print("            MENU")
    print()
    print("1. JOIN most_recent_long_alert:btc:5:STREAM")
    print("2. JOIN most_recent_short_alert:btc:5:STREAM")
    print("3. JOIN most_recent_long_alert:btc:30:STREAM")
    print("4. JOIN most_recent_short_alert:btc:30:STREAM")
    print("5. JOIN most_recent_long_alert:btc:60:STREAM")
    print("6. JOIN most_recent_short_alert:btc:60:STREAM")
    print("7. QUIT")
    print()
    choice = int(input("CHOICE: "))
    if choice == 7:
        print("Exiting...")
        sys.exit()
    if choice not in range(1, 7):
        print("Invalid choice. Try again")
        input("Press Enter to continue...")
        menu()
    else:
        rooms = []
        check_os_and_clear_screen()
        rooms = init_room_list()

        # Joining a room/feed based on the user's choice
        sio.emit(
            "join", {'room': rooms[choice - 1]}, namespace="/feed")
        print("Please wait for the feed to start:")


# start the module
def start():
    token = check_for_auth_token_and_return()
    # connect to the server and establish handshake
    # pass the auth_token as query param to the server
    sio.connect('http://162.214.120.16:5000?token=' +
                token, namespaces=["/feed"])


# Based on the result of the server authorization
# either permit the user to continue / exit
def on_connect_check_and_do(connected):
    if connected:
        print("Authorization successful")
        input("Press Enter to start")
        menu()
    else:
        print('Connection refused. Not Authorized')
        print("Disconnected!!")
        input("Press Enter to exit")
        sys.exit()


# Events reponding to the server messages
# status messages handled here
@ sio.on("status", namespace="/feed")
def status(data):
    print(data['status'])


# Events responding to user authorization
@ sio.on("auth", namespace="/feed")
def auth(data):
    connected_to_socket = data['auth']
    on_connect_check_and_do(connected_to_socket)


# Connection event handler
@ sio.on('connect', namespace="/feed")
def connect():
    print("I am connected")


# Error handler for feed namespace
@ sio.event
def connect_error(namespace="/feed"):
    print("The connection failed!")
    disconnect()


# Disconnection handler
@ sio.on('disconnect', namespace='/feed')
def disconnect(namespace="/feed"):
    print("I'm disconnected!")


# Listener to receive subscribed data feed
# in json format
@ sio.on("response", namespace="/feed")
def get_json(json):
    json_feed = []

    # socket writer reponds with None
    # then the feed is in OFF state
    if json['payload'] == None:
        print("Feed is not available")
        sys.exit()

    # if feed is ON then the payload is dumped
    # into the json_feed list
    print(json['payload'])
    json_feed.append(json['payload'])

    # write the list to a file
    # client to customize the name of the file
    # here it is feed.json
    with open('feed.json', 'w') as fh:
        fh.write('\n'.join(json_feed))


# Command line entry point
if __name__ == '__main__':
    try:
        start()
    except KeyboardInterrupt:
        print("Exiting...")
        sys.exit()

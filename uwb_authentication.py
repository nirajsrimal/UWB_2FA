# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import serial
import json

ser = None
auth_distance = 10


# Send Add Tag Command to Node to add a Tag with Long Address a64
def verify_uwb_tag(a64):
    addtag_msg = 'ADDTAG' + a64 + ' 1000 2 64 1\r\n'
    ser.write(addtag_msg.encode())

    ser_bytes = ser.readline()
    data = ser_bytes[0:len(ser_bytes) - 2].decode("utf-8")
    print(data)
    if data.find('TagAdded') != -1:
        id = ((data.split(':')[3]).split(','))[0]
        print("Tag Detected : ", id)
    ser.readline()


def login_user(user, password):
    print(user, ' ', password)
    # Get UserName
    # Get Password
    # Check username and password from DB
    # on failure, show Incorrect User ID/ Password
    # On Success, Get Tag ID (a64) from DB
    # Discover Tag ID / Try to connect to Tag ID using ADDTAG 082261444D83CA1F 1000 2 64 1 command
    # On successful Detection, reply message containing TagAdded received
    # Calculate Distance and check if within accepted Range
    # On Failure, request User to bring the Tag within the accepted range
    # On Success, Login User


def create_user(user, password):
    print(user, ' ', password)
    # Get Username
    # Get Password
    # Confirm Password
    # Discover and Bind Tag with User
    # Store {username, password, Tag Long Addr (a64)}
    # User Added Successfully


def get_distance():
    while True:
        # data = ser.readline().strip('\n\r')
        ser_bytes = ser.readline()
        data = ser_bytes[0:len(ser_bytes) - 2].decode("utf-8")
        print(data)
        data = '{' + (data.split('{', 1))[1]
        y = json.loads(data)
        print(y)
        print(y["TWR"]["D"])
        if int(y["TWR"]["D"]) < auth_distance:
            return True
        # print(data)#ser_bytes)


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    global ser
    ser = serial.Serial()
    ser.port = 'COM7'
    # try:
    ser.open()
    # sendData('GETDLIST')
    # ser_bytes = ser.readline()
    # print(ser_bytes)
    # ser_bytes = ser.readline()
    verify_uwb_tag('082261444D83CA1F')
    get_distance()
    print('User Authenticated Successfully')
    # except:
    #    print("Could not Open Port")
    #    return


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

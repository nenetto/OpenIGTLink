#!/usr/bin/env python
__author__ = 'Eugenio Marinetto'
__version__ = '1'
__date__ = 'March 18 2015'

import sys
import socket
import time
import struct
import ctypes
from threading import Thread, Semaphore, Event
import numpy as np
import copy
# VTK and BiiGTK
sys.path.insert(0, r'J:\Build\BiiGTKvs13\PythonTools')
sys.path.insert(0, r'J:\Build\BiiGTKvs13\Slicer-build\Slicer-build\bin\Release')
sys.path.insert(0, r'J:\Build\BiiGTKvs13\Slicer-build\Slicer-build\bin\Python')
sys.path.insert(0, r'J:\Build\BiiGTKvs13\Slicer-build\Slicer-build\lib\Slicer-4.4\qt-loadable-modules\Release')
sys.path.insert(0, r'J:\Build\BiiGTKvs13\Slicer-build\Slicer-build\bin\lib\Slicer-4.4\qt-loadable-modules\Python')
sys.path.insert(0, r'J:\Build\BiiGTKvs13\VTK-build\bin\Release')
sys.path.insert(0, r'J:\Build\BiiGTKvs13\VTK-build\Wrapping\Python')
sys.path.insert(0, r'J:\Build\BiiGTKvs13\Python\python27.zip')
sys.path.insert(0, r'J:\Build\BiiGTKvs13\Python\DLLs')
sys.path.insert(0, r'J:\Build\BiiGTKvs13\Python\lib')
sys.path.insert(0, r'J:\Build\BiiGTKvs13\Python\lib\plat-win')
sys.path.insert(0, r'J:\Build\BiiGTKvs13\Python\lib\lib-tk')
sys.path.insert(0, r'J:\Build\BiiGTKvs13\Python')
sys.path.insert(0, r'J:\Build\BiiGTKvs13\Python\lib\site-packages')
sys.path.insert(0, r'J:\Build\BiiGTKvs13\Python\lib\site-packages\win32')
sys.path.insert(0, r'J:\Build\BiiGTKvs13\Python\lib\site-packages\win32\lib')
sys.path.insert(0, r'J:\Build\BiiGTKvs13\Python\lib\site-packages\Pythonwin')
sys.path.insert(0, r'J:\Build\BiiGTKvs13\Python\lib\site-packages\setuptools-3.6-py2.7.egg')
sys.path.insert(0, r'J:\Build\BiiGTKvs13')
sys.path.insert(0, r'J:\Dev\BiiGTK\BiiGTK\SlicerBiiGTK')

class Inclinometer:
    def __init__(self):
        self.igtlink = IGTLinkConnection()
        self.igtlink.hostname = 'localhost'

    def connect(self):
        self.igtlink.connect()

    def disconnect(self):
        self.igtlink.disconnect()


class IGTLinkConnection:
    # Private Data Member
    __mutexTransformData = None
    __transformList = None
    __igtlinkStatus = None
    __mutexigtLinkStatus = None
    __mutexState = None
    __state = None

    def __init__(self, host = 'localhost', portnumber = 18944):
        self.hostname = host
        self.portnumber = portnumber
        self.socketobject = None
        self.remote_ip = None
        self.messageHeaderReceiveTimeoutSec=5;
        self.messageBodyReceiveTimeoutSec=50;
        self.__transformList = list()
        self.__mutexTransformData = Semaphore()
        self.__igtlinkStatus = IgtLinkStatus()
        self.__mutexigtLinkStatus = Semaphore()
        self.__state = "Disconnected"
        self.__mutexState = Semaphore()

    def getState(self):
        self.__mutexState.acquire()
        try:
            state = self.__state
        finally:
            self.__mutexState.release()
        return state

    def setState(self, newState):
        self.__mutexState.acquire()
        try:
            self.__state = newState
        finally:
            self.__mutexState.release()
        return

    def connect(self):

        if self.getState() == "Connected":
            return

        previousState = self.getState()

        if previousState == "Disconnected":
            self.setState("AttemptingToConnect")
            print "Trying to connect"
            try:
                #create an AF_INET, STREAM socket (TCP)
                self.socketobject = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            except socket.error, msg:
                print "[Error]: Cannot Connect from state: " + previousState
                self.setState(previousState)
                print 'Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1]
                sys.exit();
            print "Socket Created"

            try:
                self.remote_ip = socket.gethostbyname( self.hostname )
            except socket.gaierror:
                print "[Error]: Cannot Connect from state: " + previousState
                self.__state = previousState
                self.__mutexState.release()
                #could not resolve
                print 'Hostname could not be resolved. Exiting'
                sys.exit()

            print 'Ip address of ' + self.hostname + ' is ' + self.remote_ip

            #Connect to remote server
            self.socketobject.settimeout(1)
            self.socketobject.connect((self.remote_ip , self.portnumber))

            print 'Socket Connected to ' + self.hostname + ' on ip ' + self.remote_ip
            self.setState("Connected")
            return
        print "[Error]: Cannot Connect from state: " + previousState
        self.setState(previousState)

    def disconnect(self):

        if self.getState() == "Disconnected":
            return

        previousState = self.getState()
        if self.getState() == "Connected":
            self.setState("AttemptingToDisconnect")

            if isinstance(self.socketobject, socket.socket):
                self.socketobject.close()
                print 'Connection closed'
                self.setState("Disconnected")
                return
            else:
                print "[Error] Disconnection Failed!"
                self.setState(previousState)
                return

    def socketReadV(self):
        coding = '>H' # V is unsigned short big endian
        numberOfBytes = struct.calcsize(coding)
        socketResult = self.socketobject.recv(numberOfBytes)
        result = struct.unpack(coding,socketResult)
        #print 'Version: ', int(result[0])
        return int(result[0])

    def socketReadTYPE(self):
        coding = '>s' # TYPE is char[12] big endian
        numberOfBytes = 12
        socketResult = self.socketobject.recv(numberOfBytes)
        typeStr = ""
        for e in socketResult:
            if e.isalpha():
                typeStr = typeStr + e
        return typeStr

    def socketReadDEVICE_NAME(self):
        coding = '>s' # DEVICE_NAME is char[20] big endian
        numberOfBytes = 20
        socketResult = self.socketobject.recv(numberOfBytes)
        #print 'DEVICE_NAME: ', socketResult
        return socketResult.replace(" ", "")

    def socketReadTIME_STAMP(self):
        # Retrieve timestamp information from the 64-bit OpenIGTLink timestamp
        # Timestamps are represented as a 64-bit unsigned fixed-point number.
        # http://wiki.na-mic.org/Wiki/index.php/OpenIGTLink/Timestamp
        seconds = self.readUnsignedInt32()
        frac = self.readUnsignedInt32()

        fracbin = bin(frac)
        fracbin = fracbin[2::]
        fraction = 0.0
        n = -1
        for i in fracbin:
            fraction = fraction + int(i) * (2**n)
            n = n - 1

        timestamp = seconds + fraction

        #print 'TIME_STAMP: ', timestamp
        self.currentTimeStamp = timestamp
        return timestamp

    def socketReadBODY_SIZE(self):
        bodysize = self.readUnsignedInt64()
        #print 'BODY_SIZE: ', bodysize
        return bodysize

    def socketReadCRC64(self):
        crc64 = self.readUnsignedInt64()
        #print 'CRC64: ', crc64
        return crc64

    def socketReadBODY(self, numberOfBytes):
        # BODY is X bit unsigned int big endian
        #body = self.socketobject.recv(numberOfBytes)
        #print 'BODY: ', body
        pass

    def readUnsignedInt32(self):
        coding = '>L' #  32 bits
        numberOfBytes = struct.calcsize(coding)
        socketResult = self.socketobject.recv(numberOfBytes)
        result = struct.unpack(coding,socketResult)
        return result[0]

    def readFloat32(self):
        coding = '>f' #  32 bits
        numberOfBytes = struct.calcsize(coding)
        socketResult = self.socketobject.recv(numberOfBytes)
        result = struct.unpack(coding,socketResult)
        return result[0]

    def readUnsignedInt64(self):
        coding = '>Q' #  64 bits
        numberOfBytes = struct.calcsize(coding)
        socketResult = self.socketobject.recv(numberOfBytes)
        result = struct.unpack(coding,socketResult)
        return result[0]

    def readTransformData(self, bodySize):

        # Check if the body size is consistent with the number of bytes that we read from the stream
        # http://openigtlink.org/protocols/v2_transform.html

        if(bodySize != 48):
            print("[Error]: Wrong Transform Body Size")
        else:
            # Read data from transform
            matrixData = np.matrix(np.identity(4))

            matrixData[0,0] = self.readFloat32()
            matrixData[1,0] = self.readFloat32()
            matrixData[2,0] = self.readFloat32()

            matrixData[0,1] = self.readFloat32()
            matrixData[1,1] = self.readFloat32()
            matrixData[2,1] = self.readFloat32()

            matrixData[0,2] = self.readFloat32()
            matrixData[1,2] = self.readFloat32()
            matrixData[2,2] = self.readFloat32()

            matrixData[0,3] = self.readFloat32()
            matrixData[1,3] = self.readFloat32()
            matrixData[2,3] = self.readFloat32()



        return matrixData

    def updateStatusData(self, bodySize, timestamp):

        # Check if the body size is consistent with the number of bytes that we read from the stream
        # http://openigtlink.org/protocols/v2_status.html

        expectedSize = 2 + 8 + 20 + bodySize - 30 # C, Subcode, Error Name, Status Message
        if(bodySize != expectedSize):
            print("[Error]: Wrong Status Body Size")
        else:
            self.__mutexigtLinkStatus.acquire()
            # Read Code

            coding = '>H' # Code is unsigned short big endian
            numberOfBytes = struct.calcsize(coding)
            socketResult = self.socketobject.recv(numberOfBytes)
            Data_Code = struct.unpack(coding,socketResult)
            Data_Code = Data_Code[0]

            # Subcode

            coding = '>q' # Subcode is 64 bit integer
            numberOfBytes = struct.calcsize(coding)
            socketResult = self.socketobject.recv(numberOfBytes)
            Data_Subcode = struct.unpack(coding,socketResult)
            Data_Subcode = Data_Subcode[0]

            # Error Name

            coding = '>' + 's' # Error Name is char[20]
            numberOfBytes = struct.calcsize(coding)
            socketResult = self.socketobject.recv(numberOfBytes)
            Data_ErrorName = struct.unpack(coding,socketResult)
            Data_ErrorName = Data_ErrorName[0]

            # Error Name

            coding = '>' + 's'
            numberOfBytes = struct.calcsize(coding)
            socketResult = self.socketobject.recv(numberOfBytes)
            Data_StatusMessage = struct.unpack(coding,socketResult)
            Data_StatusMessage = Data_StatusMessage[0]

            self.__igtlinkStatus.setNewData( Data_Code, Data_Subcode, Data_ErrorName, Data_StatusMessage, timestamp )

            self.__mutexigtLinkStatus.release()

    def readingThread(self):
        # Read a complete message
        previousState = self.getState()
        #if self.getState() == "Listening":
        if True:
            self.setState("AttemptingToRecieveNewData")
            # Read header
            data_version = self.socketReadV()
            data_type = self.socketReadTYPE()
            data_devicename = self.socketReadDEVICE_NAME()
            data_timestamp = self.socketReadTIME_STAMP()
            data_bodysize = self.socketReadBODY_SIZE()
            data_crc64 = self.socketReadCRC64()

            if data_type == "TRANSFORM":
                data_transform = self.readTransformData(data_bodysize)
                # Check if transform was readed before
                transform = self.getFromTransformList(data_devicename)
                if transform == None:
                    # Creating new device and add to the list
                    transform = IgtLinkTransform(data_devicename)
                    self.appendToTransformList(transform)
                # Addind new data to the transform
                transform.setNewData(data_transform,data_timestamp)
                print transform
            elif data_type == "STATUS":
                self.updateStatusData(data_bodysize, data_timestamp)
                print self.__igtlinkStatus
            else:
                # Read and forget body
                print "Type is not recognised: " + data_type
                print "Size of Body: " + str(data_bodysize)
                self.socketReadBODY(data_bodysize)

            self.setState(previousState)


        else:
            print "[Error]: Cannot Read new Data from state: " + previousState
            self.setState(previousState)

    def getFromTransformList(self, newname):
        self.__mutexTransformData.acquire()
        for t in self.__transformList:
            if t.isTransformName(newname):
                self.__mutexTransformData.release()
                return t
        # Not found in previous transformations... returning None
        self.__mutexTransformData.release()
        return None

    def appendToTransformList(self, newtransform):
        self.__mutexTransformData.acquire()
        try:
            self.__transformList.append(newtransform)
        finally:
            self.__mutexTransformData.release()
        return


class IgtLinkStatus:
    # Private data members
    __timestampSeconds = None
    __statusCode = None
    __statusSubcode = None
    __errorName = None
    __statusMessage = None
    __statusCodeMessage = None
    __mutex = None

    def __init__(self):
        self.__timestampSeconds = None
        self.__statusCode = None
        self.__statusSubcode = None
        self.__errorName = None
        self.__statusMessage = None
        self.__statusCodeMessage = None
        self.__mutex = Semaphore()

    def __str__(self):
        statusCode, statusSubcode, errorName, statusMessage, statusCodeMessage, timestampSeconds = self.getData()
        strForPrint = "Status Message:\n"
        strForPrint = strForPrint + "Status Code        :" + str(statusCode) +"\n"
        strForPrint = strForPrint + "Status Subcode     :" + str(statusSubcode) +"\n"
        strForPrint = strForPrint + "Error Name         :" + errorName #+"\n"
        strForPrint = strForPrint + "Status Message     :" + statusMessage +"\n"
        strForPrint = strForPrint + "Status Code Message:" + statusCodeMessage +"\n"
        return strForPrint

    def setNewData(self, statusCode, statusSubcode, errorName, statusMessage, timestampSeconds ):

        self.__mutex.acquire()
        try:
            self.__timestampSeconds = timestampSeconds
            self.__statusCode = statusCode
            self.__statusSubcode = statusSubcode
            self.__errorName = errorName
            self.__statusMessage = statusMessage
            self.__statusCodeMessage = self.decodeCode(self.__statusCode)
        finally:
            self.__mutex.release()
        return

    def getData(self):
        timestampSeconds = None
        statusCode = None
        statusSubcode = None
        errorName = None
        statusMessage = None
        statusCodeMessage = None

        self.__mutex.acquire()
        try:
            timestampSeconds = copy.deepcopy(self.__timestampSeconds)
            statusCode = copy.deepcopy(self.__statusCode)
            statusSubcode = copy.deepcopy(self.__statusSubcode)
            errorName = copy.deepcopy(self.__errorName)
            statusMessage = copy.deepcopy(self.__statusMessage)
            statusCodeMessage = copy.deepcopy(self.__statusCodeMessage)
        finally:
            self.__mutex.release()

        return statusCode, statusSubcode, errorName, statusMessage, statusCodeMessage,timestampSeconds

    def decodeCode(self, code):
        messageList = (["Invalid packet - 0 is not used",
                        "OK (Default status)",
                        "Unknown error",
                        "Panic mode (emergency)",
                        "Not found (file, configuration, device etc)",
                        "Access denied",
                        "Busy",
                        "Time out - Connection lost",
                        "Overflow - Can't be reached",
                        "Checksum error",
                        "Configuration error",
                        "Not enough resource (memory, storage etc)",
                        "Illegal/Unknown instruction (or feature not implemented / Unknown command received)",
                        "Device not ready (starting up)",
                        "Manual mode (device does not accept commands)",
                        "Device disabled",
                        "Device not present",
                        "Device version not known",
                        "Hardware failure",
                        "Exiting / shut down in progress"])

        return messageList[code]


class IgtLinkTransform:
    # Private data members
    __timestampSeconds = None
    __transformName = None
    __transformMatrix = None
    __mutex = None

    def __init__(self, name = "NoName"):
        self.__timestampSeconds = None
        self.__transformName = name
        self.__transformMatrix = np.matrix(np.identity(4))
        self.__mutex = Semaphore()

    def __str__(self):
        transformName, transformMatrix, timestamp = self.getData()
        strForPrint = "Transform Name: " + transformName +  "\n"
        strForPrint = strForPrint + "     TimeStamp: " + timestamp.__str__() +  "\n"
        strForPrint = strForPrint + "          Data: \n" + transformMatrix.__str__() +  "\n"
        return strForPrint

    def setNewData(self, trasform, timestamp):

        self.__mutex.acquire()
        try:
            self.__timestampSeconds = timestamp
            self.__transformMatrix = trasform
        finally:
            self.__mutex.release()

    def getData(self):
        timestamp = None
        transformName = None
        transformMatrix = None

        self.__mutex.acquire()
        try:
            timestamp = copy.deepcopy(self.__timestampSeconds)
            transformMatrix = self.__transformMatrix.copy()
            transformName = copy.deepcopy(self.__transformName)
        finally:
            self.__mutex.release()

        return transformName, transformMatrix, timestamp

    def isTransformName(self, name):
        self.__mutex.acquire()
        try:
            thisName = self.__transformName
        finally:
            self.__mutex.release()
        if name == thisName:
            return True
        else:
            return False





#Bytes
#0   2                       14                                      34             42               50              58
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+.....
#| V |          TYPE         |              DEVICE_NAME              |   TIME_STAMP  |   BODY_SIZE   |     CRC64     |   BODY
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+.....

def TestPhidgetIGTLink():
    print "Creating inclinometer"
    inclinometer = Inclinometer()
    print "Connecting inclinometer"
    inclinometer.connect()
    while True:
        print "Reading inclinometer"
        inclinometer.igtlink.readingThread()
    print "Closing inclinometer"
    inclinometer.disconnect()

    """
    inclinometer = Inclinometer()
    inclinometer.connect()
    while True:
        v = inclinometer.igtlink.socketReadV()
        typemsg = inclinometer.igtlink.socketReadTYPE()
        devname = inclinometer.igtlink.socketReadDEVICE_NAME()
        timestamp = inclinometer.igtlink.socketReadTIME_STAMP()
        bodySize = inclinometer.igtlink.socketReadBODY_SIZE()
        crc = inclinometer.igtlink.socketReadCRC64()
        body = inclinometer.igtlink.socketReadBODY(bodySize)
    inclinometer.disconnect()
    """
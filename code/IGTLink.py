#!/usr/bin/env python
__author__ = 'Eugenio Marinetto'
__version__ = '1'
__date__ = 'March 18 2015'

import sys
import socket
import time
import struct
from threading import Thread, Semaphore
import numpy as np
import copy
import math


class IGTLinkConnection:
    # Private Data Member
    __mutexTransformData = None
    __transformList = None
    __igtlinkStatus = None
    __mutexigtLinkStatus = None
    __mutexState = None
    __state = None

    #Bytes
    #0   2                       14                                      34             42               50              58
    #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+.....
    #| V |          TYPE         |              DEVICE_NAME              |   TIME_STAMP  |   BODY_SIZE   |     CRC64     |   BODY
    #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+.....


    def __init__(self, host = 'localhost', portnumber = 18944):
        print "__init__"
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
        self._readingthread = None
        self.__mutexStopSignal = Semaphore()
        self.__threadStopSignal = True
        self.__numberOfCalls = 0

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

    def getStopSignal(self):
        self.__mutexStopSignal.acquire()
        try:
            state = self.__threadStopSignal
        finally:
            self.__mutexStopSignal.release()
        return state

    def setStopSignal(self, newState):
        self.__mutexStopSignal.acquire()
        try:
            self.__threadStopSignal = newState
        finally:
            self.__mutexStopSignal.release()
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
                self.setState(previousState)
                return
            print "Socket Created"

            try:
                self.remote_ip = socket.gethostbyname( self.hostname )
            except socket.gaierror:
                print "[Error]: Cannot Connect from state: " + previousState
                self.setState(previousState)
                return
                print 'Hostname could not be resolved. Exiting'
                sys.exit()

            print 'Ip address of ' + self.hostname + ' is ' + self.remote_ip

            #Connect to remote server
            self.socketobject.settimeout(1)

            connected = False
            counter = 0
            while connected == False:
                counter = counter + 1
                try:
                    self.socketobject.connect((self.remote_ip , self.portnumber))
                    connected = True
                except Exception, e:
                    print('[Error]:Connection to socket was wrong %s:%d. ' % (self.remote_ip, self.portnumber))
                    print('        Exception type is %s' % e)
                    connected = False
                    if counter == 10:
                        self.setState(previousState)
                        print "[Error]: Cannot Connect socket"
                        return



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
        bytes_recd = 0
        while bytes_recd < numberOfBytes:
            chunk = self.socketobject.recv(min(numberOfBytes - bytes_recd, 2048))
            bytes_recd = bytes_recd + min(numberOfBytes - bytes_recd, 2048)
        return


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
            self.setState(previousState)
            return -1
        else:
            matrixData = np.matrix(np.identity(4))
            # Read data from transform
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

        coding = '>' + 'c'*20 # Error Name is char[20]
        numberOfBytes = struct.calcsize(coding)
        socketResult = self.socketobject.recv(numberOfBytes)
        Data_ErrorName = struct.unpack(coding,socketResult)
        Data_ErrorName = Data_ErrorName[0]

        # Error Name

        coding = '>' + 'c' * (bodySize - 30)
        numberOfBytes = struct.calcsize(coding)
        socketResult = self.socketobject.recv(numberOfBytes)
        Data_StatusMessage = struct.unpack(coding,socketResult)
        Data_StatusMessage = Data_StatusMessage[0]

        self.__igtlinkStatus.setNewData( Data_Code, Data_Subcode, Data_ErrorName, Data_StatusMessage, timestamp )


    def readingThread(self):
        self.__numberOfCalls = self.__numberOfCalls + 1
        print "Thread Called: ", self.__numberOfCalls, " times"

        # Read a complete message
        previousState = self.getState()
        while self.getState() == "Listening" and self.getStopSignal() == False:
            self.setState("AttemptingToRecieveNewData")
            # Read header
            try:
                data_version = self.socketReadV()
                data_type = self.socketReadTYPE()
                data_devicename = self.socketReadDEVICE_NAME()
                data_timestamp = self.socketReadTIME_STAMP()
                data_bodysize = self.socketReadBODY_SIZE()
                data_crc64 = self.socketReadCRC64()
            except:
                print "Link could be death... Stopping Listening"
                self.stopListening()
                return -1

            if data_type == "TRANSFORM":
                try:
                    data_transform = self.readTransformData(data_bodysize)
                except:
                    print "Link could be death... Stopping Listening"
                    self.stopListening()
                    return -1
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
                try:
                    self.updateStatusData(data_bodysize, data_timestamp)
                except:
                    print "Link could be death... Stopping Listening"
                    self.stopListening()
                    return -1
                print self.__igtlinkStatus
            else:
                # Read and forget body
                print "Type is not recognised: " + data_type
                print "Size of Body: " + str(data_bodysize)
                try:
                    self.socketReadBODY(data_bodysize)
                except:
                    print "Link could be death... Stopping Listening"
                    self.stopListening()
                    return -1

            self.setState("Listening")


        self.setState("Connected")

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

    def startListening(self):
        previousState = self.getState()

        if previousState == "Connected":
            self.setState("Listening")
            self.setStopSignal(False)
            # Launch Thread for reading
            self._readingthread = Thread(target=self.readingThread, args=())
            self._readingthread.daemon = True   # Daemonize thread
            self._readingthread.start()

    def stopListening(self):
        self.setStopSignal(True)

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
        strForPrint = strForPrint + "Error Name         :" + str(errorName) +"\n"
        strForPrint = strForPrint + "Status Message     :" + str(statusMessage) +"\n"
        strForPrint = strForPrint + "Status Code Message:" + str(statusCodeMessage) +"\n"
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
    __angleTotal = None

    def __init__(self, name = "NoName"):
        self.__timestampSeconds = None
        self.__transformName = name
        self.__transformMatrix = np.matrix(np.identity(4))
        self.__mutex = Semaphore()
        self.__angleTotal = 0.0

    def __str__(self):
        transformName, transformMatrix, timestamp, angle = self.getData()
        strForPrint = "Transform Name: " + transformName +  "\n"
        #strForPrint = strForPrint + "     TimeStamp: " + timestamp.__str__() +  "\n"
        #strForPrint = strForPrint + "          Data: \n" + transformMatrix.__str__() +  "\n"
        strForPrint = strForPrint + "         Angle: " + str(angle) +  "\n"
        return strForPrint

    def setNewData(self, trasform, timestamp):

        self.__mutex.acquire()
        try:
            self.__timestampSeconds = timestamp
            self.__transformMatrix = trasform
            self.__angleTotal = self.calculateAngle(trasform)
        finally:
            self.__mutex.release()

    def calculateAngle(self, matrix):

        # Plane XY rotated, cross is the perpendicular vector to the rotated plane
        #crossX = matrix[0,1] * matrix[1,2] - matrix[0,2] * matrix[1,1]
        #crossY = matrix[0,2] * matrix[1,0] - matrix[0,0] * matrix[1,2]
        crossZ = matrix[0,0] * matrix[1,1] - matrix[0,1] * matrix[1,0]

        # Product of the rotated plane vector and Z (Original position)
        dot = crossZ
        return math.degrees(math.acos(dot))


    def getData(self):
        timestamp = None
        transformName = None
        transformMatrix = None
        angle = 0.0

        self.__mutex.acquire()
        try:
            timestamp = copy.deepcopy(self.__timestampSeconds)
            transformMatrix = self.__transformMatrix.copy()
            transformName = copy.deepcopy(self.__transformName)
            angle = copy.deepcopy(self.__angleTotal)
        finally:
            self.__mutex.release()

        return transformName, transformMatrix, timestamp, angle

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




def TestIGTLink():

    igtlink = IGTLinkConnection()
    igtlink.hostname = '10.140.18.210'
    igtlink.connect()
    igtlink.startListening()
    time.sleep(10)
    igtlink.stopListening()
    igtlink.disconnect()


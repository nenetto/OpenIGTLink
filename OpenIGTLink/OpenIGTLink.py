#!/usr/bin/env python
__author__ = 'Eugenio Marinetto'
__version__ = '1'
__date__ = 'March 11 2016'


import threading
import copy
import numpy
import struct
import socket
import helpers
import pandas
import time
import signal

class OpenIGTLinkHeader:

    # Private data members
    _mutex = None
    __coding_V = '>H' # V is unsigned short big endian
    __maxCharLength_TYPE = 12
    __maxCharLength_DEVICE_NAME = 20
    __coding_TIME_STAMP = '>LL' # TIME_STAMP is 2 Int 32
    __coding_BODY_SIZE = '>Q' # BODY_SIZE is 64 unsigned int
    __coding_CRC64 = '>Q' # CRC64 is 64 unsigned int

    IGTLinkHeaderSize = struct.calcsize(__coding_V) + \
                        __maxCharLength_TYPE + \
                        __maxCharLength_DEVICE_NAME + \
                        struct.calcsize(__coding_TIME_STAMP) + \
                        struct.calcsize(__coding_BODY_SIZE) + \
                        struct.calcsize(__coding_CRC64)

    #Bytes
    #0   2                       14                                      34             42               50              58
    #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #| V |          TYPE         |              DEVICE_NAME              |   TIME_STAMP  |   BODY_SIZE   |     CRC64     |
    #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

    def __init__(self, version = 1):

        # Create mutex for changes
        self._mutex =threading.Semaphore()

        # V: Header version number
        # The version number field specifies the header format version. 
        # Currently the version number is 1. 
        # Please note that this is different from the protocol version.
        self.__V = version

        # TYPE:  name of data
        self.__TYPE = None

        # DEVICE_NAME: Unique device name
        self.__DEVICE_NAME = None

        # TIME_STAMP: Timestamp or 0 if unused
        self.__TIME_STAMP_SECONDS = None
        self.__TIME_STAMP_FRACTION = None

        # BODY_SIZE: Size of body in bytes
        self.__BODY_SIZE = None

        # CRC: 64 bit CRC for body data
        # CRC The 64-bit CRC used in OpenIGTLink protocol is based on ECMA-182 standard.
        self.__CRC64 = None

    def setV(self, newversion):
        self._mutex.acquire()
        try:
            self.__V = copy.deepcopy(newversion)
        except Exception as inst:
            print '[OpenIGTLinkHeader][ERROR]: Cannot set Version'
            print instruction
        finally:
            self._mutex.release()

    def getV(self):
        self._mutex.acquire()
        try:
            return copy.deepcopy(self.__V)
        except Exception as inst:
            print '[OpenIGTLinkHeader][ERROR]: Cannot get Version'
            print inst
        finally:
            self._mutex.release()

    def getVBits(self):
        self._mutex.acquire()
        result = None
        try:
            result = struct.pack(self.__coding_V, self.__V)
        except Exception as inst:
            print '[OpenIGTLinkHeader][ERROR]: Cannot get Version'
            print inst
        finally:
            self._mutex.release()
            return result

    def setTYPE(self, newtype):
        self._mutex.acquire()
        try:

            # Check valid TYPE: char[12]
            if   newtype == 'TRANSFORM':
                self.__TYPE_GROUP = 0
            elif newtype == 'QTRANS':
                self.__TYPE_GROUP = 0
            elif newtype == 'POSITION':
                self.__TYPE_GROUP = 0
            elif newtype == 'IMAGE':
                self.__TYPE_GROUP = 0
            elif newtype == 'STATUS':
                self.__TYPE_GROUP = 0
            elif newtype == 'CAPABILITY':
                self.__TYPE_GROUP = 0
            elif newtype == 'IMGBETA':
                self.__TYPE_GROUP = 2
            elif newtype == 'LBMETA':
                self.__TYPE_GROUP = 2
            elif newtype == 'COLORT':
                self.__TYPE_GROUP = 2
            elif newtype == 'POINT':
                self.__TYPE_GROUP = 2
            elif newtype == 'TRAJ':
                self.__TYPE_GROUP = 2
            elif newtype == 'TDATA':
                self.__TYPE_GROUP = 2
            elif newtype == 'QTDATA':
                self.__TYPE_GROUP = 2
            elif newtype == 'SENSOR':
                self.__TYPE_GROUP = 3
            elif newtype == 'STRING':
                self.__TYPE_GROUP = 3
            elif newtype == 'NDARRAY':
                self.__TYPE_GROUP = 3
            elif newtype == 'BIND':
                self.__TYPE_GROUP = 3
            elif newtype == 'POLYDATA':
                self.__TYPE_GROUP = 3
            else:
                raise

            self.__TYPE = newtype
        except Exception as inst:
            print '[OpenIGTLinkHeader][ERROR]: Cannot set TYPE'
            print inst
        finally:
            self._mutex.release()

    def getTYPE(self):
        self._mutex.acquire()
        try:
            return copy.deepcopy(self.__TYPE)
        except Exception as inst:
            print '[OpenIGTLinkHeader][ERROR]: Cannot get TYPE'
            print inst
        finally:
            self._mutex.release()

    def getTYPEBits(self):
        self._mutex.acquire()
        result = None
        try:
            if len(self.__TYPE) < self.__maxCharLength_TYPE:
                diffLength = self.__maxCharLength_TYPE - len(self.__TYPE)
                result = self.__TYPE + '\x00' * diffLength
            else:
                raise
        except Exception as inst:
            print '[OpenIGTLinkHeader][ERROR]: Cannot get TYPE'
            print inst
        finally:
            self._mutex.release()
            return result

    def setDEVICE_NAME(self, newdevice_name):
        self._mutex.acquire()
        try:
            # Check valid DEVICE_NAME: char[20]
            if len(newdevice_name) > self.__maxCharLength_DEVICE_NAME:
                print '[OpenIGTLinkHeader][ERROR]: DEVICE_NAME too long. Max 20 char'
                raise
            else:
                self.__DEVICE_NAME = newdevice_name
        except Exception as inst:
            print '[OpenIGTLinkHeader][ERROR]: Cannot set DEVICE_NAME'
            print inst
        finally:
            self._mutex.release()

    def getDEVICE_NAME(self):
        self._mutex.acquire()
        try:
            return copy.deepcopy(self.__DEVICE_NAME)
        except Exception as inst:
            print '[OpenIGTLinkHeader][ERROR]: Cannot get DEVICE_NAME'
            print inst
        finally:
            self._mutex.release()

    def getDEVICE_NAMEBits(self):
        self._mutex.acquire()
        result = None
        try:
            if len(self.__DEVICE_NAME) <= self.__maxCharLength_DEVICE_NAME:
                diffLength = self.__maxCharLength_DEVICE_NAME - len(self.__DEVICE_NAME)
                result = self.__DEVICE_NAME + '\x00' * diffLength
            else:
                raise
        except Exception as inst:
            print '[OpenIGTLinkHeader][ERROR]: Cannot get DEVICE_NAME'
            print inst
        finally:
            self._mutex.release()
            return result

    def setTIME_STAMP(self, newseconds, newfraction):
        self._mutex.acquire()
        try:
            self.__TIME_STAMP_SECONDS = copy.deepcopy(newseconds)
            self.__TIME_STAMP_FRACTION = copy.deepcopy(newfraction)
        except Exception as inst:
            print '[OpenIGTLinkHeader][ERROR]: Cannot set TIME_STAMP'
        finally:
            self._mutex.release()

    def getTIME_STAMP(self):
        self._mutex.acquire()
        try:
            return self.__TIME_STAMP_SECONDS + self.__TIME_STAMP_FRACTION
        except Exception as inst:
            print '[OpenIGTLinkHeader][ERROR]: Cannot get TIME_STAMP'
            print inst
        finally:
            self._mutex.release()

    def getTIME_STAMPBits(self):
        self._mutex.acquire()
        result = None
        try:
            seconds = self.__TIME_STAMP_SECONDS
            fraction = self.__TIME_STAMP_FRACTION
            # Get 32 bits fraction

            fractionInt32 = int(fraction / 2**(-32))
            secondsInt32 = int(seconds)

            # Pass from bits to int(bits,2) -> to string

            result = struct.pack(self.__coding_TIME_STAMP, secondsInt32, fractionInt32)

        except Exception as inst:
            print '[OpenIGTLinkHeader][ERROR]: Cannot get TIME_STAMP'
            print inst
        finally:
            self._mutex.release()
            return result
        
    def setBODY_SIZE(self, newbody_size):
        self._mutex.acquire()
        try:
            self.__BODY_SIZE = copy.deepcopy(newbody_size)
        except Exception as inst:
            print '[OpenIGTLinkHeader][ERROR]: Cannot set Body Size'
            print inst
        finally:
            self._mutex.release()

    def getBODY_SIZE(self):
        self._mutex.acquire()
        try:
            return copy.deepcopy(self.__BODY_SIZE)
        except Exception as inst:
            print '[OpenIGTLinkHeader][ERROR]: Cannot get Body Size'
            print inst
        finally:
            self._mutex.release()

    def getBODY_SIZEBits(self):
        self._mutex.acquire()
        result = None
        try:
            result = struct.pack(self.__coding_BODY_SIZE, self.__BODY_SIZE)
        except Exception as inst:
            print '[OpenIGTLinkHeader][ERROR]: Cannot get Body Size'
            print inst
        finally:
            self._mutex.release()
            return result

    def setCRC64(self, bodyData):
        self._mutex.acquire()
        try:
            self.__CRC64 = helpers.crc64(bodyData)
        except Exception as inst:
            print '[OpenIGTLinkHeader][ERROR]: Cannot set CRC64'
            print inst
        finally:
            self._mutex.release()

    def getCRC64(self):
        self._mutex.acquire()
        try:
            return copy.deepcopy(self.__CRC64)
        except Exception as inst:
            print '[OpenIGTLinkHeader][ERROR]: Cannot get Body Size'
            print inst
        finally:
            self._mutex.release()

    def getCRC64Bits(self):
        self._mutex.acquire()
        result =  None
        try:
            result = struct.pack(self.__coding_CRC64, self.__CRC64)
        except Exception as inst:
            print '[OpenIGTLinkHeader][ERROR]: Cannot get CRC64 bits'
        finally:
            self._mutex.release()
            return result

    def getHeaderMessage(self):
        self._message =  self.getVBits() + self.getTYPEBits() + self.getDEVICE_NAMEBits() + self.getTIME_STAMPBits() + self.getBODY_SIZEBits() + self.getCRC64Bits()
        return self._message

    def __str__(self):

        strForPrint = '#### Header \n\n'

        strForPrint = strForPrint + '####        Version             :' + str(self.getV()) + '\n'
        strForPrint = strForPrint + '####        Type                :' + str(self.getTYPE()) +'\n'
        strForPrint = strForPrint + '####        Device Name         :' + str(self.getDEVICE_NAME()) +'\n'
        strForPrint = strForPrint + '####        Time Stamp          :' + str(self.getTIME_STAMP()) +' sec.\n'
        strForPrint = strForPrint + '####        Body Size           :' + str(self.getBODY_SIZE()) +' B\n'
        strForPrint = strForPrint + '####        CRC64               :' + str(self.getCRC64()) +'\n'
        strForPrint = strForPrint + '####        Byte Representation :' + repr(self.getHeaderMessage()) +'\n\n'

        return strForPrint

    def unpack(self, headerDataString):  

        # Read V
        result = struct.unpack(self.__coding_V,headerDataString[0:2])
        self.setV(int(result[0]))
        headerDataString = headerDataString[2::]

        # Read TYPE
        typeStr = headerDataString[0:self.__maxCharLength_TYPE].replace('\x00', '')
        self.setTYPE(typeStr)
        headerDataString = headerDataString[self.__maxCharLength_TYPE::]

        # Read DEVICE_NAME
        typeStr = headerDataString[0:self.__maxCharLength_DEVICE_NAME].replace('\x00', '')
        self.setDEVICE_NAME(typeStr)
        headerDataString = headerDataString[self.__maxCharLength_DEVICE_NAME::]

        # Read TIME_STAMP
        seconds, frac = struct.unpack(self.__coding_TIME_STAMP,headerDataString[0:8])

        fraction = frac * 2**(-32)
        self.setTIME_STAMP(seconds, fraction)

        headerDataString = headerDataString[8::]

        # Read BODY_SIZE
        bodySize = struct.unpack(self.__coding_BODY_SIZE,headerDataString[0:8])[0]
        self.setBODY_SIZE(bodySize)
        headerDataString = headerDataString[8::]

        # Read CRC64
        crc = struct.unpack(self.__coding_CRC64,headerDataString[0:8])
        self._mutex.acquire()
        try:
            self.__CRC64 = copy.deepcopy(crc)
        except Exception as inst:
            print inst
        finally:
            self._mutex.release()

class OpenIGTLinkBody:

    # Private data members
    _mutex = None
    _message = None

    def __init__(self):

        # Create mutex for changes
        self._mutex =threading.Semaphore()

        # Body message
        self._message = None

    def setBodyMessage(self, newbodymsg):
        self._mutex.acquire()
        try:
            self._message = copy.deepcopy(newbodymsg)
        except Exception as inst:
            print '[OpenIGTLinkBody][ERROR]: Cannot set Body Message'
            print inst
        finally:
            self._mutex.release()

    def getBodyMessage(self):
        self._mutex.acquire()
        try:
            return copy.deepcopy(self._message)
        except Exception as inst:
            print '[OpenIGTLinkBody][ERROR]: Cannot get Body Message'
            print inst
        finally:
            self._mutex.release()

    def __str__(self):

        strForPrint = '#### Body \n\n'

        strForPrint = strForPrint + '####        Byte Representation :' + repr(self.getBodyMessage()) +'\n\n'


        return strForPrint

class OpenIGTLinkMessage:

    # Private data members
    _mutex = None

    # Complete Message 
    _message = None

    def __init__(self, device_name = 'None'):

        # Create mutex for changes
        self._mutex =threading.Semaphore()

        # Header message
        self.header = OpenIGTLinkHeader()
        self.header.setDEVICE_NAME(device_name)

        # Body message
        self.body = OpenIGTLinkBody()

    def __updateMessage__(self, bodycoding):
        # Att. This function is not mutex controlled, only must be called inside functions not from outside

        # Calculate CRC64 for body
        self.header.setCRC64(bodyData = self.body.getBodyMessage())

        # Calculate body size and set header
        self.header.setBODY_SIZE(newbody_size = struct.calcsize(bodycoding))

        # Prepare message for sending
        self._message =  self.header.getHeaderMessage() + self.body.getBodyMessage()

    def setTimeStamp(self, newTimeStampSeconds):

        seconds = int(newTimeStampSeconds)
        fraction = newTimeStampSeconds - int(newTimeStampSeconds)
        self.header.setTIME_STAMP(seconds, fraction)

    def getTimeStamp(self):

        return self.header.getTIME_STAMP()

    def __str__(self):
        strForPrint = '########################\n\n'

        strForPrint = strForPrint + '#### IGTLink Message\n\n'

        strForPrint = strForPrint  + str(self.header.__str__()) 
        strForPrint = strForPrint  + str(self.body.__str__()) 


        strForPrint = strForPrint  + '########################\n'

        return strForPrint

class OpenIGTLinkTransform(OpenIGTLinkMessage, object):

    # Private data members
    __transform = numpy.eye(4)
    __coding_transform = '>ffffffffffff' # 12 x 32b floats http://openigtlink.org/protocols/v2_transform.html

    def __init__(self, transform_name = 'Transform'):

        # Call father init
        super(OpenIGTLinkTransform, self).__init__(device_name = transform_name)

        # Set type
        self.header.setTYPE('TRANSFORM')

    def setTransform(self, newtransform, newtimestamp):
        self._mutex.acquire()
        try:
            self.__transform = copy.deepcopy(newtransform)

            # Set header data
            self.setTimeStamp(newtimestamp)

        except Exception as inst:
            print '[OpenIGTLinkTransform][ERROR]: Cannot set Transform'
            print inst
        finally:
            self._mutex.release()

    def setOpenIGTLinkTransform(self, npTransform = numpy.eye(4), floatTimeStamp = 0.0, transformName = 'RigidToTracker'):

        self._mutex.acquire()
        try:
            # Copy transform to internal 
            self.__transform = copy.deepcopy(npTransform)

            # Set header data
            self.header.setTYPE('TRANSFORM')
            self.header.setDEVICE_NAME(transformName)
            self.setTimeStamp(floatTimeStamp)

        except Exception as inst:
            print '[OpenIGTLinkTransform][ERROR]: Cannot create Transform'
            print inst
        finally:
            self._mutex.release()

        result = self.getMessageToSend()
        return result

    def getTransform(self):
        self._mutex.acquire()
        result = None
        try:
            result = copy.deepcopy(self.__transform)
        except Exception as inst:
            print '[OpenIGTLinkTransform][ERROR]: Cannot get Transform'
            print inst
        finally:
            self._mutex.release()
            return result

    def getMessageToSend(self):
        self._mutex.acquire()
        result = None
        try:

            # Set body data for message
            bodymsg = struct.pack(self.__coding_transform,  self.__transform[0,0], self.__transform[1,0], self.__transform[2,0],\
                                                            self.__transform[0,1], self.__transform[1,1], self.__transform[2,1],\
                                                            self.__transform[0,2], self.__transform[1,2], self.__transform[2,2],\
                                                            self.__transform[0,3], self.__transform[1,3], self.__transform[2,3])
            
            self.body.setBodyMessage(bodymsg)

            # Update Message

            self.__updateMessage__(bodycoding = self.__coding_transform)

            result = copy.deepcopy(self._message)
        except Exception as inst:
            print '[OpenIGTLinkTransform][ERROR]: Cannot get Message to send'
            print inst
        finally:
            self._mutex.release()
            return result

    def __str__(self):
        strForPrint = '########################\n\n'

        strForPrint = strForPrint + '#### Transform Message\n\n'

        strForPrint = strForPrint + '####        Transform           :\n' + str(self.getTransform()) +'\n'
        strForPrint = strForPrint + '####        Byte Representation :' + repr(self.getMessageToSend()) +'\n\n'

        #strForPrint = strForPrint  + str(self.header.__str__()) 
        #strForPrint = strForPrint  + str(self.body.__str__()) 


        strForPrint = strForPrint  +'########################\n'

        return strForPrint

    def unpackTransform(self, bodyDataString):
        self._mutex.acquire()
        try:

            if len(bodyDataString) != struct.calcsize(self.__coding_transform):
                print '[OpenIGTLinkTransform][ERROR]: length of body is not correct'
                raise
            # Decode header
            self.__transform[0,0], self.__transform[1,0], self.__transform[2,0],\
            self.__transform[0,1], self.__transform[1,1], self.__transform[2,1],\
            self.__transform[0,2], self.__transform[1,2], self.__transform[2,2],\
            self.__transform[0,3], self.__transform[1,3], self.__transform[2,3] = struct.unpack(self.__coding_transform, bodyDataString)

        except Exception as inst:
            print '[OpenIGTLinkTransform][ERROR]: Cannot set Transform'
            print inst
        finally:
            self._mutex.release()

    def getDictRepresentation(self):

        t = self.getTransform()
        dictRepr = {'TYPE':'TRANSFORM',\
                    'DEVICE_NAME': self.header.getDEVICE_NAME(),\
                    'TIME_STAMP': self.header.getTIME_STAMP(),\
                    'T00': t[0,0],\
                    'T01': t[0,1],\
                    'T02': t[0,2],\
                    'T03': t[0,3],\
                    'T10': t[1,0],\
                    'T11': t[1,1],\
                    'T12': t[1,2],\
                    'T13': t[1,3],\
                    'T20': t[2,0],\
                    'T21': t[2,1],\
                    'T22': t[2,2],\
                    'T23': t[2,3],\
                    }
        return dictRepr

class OpenIGTLinkStatus(OpenIGTLinkMessage, object):

    # Private data members
    __statusCode = None
    __statusSubcode = None
    __errorName = None
    __statusMessage = ''

    __coding_CODE = '>H' # Code is 16b unsigned short big endian
    __coding_SUBCODE = '>q' # Subcode is 64 bit integer

    __maxCharLength_ERROR_NAME = 20
    __length_STATUS_MESSAGE = None

    _messageCode = ([  'Invalid packet - 0 is not used',\
                        'OK (Default status)',\
                        'Unknown error',\
                        'Panic mode (emergency)',\
                        'Not found (file, configuration, device etc)',\
                        'Access denied',\
                        'Busy',\
                        'Time out - Connection lost',\
                        'Overflow - Can\'t be reached',\
                        'Checksum error',\
                        'Configuration error',\
                        'Not enough resource (memory, storage etc)',\
                        'Illegal/Unknown instruction (or feature not implemented / Unknown command received)',\
                        'Device not ready (starting up)',\
                        'Manual mode (device does not accept commands)',\
                        'Device disabled',\
                        'Device not present',\
                        'Device version not known',\
                        'Hardware failure',\
                        'Exiting / shut down in progress'])

    def __init__(self, device_name = 'Status', code = 1):

        # Call father init
        super(OpenIGTLinkStatus, self).__init__(device_name = device_name)

        # Set type
        self.header.setTYPE('STATUS')

        # Set default value
        self.setStatus(newStatusCode = code, newStatusSubcode = 0, newErrorMessage = 'OK')

    def __str__(self):
        strForPrint = '########################\n\n'

        strForPrint = strForPrint + '#### Status Message\n\n'

        strForPrint = strForPrint + '####        Status Code         :' + str(self.getCODE()) +'\n'
        strForPrint = strForPrint + '####        Status Subcode      :' + str(self.getSUBCODE()) +'\n'
        strForPrint = strForPrint + '####        Error Name          :' + str(self.getERROR_NAME()) +'\n'
        strForPrint = strForPrint + '####        Status Message      :' + str(self.getSTATUS_MESSAGE()) +'\n'
        strForPrint = strForPrint + '####        Byte Representation :' + repr(self.getMessageToSend()) +'\n\n'

        #strForPrint = strForPrint  + str(self.header.__str__())
        #strForPrint = strForPrint  + str(self.body.__str__()) 

        strForPrint = strForPrint + '########################\n'

        return strForPrint

    def setStatus(self, newStatusCode, newStatusSubcode, newErrorMessage, newStatusMessage = None, newtimestamp = 0.0):
        self.setCODE(newStatusCode)
        self.setSUBCODE(newStatusSubcode)
        self.setERROR_NAME(newErrorMessage)
        if newStatusMessage is None:
            newStatusMessage = self.getErrorString()
        self.setSTATUS_MESSAGE(newStatusMessage)
        self.setTimeStamp(newtimestamp)

    def setOpenIGTLinkStatus(self, statusCode = 1, statusSubCode = 0, errorName = 'OK', statusMessage = None, deviceName = 'Tracker', floatTimeStamp = 0.0):

        try:
            # Copy variables to internal 
            self.setCODE(statusCode)
            self.setSUBCODE(statusSubCode)
            self.setERROR_NAME(errorName)
            if statusMessage is None:
                statusMessage = self.getErrorString()
            self.setSTATUS_MESSAGE(statusMessage)

            # Set header data
            self.header.setTYPE('STATUS')
            self.header.setDEVICE_NAME(deviceName)
            self.setTimeStamp(floatTimeStamp)

        except Exception as inst:
            print '[setOpenIGTLinkStatus][ERROR]: Cannot create Status'
            print inst

        result = self.getMessageToSend()
        return result

    def setCODE(self, newcode):
        self._mutex.acquire()
        try:
            self.__statusCode = copy.deepcopy(newcode)
        except Exception as inst:
            print '[OpenIGTLinkStatus][ERROR]: Cannot set CODE'
            print inst
        finally:
            self._mutex.release()

    def getCODE(self):
        self._mutex.acquire()
        try:
            return copy.deepcopy(self.__statusCode)
        except Exception as inst:
            print '[OpenIGTLinkStatus][ERROR]: Cannot get CODE'
            print inst
        finally:
            self._mutex.release()

    def getCODEBits(self):
        self._mutex.acquire()
        result = None
        try:
            result = struct.pack(self.__coding_CODE, self.__statusCode)
        except Exception as inst:
            print '[OpenIGTLinkStatus][ERROR]: Cannot get CODE'
            print inst
        finally:
            self._mutex.release()
            return result

    def setSUBCODE(self, newsubcode):
        self._mutex.acquire()
        try:
            self.__statusSubcode = copy.deepcopy(newsubcode)
        except Exception as inst:
            print '[OpenIGTLinkStatus][ERROR]: Cannot set SUBCODE'
            print inst
        finally:
            self._mutex.release()

    def getSUBCODE(self):
        self._mutex.acquire()
        try:
            return copy.deepcopy(self.__statusSubcode)
        except Exception as inst:
            print '[OpenIGTLinkStatus][ERROR]: Cannot get SUBCODE'
            print inst
        finally:
            self._mutex.release()

    def getSUBCODEBits(self):
        self._mutex.acquire()
        result = None
        try:
            result = struct.pack(self.__coding_SUBCODE, self.__statusSubcode)
        except Exception as inst:
            print '[OpenIGTLinkStatus][ERROR]: Cannot get SUBCODE'
            print inst
        finally:
            self._mutex.release()
            return result

    def setERROR_NAME(self, newerror_name):
        self._mutex.acquire()
        try:
            # Check valid ERROR_NAME: char[20]
            if len(newerror_name) > self.__maxCharLength_ERROR_NAME:
                print '[OpenIGTLinkStatus][ERROR]: ERROR_NAME too long. Max 20 char'
                raise
            else:
                self.__errorName = newerror_name
        except Exception as inst:
            print '[OpenIGTLinkStatus][ERROR]: Cannot set ERROR_NAME'
            print inst
        finally:
            self._mutex.release()

    def getERROR_NAME(self):
        self._mutex.acquire()
        try:
            return copy.deepcopy(self.__errorName)
        except Exception as inst:
            print '[OpenIGTLinkStatus][ERROR]: Cannot get ERROR_NAME'
            print inst
        finally:
            self._mutex.release()

    def getERROR_NAMEBits(self):
        self._mutex.acquire()
        result = None
        try:
            if len(self.__errorName) < self.__maxCharLength_ERROR_NAME:
                diffLength = self.__maxCharLength_ERROR_NAME - len(self.__errorName)
                result = self.__errorName + '\x00' * diffLength
            else:
                raise
        except Exception as inst:
            print '[OpenIGTLinkStatus][ERROR]: Cannot get ERROR_NAME'
            print inst
        finally:
            self._mutex.release()
            return result

    def setSTATUS_MESSAGE(self, newerror_statusmessage):
        self._mutex.acquire()
        try:
            self.__statusMessage = newerror_statusmessage
            self.__length_STATUS_MESSAGE = len(newerror_statusmessage)

            if self.__length_STATUS_MESSAGE > 0:
                self.__coding_status = '>Hq' + 'c'*20 + 'c' * self.__length_STATUS_MESSAGE
            else:
                self.__coding_status = '>Hq' + 'c'*20

        except Exception as inst:
            print '[OpenIGTLinkStatus][ERROR]: Cannot set STATUS_MESSAGE'
            print inst
        finally:
            self._mutex.release()

    def getSTATUS_MESSAGE(self):
        self._mutex.acquire()
        try:
            return copy.deepcopy(self.__statusMessage)
        except Exception as inst:
            print '[OpenIGTLinkStatus][ERROR]: Cannot get STATUS_MESSAGE'
            print inst
        finally:
            self._mutex.release()

    def getSTATUS_MESSAGEBits(self):
        self._mutex.acquire()
        result = None
        try:
            result = self.__statusMessage
        except Exception as inst:
            print '[OpenIGTLinkStatus][ERROR]: Cannot get STATUS_MESSAGE'
            print inst
        finally:
            self._mutex.release()
            return result

    def getErrorString(self):

        return self._messageCode[self.__statusCode]

    def getMessageToSend(self):

        bodymsg = self.getCODEBits() + self.getSUBCODEBits() + self.getERROR_NAMEBits() + self.getSTATUS_MESSAGEBits()

        self._mutex.acquire()
        result = None
        try:

            # Set body data for message
            self.body.setBodyMessage(bodymsg)

            # Update Message
            self.__updateMessage__(bodycoding = self.__coding_status)

            result = copy.deepcopy(self._message)
        except Exception as inst:
            print '[OpenIGTLinkStatus][ERROR]: Cannot get Message to Send'
            print inst
        finally:
            self._mutex.release()
            return result

    def unpackStatus(self, bodyDataString):
        
        # Read CODE
        result = struct.unpack(self.__coding_CODE,bodyDataString[0:2])[0]
        self.setCODE(int(result))
        bodyDataString = bodyDataString[2::]

        # Read SUBCODE
        result = struct.unpack(self.__coding_SUBCODE,bodyDataString[0:8])[0]
        self.setSUBCODE(int(result))
        bodyDataString = bodyDataString[8::]

        # Read ERROR_NAME
        typeStr = bodyDataString[0:self.__maxCharLength_ERROR_NAME].replace('\x00', '')
        self.setERROR_NAME(typeStr)
        bodyDataString = bodyDataString[self.__maxCharLength_ERROR_NAME::]

        # Read STATUS_MESSAGE
        typeStr = bodyDataString.replace('\x00', '')
        self.setSTATUS_MESSAGE(typeStr)

    def getDictRepresentation(self):

        dictRepr = {'TYPE':'STATUS',\
                    'DEVICE_NAME': self.header.getDEVICE_NAME(),\
                    'TIME_STAMP': self.header.getTIME_STAMP(),\
                    'CODE': self.getCODE(),\
                    'SUBCODE': self.getSUBCODE(),\
                    'ERROR_NAME': self.getERROR_NAME(),\
                    'STATUS_MESSAGE': self.getSTATUS_MESSAGE(),\
                    }

        return dictRepr

class OpenIGTLinkConnection:

    # Private Data Member
    __mutexState = None
    __state = None
    __messageList = None
    __readingthread = None
    __mutexStopSignal = None
    __threadStopSignal = True
    __numberOfCalls = 0
    __messageListDf = None
    __connectingthread = None
    __mutexConnections = None
    __connectedSockets = None

    def __init__(self, connectionType = 'server', host = 'localhost', portnumber = 18944, maximumConnections = 10):

        self.hostname = host
        self.portnumber = portnumber
        self.__state = "Disconnected"
        self.__mutexStopSignal = threading.Semaphore()
        self.__mutexState = threading.Semaphore()
        self.__mutexConnections = threading.Semaphore()
        self.__connectedSockets = list()
        self.maxConnection = maximumConnections
        self.connectionType = connectionType

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
            print "Already Connected"
            return

        previousState = self.getState()

        if previousState == "Disconnected":
            self.setState("AttemptingToConnect")
            print "Trying to connect"
            try:
                #create an AF_INET, STREAM socket (TCP)
                self.socketConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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

            try:

                if self.connectionType == 'server':
                    self.socketConnection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    self.socketConnection.bind((self.remote_ip , self.portnumber))
                    self.socketConnection.listen(self.maxConnection)
                

                # Launch Thread for reading
                self.setStopSignal(False)
                self.__connectingthread = threading.Thread(target=self.connectThread, args=())
                self.__connectingthread.daemon = True   # Daemonize thread
                self.__connectingthread.start()

                if self.connectionType == 'server':
                    self.setState("Connected")
                elif self.connectionType == 'client':
                    for i in range(30):
                        helpers.PrintPercentage(100.0*(i+1.0)/(30), 'Waiting for server...')
                        time.sleep(1)
                        if self.getState() == 'Connected':
                            return

            except KeyboardInterrupt:
                self.setState(previousState)

    def disconnect(self):

        if self.getState() == "Disconnected":
            print "Already disconnected"
            return

        previousState = self.getState()
        if self.getState() == "Connected":
            self.setState("AttemptingToDisconnect")

            if isinstance(self.socketConnection, socket.socket):
                self.socketConnection.close()
                print 'Connection closed'
                self.setState("Disconnected")
                return
            else:
                print "[Error] Disconnection Failed!"
                self.setState(previousState)
                return

    def sendMessage(self, message):

        if self.getState() == "SendingUnique":
            return

        previousState = self.getState()

        if previousState == "Connected":
            self.setState("AttemptingToSendUnique")
            print "Trying to connect"
            try:
                # Send Message
                self.socketobject.send(message)
            except socket.error, msg:
                print "[Error]: Cannot Send from state: " + previousState
                self.setState(previousState)
                print 'Failed to send Message. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1]
                self.setState(previousState)
                return
            print "Sent message"
            self.setState("Connected")
            return

    def startSending(self, timeOut = 60, rate = 0.25):
        previousState = self.getState()

        try:

            if previousState == "Connected":
                self.setState("Sending")
                self.setStopSignal(False)
                self.rate = rate
                # Launch Thread for reading
                self.__readingthread = threading.Thread(target=self.sendingThread, args=())
                self.__readingthread.daemon = True   # Daemonize thread
                self.__readingthread.start()

                for i in range(timeOut*4):
                    helpers.PrintPercentage(100.0*(i+1.0)/(timeOut*4), 'Sending time to finish: Press Ctrl + C for end server ')
                    time.sleep(0.25)
                self.setStopSignal(True)
                self.setState("Connected")

        except KeyboardInterrupt:
            self.setState("Connected")
            self.setStopSignal(True)
            self.disconnect()

    def stopThreads(self):

        self.setStopSignal(True)

    def sendingThread(self):
        self.__numberOfCalls = self.__numberOfCalls + 1
        print "Thread Called: ", self.__numberOfCalls, " times"

        # Read a complete message
        previousState = self.getState()
        while self.getState() == "Sending" and self.getStopSignal() == False:
            self.setState("AttemptingToSendNewData")
            # Send messages
            N = len(self.__messageList)
            for i in range(N):
                time.sleep(self.rate)

                self.__mutexConnections.acquire()

                for s in self.__connectedSockets:
                    try:
                        s.send(self.__messageList[i])
                    except:
                        s.close()
                        self.__connectedSockets.remove(s)
                        print '* One link removed'

                self.__mutexConnections.release()

            self.setState("Sending")

        self.setState("Connected")

    def startListening(self, timeOut = 60):
        previousState = self.getState()


        try:
            if previousState == "Connected":
                self.setState("Listening")
                self.__messageListDf = list()
                self.setStopSignal(False)
                # Launch Thread for reading
                self.__readingthread = threading.Thread(target=self.readingThread, args=())
                self.__readingthread.daemon = True   # Daemonize thread
                self.__readingthread.start()

                for i in range(timeOut*4):
                    helpers.PrintPercentage(100.0*(i+1.0)/(timeOut*4), 'Listening time to finish: Press Ctrl + C for end client ')
                    time.sleep(0.25)
                self.setStopSignal(True)
                self.setState("Connected")

        except KeyboardInterrupt:
            self.setState("Connected")
            self.setStopSignal(True)
            self.disconnect()

    def readMessage(self):
        # Create header
        header = OpenIGTLinkHeader()

        # Receive data from socket
        socketHeader = self.socketConnection.recv(header.IGTLinkHeaderSize)

        # Unpack header
        header.unpack(socketHeader)

        # Read Body Size
        bodySize = header.getBODY_SIZE()
        socketBody = self.socketConnection.recv(bodySize)


        try:
            # Check Type of message
            if header.getTYPE() == 'STATUS':
                status = OpenIGTLinkStatus()
                status.header.unpack(socketHeader)
                status.unpackStatus(socketBody)
                self.__messageListDf.append(status.getDictRepresentation())
                #print "[Status]"
            elif header.getTYPE() == 'TRANSFORM':
                transform = OpenIGTLinkTransform()
                transform.header.unpack(socketHeader)
                transform.unpackTransform(socketBody)
                self.__messageListDf.append(transform.getDictRepresentation())
                #print "[Transform]"


            else:
                print "Message Type is not recognised: " + header.getTYPE()
        except Exception as inst:
            print inst

    def readingThread(self):
        self.__numberOfCalls = self.__numberOfCalls + 1
        print "Thread Called: ", self.__numberOfCalls, " times"

        # Read a complete message
        previousState = self.getState()
        while self.getState() == "Listening" and self.getStopSignal() == False:
            self.setState("AttemptingToRecieveNewData")
            # Read header
            try:
                self.readMessage()

            except:
                pass
                #print "waiting..."
                #self.stopThreads()

            self.setState("Listening")


        self.setState("Connected")

    def connectThread(self):

        previousState = self.getState()

        connected = False
        counter = 0

        previousState = self.getState()

        try:

            if self.connectionType == 'server':
                print 'Connecting as a server. Waiting for connections...'

                while self.getStopSignal() == False:
                    socketobject, addr = self.socketConnection.accept()

                    self.__mutexConnections.acquire()
                    try:
                        self.__connectedSockets.append(socketobject)
                        print "Adding new connection at", addr[1]
                    finally:
                        self.__mutexConnections.release()
                

            elif self.connectionType == 'client':
                print 'Connecting as a client. Waiting for connect...'
                
                connected = False
                counter = 0
                while connected == False:
                    counter = counter + 1
                    try:

                        self.socketConnection.settimeout(1)
                        self.socketConnection.connect((self.remote_ip , self.portnumber))
                        connected = True


                    except Exception, e:
                        print "Trying to connect to server. {0:d} attempst left".format(10 - counter)
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
                
                
                
        except Exception, e:
            print('[Error]:Connection to socket was wrong %s:%d. ' % (self.remote_ip, self.portnumber))
            print('        Exception type is %s' % e)
            connected = False
            if counter == 10:
                self.setState("Disconnected")
                print "[Error]: Cannot Connect socket"

    def loadFileMessages(self, filepath):

        if self.getState() == "ReadingMessageFile":
            return

        previousState = self.getState()

        if previousState == "Disconnected":
            self.setState("AttemptingToReadMessageFile")
            print "Trying to Read Message File"


            try:
                self.__messageList = list()
                df = pandas.read_csv(filepath)
                df
                for i in range(len(df.index)):
                    message = df.loc[i]
                    
                    m = None
                    if message['TYPE'] == 'TRANSFORM':
                        
                        npTransform = numpy.eye(4)
                        for ii in range(3):
                            for jj in range(4):
                                npTransform[ii,jj] = float(message['T' + str(ii) + str(jj)])
                        
                        
                        t = OpenIGTLinkTransform()
                        m = t.setOpenIGTLinkTransform(npTransform = npTransform,\
                            floatTimeStamp = float(message['TIME_STAMP']),\
                            transformName = message['DEVICE_NAME'])
                        self.__messageList.append(m)
                    
                    elif message['TYPE'] == 'STATUS':
                        s = OpenIGTLinkStatus()
                        m = s.setOpenIGTLinkStatus(statusCode = int(message['CODE']),\
                                                         statusSubCode = int(message['SUBCODE']),\
                                                         errorName = message['ERROR_NAME'],\
                                                         statusMessage = message['STATUS_MESSAGE'],\
                                                         deviceName = message['DEVICE_NAME'],\
                                                         floatTimeStamp = float(message['TIME_STAMP']))
                        self.__messageList.append(m)
                    else:
                        print "Problem readind row: ", i
            except Exception as inst:
                print "[Error]: Cannot Load File"
                print inst

            self.setState(previousState)
            print "File Readed. Number of read messages:", len(self.__messageList)


        else:
            print "[Error]: Cannot Load File from state: " + previousState
            self.setState(previousState)
            return
            
    def writeFileMessages(self, filepath):

        if self.getState() == "WritingMessageFile":
            return

        previousState = self.getState()

        if previousState == "Disconnected":
            self.setState("AttemptingToWriteMessageFile")
            print "Trying to Write Message File"


            try:
                df = pandas.DataFrame(self.__messageListDf)
                df.to_csv(filepath, index = False, na_rep = 'NaN')

            except Exception as inst:
                print "[Error]: Cannot Write File"
                print inst

            self.setState(previousState)
            print "File Written. Number of messages:", len(self.__messageListDf)


        else:
            print "[Error]: Cannot Write File from state: " + previousState
            self.setState(previousState)
            return



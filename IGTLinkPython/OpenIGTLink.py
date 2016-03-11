#!/usr/bin/env python
__author__ = 'Eugenio Marinetto'
__version__ = '1'
__date__ = 'March 11 2016'


import threading
import copy

class OpenIGTLinkHeader:

    # Private data members
    __mutex = None
    __coding_V = '>H' # V is unsigned short big endian
    __maxCharLength_TYPE = 12
    __maxCharLength_DEVICE_NAME = 20

    #Bytes
    #0   2                       14                                      34             42               50              58
    #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #| V |          TYPE         |              DEVICE_NAME              |   TIME_STAMP  |   BODY_SIZE   |     CRC64     |
    #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

    def __init__(self, version = 1):

        # Create mutex for changes
        self.__mutex =threading.Semaphore()

        # V: Header version number
        # The version number field specifies the header format version. 
        # Currently the version number is 1. 
        # Please note that this is different from the protocol version.
        self.V = version

        # TYPE:  name of data
        self.TYPE = None

        # DEVICE_NAME: Unique device name
        sefl.DEVICE_NAME = None

        # TIME_STAMP: Timestamp or 0 if unused
        sefl.TIME_STAMP = None

        # BODY_SIZE: Size of body in bytes
        sefl.BODY_SIZE = None

        # CRC: 64 bit CRC for body data
        # CRC The 64-bit CRC used in OpenIGTLink protocol is based on ECMA-182 standard.
        sefl.CRC = None

    def setV(self, newversion):
        self.__mutex.acquire()
        try:
            self.V = copy.deepcopy(newversion)
        except:
            print '[OpenIGTLinkHeader][ERROR]: Cannot set Version'
        finally:
            self.__mutex.release()

    def getV(self):
        self.__mutex.acquire()
        try:
            return copy.deepcopy(self.V)
        except:
            print '[OpenIGTLinkHeader][ERROR]: Cannot get Version'
        finally:
            self.__mutex.release()

    def getVBits(self):
        self.__mutex.acquire()
        try:
            result = struct.pack(self.__coding_V, self.V)
        except:
            print '[OpenIGTLinkHeader][ERROR]: Cannot get Version'
        finally:
            self.__mutex.release()

        return result

    def setTYPE(self, newtype):
        self.__mutex.acquire()
        try:

            # Check valid TYPE: char[12]
            if   newtype == 'TRANSFORM':
                self.TYPE_GROUP = 0
            elif newtype == 'QTRANS':
                self.TYPE_GROUP = 0
            elif newtype == 'POSITION':
                self.TYPE_GROUP = 0
            elif newtype == 'IMAGE':
                self.TYPE_GROUP = 0
            elif newtype == 'STATUS':
                self.TYPE_GROUP = 0
            elif newtype == 'CAPABILITY':
                self.TYPE_GROUP = 0
            elif newtype == 'IMGBETA':
                self.TYPE_GROUP = 2
            elif newtype == 'LBMETA':
                self.TYPE_GROUP = 2
            elif newtype == 'COLORT':
                self.TYPE_GROUP = 2
            elif newtype == 'POINT':
                self.TYPE_GROUP = 2
            elif newtype == 'TRAJ':
                self.TYPE_GROUP = 2
            elif newtype == 'TDATA':
                self.TYPE_GROUP = 2
            elif newtype == 'QTDATA':
                self.TYPE_GROUP = 2
            elif newtype == 'SENSOR':
                self.TYPE_GROUP = 3
            elif newtype == 'STRING':
                self.TYPE_GROUP = 3
            elif newtype == 'NDARRAY':
                self.TYPE_GROUP = 3
            elif newtype == 'BIND':
                self.TYPE_GROUP = 3
            elif newtype == 'POLYDATA':
                self.TYPE_GROUP = 3
            else:
                raise

            self.TYPE = newtype
        except:
            print '[OpenIGTLinkHeader][ERROR]: Cannot set TYPE'
        finally:
            self.__mutex.release()

    def getTYPE(self):
        self.__mutex.acquire()
        try:
            return copy.deepcopy(self.TYPE)
        except:
            print '[OpenIGTLinkHeader][ERROR]: Cannot get TYPE'
        finally:
            self.__mutex.release()

    def getTYPEBits(self):
        self.__mutex.acquire()
        try:
            if len(self.TYPE) < __maxCharLength_TYPE:
                diffLength = __maxCharLength_TYPE - len(self.TYPE)
                result = self.TYPE + ' ' * diffLength
            else:
                raise
        except:
            print '[OpenIGTLinkHeader][ERROR]: Cannot get TYPE'
        finally:
            self.__mutex.release()

        return result

    def setDEVICE_NAME(self, newdevice_name):
        self.__mutex.acquire()
        try:
            # Check valid DEVICE_NAME: char[20]
            if len(newdevice_name) > 20:
                print '[OpenIGTLinkHeader][ERROR]: DEVICE_NAME too long. Max 20 char'
                raise
            else:
                self.DEVICE_NAME = newdevice_name
        except:
            print '[OpenIGTLinkHeader][ERROR]: Cannot set DEVICE_NAME'
        finally:
            self.__mutex.release()

    def getDEVICE_NAME(self):
        self.__mutex.acquire()
        try:
            return copy.deepcopy(self.DEVICE_NAME)
        except:
            print '[OpenIGTLinkHeader][ERROR]: Cannot get DEVICE_NAME'
        finally:
            self.__mutex.release()

    def getDEVICE_NAMEBits(self):
        self.__mutex.acquire()
        try:
            if len(self.DEVICE_NAME) < __maxCharLength_TYPE:
                diffLength = __maxCharLength_DEVICE_NAME - len(self.DEVICE_NAME)
                result = self.DEVICE_NAME + ' ' * diffLength
            else:
                raise
        except:
            print '[OpenIGTLinkHeader][ERROR]: Cannot get DEVICE_NAME'
        finally:
            self.__mutex.release()

        return result

    def setTIME_STAMP(self, newtimestamp):
        self.__mutex.acquire()
        try:
            self.TIME_STAMP = copy.deepcopy(newtimestamp)
        except:
            print '[OpenIGTLinkHeader][ERROR]: Cannot set TIME_STAMP'
        finally:
            self.__mutex.release()

    def getTIME_STAMP(self):
        self.__mutex.acquire()
        try:
            return copy.deepcopy(self.TIME_STAMP)
        except:
            print '[OpenIGTLinkHeader][ERROR]: Cannot get TIME_STAMP'
        finally:
            self.__mutex.release()

    def getTIME_STAMPBits(self):
        self.__mutex.acquire()
        try:
            seconds = int(self.TIME_STAMP)
            fraction = self.TIME_STAMP - seconds

        fracbin = '0b'
        rest = 1.0
        n = -1
        rest = fraction
        while rest != 0.0:
            if (rest / 2 ** (n)) >= 1.0:
                fracbin = fracbin + '1'
                rest = rest - 2 ** (n)
                print n, 2 ** (n) , rest
            else:
                fracbin = fracbin + '0'
                print n, '0', rest
            n = n - 1


        except:
            print '[OpenIGTLinkHeader][ERROR]: Cannot get TIME_STAMP'
        finally:
            self.__mutex.release()

        return result
        



def socketReadV(self):
        coding = '>H' # V is unsigned short big endian
        numberOfBytes = struct.calcsize(coding)
        socketResult = self.socketobject.recv(numberOfBytes)
        result = struct.unpack(coding,socketResult)
        #print 'Version: ', int(result[0])
        return int(result[0])
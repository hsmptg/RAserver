import Queue
from threading import Thread
import socket
#import serial.tools.list_ports  # @UnresolvedImport
import serial

def _listMsgs(q):    
    try:
        while True:
            yield q.get_nowait()
    except Queue.Empty:
        raise StopIteration
    
class myNet(object):
    def __init__(self, parent=None):
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.fifo = Queue.Queue()    
        self.onMsg = None   
    
    def connect(self, ip, port):
        try:
            self.soc.connect((ip, port))
            self._exit = False
            self.th = Thread(target=self._th_read)
            self.th.daemon = True
            self.th.start()
            return True            
        except Exception,e:
            print str(e)
            return False
  
    def disconnect(self):
        self._exit = True
        self.th.join()
        self.soc.close()
            
    def sendMsg(self, msg):
        try:
            #self.soc.send(msg + '\r\n')
            self.soc.sendall(msg + "\r\n")
        except AttributeError:
            print("Not connected yet!")
        except socket.error:
            print("Lost connection!")        

    def readMsg(self):
        return list(_listMsgs(self.fifo))
    
    def _th_read(self):
        self.soc.settimeout(1)
        buf = ""
        while not self._exit:
            try:
                s = self.soc.recv(1024)
                if s == "":
                    print("Disconnected")
                    break # if conn lost get out!
                buf = buf + s
                while "\r\n" in buf:
                    (cmd, buf) = buf.split("\r\n", 1)
                    if cmd <> "":
                        self.fifo.put(cmd)
                        if self.onMsg:
                            self.onMsg(cmd)
            except socket.timeout:
                continue
            except socket.error:
                print("Lost connection!")
                break            

    def stop(self):
        if not self._exit:
            self.disconnect()        
            
# http://pyserial.sourceforge.net/pyserial_api.html
class mySerial(object):
    def __init__(self, parent=None):
        self.ser = serial.Serial()
        self.fifo = Queue.Queue()     
        self.onMsg = None
#        self.onLog = None
    
    def connect(self, port):
#        if self.onLog:
#            self.onLog("Connect to port " + port)
        try:
            self.ser.port = port
            self.ser.baudrate = 115200
            self.ser.timeout = 1
            self.ser.open()
            self._exit = False
            self.th = Thread(target=self._th_read)
            self.th.daemon = True
            self.th.start()
            return True            
        except serial.SerialException as e:
            print(e)
            return False        
                
    def disconnect(self):
#        if self.onLog:
#            self.onLog("Disconnect")
        self._exit = True
        self.th.join()
        self.ser.close()
            
    def sendMsg(self, msg):
#        if self.onLog:
#            self.onLog("Send message: " + msg)
        try:
            self.ser.write(msg + "\r")
        except serial.SerialException as e:
            print(e)
    
    def readMsg(self):
        return list(_listMsgs(self.fifo))
    
    def getPorts(self):
        return list(serial.tools.list_ports.comports())
 
    def _th_read(self):
        while not self._exit:
            try:
                # depois mudar o eol para '\n'
                # http://stackoverflow.com/questions/16470903/pyserial-2-6-specify-end-of-line-in-readline
                cmd = self.ser.readline().rstrip('\n')
                if cmd <> "":
                    self.fifo.put(cmd)
                    if self.onMsg:
                        self.onMsg(cmd)
            except serial.SerialException as e:
                print(e)
    
    def stop(self):
        if not self._exit:
            self.disconnect()

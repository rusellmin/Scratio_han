# coding=utf-8

import socket
import threading
import time
import logging
from arduino import *

class server():

    def __init__(self,port):
        host = socket.gethostbyname('localhost')
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(1)
        self.sock.bind((host, self.port))
        self.sock.listen(1)
        self.ser = arduino()
        self.sockflg = 0

        #print 'waiting for connection...'

    def call_arduino(self,port):
        self.ser = arduino()
        if self.ser.open(port,115200):
            self.ser.main()

    def sendResponse(self,s):
        crlf = '\r\n'
        msg = 'HTTP/1.1 200 OK' + crlf
        msg += 'Content-Type: text/html; charset=ISO-8859-1' + crlf
        msg += 'Access-Control-Allow-Origin: *' + crlf
        msg += crlf
        msg += s + crlf
        self.client_sock.send(msg.encode())

    def htmlRequest(self,header):
        if  header.find('GET ') == -1:
            #print 'Este servidor solo acepta conexiones HTTP GET'
            return
        i = header.find('HTTP/1')

        if i < 0:
            #print 'Cabezera HTTP GET incorracta.'
            return

        header = header[5:i-1]

        if header == 'favicon.ico':
            return # igore browser favicon.ico requests
        elif header == 'crossdomain.xml':
            #self.sendPolicyFile();
            print("policy")
        elif len(header) == 0:
            self.doHelp();
        else:
            self.doCommand(header)

    def getState(self,state):
        if int(state) != 1:
            return "true"
        else:
            return "false"

    def getCapState(self,state):
        if int(state) == 1:
            return "true"
        else:
            return "false"

    def checkOpenflg(self):
      return self.ser.checkOpenflg()

    def doCommand(self,header):
        if self.checkOpenflg() == 0:
            return
        if header == 'poll':
            dp_in = self.ser.getDigitalState()
            ap = self.ser.getAnalogState()
            cap_in = self.ser.getCapState()
            msg = ""
            for num in range(len(ap)):
                if  ap[num] != -1:
                    if num == 4:
                        msg += 'analogRead/A' + str(num) + ' ' + str(ap[num]) + chr(10)
                        msg += 'brightness ' + str(ap[num]) + chr(10)
                    elif num == 5:
                        msg += 'analogRead/A' + str(num) + ' ' + str(ap[num]) + chr(10)
                        msg += 'sound ' + str(ap[num]) + chr(10)
                    elif num == 6:
                        msg += 'slider ' + str(ap[num]) + chr(10)
                    else:
                        msg += 'analogRead/A' + str(num) + ' ' + str(ap[num]) + chr(10)
            for num in range(len(dp_in)):  #D2,D3,D4
                if dp_in[num] != -1:
                    if num == 0:
                        msg += 'button ' + self.getState(dp_in[num]) + chr(10)
                    msg += 'digitalRead/D' + str(num+2) + ' '+ self.getState(dp_in[num]) + chr(10)
            for num in range(len(cap_in)):
                if cap_in[num] != -1:
                    msg += 'capRead/C' + str(num) + ' ' + self.getCapState(cap_in[num]) + chr(10)
            if len(msg) > 0:
                #print msg
                self.sendResponse(msg)
        elif header == 'reset_all':
                #moControl.getArduino().resetAll();
                #print "reset_all"
                self.sendResponse("ok")
        else:
            las = header.split("/")
            if las[0] == 'digitalWriteOn':
                pin = las[1][1:]
                self.ser.sendCommand("D",pin,1)
            elif las[0] == 'digitalWriteOff':
                pin = las[1][1:]
                self.ser.sendCommand("D",pin,0)
            elif las[0] == 'analogWrite':
                pin = las[1][1:]
                self.ser.sendCommand("A",pin,int(las[2]))
            elif las[0] == 'tone':
                val = int(las[1])
                if val < 0:
                    val = 0
                self.ser.sendCommand("T","9",val)
            elif las[0] == 'servoangle':
                pin = las[1][1:]
                angle = int(las[2])
                if angle > 180:
                    angle = 180
                elif angle < 0:
                    angle = 0
                self.ser.sendCommand("SA",pin,angle)
            elif las[0] == 'servodetach':
                pin = las[1][1:]
                self.ser.sendCommand("SD",pin,0)
            elif las[0] == 'ledon':
                self.ser.sendCommand("D",13,1)
            elif las[0] == 'ledoff':
                self.ser.sendCommand("D",13,0)
            else:
                #print "else"
                self.sendResponse("ok")

    def doHelp(self):
        # Optional: return a list of commands understood by this server
        help = "Server HTTP Extension BlocklyDuino<br><br>";
        self.sendResponse(help)

    def main(self):
        #print "Server started"
        self.stop_event = threading.Event() #スレッドを停止させるフラグ
        #スレッドの作成と開始
        self.thread = threading.Thread(target=self.readSocket)
        self.thread.setDaemon(True)
        self.thread.start()

    def readSocket(self):
        #while True:
        while not self.stop_event.is_set():
            try:
                (self.client_sock, self.client_addr) = self.sock.accept()
                self.client_sock.settimeout(None)
            except socket.timeout:
                continue
            msg = ''
            while msg.find('\n') == -1:
                msg = self.client_sock.recv(1024).decode("utf-8")
                if len(msg) > 0:
                    msg += msg;
            #logging.info("request msg:{}".format(msg))
            self.htmlRequest(msg)
            self.client_sock.close()
            #time.sleep(0.1)

    def close(self):
        #print "server close()"
        self.ser.close()
        self.stop_event.set()   #スレッドの停止
        self.thread.join()   #スレッドが停止するのを待つ
        self.sock.close()

if __name__ == "__main__":
    server = server(8099)
    server.main()
#    server.call_arduino("COM26")
    server.call_arduino("/dev/cu.usbmodem411")
#    server.call_arduino("/dev/cu.usbserial-A901OFEZ")

    while True:
        try:
            time.sleep(0.1)
        except (KeyboardInterrupt, SystemExit):
             break
        except:
            #print "error"
            break

    #ser.close()
    server.close()

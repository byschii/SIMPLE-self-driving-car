import io
import socket
import struct
import time
import picamera
import threading
import SocketServer
import serial#per la comunicazione tramite usb
from PIL import Image #libreria per a gestione di img

class ArduinoControllHandler(SocketServer.StreamRequestHandler):
    def handle(self):
        print "server controllo arduino iniziato"
        stream_bytes = ''
        usb =0
        try:
            while True:
                #ricevo i dati dal pc
                time.sleep(0.06)
                stream_bytes = self.rfile.read(9)#leggo la correzione che è stata inviata, prendendo 9 bytes
                correzione =int(stream_bytes.split(',')[1])#prendo un dato che sia integlo
                posizione = int((correzione/2)+101)#formatto per adattre ad arduino
                print (correzione,posizione)#stampo per debug
                usb = serial.Serial("/dev/ttyACM0", baudrate=9600) #preparo l oggetto per la comunicazione usb
                try:
                    usb.write(struct.pack('>B', posizione))#provo ad inviare
                except:
                    "non ho raggiunto arduino"#se non riesco, lo scrivo
        except:
            print "errore"

def controlla(host,port):
    server = SocketServer.TCPServer((host,port), ArduinoControllHandler)
    server.serve_forever()

def scatta(ip,port):
    print "soket di invio foto iniziata"
    client_socket = socket.socket()#preparo la sock
    client_socket.connect((ip, port))
    connection = client_socket.makefile('wb') # e l oggetto file
    try:
        with picamera.PiCamera() as cam:#creo l oggetto per scattare le foto
            cam.resolution = (640, 480)#preparo le impostazioni
            cam.vflip = True
            cam.hflip = True
            cam.brightness = 60
            
            cam.start_preview()
            time.sleep(3)#tempo di pausa per 'scaldare' la fotocamera

            start = time.time() #prendo il tempo, la macchina funziona a tempo
            stream = io.BytesIO()#preparo l oggetto su cui 'scrivere' le foto

            for foo in cam.capture_continuous(stream, 'jpeg', use_video_port=True): #incomincio a scattare foto in continuazione
                connection.write(struct.pack('<L', stream.tell()))#controllo la dim dell immagine
                connection.flush()

                stream.seek(0)#azzero il 'cursore' del file
                connection.write(stream.read())#e scrivo l immagine nella sock
                
                if time.time() - start > 60: #se e' passato un minuto 
                    break#interrompo tutto

                # Reset dello stream per il prossimo scatto
                stream.seek(0)
                stream.truncate()
        #comunico l' interruzione dello stream
        connection.write(struct.pack('<L', 0))
    finally:
        connection.close()
        client_socket.close()

#preparo i due thread
thread_scatto = threading.Thread(
    target = scatta, args=('192.168.1.5', 8020)) #connessione al pc
thread_controllo = threading.Thread(
    target =controlla, args=('192.168.1.91', 8021))#connessione qui

#li faccio partire
thread_scatto.start()
time.sleep(3)
thread_controllo.start()


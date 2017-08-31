#serie di dipendenze
import threading#per dividere in thread
import SocketServer#per fare da server(primo thread)
import cv2#computer vision
import numpy as np#gestione di grandi array/matrici 
import math#per funzioni matematiche, tipo radice
import socket#per fare da client(secondo thread)
import time#per operazioni col tempo
from lane_detect_class import Direzionatore#classe che trova le linee

#variabile globale dove viene memorizzata la foto dal server
#e trovate le linee dal secondo
image = np.array([])

#funzione per disegnare linee nelle immagini
def draw_linesP(img,lines, color = [20, 244, 66], size = 2 ):
	for x1,y1,x2,y2 in lines:
		cv2.line(img, (x1,y1), (x2,y2), color, size)
	return img

#override della classe StreamRequestHandler per adattarla allo scopo di riceve foto
class VideoStreamHandler(SocketServer.StreamRequestHandler):
    def handle(self):
        stream_bytes = ' '
        print "server di acuisizione video iniziato"
        try:
            while True:
                stream_bytes += self.rfile.read(1024) #leggo dalla socket
                first = stream_bytes.find('\xff\xd8')#creco inizio e fine della foto
                last = stream_bytes.find('\xff\xd9')
                
                if first != -1 and last != -1:#se li trovo
                    jpg = stream_bytes[first:last+2]#isolo l immagine
                    stream_bytes = stream_bytes[last+2:]#e rimetto i bytes in piu nella variabile
                    global image
                    image = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.CV_LOAD_IMAGE_UNCHANGED)#converto i byte in un array, che varà visto come immagine
                    cv2.imshow('image', image) #mosto l immagine catturata
                    cv2.waitKey(1)#per un millisecondo
        finally:
            cv2.destroyAllWindows()#a fine trasmissione chiudo fa finestra


def server_thread(host, port):
        server = SocketServer.TCPServer((host, port), VideoStreamHandler)#istanzio l oggetto della server
        server.serve_forever()#lo faccio partire

def risposta(ip, port):#funzione per il client che risponde
    print "socket di risposta con le info iniziato"
    client_socket = socket.socket()#creo la sock
    client_socket.connect((ip, port))#mi connetto
    connection = client_socket.makefile('wb')#creo un oggetto file-like per meglio gestire la sock 
    global image
    try:
        while True:#ciclo di 'comunicazione' con il pi
            risp=0#valore della correzione
            try:
                sterzo = Direzionatore(image,0.25,7.5,70,50,5)#creo l oggtto che trova le linee
                cv2.imshow("server",draw_linesP(sterzo.IMG,sterzo.lanes, size =3))#mostro "quello che vede" il computer
                cv2.waitKey(1)
                risp,_ = sterzo.correzione()#prendo i dati sulla correzione
            except Exception as e:
                print e
                
            connection.write(str(risp)+",")#li invio separati da virgole al pi
            connection.flush()
    finally:
        connection.close()
        client_socket.close()       


#preparo i thread con funzione e ip di riferimento  
thread_acquisizione = threading.Thread(
    target=server_thread, args=('192.168.1.5', 8020))#connessione a me
thread_risposta = threading.Thread(
    target = risposta, args=('192.168.1.91', 8021)) #connessione al raspberry
#avvo di due thread
thread_acquisizione.start()
time.sleep(6)
thread_risposta.start()



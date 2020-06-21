# -*- coding: utf-8 -*-
"""
Created on Sat Apr 14 21:39:54 2018

@author: alonso
"""
from CreadorMIDI import *
import cv2
import matplotlib.pyplot as plt
import numpy as np
import math
import time
import pickle
import threading
import pyaudio
import os

class musica():
    
    def __init__(self):
        self.mano_uno = ''
        self.lista_abierta = []  
        self.lista_cerrada = []
        self.abierta = ''
        self.cerrada = ''
        self.array_supremo = ['', '']
        self.canciones = []
        self.name = "partituramusical.ly"
        
    def grabar(self):
        cap = cv2.VideoCapture(0)
        while True:
            lista = []
            c = 0
            ret, img = cap.read()
            binarizar = self.procesado(img)
            cv2.rectangle(img,(50,215),(100,265),(255,0,0),3)
            cv2.rectangle(img,(295,50),(345,100),(255,0,0),3)
            cv2.rectangle(img,(540,215),(590,265),(255,0,0),3)
            cv2.rectangle(img,(295,380),(345,430),(255,0,0),3)
            imgCrop1 = self.cuadrado(binarizar,50,215,100,265)
            imgCrop2 = self.cuadrado(binarizar,295,50,345,100)            
            imgCrop3 = self.cuadrado(binarizar,540,215,590,265)
            imgCrop4 = self.cuadrado(binarizar,295,380,345,430)
            
            lista = [imgCrop1,imgCrop2,imgCrop3,imgCrop4]
            c = max(lista)
            if imgCrop1 == c:
                nota = "do"
            elif imgCrop2 == c:
                nota = "la#"
            elif imgCrop3 == c:
                nota = "re"
            elif imgCrop4 == c:
                nota = "fa#"
            #self.mano_uno = self.contornos(binarizar)
            #cv2.imshow("Imagen", img)
            cv2.imshow("Binarizar", binarizar)
#            self.escribir_aarchivo("cancion",nota)
            self.nota_musical(nota)
            self.canciones.append(nota)
            if cv2.waitKey(1) == 13:
#                self.hilo(self.mano_uno, self.lista_abierta)
#                self.hilo(self.mano_uno, self.lista_cerrada)
                cap.release()
                cv2.destroyAllWindows()
                self.escribir_aarchivo(self.name, self.canciones)
                break            
            
    def procesado(self, img):
        
        gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        suavizar = cv2.GaussianBlur(gris, (3,3), 0)
        kernel = np.ones((5, 5), np.float32) / 25
        dst = cv2.filter2D(suavizar, -1, kernel)
        ret, binarizar = cv2.threshold(dst, 100, 255, cv2.THRESH_BINARY_INV)
        
        return binarizar
        
    def cuadrado(self,img,x,y,w,h):
        
        d = 10
        imgCrop = None
        if np.any(imgCrop == None):
            imgCrop = img[y:y+h, x:x+w]
        else:
            imgCrop = np.vstack((imgCrop, img[y:y+h, x:x+w]))
            cv2.rectangle(img, (x,y), (x+w, y+h), (0,255,0), 2)
        x=x+w+d
        y=y+h+d
        x = 0
        dimx = imgCrop.shape[0]
        dimy = imgCrop.shape[1]
        for i in xrange(dimx):
            for j in xrange(dimy):
                x = x + imgCrop[i][j]
        return x
        
    def contornos(self, img):
        
        #canny_img = cv2.Canny(img,50,150)
        contornos, xxx = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        for c in contornos:
            accuracy = 0.01 * cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, accuracy, True)
            cv2.drawContours(img, [approx], 0, (0, 255, 0), 2)
        n = len(contornos) - 1
        sorted(contornos, key=cv2.contourArea, reverse=True)[:n]
        return contornos
        
#    def importar_manos(self):
#        lista_abierta = []
#        lista_cerrada = []
#        
#        for h in range(11):
#            nombre = "mano_abierta"+str(h)+".txt"
#            lista_abierta.append(nombre)
#            
#        for h in range(11):
#            nombre = "mano_cerrada"+str(h)+".txt"
#            lista_cerrada.append(nombre)
#            
#        for l in lista_abierta:
#            f = open(l,"r")
#            u = pickle.Unpickler(f)
#            x = u.load()
#            self.lista_abierta.append(x)
#            
#        for j in lista_cerrada:
#            f = open(j,"r")
#            u = pickle.Unpickler(f)
#            x = u.load()
#            self.lista_cerrada.append(x)            
   
#    def comparar(self, img, lista):
#
#        
#    def supremo(self):
#        try:
#            for c in self.array_supremo: print c
#            d = max(self.array_supremo)
#            h = self.array_supremo.index(d)
#            if self.array_supremo[0] == self.array_supremo[1]:
#                print "No match"
#            elif h == 0:
#                print "Mano abierta"
#            elif h == 1:
#                print "Mano cerrada"
#        except:
#            pass

#    def hilo(self, img, lista):
#        th = threading.Thread(target = self.comparar, args = (img, lista))
#        th.daemon = True
#        th.start()

    def escribir_aarchivo(self, name, notas):
 
        song = Midi(2)
        for elem in self.canciones:
            song.agregar_nota(elem,4,'p',Midi.NEGRA,True,1)
        with open("ghffhcj.mid", "wb") as file:
            song.save(file)     
            
        char2notes = {
            'do':("c'"),
            'do#':("cis'"),
            're':("d'"),
            're#':("dis'"),
            'mi':("e'"),
            'fa':("f'"),
            'fa#':("fis'"),
            'sol':("g'"),
            'sol#':("gis'"),
            'la':("a'"),
            'la#':("ais'"),
            'si':("b'"),
            'doAlto':("c''"),
            'do#Alto':("cis''"),
            'reAlto':("d''"),
            're#Alto':("dis''"),
            'miAlto':("e''"),
            'faAlto':("f''"),
            'fa#Alto':("fis''"),
            'solAlto':("g''"),
            'sol#Alto':("gis''"),
            'laAlto':("a''"),
            'la#Alto':("ais''"),
            'siAlto':("b''")
        }
        partitura = "\relative c {\n"
        for i in notas:
            partitura += char2notes[i] + ' '
        partitura = partitura[:-1]
        partitura += '\n}'
    
        title = """\header {
          title = "¡¡Dj FullDupleX!!"
          composer = "Jessy, Alonso, Felipe, Aldo"
        }"""
        

        partitura += title
        print partitura
    
        with open(name, "w") as archivo:
            archivo.write(partitura)
    
        os.popen(self.name)
            
            
    def nota_musical(self, nota): # sine frequency, Hz.
        # Octava 4
        fs = 44100
        if nota == 'do':
            f = 261.625565
        elif nota == 'do#':
            f = 277.182631
        elif nota == 're':
            f = 293.664768
        elif nota == 're#':
            f = 311.126984
        elif nota == 'mi':
            f = 329.627557
        elif nota == 'fa':
            f = 349.228231
        elif nota == 'fa#':
            f = 369.994423
        elif nota == 'sol':
            f = 391.995436
        elif nota == 'sol#':
            f = 415.304698
        elif nota == 'la':
            f = 440.000000
        elif nota == 'la#':
            f = 466.163762
        elif nota == 'si':
            f = 493.883301
        # Octava 5
        elif nota == 'doAlto':
            f = 523.251131
        elif nota == 'do#Alto':
            f = 554.365262
        elif nota == 'reAlto':
            f = 587.329536
        elif nota == 're#Alto':
            f = 622.253967
        elif nota == 'miAlto':
            f = 659.255114
        elif nota == 'faAlto':
            f = 698.456463
        elif nota == 'fa#Alto':
            f = 739.988845
        elif nota == 'solAlto':
            f = 783.990872
        elif nota == 'sol#Alto':
            f = 830.609395
        elif nota == 'laAlto':
            f = 880.000000
        elif nota == 'la#Alto':
            f = 932.327523
        else: # Default Value: 'siAlta'
            f = 987.766603
        
        p = pyaudio.PyAudio()
        
        volume = 0.5     # range [0.0, 1.0]
        duration = 1.0   # in seconds, may be float
        
        # generate samples, note conversion to float32 array
        samples = (np.sin(2*np.pi*np.arange(fs*duration)*f/fs)).astype(np.float32)
        
        # for paFloat32 sample values must be in range [-1.0, 1.0]
        stream = p.open(format=pyaudio.paFloat32,
                        channels=1,
                        rate=fs,
                        output=True)
        
        # play. May repeat with different volume values (if done interactively) 
        stream.write(volume*samples)
        
        stream.stop_stream()
        stream.close()
        
        p.terminate()
        
        def miraquelindomidi(lista_notas):
            song = Midi(2)
            for elem in self.canciones:
                song.agregar_nota(elem,4,'p',Midi.NEGRA,True,1)
            with open("Pequena Serenata Nocturna.mid", "wb") as file:
                song.save(file)


m = musica()
m.grabar()

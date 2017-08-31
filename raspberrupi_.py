import cv2
import numpy as np
from os import listdir,getcwd,system
import os.path
from math import sqrt
import sys


import random

class Direzionatore(object):
	"""il nome e' totalmente a caso
	serve a dare una direzione alla macchinina"""
	def __init__(self,
	 IMG, m_linee_dritte, m_linee_verticali,thresh_houg,min_lenght,max_gap):
		#super(Direzionatore, self).__init__()
		self.IMG = self.preset_img(IMG)
		self.m_linee_dritte = m_linee_dritte
		self.m_linee_verticali = m_linee_verticali
		self.thresh_houg = thresh_houg
		self.min_lenght = min_lenght
		self.max_gap = max_gap
		self.lanes = self.trova_linee()#[sx,dx]

	def preset_img(self, IMG):
		try:
			#convert to grigio x meno dati
			IMG = cv2.cvtColor(IMG,cv2.COLOR_RGB2GRAY)
			#imgrandisco per rendere visibile
			IMG = cv2.resize(IMG, None, fx=1.6, fy=1.6)
			#la sfoco un pelo
			IMG = cv2.GaussianBlur(IMG, (7, 7), 0)
			#trovo i bordi principali
			v= np.median(IMG)
			lower = int(max(0, (1.0 - 0.33) * v))
			upper = int(min(255, (1.0 + 0.33) * v))
			IMG = cv2.Canny(IMG, lower, upper)
			#ri-sfoco le linee
			IMG = cv2.GaussianBlur(IMG, (3, 3), 0)
		except Exception as e:
			pass

		return IMG

	def get_line_info(l):
		x1,y1,x2,y2=l
		m = (float(y2)-y1)/(x2-x1)*-1.0
		q = -(float(x1)*y2 - x2*y1) / (x1 - x2)
		dim = sqrt((x1-x2)**2 + (y1-y2)**2)
		return (m,q,dim)

	def correzione(self):

		#estrapolo le dimensioni dall immagine
		try:
			dim_y , dim_x = self.IMG.shape
		except:
			dim_y , dim_x , _ = self.IMG.shape

		x_l,x_r = 0,0 #coordinata x delle due linee laterali
		x_c = dim_x/2 # e' automaticamente castato ad intero
		
		x1,y1,x2,y2=self.lanes[0]
		q = (float(x1)*y2 - x2*y1) / (x1 - x2) 
		m = (float(y2)-y1) / (x2-x1)
		x_l = (0.75*dim_y - q)/m
		
		x1,y1,x2,y2=self.lanes[1]
		q = (float(x1)*y2 - x2*y1) / (x1 - x2) 
		m = (float(y2)-y1) / (x2-x1)
		x_r = (0.75*dim_y - q)/m

		corr = (x_c - x_l) - (x_r - x_c)

		return (int(corr),
			[int(x_l), int(x_c), int(x_r)] )

	def trova_linee(self):
		#estrapolo le dimensioni dall immagine
		try:
			dim_y , dim_x = self.IMG.shape
		except:
			try:
				dim_y , dim_x , _ = self.IMG.shape
			except: 
				return [[0,0,0,0],[0,0,0,0]]

		#ritalgio l immagine per non carcare linee dove non c'e' bisgono
		v = np.array([
			[0  ,  dim_y],#1
			[0  ,  int(4.0/6*dim_y)],#2
			[int(2.0/6*dim_x)  ,  int(3.0/6*dim_y)],#3
			[int(4.0/6*dim_x)  ,  int(3.0/6*dim_y)],#4
			[dim_x  ,  int(4.0/6*dim_y)],#5
			[dim_x  ,  dim_y],#6
			[int(5.0/6*dim_x)  ,  dim_y],#7
			[int(3.0/6*dim_x)  ,  int(4.0/6*dim_y)],#8
			[int(1.0/6*dim_x)  ,  dim_y]])#9
		mask = np.zeros_like(self.IMG)
		cv2.fillPoly(mask,[v],255)
		IMGG = cv2.bitwise_and(self.IMG, mask)

		lines = cv2.HoughLinesP(
			IMGG,1,np.pi/180, self.thresh_houg, np.array([]),  self.min_lenght, self.max_gap)
		
		try:
			lines = lines.tolist()[0]
			#rimuovo le linee che sono probabili errori grossolani
			dimensione_med_l = 0
			for l in lines[:]:#ciclo per eliminare le linne in base all inclinazione
				x1,y1,x2,y2=l
				# quelle piu o meno orizzontali o verticali
				m=0
				try:
					m = (float(y2)-y1)/(x2-x1)*-1
				except:
					pass
				if -self.m_linee_dritte<m<self.m_linee_dritte or m<-self.m_linee_verticali or m>self.m_linee_verticali:
					lines.remove(l)
				else:#se non la rimuovo la uso per il calcolo della lunghezza media
					dimensione_med_l += sqrt((x1-x2)**2 + (y1-y2)**2)#calcolo lunghezza della linea

			dimensione_med_l /= len(lines)#media lunghezza
			for l in lines[:]:#ciclo per elimare la linee per la loro grandeza e posizione
				x1,y1,x2,y2=l
				dim = sqrt((x1-x2)**2 + (y1-y2)**2)
				if dim < dimensione_med_l/3.5:#se e' piccola, e' poco probabile che sia un linea
					lines.remove(l)

				x_med = (x1+x2)/2.0#posizione nella immagine
				m = (float(y2)-y1)/(x2-x1)*-1#orinatamento
				if (x_med<dim_x/2.0 and m<0) or (x_med>dim_x/2.0 and m>0):
				#se nella 1a meta inclinata male, non la considero
					lines.remove(l)
			del dimensione_med_l

			#calcolo una media di tutte le linee rimaste, divise in destra e sinistra
			lines_summary = [[],[]]#la prima lista e' per le linee sul lato sinistro, la seconda per quelle di destra
			for l in lines:#ciclo per dividere le linee
				x1,y1,x2,y2=l
				m = (float(y2)-y1)/(x2-x1)*-1
				if m<0: lines_summary[1].append(l)
				else : lines_summary[0].append(l) 
			lines_medie = []
			for lane in lines_summary:#ciclo per calcolare le medie(delle coordinate dei segmenti)
				x1_med,y1_med = 0,0
				x2_med,y2_med = 0,0
				for l in lane:
					x1,y1,x2,y2 =l
					x1_med += x1
					y1_med += y1
					x2_med += x2
					y2_med += y2
				x1_med = int(x1_med / len(lane))
				y1_med = int(y1_med / len(lane))
				x2_med = int(x2_med / len(lane))
				y2_med = int(y2_med / len(lane))
				lines_medie.append([x1_med,y1_med,x2_med,y2_med])
			del lines_summary

			#allungo le linee
			ris_finale = []
			for l in lines_medie:
				x1,y1,x2,y2 = l
				q = -(float(x1)*y2 - x2*y1) / (x1 - x2) 
				m = (float(y2)-y1) / (x2-x1) 
				ris_finale.append(list(map(lambda x: int(x),
					[ (q+dim_y)/m ,  dim_y ,  (q+(dim_y/2))/m ,  dim_y/2 ])))
				#       x1,           y1,           x2,             y2
			del lines_medie

			for n,l in enumerate(ris_finale):
				x1,y1,x2,y2=l
				if x1>dim_x: x1=dim_x
				if x2>dim_x: x2=dim_x
				if y1>dim_y: y1=dim_y
				if y2>dim_y: y2=dim_y

				if x1<0: x1=0
				if x2<0: x2=0
				if y1<0: y1=0
				if y2<0: y2=0
				ris_finale[n]=[x1,y1,x2,y2]

		except Exception as e:
			x,_, exc_tb = sys.exc_info()
			print (e,x)
			print "line:"+str(exc_tb.tb_lineno)
			return [[0,dim_y,dim_x/2,dim_y/2],[dim_x,dim_y,dim_x/2,dim_y/2]]
		
		return ris_finale








#standartd init:
#Direzionatore(0.25,7.5,70,50,5)
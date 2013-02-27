#!/usr/bin/python2
# -*- coding: utf-8 -*-

import os
import sys
import time
import serial

COMANDOS_DEFAULT='MT?\\nTT?\\nIA2?\\nID?\\nCS?\\nMC?\\nGS?\\nMR?'

MAX_LINE=9

SLEEP_TIME=0.5
SLEEP_MINI=0.05
SLEEP_FLUSH=2

class ConexionSerial:
	def __init__(self, PortSerialNumber='0', Comandos='MT?\\nTT?\\nIA2?\\nID?\\nCS?\\nMC?\\nGS?\\nMR?'):
		self.MiscVarInit(PortSerialNumber, Comandos)
		self.Connect()
	def MiscVarInit(self, PortSerialNumber, Comandos):
		self.PortConstant='/dev/ttyUSB'+PortSerialNumber
		self.Comandos=self.GetInstructionsSet(Comandos)
		
	def Ask(self, comando):	
		self.ser.write(comando)
		data=self.ser.readline()
		return data
	def AskData(self):
		Data=[]
		for instruccion in self.Comandos:
			self.ser.write(instruccion)
			time.sleep(SLEEP_MINI)
			Data.append(self.ser.readline())
		return Data
	def Connect(self):
		self.ser=serial.Serial(self.PortConstant)
		self.ser.timeout=0.1
		time.sleep(SLEEP_MINI)
	def Disconnect(self):
		self.ser.close()
	def Flush(self):
		self.ser.flushInput()
		time.sleep(SLEEP_FLUSH)
	def GetInstructionsSet  	(self, Comandos):
		Temp=Comandos.replace('\\n', '\n')
		Instrucciones=Temp.splitlines(True)
		return Instrucciones
	def SetInstructionsSet(self, Comandos):
		self.Comandos=self.GetInstructionsSet(comandos)
	def SetTimeOut(self, TPO):
		self.ser.timeout=TPO
if __name__ == '__main__':
	if len(sys.argv) == 1:
		CS=ConexionSerial('0',         'MT?\\nTT?\\nIA2?\\nID?\\nCS?\\nMC?\\nGS?\\nMR?')	
	elif len(sys.argv) == 2:
		CS=ConexionSerial(sys.argv[1], 'MT?\\nTT?\\nIA2?\\nID?\\nCS?\\nMC?\\nGS?\\nMR?')
	else:
		CS=ConexionSerial(sys.argv[1], sys.argv[2])
	i=0
	while(True):
		if i > 10:
			break
		Data=CS.AskData()
		print Data
		i+=1

















#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Clase encargada de abrir los sockets y configurarlos para el correcto
funcionamiento de  """

import subprocess
import os, sys
import time
import threading

def IncFileName(FILENAME):
	FileNumber=int(FILENAME[-3:])
	FileNumber+=1
	FileNumber=str(FileNumber)
	NewFN=FILENAME[:-3]+(FileNumber.zfill(3))
	return NewFN

def GetFileName(OUTPUTDIR, CURRENTDIR):
#	ls=subprocess.Popen(["ls", "/home/karl/U/2012 2/ELO322/Proyecto/src/log"], \
	ls=subprocess.Popen(["ls", CURRENTDIR], stdout=subprocess.PIPE, \
	                    stderr=subprocess.STDOUT).communicate()[0]
	date=subprocess.Popen(["date", "+%y-%m-%d"], stdout=subprocess.PIPE, \
				          stderr=subprocess.STDOUT).communicate()[0]

	#print ls
	if date.endswith("\n"):
		date=date[:-1]
	if len(ls)==0:
		return OUTPUTDIR+"/"+date+"_001"
	else:
		if ls.endswith("\n"):
			ls=ls[:-1]
		files=ls.split("\n")
		i=-1
		count=1
		largo=len(files)
		if largo > 0:
			while (date in files[i]):
				i-=1
				count+=1
				if (count-1)==largo:
					break
		zero_pad="_00"
		division=10
		countTemp=count
		while ((countTemp/division)>0):
			countTemp=countTemp/10
			zero_pad=zero_pad[:-1]
			if len(zero_pad) <= 1:
				break
		return OUTPUTDIR+"/"+date+zero_pad+str(count)
		
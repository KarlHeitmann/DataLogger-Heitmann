#!/usr/bin/python2
# -*- coding: utf-8 -*-

""" Principales: MT?\\nTT?\\nIA 2?\\nID?\\nCS?\\nMC?\\nGS?\\nMR?
				'MT?\\nTT?\\nIA 2?\\nID?\\nCS?\\nMC?\\nGS?\\nMR?'
MT: Transmitter status
TT: Get current time and date
IA 2: Read analogue input #2 value
ID: Get digital inputs
CS: Get script version
MC: Get number of forward messages buffered
GS: GPS status
MR: Receiver status

UTILIZADOS:      MT?\\nTT?\\nIA 2?\\nID?\\nCS?\\nMC?\\nGS?\\nMR?
"""

import os
import sys
import time
import FileSystemKarl
import SataKernel
import ConexionSerial
import curses

MAX_LINE=9

SLEEP_TIME=0.5
TIME_OUT=5000
SLEEP_MINI=0.05
SLEEP_FLUSH=2

TIMER_PERIODIC=3600

SCRIPT_FILE = "/home/karl/Carpetas compartidas/RW/Guard service/fork GS estable/Guard Service Fork 4_44.dat"
#SCRIPT_FILE="/home/karl/GuardService/SATScript/GuardService.dat"

LOG_SCRIPT_FILE = "./log_script_file"


SHUTDOWN=4048
OPENBOX=3584
BATERIA=2576
ASSAULT=1536
OK=512
DELAY_ROUND=5
FLAGS={'Esperando':False, 'Transmitiendo':False, 'Complete':True}

MyScreen=curses.initscr()
curses.start_color()

TxState=''
TxTime=''
msgCola=''
CurrentTimeAndDate=''
Canal=''
Lectura=''
DigitalInputState=''
ScriptVersion=''
GPSStatus=''
OutputFileName=''
TimerPeriodicValue=''
EventTime=0

def MiscVarInit(LogDir):
	global OutputFileName
	OutputFileName=FileSystemKarl.GetFileName(LogDir, LogDir)
	Clear()
	return OutputFileName 
def Clear():
	global TxState, TxTime, msgCola, CurrentTimeAndDate, Canal, Lectura, \
			DigitalInputState, ScriptVersion, GPSStatus, EventTime, TimerPeriodicValue
	global MyScreen
	TxState=''
	TxTime=''
	msgCola=''
	CurrentTimeAndDate=''
	Canal=''
	Lectura=''
	DigitalInputState=''
	ScriptVersion=''
	TimerPeriodicValue=''
	GPSStatus=''
	MyScreen.clear()
	MyScreen.border(0)

#def CambiaNombreArchivo():
#	global OutputFileName
#	FileNumber=OutputFileName[-3:]
#	return FileNumber

def CheckComment(Instruction):
	Comentario = (Instruction.startswith('//')) or (Instruction == '') or (Instruction == '\r\n')
	return Comentario

def DetectarAlarma():
	global TxState, TxTime, msgCola, CurrentTimeAndDate, Canal, Lectura, \
			DigitalInputState, ScriptVersion, GPSStatus, EventTime, TimerPeriodicValue
#	EventTime=time.time()
	if (Lectura < 4048):
		if (DigitalInputState[-2] == '1'):
			Alarm='Apagandose CONFIRMADO'
		else:
			Alarm='Apagandose ANULADO'
	if Lectura < 3584:
		if (DigitalInputState[-2] == '1'):
			Alarm='Tapa abierta\t'
		else:
			Alarm='Tapa cerrada\t'
	if Lectura < 2576:
		if (DigitalInputState[-2] == '1'):
			Alarm='Desenchufado de la red'
		else:
			Alarm='Enchufado a la red'
	if Lectura < 1536:
		if (DigitalInputState[-2] == '1'):
			Alarm='EMERGENCIA ON'
		else:
			Alarm='EMERGENCIA CANCELADA'
	if Lectura < 512:
		pass
		#Alarm='Reporte de posicion 5'
	if Lectura == 0:
		Alarm='Fallo de componente 6'
	return Alarm

def Display():
	global TxState, TxTime, msgCola, CurrentTimeAndDate, Canal, Lectura, \
			DigitalInputState, ScriptVersion, GPSStatus, EventTime, TimerPeriodicValue
	global MyScreen
	MyScreen.addstr( 4, 2, "Numero del Tx (2, 3 o 4): " + str(TxState))
	MyScreen.addstr( 5, 2, "Hora ultima Tx:           " + str(TxTime))
	MyScreen.addstr( 6, 2, "Mensajes encolados:       " + str(msgCola))
	MyScreen.addstr( 7, 2, "Hora GPS:                 " + str(CurrentTimeAndDate))
	MyScreen.addstr( 8, 2, "Canal ADC:                " + str(Canal))
	MyScreen.addstr( 9, 2, "Lectura ADC:              " + str(Lectura))
	MyScreen.addstr(10, 2, "I/O State:                " + str(DigitalInputState))
	MyScreen.addstr(11, 2, "Script version            " + str(ScriptVersion))
	MyScreen.addstr(12, 2, "Estado GPS                " + str(GPSStatus))
	MyScreen.addstr(13, 2, "Timer Periodic Value:     " + str(TimerPeriodicValue))
	MyScreen.addstr(14, 2, "Hora ultimo evento:       " + str(EventTime))
	MyScreen.addstr( 7,50, "Umbrales:")#, curses.A_BLINK )
	MyScreen.addstr( 8,50, "Alarma     - Voltaje Digital")
	MyScreen.addstr( 9,50, "Apagandose < 4048")
	MyScreen.addstr(10,50, "Tapa       < 3584")
	MyScreen.addstr(11,50, "Red        < 2576")
	MyScreen.addstr(12,50, "Emergencia < 1536")
	MyScreen.addstr(13,50, "Error Comp =    0")

def LoadDefaultScript():
	ScriptFile = open(SCRIPT_FILE)
	LogScriptFile = open(LOG_SCRIPT_FILE, 'w')
	for Instruction in ScriptFile:
		if not(CheckComment(Instruction)):
			ser.write(Instruction)
			Response = ser.readline()
			print Instruction
			print Response
			LogScriptFile.write(Instruction)
			LogScriptFile.write(Response)
#	ResetPort()	

def Record(Inter, (Alarm, ETime, Lect), TxTime):
	global OutputFileName
	text=       "Intervalo:       "    + str(int(Inter))              + '\n'
	if ((Alarm==-1) and (ETime == -1) and (Lect == -1)):
		if Lect == -1:
			text=text + "Ultima Alarma: "  + "Perdida"                + '\n'
		else:
			text=text + "Ultima Alarma: "  + "Perdida"                + '\n'
		text=text + "Hora del evento: "    + "Perdido"                + '\n'     
	else:
		if Lect == -1:
			text=text + "Ultima Alarma: "  + Alarm + "\tNOT AN TRIG " + '\n'
		else:
			if Alarm == 'EMERGENCIA ON':
				text=text + "Ultima Alarma: "  + Alarm + '\t\t' + str(Lect) + '\n'
			else:
				text=text + "Ultima Alarma: "  + Alarm + '\t' + str(Lect) + '\n'
		text=text + "Hora del evento: "    + ETime                    + '\n'     
	text=text + "Hora Tx evento:  "        + TxTime               
	
	f=open(OutputFileName, 'a')
		
	f.write(text)
	f.write('\n\n')
	f.close()
#	return text
	return text.split('\n')
def run(LogDir, SerialNumber):
	global TxState, TxTime, msgCola, CurrentTimeAndDate, Canal, Lectura, \
			DigitalInputState, ScriptVersion, GPSStatus, TimerPeriodicValue, FLAGS
	global MyScreen, OutputFileName
	MiscVarInit(LogDir)        
	input=''              
#	CS=ConexionSerial.ConexionSerial('0'         , 'MC?\\nMT?\\nTT?\\nIA2?\\nID?\\nCS?\\nMC?\\nGS?\\nMR?')	
#	CS=ConexionSerial.ConexionSerial(SerialNumber, 'MT?\\nTT?\\nIA2?\\nID?\\nCS?\\nMC?\\nGS?\\nMR?')
#	CS=ConexionSerial.ConexionSerial(SerialNumber, 'TV5?\\nGS?\\nCS?\\nMT?\\nTT?\\nIA2?\\nID?\\nMT?')
	CS=ConexionSerial.ConexionSerial(SerialNumber, 'MT?\\nTV5?\\nCS?\\nMT?\\nTT?\\nIA2?\\nID?\\nGS?')
	Kernel=SataKernel.kernel()
	Delay=0
	Ready=True
	t1=0.0
	ListAlarms=[]
	TextoAppend=""
	AlarmaInicio=False
	UltimaAlarma=""
	#LogAlarmas son las que se registran en el log, y aparecen en bold a la derecha
	LogAlarmas=[]
	#QueueAlarm indica las alarmas que estan en la cola, estan a la izquierda y parpadean
	QueueAlarm=[]
	LecturaAlarma=0
	MyScreen.timeout(TIME_OUT)
	MyScreen.nodelay(1)
	MyScreen.notimeout(0)
	ArchivoAbierto=False
	Clear()
	while(True):
		#Pedir respuestas al puerto serial
		Data=CS.AskData()
		os.system('clear')
		datos=['mt','tt','ia','id','cs','gs', 'tv 05']
		
		#Decodificacion de respuestas
		j=0
		for msg in Data:
			if   msg     == '':
				
#				MyScreen.addstr(1, 2+(18*j), "Respuesta perdida|") #FIXME
				MyScreen.addstr    ( 1, 2, "Respuesta perdida|") #FIXME
				pass
			elif msg[:2] == 'mt':
				TxState, TxTime, msgCola=Kernel.MTTimingV2(msg)
				try:
					datos.remove('mt')
				except:
					MyScreen.addstr( 2, 2, "Fallo al remover 'mt' dentro de la lista") #FIXME
					pass
			elif msg[:5] == 'tv 05':
				Temp=Kernel.TVDecode(msg)
				TimerPeriodicValue=Temp['2 Value']
				datos.remove('tv 05')
			elif msg[:2] == 'tt':
				CurrentTimeAndDate=Kernel.TTDecode(msg)
				datos.remove('tt')
			elif msg[:2] == 'ia':
				Canal, Lectura    =Kernel.IATuple(msg)
				datos.remove('ia')
			elif msg[:2] == 'id':
				DigitalInputState =Kernel.IDDecode(msg)
				datos.remove('id')
			elif msg[:2] == 'cs':
				ScriptVersion     =Kernel.CSDecode(msg)
				datos.remove('cs')
			elif msg[:2] == 'gs':
				GPSStatus         =Kernel.GSDecode(msg)
				datos.remove('gs')
			else:
#				MyScreen.addstr(3, 2+(27 *j), "Respuesta '" + msg[:2] +"' desconocida|")
#				MyScreen.addstr( 3, 2, "Respuesta '" + str(msg[:2]) +"' desconocida|")
				MyScreen.addstr( 3, 2, "Respuesta '" + str(msg) +"' desconocida|")
			j+=1
		#Chequea si faltaron respuestas
		gravedad = False
		if len(datos) > 0:
			posicion_cursor=15
			#	datos=['mt','tt','ia','id','cs','gs', 'tv 05']

			if 'gs' in datos:
				MyScreen.addstr( posicion_cursor, 50, '¿gs?')
				posicion_cursor+=1
			if 'cs' in datos:
				MyScreen.addstr( posicion_cursor, 50, '¿cs?')
				posicion_cursor+=1
			if 'tv 05' in datos:
				MyScreen.addstr( posicion_cursor, 50, '¿tv 05?')
				posicion_cursor+=1
				TimerPeriodicValue=-1
			if 'id' in datos:
				MyScreen.addstr( posicion_cursor, 50, '¿id?')
				posicion_cursor+=1
				gravedad=True
			if 'ia' in datos:
				MyScreen.addstr( posicion_cursor, 50, '¿ia?')
				posicion_cursor+=1
				gravedad=True
			if 'tt' in datos:
				MyScreen.addstr( posicion_cursor, 50, '¿tt?')
				posicion_cursor+=1
			if 'mt' in datos:
				MyScreen.addstr( posicion_cursor, 50, '¿mt?')
				posicion_cursor+=1
				gravedad=True
			if gravedad:
				MyScreen.addstr(2,3,str(datos))
				MyScreen.refresh()
				CS.Flush()
				continue
			
		
		#Si recien se recibio una alerta, espera ciertas rondas de forma tal de
		#ignorar alarmas repetidas (eg: que pregunte dos veces en el mismo segundo)
		if not(Ready):
			if Delay > DELAY_ROUND:
				Ready=True
				Delay=0
			else:
				Delay+=1
				
		if not(AlarmaInicio):
			if (TxTime == '99:99') and (msgCola == 1): 
				EventTime=CurrentTimeAndDate
				Alarm='Encendido!'
				Ready=False
				ListAlarms.append((Alarm, EventTime, -1))
				AlarmaInicio=True
				LogAlarmas.append(Alarm)
				QueueAlarm.append(Alarm)
		#Chequea la entrada digital, de darse el aviso de alarma chequea las entradas
		if (Ready) and (DigitalInputState[-4]== '1'):
			EventTime=CurrentTimeAndDate
			Alarm = DetectarAlarma()
			Ready=False
			ListAlarms.append((Alarm, EventTime, Lectura))
			QueueAlarm.append(Alarm)
			LogAlarmas.append(Alarm+'__'+str(Lectura))
		if (Ready) and (TimerPeriodicValue >= TIMER_PERIODIC - 1):
			if (TimerPeriodicValue != -1):
				EventTime=CurrentTimeAndDate
				if   ((TIMER_PERIODIC % 3600) == 0):
					Alarm="Reporte periodico " + str(TIMER_PERIODIC / 3600) + " hora[s]"
				elif ((TIMER_PERIODIC %   60) == 0):
					Alarm="Reporte periodico " + str(TIMER_PERIODIC /   60) + " minuto[s]"
				else:
					Alarm="Reporte periodico " + str(TIMER_PERIODIC)        + " segundo[s]"
				Ready=False
				ListAlarms.append((Alarm, EventTime, -1))
				LogAlarmas.append(Alarm)
				QueueAlarm.append(Alarm)
		if FLAGS['Complete']:
			TextoAppend="Estado: Complete"
			#Estado actual, no hace nada
			if (TxState == 0) or (TxState == 1) or (TxState == 4):
				pass
			elif (TxState == 2):
				t1=time.time()
				FLAGS['Complete'] =False
				FLAGS['Esperando']=True 
		elif FLAGS['Esperando']:
			TextoAppend="Estado: Esperando"
			#Estado actual, no hace nada
			if TxState == 2:
				pass
			elif TxState == 3:
				FLAGS['Transmitiendo']=True
				FLAGS['Esperando']=False
		elif FLAGS['Transmitiendo']:
			TextoAppend="Estado: Transmitiendo"
			#Estado actual, no hace nada
			if (TxState == 3):
				pass
			elif   (TxState == 2) or (TxState == 4):
#				FLAGS['Esperando']=True #Esperando=True cuando TxState=2
				Intervalo=t1-time.time()
				TxTime
				t1=time.time()
#				TxTime=CurrentTimeAndDate
				TxSend=CurrentTimeAndDate
				if len(ListAlarms) > 0:
					QueueAlarm.pop(0)
					UltimaAlarma=Record(Intervalo, ListAlarms.pop(0), TxSend)
				else:
					UltimaAlarma=Record(Intervalo, (-1, -1, -1), TxSend)
				ArchivoAbierto=True
				TextoAppend=TextoAppend #+ UltimaAlarma
				FLAGS['Transmitiendo']=False 
				FLAGS['Esperando']=bool(TxState-4)
				FLAGS['Complete']=bool(TxState-2)
				
			#Antiguo	
#			elif (TxState == 4):
#				FLAGS['Complete']     =True #Complete=True cuando TxState=4
#				FLAGS['Transmitiendo']=False
		Display()	
		#Desde el 15 esta disponible
		MyScreen.addstr(15, 2, TextoAppend, curses.A_BOLD )
		MyScreen.addstr(16, 2, "Alarmas en cola:", curses.A_BOLD)#, curses.color_pair(1))# + QueueAlarm)
		i=0
		for temp in QueueAlarm:
			MyScreen.addstr(17+i, 2, temp, curses.A_BLINK)
			i+=1
		j=0
		for temp in LogAlarmas:
			MyScreen.addstr(17+j,50, temp, curses.A_BOLD)
			j+=1
		MyScreen.addstr(17+i, 2, "Ultima alarma registrada", curses.A_BOLD)
#		MyScreen.addstr(18+i, 2, UltimaAlarma )
		
		k=0
		for temp in UltimaAlarma:
			MyScreen.addstr(18+i+k, 2, temp)
			k+=1
		MyScreen.addstr(19+i+k, 2, OutputFileName)
		MyScreen.addstr(20+i+k, 1, '?')
		input = MyScreen.getch()
		if input != -1:
			input=chr(input)
			if (input == 'q'):
				break
			if (input == 'a'):
				if ArchivoAbierto:
					Temp=OutputFileName
					OutputFileName=FileSystemKarl.IncFileName(Temp)
					LogAlarmas=QueueAlarm
					ArchivoAbierto=False
			if (input == 's'):
				CS.Flush()
				pass
			if (input == 'w'):
				MyScreen.refresh()
				ScriptFile = open(SCRIPT_FILE)
				LogScriptFile = open(LOG_SCRIPT_FILE, 'w')
				CS.SetTimeOut(0.3)
				for Instruction in ScriptFile:
					if not(CheckComment(Instruction)):
						Response=CS.Ask(Instruction)
#						ser.write(Instruction)
#						Response = ser.readline()
						MyScreen.addstr(2, 2, Instruction)
						MyScreen.addstr(3, 2, Instruction)
#						print Instruction
#						print Response
						LogScriptFile.write(Instruction)
						LogScriptFile.write(Response)
						MyScreen.refresh()
				CS.SetTimeOut(0.1)
				LogScriptFile.close()
				ScriptFile.close()
				pass
		#Limpiar datos
		MyScreen.refresh()
		#time.sleep(SLEEP_TIME)
		Clear()
	CS.Disconnect()
	curses.endwin()
	
if __name__ == '__main__':
	if len(sys.argv)   == 1:
		run('./log_alarm',         '0')	
	elif len(sys.argv) == 2:
		run('./log_alarm'    , sys.argv[1])
	else:
		run(sys.argv[2], sys.argv[1])
	


















#def LoadDefaultScript():
#	ScriptFile = open(SCRIPT_FILE)
#	LogScriptFile = open(LOG_SCRIPT_FILE, 'w')
#	for Instruction in ScriptFile:
#		if not(CheckComment(Instruction)):
#			ser.write(Instruction)
#			Response = ser.readline()
#			print Instruction
#			print Response
#			LogScriptFile.write(Instruction)
#			LogScriptFile.write(Response)
##	ResetPort()
	
#def CheckComment(Instruction):
#	Comentario = (Instruction.startswith('//')) or (Instruction == '') or (Instruction == '\r\n')
#	return Comentario

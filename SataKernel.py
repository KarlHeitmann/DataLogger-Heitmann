#!/usr/bin/python2
# -*- coding: utf-8 -*-


"""Command summary: pag. 119, 7.18
TIPS:
-Al analizar un solo bit N (eg, el bit #9 de X registro), basta con utilizar 
 X[N] (eg: X[9])
-Al analizar mas de un bit de un registro X (eg, 7..9: 3 bits), hay que tomar el
 bit inicial y sumarle la cantidad de bits a analizar. Utilizar operacion reba-
 nado para ello (eg: 7+3=10 -> X[7:10])

TODO:
-Todo lo que esta marcado
-Investigar acerca de comando 7.14.14: DS TT
"""

import DiccionarioDefiniciones

DCONFIGURACION_ALARMA={'0 Alarm Channel':'', '1 Alarm Enable':False, '2 Latch Alarm':False, \
                       '3 Auto Latch Release':False, '4 Operation NumberLP':'',\
                       '6 Threshold Comparison Mode':'', '7 Target Register Number':'',\
                       '8 Target Module Number':'', '5 Operation NumberHP':''}
DRECEIVER_STATUS={'1 Condition':False, '2 BB Alarm': False, \
                  '3 BB Traffic Indicator':False, '4 Receiver Status Code':''}
class kernel:
	def __init__(self):
		self.MiscVarInit()
	def MiscVarInit(self):
		self.DConfiguracionAlarma=DCONFIGURACION_ALARMA
		self.AnalogueInput={'1 Canal':'', '2 Lectura':''}
		self.ReceiverStatus=DRECEIVER_STATUS
	#Convierte String a Binario
	def StrToBin(self, number, largo):
		a=bin(int(number, 16))[2:]
		l=len(a)
		if l < largo:
			a = '0'*(largo-l) + a
		return a
	def Str32ToBin(self, number):
		a=bin(int(number, 16))[2:]
		l=len(a)
		if l < 32:
			a = '0'*(32-l) + a
		return a
	#AC: Configure Alarms R/W
	def ACDecodeOld(self, Resp):
		"""Configure Alarms, receive config_value 7.6.1, 
		   section 5.5 Alarm Module details, 5.5.3, Table 22"""
		if ((Resp <> '') and (Resp <> '0')):
			try:
				#pdb.set_trace()
				#channel = int((Resp[3:7]), 16)
				#pdb.set_trace()
				number = Resp[3:5]
				alarmnumber = 'Alarm ' + number
				AlarmNumber = alarmnumber + '\n'
				
				configvalue = str(bin(int((Resp[6:14]),16)) )
				configvalue = configvalue.replace('0b','')
				
				while (len(configvalue) <= 32):
					configvalue = '0' + configvalue
				
				ConfigValue = configvalue + '\n'
				
				if (configvalue[-1] == '1'):
					ConfigValue = ConfigValue + alarmnumber + ' enable\n'
				else:
					ConfigValue = ConfigValue + alarmnumber + ' disable\n'
					
				if (configvalue[-2] == '1'):
					ConfigValue = ConfigValue + alarmnumber + ' latch ON\n'
				else:
					ConfigValue = ConfigValue + alarmnumber + ' Latch DISABLE\n'
				
				if (configvalue[-3] == '1'):
					ConfigValue = ConfigValue + alarmnumber + ' Auto latch ON\n'
				else:
					ConfigValue = ConfigValue + alarmnumber + ' A. LATCH DISABLE\n'
				
				ConfigValue = ConfigValue + 'Low part operation number: ' + configvalue[-8:-3] + '\n'
				
				ConfigValue = ConfigValue + 'Threshold comparison mode: ' + str(int(configvalue[-12:-8],2)) + '\n'
				
				ConfigValue = ConfigValue + 'Reserved - leave as zero: ' + str(int(configvalue[-15:-12])) + '\n'
				
				ConfigValue = ConfigValue + 'High part operation number: ' + configvalue[-19:-15] + '\n'

				ConfigValue = ConfigValue + 'Reserved - leave as zero: ' + configvalue[-20] + '\n'
				
				ConfigValue = ConfigValue + 'Target register number: ' + configvalue[-28:-20] + '\n'
				
				ConfigValue = ConfigValue + 'Target module register: ' + configvalue[-32:-28] + '\n'
				
				return AlarmNumber + ConfigValue
				
			except:
				return 'ERROR AC alarm config: ' + Resp
		else:
			return
	#ACDecode tiene bugs!!! ['ac 19 12345678\r\n', 'ac 07 87654321\r\n']
	def ACDecode(self, Resp):
		"""
		Configure Alarms, receive config_value 7.6.1, 
		section 5.5 Alarm Module details, 5.5.3, Table 22
		eg: "ac 12 12345678\r\n"
		"""
		
		try:
			ConfigValue         =self.Str32ToBin(Resp[ 6:14])
			AlarmNumber         =int(self.StrToBin(Resp[ 3: 5], 8), 2)
			   
			AlarmEnable         =int(ConfigValue[ -1:   ], 2)
			LatchAlarm          =int(ConfigValue[ -2: -1], 2)
			AutoLatchRelease    =int(ConfigValue[ -3: -2], 2)
			OperationNumberLP   =int(ConfigValue[ -8: -3], 2)
			ThresholdCompMode   =int(ConfigValue[-12: -8], 2)
			Reserved            =int(ConfigValue[-16:-12], 2)
			OperationNumberHP   =int(ConfigValue[-19:-16], 2)
			Reserved            =int(ConfigValue[-20:-19], 2)
			TargetRegisterNumber=int(ConfigValue[-28:-20], 2)
			TargetModuleNumber  =int(ConfigValue[-32:-28], 2)
			
			Resp='Alarm Enable' + str(bool(AlarmEnable)) +'\nLatchAlarm'
			
			self.DConfiguracionAlarma['0 Alarm Channel']             =str(AlarmNumber)
			self.DConfiguracionAlarma['1 Alarm Enable']              =bool(AlarmEnable)
			self.DConfiguracionAlarma['2 Latch Alarm']               =bool(LatchAlarm)
			self.DConfiguracionAlarma['3 Auto Latch Release']        =bool(AutoLatchRelease)
			self.DConfiguracionAlarma['4 Operation NumberLP']        =str(OperationNumberLP)
			self.DConfiguracionAlarma['6 Threshold Comparison Mode'] =str(ThresholdCompMode)
			self.DConfiguracionAlarma['7 Target Register Number']    =str(TargetRegisterNumber)
			self.DConfiguracionAlarma['8 Target Module Number']      =str(TargetModuleNumber)
			self.DConfiguracionAlarma['5 Operation NumberHP']        =str(OperationNumberHP)
			
			return self.DConfiguracionAlarma
		except:
			return "ERROR" 
	def ACDisplay(self, msg):
		DAC=self.ACDecode(msg)
		keys=DAC.keys()
		keys.sort()
		DataDisplay=''
		for k in keys:
			DataDisplay=DataDisplay+k[2:]+': '+str(DAC[k])+'\n'
		return DataDisplay
	def ACDecodeExpressOld(self, Resp):
		"""Fast configure alarms R/W"""
		if ((Resp <> '') and (Resp <> '0')):
			try:
				#pdb.set_trace()
				#channel = int((Resp[3:7]), 16)
				#pdb.set_trace()
				number = Resp[3:5]
				alarmnumber = 'Alarm ' + number
				AlarmNumber = alarmnumber + '\n'

				configvalue = str(bin(int((Resp[6:14]),16)) )
				configvalue = configvalue.replace('0b','')
				
				while (len(configvalue) <= 32):
					configvalue = '0' + configvalue
				
				ConfigValue = configvalue + '\n'
				
				if (configvalue[-1] == '1'):
					ConfigValue = ConfigValue + alarmnumber + ' enable\n'
				else:
					ConfigValue = ConfigValue + alarmnumber + ' disable\n'
					
				if (configvalue[-2] == '1'):
					ConfigValue = ConfigValue + alarmnumber + ' latch ON\n'
				else:
					ConfigValue = ConfigValue + alarmnumber + ' Latch DISABLE\n'
				
				if (configvalue[-3] == '1'):
					ConfigValue = ConfigValue + alarmnumber + ' Auto latch ON\n'
				else:
					ConfigValue = ConfigValue + alarmnumber + ' A. LATCH DISABLE\n'
				return AlarmNumber + ConfigValue
				
			except:
				return 'ERROR AC alarm config: ' + Resp
		else:
			return
	def CEWhat(self):
		return "Get/Set Terminal Power Control State"
	
	def CPWhat(self):
		"""7.3.7"""
		return "CP – Get MSP Firmware Version"
	
	def CEDecode(self, Resp):
		"""7.3.3 Get/Set Terminal Power Control State - <power_ctrl>
		<power_ctrl>: module 0x0 register 0x03 
		5.3.4
		"""
		power_ctrl=self.StrToBin(Resp[3:5], 8)
		if power_ctrl[-1] == '1':
			decode='Enable RS-232 serial port drivers'
		else:
			decode='Disable RS-232 serial port drivers'
		if power_ctrl[-2] == '1':
			decode=decode + 'Enable terminal power\n'
		else:
			decode=decode + 'Disable terminal power\n'
		if power_ctrl[-2] == '1':
			decode=decode + 'Enable terminal power\n'
		else:
			decode=decode + 'Disable terminal power\n'
		if power_ctrl[-3] == '1':
			decode=decode + 'Enable terminal ind LED\n'
		else:
			decode=decode + 'Disable terminal ind LED\n'
		if power_ctrl[-4] == '1':
			decode=decode + 'Enable terminal ADC\n'
		else:
			decode=decode + 'Disable terminal ADC\n'
		if power_ctrl[-5] == '1':
			decode=decode + 'Disable GPS recvr\n'
		else:
			decode=decode + 'Enable GPS recvr\n'
		if power_ctrl[-9] == '1':
			decode=decode + 'Enable ISAT M2M slotted receive mode\n'
		else:
			decode=decode + 'Disable ISAT M2M slotted receive mode\n'
	#CS: Script Version
	def CSDecode(self, Resp):
		"""Get/Set Application Script Version 32 bit register in byte reversed 
		order.  
		Module: 0x0 
		Register: 0x07 
		DOC: 7.3.9, 5.3.7"""
		try:
			ScriptVersion=Resp[3:7]
			return ScriptVersion
		except:
			return 0
	def Er10What(self):
		return "Invalid Command, Command Not Recognized"
	def GAWhat(self):
		return "Get Current GPS Altitude"
	def GPWhat(self):
		return "Get Current GPS Position"
	#GS: GPS status
	def GSDecodeOld(self, Resp):
		"""GPS Status: Validez del reporte de posicion GPS. valor: valid_flag
		Modulo 0x04
		Registro 0x00
		DOC: 7.8.1.2, 5.7.1.1"""
		try:
			if (Resp[-3] == '1'):
				return 'GPS OK\n' 
			elif (Resp[-3] == '0'):
				return '******DATA GPS INVALID*******\n'
		except:
			return 0
	def GSDecode(self, Resp):
		"""GPS Status: Validez del reporte de posicion GPS. valor: valid_flag
		Modulo 0x04
		Registro 0x00
		DOC: 7.8.1.2, 5.7.1.1"""
		try:
			ValidFlag=Resp[3:5]
			if ValidFlag[-1] == '0':
				return '****GPS INVALIDO****** '
			else:
				return 'GPS OK'
		except:
			return 0
	#IA: Analog Input XXX: lleva numero: 'IA 2?\n'
	def IADecode(self, Resp):
		"""IA Get/Set Analog Input: 
		DOC: 7.4.1, 5.6.2
		""" 
		try:
			Channel=Resp[3:5]
			Value  =Resp[6:9]
			
			Value=str(int(self.StrToBin(Value, 12), 2))
			self.AnalogueInput['1 Canal']  =Channel
			self.AnalogueInput['2 Lectura']=Value
			return self.AnalogueInput
		except:
			return 0
	def IATuple(self, Resp):
		"""IA Get/Set Analog Input: 
		DOC: 7.4.1, 5.6.2
		""" 
		try:
			Channel=Resp[3:5]
			Value  =Resp[6:9]
			
			Value=int(self.StrToBin(Value, 12), 2)
			return (int(Channel), Value)
		except:
			return (None, None)
	def IADisplay(self, msg):
		DIA=self.IADecode(msg)
		keys=DIA.keys()
		keys.sort()
		DataDisplay=''
		for k in keys:
			DataDisplay=DataDisplay+k[2:]+': '+str(DIA[k])+'\n'
		return DataDisplay
	#ID: Get Digital Inputs
	def IDDecode(self, Resp):
		""" ID Get Digital Inputs
		DOC: 7.4.3, 5.6.3
		2 ASCII HEX, indicando el estado de las entradas digitales:
		0-NO es DIGITAL INPUT
		1-SI es DIGITAL INPUT
		"""
		try:
			Value=Resp[3:5]
			Value=self.StrToBin(Value, 8)
			return Value[0:4]+'_'+Value[4:8]
		except:
			return 0
	#MC: Get Number of Forward Messages Buffered
	def MCDecode(self, Resp):
		"""MC - Get Number of Forward Messages Buffered
		DOC: 7.9.1.2"""
		try:
			return Resp[3:4]
		except:
			return 0
	#MR: Receiver Status
	def MRDecodeOld(self, Resp):
		"""MR - Receiver Status
		DOC: 7.9.2.8, 5.8.7.2, 5.8.7.3"""
		if ((Resp <> '') and (Resp <> '0')):
			try:
				#channel = int((Resp[3:7]), 16)
				channel = 'Channel: ' + (Resp[3:7])
				quality = int((Resp[8:12]),16)
				#status = str(int((Resp[13:15]),16))
				status = str( bin(int((Resp[13:15]),16)) )
				status = status.replace('0b','')
				
				Channel = channel + '\n'
				Quality = 'Signal: ' + str((quality * 10) / 4096) + 'dB\n'

				while (len(status) <= 7):
					status = '0' + status			

				Status = status + '\n'
				#print "Resp:", Resp
				#print "Channel:",Channel, "|", str(channel)
				#print "Quality:",Quality,"|", str(quality)
				#print "Status:",Status, "|",str(status)
				#raw_input()
				
				if (status[-1] == '0'):
					Status = Status + 'Condition normal\n'
				else:
					Status = Status + 'Condition abnormal\n'
				if (status[-2] == '0'):
					Status = Status + 'BB Alarm normal\n'
				else:
					Status = Status + 'BB Alarm abnormal\n'
				if (status[-3] == '0'):
					Status = Status + 'BB/Traffic Indicator BB\n'
				else:
					Status = Status + 'BB/Traffic Indicator TC\n'
				Status = Status + 'Reserved: ' + status[-4] + '\n'
				#pdb.set_trace()
				if (status[-7:-4] == '000'):
					Status = Status + 'DSP Reset\n' 
				elif (status[-7:-4] == '001'):
					Status = Status + 'Configuring\n'
				elif (status[-7:-4] == '010'):
					Status = Status + 'Wideband Acquisition\n'
				elif (status[-7:-4] == '011'):
					Status = Status + 'Narrowband BB\n'
				elif (status[-7:-4] == '100'):
					Status = Status + 'BB Tracking and Demodulation\n'
				elif (status[-7:-4] == '101'):
					Status = Status + 'Narrowband Traffic\n'
				elif (status[-7:-4] == '110'):
					Status = Status + 'Traffic Tracking and Demodulation\n'
				elif (status[-7:-4] == '111'):
					Status = Status + 'Reserved\n'
				Status = Status + 'Reserved: ' + status[-8] + '\n' 
				return Channel + Quality + Status
			except:
				return 'ERROR message receive status' + Resp
		else:
			return Resp
	def MRDecode(self, Resp):
		"""MR - Receiver Status
		DOC: 7.9.2.8, 5.8.7.2, 5.8.7.3"""
		channel = Resp[3:7]
		quality = int((Resp[8:12]),16)
		Quality = str((quality * 10) / 4096) + 'dB'
		#status  = str(    int((Resp[13:15]),16))
#		status   = str(bin(int((Resp[13:15]),16)) )
		status = self.StrToBin(Resp[13:15], 8)
		self.ReceiverStatus['1 Condition'] = bool(int(status[ -1:   ]))
		self.ReceiverStatus['2 BB Alarm' ] = bool(int(status[ -2: -1]))
		self.ReceiverStatus['3 BB Traffic Indicator'] = bool(int(status[ -3: -2]))
		self.ReceiverStatus['4 Receiver Status Code'] = str(int(status[ -7: -4]))
		return self.ReceiverStatus
	def MRDisplay(self, Resp):
		DMR=self.MRDecode(Resp)
		keys=DMR.keys()
		keys.sort()
		DataDisplay=''
		for k in keys:
			DataDisplay=DataDisplay+k[2:]+': '+str(DMR[k])+'\n'
		return DataDisplay
	def MRWhat(self):
		return "Report Receiver Status"
	#MT: Transmiter Status
	def MTTiming(self, Resp):
		"""MT Report Transmitter status 7.9.2.10, 5.8.8"""
		if len(Resp) == 0:
			return "ERROR Resp: Todos los valores son ceros!"
		else:
			Status=Resp[3:11] #Status mide 8 bits
			Status = self.Str32ToBin(Status)
			TransmissionState    =int(Status[ -3:   ], 2)
			Minutes1             =Resp[5]#str(int(Status[-20:-16], 16))
			Minutes2             =Resp[6]#str(int(Status[-24:-20], 16))
			Hours1               =Resp[3]#str(int(Status[-28:-24], 16))
			Hours2               =Resp[4]#str(int(Status[-32:-28], 16))
			
			if TransmissionState == 0:
				Estado=0
				return_value='TransmissionState: Reserved\n'
			elif TransmissionState == 1:
				Estado=1
				return_value='TransmissionState: Tx Acceptance\n'
			elif TransmissionState == 2:
				Estado=2
				return_value='TransmissionState: Waiting to transmit\n'
#				Start=True
			elif TransmissionState == 3:
				Estado=0
				return_value='TransmissionState: Transmitting\n'
#				Start=True
#				Warning=True
			elif TransmissionState == 4:
				Estado=0
				return_value='TransmissionState: Transmission complete\n'
			
			TimeTx=Hours1 + Hours2 + ":" + Minutes1 + Minutes2
			
			return (TransmissionState, TimeTx)
	def MTTimingV2(self, Resp):
		"""MT Report Transmitter status 7.9.2.10, 5.8.8"""
		if len(Resp) == 0:
			return "ERROR Resp: Todos los valores son ceros!"
		else:
			Status=Resp[3:11] #Status mide 8 bits
			Status = self.Str32ToBin(Status)
			TransmissionState    =int(Status[ -3:   ], 2)
			Minutes1             =Resp[5]#str(int(Status[-20:-16], 16))
			Minutes2             =Resp[6]#str(int(Status[-24:-20], 16))
			Hours1               =Resp[3]#str(int(Status[-28:-24], 16))
			Hours2               =Resp[4]#str(int(Status[-32:-28], 16))
			msgCola=Resp[7]
			if TransmissionState == 0:
				Estado=0
				return_value='TransmissionState: Reserved\n'
			elif TransmissionState == 1:
				Estado=1
				return_value='TransmissionState: Tx Acceptance\n'
			elif TransmissionState == 2:
				Estado=2
				return_value='TransmissionState: Waiting to transmit\n'
#				Start=True
			elif TransmissionState == 3:
				Estado=0
				return_value='TransmissionState: Transmitting\n'
#				Start=True
#				Warning=True
			elif TransmissionState == 4:
				Estado=0
				return_value='TransmissionState: Transmission complete\n'
			
			TimeTx=Hours1 + Hours2 + ":" + Minutes1 + Minutes2
			
			return (TransmissionState, TimeTx, int(msgCola))
	def MTDecode(self, Resp):
		"""MT Report Transmitter status 7.9.2.10, 5.8.8"""
		if len(Resp) == 0:
			return "ERROR Resp: Todos los valores son ceros!"
		else:
			
			Status=Resp[3:11] #Status mide 8 bits
			
			Status = self.Str32ToBin(Status)
			
			TransmissionState    =int(Status[ -3:   ], 2)
			PLLUnlocked          =int(Status[ -4: -3], 2)
			TransmissionWaiting  =int(Status[ -5: -4], 2)
			TransmitInhibitReason=int(Status[ -8: -5], 2)
			TrafficControl       =int(Status[-10: -8], 2)
			BurstType            =int(Status[-12:-10], 2)
			Reserved			 =int(Status[-16:-12], 2) #ASD
			Minutes1             =Resp[5]#str(int(Status[-20:-16], 16))
			Minutes2             =Resp[6]#str(int(Status[-24:-20], 16))
			Hours1               =Resp[3]#str(int(Status[-28:-24], 16))
			Hours2               =Resp[4]#str(int(Status[-32:-28], 16))
			
			return_value='1850'
			
			if TransmissionState == 0:
				return_value='TransmissionState: Reserved\n'
			elif TransmissionState == 1:
				return_value='TransmissionState: Tx Acceptance\n'
			elif TransmissionState == 2:
				return_value='TransmissionState: Waiting to transmit\n'
			elif TransmissionState == 3:
				return_value='TransmissionState: Transmitting\n'
			elif TransmissionState == 4:
				return_value='TransmissionState: Transmission complete\n'
			
			if PLLUnlocked:
				return_value=return_value + 'PLL Unlocked\n'
			else:
				return_value=return_value + 'PLL LOCKED\n'
			
			if TransmissionWaiting:
				return_value=return_value + 'Transmission Waiting\n'
			else:
				return_value=return_value + 'Not Transmission Waiting\n'
			
			if TransmitInhibitReason == 0:
				return_value=return_value + 'Transmission enabled\n'
			elif TransmitInhibitReason == 1:
				return_value=return_value + 'Tx inhibit by PLL unlock\n'
			elif TransmitInhibitReason == 2:
				return_value=return_value + 'Tx inhibit by Rx condition\n'
			elif TransmitInhibitReason == 3:
				return_value=return_value + 'Tx inhibit by System Message\n'
			elif TransmitInhibitReason == 4:
				return_value=return_value + 'Tx inhibit by Waiting for ACK\n'
			
			return_value=return_value + 'Traffic Control: ' + str(TrafficControl) +'\n'
			
			if BurstType == 0:
				return_value=return_value + 'Burst type: ACK burst\n'
			elif BurstType == 2:
				return_value=return_value + 'Burst type: Long burst\n'
			return_value=return_value + Hours1 + Hours2 + ":" + Minutes1 + Minutes2
			return return_value
	
	
	def PIDecode(self, Resp):
		test_result=Resp[3:7]
		
	def PIReset(self):
		return "PI\r"
	
	def PSDecode(self, Resp):
		"""7.13.4 PS - Scripting Enable/Disable"""
	def PYDecode(self, Resp):
		"""7.13.7  PY – Report MSP Software Information"""
		pass
	def PYWhat(self):
		return "Report MSP Software Information"
	def RRDecode(self, Resp):
		"""7.11.1 RR - Read Register
		RR<module> <register>?\r\n"""
		
		pass
	def RWDecode(self, Resp):
		"""7.11.2 RW - Write Register """
		pass
	#TC: Configure Timer
	def TCDecodeOld(self, Resp):
		"""TC Configure Timer
		DOC: 7.5.1, Timer module register: 5.4"""
		if ((Resp <> '') and (Resp <> '0')):
			try:
				#channel = int((Resp[3:7]), 16)
				#pdb.set_trace()
				timernumber = 'Timer Number: ' + (Resp[3:5])
				configvalue = str(bin(int((Resp[6:14]),16)) )
				configvalue = configvalue.replace('0b','')
				
				TimerNumber = timernumber + '\n'
				while (len(configvalue) <= 32):
					configvalue = '0' + configvalue
					
				ConfigValue = configvalue + '\n'
				
				if (configvalue[-1] == '1'):
					ConfigValue = ConfigValue + 'Timer ENABLE\n'
				else:
					ConfigValue = ConfigValue + 'Timer disable\n'
				if (configvalue[-2] == '1'):
					ConfigValue = ConfigValue + 'REPEAT MODE ON\n'
				else:
					ConfigValue = ConfigValue + 'SINGLE SHOT MODE ON\n'
				if (configvalue[-3] == '1'):
					ConfigValue = ConfigValue + 'Time of day mode\n'
				else:
					ConfigValue = ConfigValue + 'INTERVAL mode\n'

				ConfigValue = ConfigValue + 'OPERATION NUMBER: \n' + configvalue[-8:-3] + '\n'
				#pdb.set_trace()
				TimerTrigger = str(int(configvalue[-32:-8],2)) + '\n'

				ConfigValue = ConfigValue + 'TIMERTRIGGERVALUE DEC: ' + TimerTrigger + 'TIMERTRIGGERVALUE BIN: ' + configvalue[-32:-8] + '\n'

				return TimerNumber + ConfigValue
			except:
				return 'ERROR Timer config value' + Resp
		else:
			return Resp
	def TVDecode(self, Resp):
		"""TV - Get Current Timer Value
		DOC: 7.5.8"""
		if ((Resp <> '') and (Resp <> '0')):
			try:
				timernumber = Resp[3:5]
				timervalue = int((Resp[6:14]),16)
				
				ret={'1 Number':timernumber, '2 Value':timervalue}	
				return ret
				
			except:
				return -1
		else:
			return

	
	#TV: Current Timer Value R
	
	def TVDecodeOld(self, Resp):
		"""TV - Get Current Timer Value
		DOC: 7.5.8"""
		if ((Resp <> '') and (Resp <> '0')):
			try:
				#pdb.set_trace()
				#channel = int((Resp[3:7]), 16)
				#pdb.set_trace()
				timernumber = 'Timer Number: ' + (Resp[3:5])
				timervalue = str(bin(int((Resp[6:14]),16)) )
				timervalue = timervalue.replace('0b','')
				
				TimerNumber = timernumber + '\n'
				
				timervalue = int(timervalue, 2)
				
				ret = TimerNumber + 'Timer ' + Resp[3:5] + ': ' + str(timervalue) + '\n'
				return ret
				
			except:
				return 'ERROR Timer count value: ' + Resp
		else:
			return

	#TT: Report Transmitter Status
	def TTDecode(self, Resp):
		"""TT - Get Current Time and Date
		FORMATO "hh:mm:ss dd/mm/yyyy"
		DOC: 7.5.7 7.14.14"""
		try:
			return Resp[3:22]
		except:
			return 'ERROR'
	def TTWhat(self):
		return "Get Current Time And Date (UTC)"
	#Decofidica coordenada de posicion
	def DecodePos(self, lat):
		"""Decode position from latitud value"""
		try:
			Temp = int(lat, 16)
			Temp = str(bin(Temp))
			Temp = Temp.replace('0b', '')
			if Temp[0] == 0:
				sign = '+'
			else:
				sign = '-'
			Deg = str(int(Temp[1:9],2))
			Min = str(int(Temp[9:15],2))
			Sec = str(int(Temp[15:21],2))
			HunSec = str(int(Temp[21:28],2))
			Resp = sign + Deg + ' ' + Min + ' '+ Sec+' ' +HunSec
		except:
			Resp = 'Error posicion'
		return Resp
		
if __name__ == '__main__':
#	TestKernel(0)
#	TestKernel(1)
#	TestKernel(2)
#	TestKernel(3)
	TestKernel(4)
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	

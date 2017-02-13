from tkinter import *
from threading import Thread
#from PIL import Image
import RPi.GPIO as GPIO
import time

class StopWatch(Frame):
	""" Implements a stop watch frame widget. """                                                                
	def __init__(self, parent=None, **kw):        
		Frame.__init__(self, parent, kw)
		global LapRace
		self.config(bg=colBg2)
		self._start = 0.0        
		self._elapsedtime = 0.0
		self._running = 0
		self.timestr = StringVar()
		self.lapstr = StringVar()
		self.lapSplit = StringVar()
		self.bestLap = StringVar()
		self.bestTime = 0
		self.e = 0
		self.m = 0
		self.makeWidgets()
		self.laps = []
		self.lapmod2 = 0
		self.today = time.strftime("%d %b %Y %H-%M-%S", time.localtime())
	
	def gpioTrigger(self):
		if (len(self.laps)+1 == int(LapRace.get())): # Finish Race if last lap
			self.Finish()
		else:
			self.Lap()

	def makeWidgets(self):		
		l2 = Label(self, textvariable=self.lapstr)
		self.lapstr.set('Lap: 0 / 0')
		l2.config(fg=colFg2, bg=colBg2, font=("Roboto 34 bold"))
		l2.pack(fill=X, expand=NO, pady=0, padx=0)
		
		self.l = Label(self, textvariable=self.timestr)
		self.l.config(fg=colFg2, bg=colBg2, font=("Roboto 100 bold"))
		self._setTime(self._elapsedtime)
		self.l.pack(fill=X, expand=NO, pady=0, padx=0)
		
		frm = Frame(self)
		frm.config(bg=colBg2)
		frm.pack(fill=X, expand=1, pady=(0,48))
		
		self.spt = Label(frm, textvariable=self.lapSplit, anchor=W)
		self.lapSplit.set('Split: ')
		self.spt.config(fg=colFg1, bg=colBg2, font=("Roboto 32 bold"))
		self.spt.pack(pady=0, padx=0, fill=X, expand=1, side=LEFT)
				
		self.best = Label(frm, textvariable=self.bestLap, anchor=E)
		self.bestLap.set('Best: ')
		self.best.config(fg=colFg1, bg=colBg2, font=("Roboto 32 bold"))
		self.best.pack(pady=0, padx=0, fill=X, expand=1, side=RIGHT)

		l3 = Label(self, text='- Times -')
		l3.config(fg=colFg1, bg=colBg1, font=('Roboto 24'))
		l3.pack(fill=X, expand=NO, pady=0, padx=0)
		
		Button(self, text='Finish Line', command=self.Finish, font=('Roboto 24'), bg=colFg1, fg=colBg1, highlightthickness=0, relief=FLAT).pack(side=BOTTOM, fill=X, expand=1, padx=0, pady=0)
		Button(self, text='Lap', command=self.Lap, font=('Roboto 24'), bg=colFg1, fg=colBg1, highlightthickness=0, relief=FLAT).pack(side=BOTTOM, fill=X, expand=1, padx=0, pady=10)
		
		scrollbar = Scrollbar(self, orient=VERTICAL, bg=colScroll, highlightthickness=0, relief=FLAT, troughcolor=colBg1, bd=0 )
		self.m = Listbox(self,selectmode=EXTENDED, height = 10, yscrollcommand=scrollbar.set)
		self.m.config(bd='0', fg=colFg1, bg=colBg1, highlightthickness=0, font=('Courier 30'))
		self.m.pack(side=LEFT, fill=BOTH, expand=1, pady=0, padx=0)
		scrollbar.config(command=self.m.yview)
		scrollbar.pack(side=RIGHT, fill=Y)

	def _update(self): 
		""" Update the label with elapsed time. """
		self._elapsedtime = time.time() - self._start
		self._setTime(self._elapsedtime)
		self._timer = self.after(25, self._update)

	def _setTime(self, elap):
		""" Set the time string to Minutes:Seconds:Thousandths """
		minutes = int(elap/60)
		seconds = int(elap - minutes*60.0)
		hseconds = int(((elap - minutes*60.0 - seconds)*10000)/10)                
		self.timestr.set('%02d:%02d:%03d' % (minutes, seconds, hseconds))

	def _setLapTime(self, elap):
		""" Set the time string to Minutes:Seconds:Thousandths """
		minutes = int(elap/60)
		seconds = int(elap - minutes*60.0)
		hseconds = int((elap - minutes*60.0 - seconds)*1000)           
		return '%02d:%02d:%02d' % (minutes, seconds, hseconds)
		
	def _bestLap(self, elap):
		if ((elap < self.bestTime) or (self.bestTime == 0)):
			self.bestTime = elap
			self.bestLap.set('Best: '+str(float("{0:.3f}".format(elap))))
			self.best.config(fg=colPurple)
			for i in range(3):
				time.sleep(0.3)
				self.best.config(fg=colFg1)
				time.sleep(0.3)
				self.best.config(fg=colPurple)
			

	def Start(self):                                                     
		""" Start the stopwatch, ignore if running. """
		if not self._running:            
			self._start = time.time() - self._elapsedtime
			self.lapstr.set('Lap: {} / {}'.format(len(self.laps), int(LapRace.get())))
			self._update()
			self._running = 1        
    
	def Stop(self):
		""" Stop the stopwatch, ignore if stopped. """
		if self._running:
			self.after_cancel(self._timer)            
			self._elapsedtime = time.time() - self._start    
			self._setTime(self._elapsedtime)
			self._running = 0

	def Reset(self):
		""" Reset the stopwatch. """
		self._start = time.time()
		self._elapsedtime = 0.0
		self.laps = []
		self.m.delete(0,END)
		self.lapmod2 = self._elapsedtime
		self._setTime(self._elapsedtime)
		self.lapSplit.set('Split: ')
		self.bestLap.set('Best: ')
		self.l.config(fg=colFg1)
		self.spt.config(fg=colFg1)
		self.best.config(fg=colFg1)
		self.bestTime = 0

		
	def Finish(self):
		""" Finish race for this lane """
		self.Lap()
		self.Stop()
		td = Thread(target=playBuzz, args=())
		td.start()

	def Lap(self):
		'''Makes a lap, only if started'''
		split = Thread(target=splitTimes, args=())
		tempo = self._elapsedtime - self.lapmod2
		if (self._running):
			self.laps.append([self._setLapTime(tempo),float("{0:.3f}".format(tempo))])
			self.m.insert(END, self.laps[-1][0])
			self.m.yview_moveto(1)
			self.lapmod2 = self._elapsedtime
			# Update lap counter       
			self.lapstr.set('Lap: {} / {}'.format(len(self.laps), int(LapRace.get())))
			split.start()
			bestCheck = Thread(target=self._bestLap, args=(float("{0:.3f}".format(tempo)),))
			bestCheck.start()
	
class raceWidgets(Frame):
	def __init__(self, parent=None, **kw):        
		Frame.__init__(self, parent, kw)
		global LapRace
		self.configure(bg=colBg1)
		LapRace = StringVar()
		l = Label(self, text='Set Number of Laps')
		l.config(bg=colBg1, fg=colFg1, font="Roboto 30")
		l.pack(expand=1)
		LapRace.set('10')
		et = Entry(self, textvariable=LapRace, width=5, justify='center')
		et.config(bd='0', bg=colBg2 ,fg=colFg2, highlightthickness=0, font="Roboto 34 bold")
		et.pack(expand=1, pady=8)
		
class Fullscreen_Window:
	def __init__(self):
		self.tk = Tk()
		self.tk.attributes('-zoomed', True)
		self.frame = Frame(self.tk)
		self.frame.pack()
		self.state = True
		self.tk.attributes("-fullscreen", self.state)
		self.tk.bind("<F11>", self.toggle_fullscreen)
		self.tk.bind("<Escape>", self.end_fullscreen)
		
	def toggle_fullscreen(self, event=None):
		self.state = not self.state
		self.tk.attributes("-fullscreen", self.state)
		return "break"
		
	def end_fullscreen(self, event=None):
		self.state = False
		self.tk.attributes("-fullscreen", False)
		
					
		
def triggerLap(channel):
	if ((GPIO.input(channel)) and (channel == pins[0])):
		sw.gpioTrigger()
	elif ((GPIO.input(channel)) and (channel == pins[1])):
		sw2.gpioTrigger()
	
def StartRace():
	sw.Start()
	sw2.Start()
	
def StopRace():
	sw.Stop()
	sw2.Stop()
	
def ResetRace():
	sw.Reset()
	sw2.Reset()
	
def RaceLights():
	photo = PhotoImage(file="imgs/light_off.png")
	photo2 = PhotoImage(file="imgs/light_red.png")
	photo3 = PhotoImage(file="imgs/light_green.png")
	lights = []
	coords = [[370,240],[610,240],[850,240],[1090,240],[1330,240]]

	cv = Canvas(root.tk, width=1920, height=1080, bg=colBg1, highlightthickness=0)
	cv.place(x=0, y=0)

	for i in range(5):
		lights.append(Label(root.tk, image=photo, bg=colBg1))
		lights[i].image = photo
		lights[i].place(x=coords[i][0], y=coords[i][1])
	
	lights.append(cv)
	
	root.tk.update()
	time.sleep(1)
	
	for i in range(5):
		time.sleep(1)
		lights[i].config(image = photo2)
		lights[i].image = photo2
		root.tk.update()
		
	for i in range(5):
		lights[i].config(image = photo3)
		lights[i].image = photo3
	
	time.sleep(1)
	root.tk.update()
	
	lo = Thread(target=LightsOut, args=([lights]))
	lo.start()
	
	StartRace()
	
def LightsOut(lights):
	time.sleep(1)
	for i in range(5):
		lights[i].destroy()
	lights[5].destroy()
	root.tk.update()
		
def playBuzz():
	GPIO.setup(pins[2], GPIO.OUT)
	pwm = GPIO.PWM(pins[2], 1000)
	pwm.start(20)
	time.sleep(0.1)
	pwm.ChangeDutyCycle(100) #off
	time.sleep(0.2)
	pwm.ChangeDutyCycle(20) #on
	pwm.ChangeFrequency(500)
	time.sleep(0.1)
	pwm.ChangeDutyCycle(100) #off
	time.sleep(0.1)
	pwm.ChangeDutyCycle(20) #on
	time.sleep(0.2)
	pwm.ChangeDutyCycle(100) #off
	time.sleep(0.1)
	pwm.ChangeDutyCycle(20) #on
	pwm.ChangeFrequency(1000)
	time.sleep(0.2)
	pwm.ChangeDutyCycle(100) #off
	time.sleep(0.1)
	pwm.ChangeDutyCycle(20) #on
	pwm.ChangeFrequency(1500)
	time.sleep(0.2)
	pwm.ChangeDutyCycle(100) #off
	time.sleep(0.2)
	pwm.ChangeDutyCycle(20) #on
	pwm.ChangeFrequency(2200)
	time.sleep(1)
	pwm.ChangeDutyCycle(100)
	GPIO.setup(pins[2], GPIO.IN)
	
def splitTimes():
	c1 = 0
	c2 = 0
	sameDiff = 0
	extraDiff = 0
	totalDiff = 0
	if (len(sw.laps) > len(sw2.laps)):  # Lane 1 in the lead
		sameLaps = len(sw2.laps)
		extraLaps = len(sw.laps) - len(sw2.laps)
		sameArr = [sw.laps[:sameLaps], sw2.laps[:sameLaps]]
		extraArr = sw.laps[-extraLaps:]
		for i in range(len(sameArr[0])):
			c1 += sameArr[0][i][1]
			c2 += sameArr[1][i][1]
			sameDiff = c2 - c1
		for i in range(len(extraArr)):
			extraDiff += extraArr[i][1]
		totalDiff = abs(sameDiff + extraDiff)
		sw.lapSplit.set('Split: -'+str(float("{0:.3f}".format(totalDiff))))
		sw.spt.config(fg=colGreen)
		sw.l.config(fg=colGreen)
		sw2.lapSplit.set('Split: +'+str(float("{0:.3f}".format(totalDiff))))
		sw2.spt.config(fg=colRed)
		sw2.l.config(fg=colRed)
	elif (len(sw.laps) < len(sw2.laps)):  # Lane 2 in the lead
		sameLaps = len(sw.laps)
		extraLaps = len(sw2.laps) - len(sw.laps)
		sameArr = [sw2.laps[:sameLaps], sw.laps[:sameLaps]]
		extraArr = sw2.laps[-extraLaps:]
		for i in range(len(sameArr[0])):
			c1 += sameArr[0][i][1]
			c2 += sameArr[1][i][1]
			sameDiff = c2 - c1
		for i in range(len(extraArr)):
			extraDiff += extraArr[i][1]
		totalDiff = abs(sameDiff + extraDiff)
		sw2.lapSplit.set('Split: -'+str(float("{0:.3f}".format(totalDiff))))
		sw2.spt.config(fg=colGreen)
		sw2.l.config(fg=colGreen)
		sw.lapSplit.set('Split: +'+str(float("{0:.3f}".format(totalDiff))))
		sw.spt.config(fg=colRed)
		sw.l.config(fg=colRed)
	else:  # equal Laps - just need the total same difference
		sameLaps = len(sw.laps)
		sameArr = [sw2.laps[:sameLaps], sw.laps[:sameLaps]]
		for i in range(len(sameArr[0])):
			c1 += sameArr[0][i][1]
			c2 += sameArr[1][i][1]
			totalDiff = c2 - c1
		if (totalDiff > 0):
			sw.lapSplit.set('Split: +'+str(float("{0:.3f}".format(abs(totalDiff)))))
			sw.spt.config(fg=colRed)
			sw.l.config(fg=colRed)
			sw2.lapSplit.set('Split: -'+str(float("{0:.3f}".format(abs(totalDiff)))))
			sw2.spt.config(fg=colGreen)
			sw2.l.config(fg=colGreen)
		else:
			sw2.lapSplit.set('Split: +'+str(float("{0:.3f}".format(abs(totalDiff)))))
			sw2.spt.config(fg=colRed)
			sw2.l.config(fg=colRed)
			sw.lapSplit.set('Split: -'+str(float("{0:.3f}".format(abs(totalDiff)))))
			sw.spt.config(fg=colGreen)
			sw.l.config(fg=colGreen)
				
		
				
def main():
	global root, sw, sw2, inputID, pins, LapRace, pwm, colBg1, colBg2, colFg1, colFg2, colGreen, colRed, colPurple, colScroll
	colBg1 = '#04080c'
	colBg2 = '#101e28'
	colFg1 = '#a1aeb4'
	colFg2 = '#c8d0d4'
	colGreen = '#6ca32c' 
	colRed = '#f34820'
	colPurple = '#e051d4'
	colScroll = '#273a46'	
	pins = [21,23,18] # lane1, lane2, buzzer
	
	GPIO.setmode(GPIO.BCM)
	
	root = Fullscreen_Window()
	root.tk.geometry("800x470")
	root.tk.configure(bg='#04080c')
	root.tk.title('Scalextric Race Control')
	
	bkgc = Canvas(root.tk, width=1920, height=392, bg=colBg2, highlightthickness=0)
	bkgc.place(x=0, y=0)
	
	sw = StopWatch(root.tk)
	sw2 = StopWatch(root.tk)
	sw.pack(side=LEFT, padx=30)
	sw2.pack(side=RIGHT, padx=30)

	Button(root.tk, text='Quit', command=root.tk.quit, font=('Roboto 30'), bg=colFg1, fg=colBg1, highlightthickness=0, relief=FLAT).pack(side=BOTTOM, anchor=S, fill=X, padx=48, pady=(5,72))
	Button(root.tk, text='Reset', command=ResetRace, font=('Roboto 30'), bg=colFg1, fg=colBg1, highlightthickness=0, relief=FLAT).pack(side=BOTTOM, anchor=S, fill=X, padx=48, pady=5)
	Button(root.tk, text='Stop', command=StopRace, font=('Roboto 30'), bg=colFg1, fg=colBg1, highlightthickness=0, relief=FLAT).pack(side=BOTTOM, anchor=S, fill=X, padx=48, pady=5) 
	Button(root.tk, text='Start', command=StartRace, font=('Roboto 44 bold'), bg=colGreen, fg='white', highlightthickness=0, relief=FLAT).pack(side=BOTTOM, anchor=S, fill=X, padx=48, pady=5)
	Button(root.tk, text='Start Lights', command=RaceLights, font=('Roboto 44 bold'), bg=colGreen, fg='white', highlightthickness=0, relief=FLAT).pack(side=BOTTOM, anchor=S, fill=X, padx=48, pady=5)

	raceSetup = raceWidgets(root.tk)
	raceSetup.pack(side=BOTTOM, anchor=S, fill=X, pady=20)
	
	GPIO.setup(pins[0], GPIO.IN)
	GPIO.add_event_detect(pins[0], GPIO.RISING, callback=triggerLap, bouncetime=1000)
	GPIO.setup(pins[1], GPIO.IN)
	GPIO.add_event_detect(pins[1], GPIO.RISING, callback=triggerLap, bouncetime=1000) 

	try:
		root.tk.mainloop()
	finally:
		GPIO.cleanup()
	

if __name__ == '__main__':
	main()

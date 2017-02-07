from tkinter import *
from threading import Thread
from PIL import Image
import RPi.GPIO as GPIO
import time

class StopWatch(Frame):
	""" Implements a stop watch frame widget. """                                                                
	def __init__(self, parent=None, **kw):        
		Frame.__init__(self, parent, kw)
		global LapRace
		self.configure(bg='white')
		self._start = 0.0        
		self._elapsedtime = 0.0
		self._running = 0
		self.timestr = StringVar()
		self.lapstr = StringVar()
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
		l = Label(self, textvariable=self.timestr)
		l.config(fg="dark green", bg='white', font=("Roboto 36 bold"))
		self._setTime(self._elapsedtime)
		l.pack(fill=X, expand=NO, pady=(0,2), padx=2)
		
		l2 = Label(self, textvariable=self.lapstr)
		self.lapstr.set('Lap: 0 / 0')
		l2.config(fg="gray10", bg='white', font=("Roboto 14 bold"))
		l2.pack(fill=X, expand=NO, pady=2, padx=2)

		l3 = Label(self, text='- Times -')
		l3.config(bg='white', font=('Roboto 10'))
		l3.pack(fill=X, expand=NO, pady=2, padx=2)
		
		Button(self, text='Finish Line', command=self.Finish, font=('Roboto 10')).pack(side=BOTTOM, fill=X, expand=1)
		Button(self, text='Lap', command=self.Lap, font=('Roboto 10')).pack(side=BOTTOM, fill=X, expand=1, pady=(10,0))
		
		scrollbar = Scrollbar(self, orient=VERTICAL)
		self.m = Listbox(self,selectmode=EXTENDED, height = 10, yscrollcommand=scrollbar.set)
		self.m.config(bd='0', bg='gray90', font=('Courier 12'))
		self.m.pack(side=LEFT, fill=BOTH, expand=1, pady=0, padx=(0,5))
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
		print(elap)
		minutes = int(elap/60)
		seconds = int(elap - minutes*60.0)
		hseconds = int((elap - minutes*60.0 - seconds)*1000)           
		return '%02d:%02d:%02d' % (minutes, seconds, hseconds)

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

		
	def Finish(self):
		""" Finish race for this lane """
		self.Lap()
		self.Stop()
		td = Thread(target=playBuzz, args=())
		td.start()

	def Lap(self):
		'''Makes a lap, only if started'''
		tempo = self._elapsedtime - self.lapmod2
		if (self._running):
			self.laps.append(self._setLapTime(tempo))
			self.m.insert(END, self.laps[-1])
			self.m.yview_moveto(1)
			self.lapmod2 = self._elapsedtime
			# Update lap counter       
			self.lapstr.set('Lap: {} / {}'.format(len(self.laps), int(LapRace.get())))
	
class raceWidgets(Frame):
	def __init__(self, parent=None, **kw):        
		Frame.__init__(self, parent, kw)
		global LapRace
		self.configure(bg='white')
		LapRace = StringVar()
		l = Label(self, text='Set Number of Laps')
		l.config(bg='white', fg='gray25', font="Roboto 12")
		l.pack(expand=1)
		LapRace.set('10')
		et = Entry(self, textvariable=LapRace, width=5, justify='center')
		et.config(bd='0', fg='gray25', font="Roboto 14 bold")
		et.pack(expand=1)
		
class Fullscreen_Window:
	def __init__(self):
		self.tk = Tk()
		#self.tk.attributes('-zoomed', True)
		self.frame = Frame(self.tk)
		self.frame.pack()
		self.state = False
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
	print("Pin: "+str(channel))
	if ((GPIO.input(channel)) and (channel == pins[0])):
		sw.gpioTrigger()
	elif ((GPIO.input(channel)) and (channel == pins[1])):
		sw2.gpioTrigger()
	
def StartRace():
	sw.Start()
	sw2.Start()
	print(LapRace.get())
	
def StopRace():
	sw.Stop()
	sw2.Stop()
	
def ResetRace():
	sw.Reset()
	sw2.Reset()
	
def RaceLights():
	cv = Canvas(root.tk, width=92, height=250)
	photo = PhotoImage(file="imgs/light_off.png")
	photo2 = PhotoImage(file="imgs/light_red.png")
	photo3 = PhotoImage(file="imgs/light_green.png")
	root.tk.lightoff = photo
	#cv.create_image(0,0, image=photo, anchor='nw')
	#cv.place(x=50, y=50)
	light1 = Label(root.tk, image=photo)
	light1.image = photo
	light1.place(x=154, y=100)
	
	light2 = Label(root.tk, image=photo)
	light2.image = photo
	light2.place(x=254, y=100)
	
	light3 = Label(root.tk, image=photo)
	light3.image = photo
	light3.place(x=354, y=100)
	
	light4 = Label(root.tk, image=photo)
	light4.image = photo
	light4.place(x=454, y=100)
	
	light5 = Label(root.tk, image=photo)
	light5.image = photo
	light5.place(x=554, y=100)
	
	root.tk.update()
	
	time.sleep(1)
	light1.config(image = photo2)
	light1.image = photo2
	root.tk.update()
	time.sleep(1)
	light2.config(image = photo2)
	light2.image = photo2
	root.tk.update()
	time.sleep(1)
	light3.config(image = photo2)
	light3.image = photo2
	root.tk.update()
	time.sleep(1)
	light4.config(image = photo2)
	light4.image = photo2
	root.tk.update()
	time.sleep(1)
	light5.config(image = photo2)
	light5.image = photo2
	root.tk.update()
		
def playBuzz():
	print('buzz...')
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
				
def main():
	global root, sw, sw2, inputID, pins, LapRace, pwm
	
	GPIO.setmode(GPIO.BCM)
	
	root = Fullscreen_Window()
	root.tk.geometry("800x470")
	root.tk.configure(bg='white')
	root.tk.title('Scalextric Race Control')
	
	pins = [21,23,18] # lane1, lane2, buzzer
	sw = StopWatch(root.tk)
	sw2 = StopWatch(root.tk)
	sw.pack(side=LEFT, padx=30)
	sw2.pack(side=RIGHT, padx=30)

	Button(root.tk, text='Quit', command=root.tk.quit, font=('Roboto 12')).pack(side=BOTTOM, anchor=S, fill=X, padx=40, pady=(2,30))
	Button(root.tk, text='Reset', command=ResetRace, font=('Roboto 12')).pack(side=BOTTOM, anchor=S, fill=X, padx=40, pady=2)
	Button(root.tk, text='Stop', command=StopRace, font=('Roboto 12')).pack(side=BOTTOM, anchor=S, fill=X, padx=40, pady=2) 
	## Button(root.tk, text='Start', command=StartRace, font=('Roboto 18 bold')).pack(side=BOTTOM, anchor=S, fill=X, padx=40, pady=2)
	Button(root.tk, text='Start', command=RaceLights, font=('Roboto 18 bold')).pack(side=BOTTOM, anchor=S, fill=X, padx=40, pady=2)

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

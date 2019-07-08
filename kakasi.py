import sys
import requests
import json
import time
import os
from pykakasi import *
from gtts import gTTS
from io import BytesIO
from tkinter import *

class Jta:
	"""Japanese to Romanji"""
	kakasi = kakasi()
	conv = None
	
	def genConv(self):
		self.conv = self.kakasi.getConverter()

	def __init__(self):
		self.kakasi.setMode("H", "a")
		self.kakasi.setMode("K", "a")
		self.kakasi.setMode("J", "a")
		self.kakasi.setMode("s", True)
		self.kakasi.setMode("C", True)
		self.genConv()

	def do(self, str):
		return self.conv.do(str)


class Greper:
	"""Lyric Greper"""
	id = None
	url = "http://music.163.com/api/song/lyric"
	headers = {
    	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
    	AppleWebKit/537.36 (KHTML, like Gecko) \
    	Chrome/71.0.3578.98 Safari/537.36',
	}

	def __init__(self, id):
		self.id = id

	def do(self):
		ret = {}
		resp = self.post()
		data = json.loads(resp.text)
		if data['code'] == 200:
			"""Successful"""
			lyrics = data['lrc']['lyric'].split("\n")
			ret['code']=200
			ret['lyrics']=lyrics
		else:
			"""Failed"""
			ret['code']=500
		return ret

	def post(self):
		sess = requests.Session()
		getUrl = self.url+"?id="+self.id+"&lv=1&kv=1&tv=-1"
		resp = sess.get(url=getUrl, headers=self.headers)
		return resp

	def regexHandler(self, data):
		print("regex", data)


class Tts:
	"""tts"""
	Str = None
	# mp3_fp = BytesIO()
	
	def __init__(self, str):
		self.Str = str

	def play(self):
		tts = gTTS(self.Str, lang="ja")
		tts.save("res.mp3")
		os.system("play res.mp3")
		os.system("rm res.mp3")
		#tts.write_to_fp(self.mp3_fp)


class GUI(Frame):
	"""GUI"""
	loading = False
	listData = None

	def __init__(self, master=None):
		Frame.__init__(self, master)
		self.pack()
		self.createWidgets()

	def createWidgets(self):
		# Widget Setting
		self.master.title('Kakasi')
		self.master.geometry('450x280')
		# Init Frames
		self.top = Frame(self)
		self.main = Frame(self)
		# TopFrame ID Label
		self.idLabel = Label(self.top, text='Song ID:')
		self.idLabel.pack(padx=3, pady=7, side=LEFT)
		# TopFrame ID Entry
		self.idEntry = Entry(self.top)
		self.idEntry.bind("<Return>", self.search)
		self.idEntry.pack(padx=2, pady=7, side=LEFT)
		# TopFrame do Button
		self.doButton = Button(self.top, text='Do', command=self.search)
		self.doButton.pack(padx=13, pady=7, side=LEFT)
		# TopFrame quit Button
		self.quitButton = Button(self.top, text='Quit', command=self.quit)
		self.quitButton.pack(padx=5, pady=7, side=LEFT)
		# MainFrame scrollBar
		self.scroll = Scrollbar(self.main)
		self.scroll.pack(side=RIGHT, fill=Y)
		# MainFrame lyric Listbox
		self.listbox = Listbox(self.main, yscrollcommand=self.scroll.set)
		self.listbox.bind('<Double-Button-1>', self.play_item)
		self.listbox.bind('<space>', self.change_ja)
		self.listbox.pack(side=TOP, fill=BOTH)
		# Frames pack
		self.top.pack()
		self.main.pack(side=TOP, pady=15, fill=BOTH)

	def search(self, event=None):
		if self.loading:
			return
		self.loading = True
		greper = Greper(str(self.idEntry.get()))
		result = greper.do()
		self.listData = result['lyrics']
		if result['code']==200:
			# Successfully
			for item in result['lyrics']:
				self.listbox.insert(END, str(item))
		else:
			# Faild
			pass
		self.loading = False

	def play_item(self, event):
		item = self.listbox.curselection()
		Tts(self.listData[item[0]]).play()

	def change_ja(self, event):
		jta = Jta()
		item = self.listbox.curselection()[0]
		curStr = self.listbox.get(item)
		if curStr == self.listData[item]:
			self.listbox.insert(item, jta.do(curStr))
			self.listbox.delete(item+1)
		else:
			self.listbox.insert(item, self.listData[item])
			self.listbox.delete(item+1)
			# self.listbox.set
		# if self.listData


class CLI:
	"""CLI"""
	flag = False

	def do(self):
		jta = Jta()
		self.flag = False
		for item in sys.argv:
		    if not self.flag:
		        self.flag = True
		    else:
		        print(jta.do(item))
		        Tts(item).play()


if __name__ == '__main__':
	paramLen = len(sys.argv)
	if paramLen > 1:
		"""CLI"""
		cli = CLI()
		cli.do()
	else:
		"""GUI"""
		app = GUI()
		app.mainloop()


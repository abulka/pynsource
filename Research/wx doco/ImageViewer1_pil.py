import wx, os, string, sys
from PIL import Image

# Scroll wheel and +/- do zoom in/out. f toggles full screen. r rotates.
# m changes PIL mode from low quality (fast) to high quality (slow).
# Images under 1000x1000 are automatically on high quality.
# Middle button down while dragging moves image around, as do arrow
# keys (if image is bigger than window).
# Left and right mouse buttons are next and previous image.

# There is no functionality to load an image. When an executeable is made, the
# viewer is started by opening an image with it. 
# To run this file from command line, comment out line 55 and uncomment 
# line 54, then do "viewer.py sampleImage"

# There are several lines that are Windows specific. They (probably) all have
# to do with paths, i.e, "/" vs "\". 



class ImageFrame(wx.Frame):
    def __init__(self):
    	wx.Frame.__init__(self,None,title = "viewer")
    	self.Centre()
    	self.Size = (450,450)
    	self.imageBox = wx.Window(self)
    	self.vbox = wx.BoxSizer(wx.VERTICAL)
    	self.CreateStatusBar(5) 
    	self.SetStatusWidths([-1, 70, 50, 50, 30])
    	self.cursor = wx.StockCursor(wx.CURSOR_ARROW)
    	self.moveCursor = wx.StockCursor(wx.CURSOR_SIZING)
    	self.vbox.Add(self.imageBox,proportion=1,flag = wx.EXPAND)
    	self.SetSizer(self.vbox)
    	self.Show()
    	self.sbm = 0
    	self.sbmList = []
    	self.name = ''
    	self.url = ''
    	self.dir = ''
    	self.factor = 1.0
    	self.rotation = 0
    	self.width = 0
    	self.height = 0
    	self.count = 0
    	self.size = 0
    	self.numOfPics = 0
    	self.mc = False
    	self.fs = False
    	self.mode = 0
    	self.SetStatusText(str(self.mode), 4)
    	if len(sys.argv) == 2:
    		#self.url = os.getcwd() + '\\' + sys.argv[1]
    		self.url = sys.argv[1]
    		#self.name = self.url.split('\\')[len(self.url.split('\\'))-1]
    		#self.dir = self.url.replace('\\' + self.name,'')
    		#self.loadDirectory(self.dir)
    		self.processPicture()
    	self.imageBox.Bind(wx.EVT_SIZE, lambda evt: self.rescale(evt,1))
    	self.imageBox.Bind(wx.EVT_MOUSEWHEEL,self.zoom)
    	self.imageBox.Bind(wx.EVT_KEY_DOWN, self.keyEvent)
    	self.imageBox.Bind(wx.EVT_MIDDLE_UP, self.endDrag)
    	self.imageBox.SetBackgroundColour((0,0,0,0))
    	self.imageBox.Bind(wx.EVT_LEFT_DOWN, self.__next__)
    	self.imageBox.Bind(wx.EVT_RIGHT_DOWN, self.prev)

    def nameFromUrl(self,url):
    	name = url.split('\\')
    	name = name[len(name)-1]
    	return name

    def processPicture(self, factor = 0):

    	img = Image.open(self.url)
    	self.width = img.size[0]
    	self.height = img.size[1]
    	ogHeight = self.height
    	ogWidth = self.width
    	xWin = self.imageBox.Size[0]
    	yWin = self.imageBox.Size[1]
    	winRatio = 1.0*xWin/yWin
    	imgRatio = 1.0*self.width/self.height

    	self.factor = factor*self.factor
    	if factor == 0:
    		self.factor = 1
    	mode = 0
    	if (ogWidth <=1000 and ogHeight <= 1000) or self.mode == 1:
    		mode = 1

    	if imgRatio >= winRatio: #match widths
    		self.width = self.factor*xWin
    		self.height = self.factor*xWin/imgRatio
    		img = img.resize((int(self.width),int(self.height)),mode)
    	else:	#match heights
    		self.height = self.factor*yWin
    		self.width = self.factor*yWin*imgRatio
    		img = img.resize((int(self.width),int(self.height)),mode)

    	label = str(int(100*self.width/ogWidth))
    	name = self.nameFromUrl(self.url)
    	#index = self.sbmList.index(name)
    	self.SetStatusText(name, 0)
    	self.SetStatusText(str(ogWidth) + 'x' + str(ogHeight), 1)
    	self.SetStatusText(label + '%', 2)
    	#self.SetStatusText(str(index+1) + '/' + str(self.numOfPics), 3)

    	if self.rotation % 360 != 0:
    		img = img.rotate(self.rotation)
    		self.width = img.size[0]
    		self.height = img.size[1]

    	wximg = wx.EmptyImage(img.size[0],img.size[1])
    	wximg.SetData(img.convert("RGB").tostring())
    	wximg.SetAlphaData(img.convert("RGBA").tostring()[3::4])

    	self.showPicture(wximg)

    def showPicture(self,img):
    	bmp = wx.BitmapFromImage(img)
    	x = (self.imageBox.Size[0] - self.width)/2.0
    	y = (self.imageBox.Size[1] - self.height)/2.0
    	tmp = wx.StaticBitmap(self.imageBox,wx.ID_ANY,bmp,(x,y))
    	tmp.Bind(wx.EVT_LEFT_DOWN, self.__next__)
    	tmp.Bind(wx.EVT_RIGHT_DOWN, self.prev)
    	tmp.Bind(wx.EVT_MOTION, self.drag)
    	tmp.Bind(wx.EVT_MIDDLE_UP, self.endDrag)
    	tmp.SetBackgroundColour((180,180,180,180))
    	if self.sbm:
    		self.sbm.Destroy()
    	self.sbm = tmp
    	self.imageBox.Refresh()

    def loadDirectory(self,dir):
    	self.sbmList = []
    	for image in os.listdir(dir):
    		if image.lower().endswith('jpg') or image.lower().endswith('png') or image.lower().endswith('jpeg') or image.lower().endswith('gif') or image.lower().endswith('bmp'):
    			self.sbmList.append(image)
    	self.numOfPics = len(self.sbmList)

    def next(self,event):
    	if self.name in self.sbmList:
    		n = self.sbmList.index(self.name)
    		if n == len(self.sbmList) - 1:
    			n = -1
    		self.name = self.sbmList[n + 1]
    		self.url = self.dir + '\\' + self.name
    		self.rotation = 0
    		self.processPicture()

    def prev(self,event):
    	if self.name in self.sbmList:
    		n = self.sbmList.index(self.name)
    		if n == 0:
    			n = len(self.sbmList)
    		self.name = self.sbmList[n - 1]
    		self.url = self.dir + '\\' + self.name 
    		self.rotation = 0
    		self.processPicture()

    def rescale(self,event,factor):
    	if self.url and self.GetStatusBar(): #close is seen as a size event.
    		self.processPicture(factor)

    def zoom(self,event):
    	factor = 1.25
    	if event.GetWheelRotation() < 0:
    			factor = 0.8
    	self.rescale(event,factor)

    def keyEvent(self,event):
    	code = event.GetKeyCode()
    	if code == 43: #plus
    		self.rescale(event,1.25)
    	elif code == 45: #minus
    		self.rescale(event,0.8)
    	elif code == 82 and self.url: #r
    		self.rotation = self.rotation + 90
    		self.processPicture(1)
    	elif code == 70: #f
    		self.toggleFS()
    	elif (code == 314 or code == 315 or code == 316 or code == 317) and self.sbm:
    		#left, up, right, down
    		self.scroll(code)
    	elif code == 77: #m
    		if self.mode == 0:
    			self.mode = 1
    		else:
    			self.mode = 0
    		self.SetStatusText(str(self.mode), 4)
    		self.processPicture(1)


    def scroll(self,code):
    	boxPos = self.imageBox.GetScreenPositionTuple()
    	imgPos = self.sbm.GetScreenPositionTuple()
    	delta = 20
    	if code == 314 and self.width > self.imageBox.Size[0]:
    		compare = boxPos[0] - imgPos[0]
    		if compare <= delta:
    			delta = max(compare,0)
    		self.imageBox.ScrollWindow(delta,0)
    	if code == 315 and self.height > self.imageBox.Size[1]:
    		compare = boxPos[1] - imgPos[1]
    		if compare <= delta:
    			delta = max(compare,0)
    		self.imageBox.ScrollWindow(0,delta)
    	if code == 316 and self.width > self.imageBox.Size[0]:
    		compare =  imgPos[0] + self.sbm.Size[0] - boxPos[0] - self.imageBox.Size[0]
    		if compare <= delta:
    			delta = max(compare,0)
    		self.imageBox.ScrollWindow(-delta,0)
    	if code == 317 and self.height > self.imageBox.Size[1]:
    		compare =  imgPos[1] + self.sbm.Size[1] - boxPos[1] - self.imageBox.Size[1]
    		if compare <= delta:
    			delta = max(compare,0)
    		self.imageBox.ScrollWindow(0,-delta)

    def drag(self,event):
    	if event.MiddleIsDown():
    		if not self.mc:
    			self.SetCursor(self.moveCursor)
    			self.mc = True
    		boxPos = self.imageBox.GetScreenPositionTuple()
    		imgPos = self.sbm.GetScreenPositionTuple()
    		if self.count == 0:
    			self.x = event.GetX()
    			self.y = event.GetY()
    		self.count = self.count + 1
    		if self.count > 1:
    			deltaX = event.GetX() - self.x
    			deltaY = event.GetY() - self.y
    			if imgPos[0] >= boxPos[0] and deltaX > 0:
    				deltaX = 0
    			if imgPos[0] + self.width <= boxPos[0] + self.imageBox.Size[0] and deltaX < 0:
    				deltaX = 0
    			if imgPos[1] >= boxPos[1] and deltaY > 0:
    				deltaY = 0
    			if imgPos[1] + self.height <= boxPos[1] + self.imageBox.Size[1] and deltaY < 0:
    				deltaY = 0
    			self.imageBox.ScrollWindow(2*deltaX,2*deltaY)
    			self.count = 0

    def endDrag(self,event):
    	self.count = 0
    	self.SetCursor(self.cursor)
    	self.mc = False

    def toggleFS(self):
    	if self.fs:
    		self.ShowFullScreen(False)
    		self.fs = False
    	else:
    		self.ShowFullScreen(True)
    		self.fs = True




app = wx.App(redirect = False)
frame = ImageFrame()
app.MainLoop()
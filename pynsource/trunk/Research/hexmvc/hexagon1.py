
# BOOT WIRING

from hexappmodel import App, ModelA
from hexpersistence import PersistenceMock, PersistenceMock2

#app = App(PersistenceMock()) 
app = App(PersistenceMock2())

# UNIT TEST

app.Load()
print app.modelmgr

a = app.GetA(0)
app.CmdAddInfoToA(a, "once")
print app.modelmgr

app.New()
app.CreateA("once")
app.CreateA("upon a time")
app.Save()
print app.modelmgr

app.New()
print app.modelmgr

app.Load()
print app.modelmgr


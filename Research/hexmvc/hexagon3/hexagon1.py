
# BOOT WIRING

from hexappmodel import App, Thing
from hexpersistence import PersistenceMock, PersistenceMock2

#app = App(PersistenceMock()) 
app = App(PersistenceMock2())

# UNIT TEST

app.Load()
print app.model

thing1 = app.GetThing(0)
app.AddInfoToThing(thing1, "once")
print app.model

app.New()
app.CreateThing("once")
app.CreateThing("upon a time")
app.Save()
print app.model

app.New()
print app.model

app.Load()
print app.model


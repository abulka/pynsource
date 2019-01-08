# http://www.andypatterns.com/index.php/blog/object_relational_mapping_pattern_-_using_sqlobj/
# http://www.ibm.com/developerworks/opensource/library/os-pythonsqlo/

from sqlobject import *
from sqlobject.sqlite import builder; SQLiteConnection = builder()
conn = SQLiteConnection('andyormtest1.db', debug=False)

class Cubicle(SQLObject):
    _connection = conn
    location = StringCol(length=20, default="unknown")
    occupant = ForeignKey('Person', default=None)

    def SetOccupant(self, person):
        # Evict any previous occupant
        if self.occupant:
            self.occupant.cubicle = None
        self.occupant = person  # New occupant wired in
        person.cubicle = self   # back pointer

class Person(SQLObject):
    _connection = conn
    firstname = StringCol(length=20)
    lastname = StringCol(length=20)
    cubicle = ForeignKey('Cubicle', default=None)
    orders = MultipleJoin('GiftOrder')
    addresses = RelatedJoin('Address')

    def AddOrder(self, giftOrder):
        #self.orders.append(giftOrder)  # one to many # SQL OBJECT doesn't need this
        giftOrder.person = self        # back pointer ** becomes the primary info sqlobject goes on

    def SetAddress(self, address):
        #self.addresses.append(address) # many to many # SQL OBJECT doesn't need this
        #address.residents.append(self) # back pointer (note the 'append' cos many to many) # SQL OBJECT doesn't need this
        address.addPerson(self)  # SQLobject created this "addWHATEVER" method for us

class GiftOrder(SQLObject):
    _connection = conn
    orderNumber = IntCol()
    description = StringCol()
    person = ForeignKey('Person', default=None)

class Address(SQLObject):
    _connection = conn
    street = StringCol(length=20)
    suburb = StringCol(length=20)
    postcode = StringCol(length=20)
    residents = RelatedJoin('Person')
    #def _init(self):
    #    SQLObject._init(self, *args, **kw)
    #    self.postcodesDict = {'2323':'Brighton','22222':'Werribee'}


Cubicle.dropTable(True)
Cubicle.createTable()
Person.dropTable(True)
Person.createTable()
GiftOrder.dropTable(True)
GiftOrder.createTable()
Address.dropTable(True)
Address.createTable()


# Test One to one

cubicle1 = Cubicle(location="North Wing D4")
tom = Person(firstname="Tom", lastname="Jones")
cubicle1.SetOccupant(tom)
assert cubicle1.occupant == tom

# Test One to many

o1 = GiftOrder(orderNumber=12345, description="new ipaq")
o2 = GiftOrder(orderNumber=12346, description="new ipod")
tom.AddOrder(o1)
tom.AddOrder(o2)
assert len(tom.orders) == 2
assert o1 in tom.orders
assert o2 in tom.orders

# Test Many to many

angelina = Person(firstname="Angelina", lastname="Jolie")
a1 = Address(street="Fox Studios", suburb="California", postcode="3186") # tom and angelina both work here
a2 = Address(street="Brads Place", suburb="Manhattan", postcode="40004")

angelina.SetAddress(a1)
angelina.SetAddress(a2)
tom.SetAddress(a1)
assert a1 in angelina.addresses
assert angelina in a1.residents
assert angelina in a2.residents
assert tom in a1.residents
assert tom not in a2.residents

################## Now do some more complex manipulations #########

# Move angelina into the North Wing D4 cubicle and
# move Tom into a new cubicle

cubicle1.SetOccupant(angelina)
assert cubicle1.occupant == angelina
assert tom.cubicle == None



cubicle2 = Cubicle(location="West Wing D5")
cubicle2.SetOccupant(tom)
assert tom.cubicle == cubicle2

# Now SQLOBJECT lets us do other magic things, that leverage relational db technology
p = Person.get(1)
print(p)

#ps = Person.select(Person.q.firstName=="John")
#print list(ps)

#ps = Person.select("""address.id = person.id AND
#                         address.postcode LIKE '40004%'""",
#                      clauseTables=['address'])
ps = Person.select("""address.postcode LIKE '3186'""",
                      clauseTables=['address'])
print(list(ps))

print('all people')
ps = Person.select()
print(list(ps))

print('Done!')

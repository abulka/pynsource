from ModelSql import Model, Thing
from ModelAdapterBase import ModelAdapterBase

from sqlobject.sqlite import builder
from sqlobject import sqlhub

class ModelSqlObjectAdapter(ModelAdapterBase):
    def DeleteThing(self, thing):
        Thing.delete(thing.id)
        self.observers.MODEL_THING_DELETED(thing)
    
    @classmethod
    def GetModel(self):
        SQLiteConnection = builder()
        conn = SQLiteConnection('hexmodel_sqlobject.db', debug=False)
        sqlhub.processConnection = conn
        try:
            model = Model.get(1)
            #a_thing = Thing.get(1)
        except:
            print "Oops - possibly no database - creating one now..."
            Model.dropTable(True)
            Model.createTable()
            Thing.dropTable(True)
            Thing.createTable()
    
            the_model = Model()
            assert the_model == Model.get(1)
            #~ thing1 = Thing(info="mary", model=model)
            #~ thing2 = Thing(info="fred", model=model)
            
            model = Model.get(1)
            
        return model

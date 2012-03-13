# Home grown - needs to know about model's innards

from ModelOo import Model, Thing

DEFAULT_FILENAME = "hexmodel_homegrown.txt"

class Persistence:
        
    def LoadAll(self, model, filename):
        if not filename:
            filename = DEFAULT_FILENAME
        output = open(filename, 'r')
        
        # Could also just create a new model e.g.
        #   model = Model()
        # since we return a model object
        # (whether its totally new or just the old existing one repopulated) 
        # and the layer above resets the app to use whatever we return here.
        model.Clear()

        # read model container, with all important next id allocator
        label, id = output.readline().strip().split('=')
        model.next_id = int(id)
                                
        for line in output.readlines():
            id, info = line.strip().split(',')
            model.AddThing(info, int(id))
        output.close()
        
        return model

    def SaveAll(self, model, filename):
        if not filename:
            filename = DEFAULT_FILENAME
        output = open(filename, 'w')

        # persist model container, with all important id allocator
        output.write("model.next_id=%s\n" % model.next_id)
        
        for thing in model.things:
            output.write("%s,%s\n" % (thing.id, thing.info))
        output.close()

        
import pickle

# Safer if Persistence doesn't permanently have a ref to the model since the
# model changes when loaded fresh, so hanging on to an old model would be bad.
# We could safely update our reference to self.model in our LoadAll() but
# perhaps that would be presumptious.

# This particular pickle persistence technique is oblivious of the
# innards of the model.

class Persistence:
    def __init__(self, filename):
        self.filename = filename
        
    def LoadAll(self, model):
        # ignore existing model paramter since pickle creates a new one.
        output = open(self.filename, 'r')
        model = pickle.load(output)
        output.close()
        return model

    def SaveAll(self, model):
        output = open(self.filename, 'w')
        pickle.dump(model, output, protocol=0)
        output.close()

        
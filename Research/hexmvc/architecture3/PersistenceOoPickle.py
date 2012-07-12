import pickle

# Safer if Persistence doesn't permanently have a ref to the model since the
# model changes when loaded fresh, so hanging on to an old model would be bad.
# We could safely update Persistence class's reference to self.model in our
# LoadAll() but perhaps that would be presumptious since we don't really know
# how the model is being managed and referred to.

# This particular pickle persistence technique is oblivious of the
# innards of the model.

DEFAULT_FILENAME = "hexmodel_sqlobject.pickle"

class Persistence:
        
    def LoadAll(self, model, filename):
        if not filename:
            filename = DEFAULT_FILENAME
        # ignore existing model paramter since pickle creates a new one.
        output = open(filename, 'r')
        model = pickle.load(output)
        output.close()
        return model

    def SaveAll(self, model, filename):
        if not filename:
            filename = DEFAULT_FILENAME
        output = open(filename, 'w')
        pickle.dump(model, output, protocol=0)
        output.close()

        
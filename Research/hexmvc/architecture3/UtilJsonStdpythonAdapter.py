import simplejson as json  # easy_install simplejson

def JsonFromDictFunction(o): 
    print "python json.dumps"
    return json.dumps(o)
    
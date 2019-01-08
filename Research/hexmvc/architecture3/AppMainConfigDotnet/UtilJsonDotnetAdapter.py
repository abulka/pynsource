#from System.Runtime.Serialization.Json import DataContractJsonSerializer
#
#Whats the proper way to use this class ?

# Andy hack
def JsonFromDictFunction(o): 
    print("dotnet json.dumps")
    s = str(o)
    return s.replace("\'", "\"")  # json require double quotes, not single
    
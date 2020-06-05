import numpy
import json
import dill
try:
    import cPickle as pickle
except:
    import pickle

class NumpySerializer:
    
    def __init__(self, path):
        self.path = path

    def serialize(self, data):
        numpy.save(self.path, data)
    
    def load(self):
        return numpy.load(self.path)
    
    def deserialize(self, ending=".npy"):
        return numpy.load(self.path + ending)

class PickleSerializer:
    
    def __init__(self, path):
        self.path = path
    
    def serialize(self, obj):
        f = open(self.path, "wb+")
        pickle.dump(obj, f)
        f.close()
    
    def deserialize(self):
        f = open(self.path, "rb")
        data = pickle.load(f)
        f.close()
        return data

class DillSerializer:
    
    def __init__(self, path):
        self.path = path
    
    def serialize(self, obj):
        f = open(self.path, "wb+")
        dill.dump(obj, f)
        f.close()
        
    def deserialize(self):
        f = open(self.path, "rb")
        data = dill.load(f)
        f.close()
        return data
    
class JsonSerializer:
    
    def __init__(self, path):
        self.path = path
    
    def serialize(self, obj):
        f = open(self.path, "w+")
        json.dump(obj, f)
    
    def deserialize(self):
        f = open(self.path, "r")
        return json.loads(f.read())
    
if __name__ == "__main__":
    import pandas
    from utils.nested_dict import nested_dict
    from coupling.device_grouping.online.machine_learning_features import Classifier
    
    basic_features_selection = nested_dict(3, dict)
    for clf in Classifier:
        basic_features_selection[2][0.05][clf] = pandas.DataFrame(
            {'feature': ["length","max","mean", "median", "min", "std", "sum", "var"],
             'relative_importance': [0.000000, 4.416329, 5.198687, 5.364500, 3.102737, 3.586680, 5.439479, 2.891588]
             })
    
    data = list()
    data.append("a")
    data.append("b")
    data.append("c")
    
    path = "./test"
    DillSerializer(path).serialize(basic_features_selection)
    test_data = DillSerializer(path).deserialize()
    print(test_data)
    
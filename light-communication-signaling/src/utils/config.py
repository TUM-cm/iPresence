import os
import ConfigParser
from utils.input import Input

class Config(object):
    
    def __init__(self, path, section_name):
        f = os.path.join(path, Input.config)
        self.config = ConfigParser.ConfigParser()
        self.config.read(f)
        self.section = self.config_section_map(section_name)
    
    def config_section_map(self, section):
        dict1 = {}
        options = self.config.options(section)
        for option in options:
            try:
                dict1[option] = self.config.get(section, option)
                if dict1[option] == -1:
                    print("skip: %s" % option)
            except:
                print("exception on %s!" % option)
                dict1[option] = None
        return dict1
    
    def get(self, key):
        return self.section[key.lower()]
    
    @staticmethod
    def create_dict(value, element_delim=",", item_delim=":"):
        return dict((k.strip(), v.strip()) for k, v in (item.split(item_delim)
                                                        for item in value.split(element_delim)))
    
    @staticmethod
    def create_list(value, item_delim=","):
        return [int(item) for item in value.split(item_delim)]

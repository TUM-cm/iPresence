from collections import defaultdict
from coupling.utils.defaultordereddict import DefaultOrderedDict

def nested_ordered_dict(n, data_type):
    if n == 1:
        return DefaultOrderedDict(data_type)
    else:
        return DefaultOrderedDict(lambda: nested_dict(n-1, data_type))

def nested_dict(n, data_type):
    if n == 1:
        return defaultdict(data_type)
    else:
        return defaultdict(lambda: nested_dict(n-1, data_type))

if __name__ == "__main__":
    result = nested_dict(3, list)
    result[1][2][3].append(12323)
    print("defaultdict")
    print(result)
    
    result = nested_ordered_dict(3, dict)
    result[1][2][3][4] = 12323
    print("ordered defaultdict")
    print(result)
    
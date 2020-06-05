
class Entry(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value

def enum_basic(**enums):
    return type('Enum', (), enums)

def enum_seq(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

def enum_name(*named):
    enums = dict()
    for name in named:
        enums[name] = name
    return type('Enum', (), enums)

def enum_rev(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    enums['name'] = dict((value, key) for key, value in enums.items())
    return type('Enum', (), enums)

def enum_pair(**named):
    enums = dict()
    for name, value in named.items():
        enums[name] = Entry(name, value)
    return type('Enum', (), enums)

def main():
    Action = enum_name("send", "pattern_hello")
    print(Action.send)
    print(Action.pattern_hello)
    
    numbers = enum_pair(ONE=1, TWO=2, THREE='three')
    print(numbers.ONE.value)
    print(numbers.ONE.name)

if __name__ == "__main__":
    main()

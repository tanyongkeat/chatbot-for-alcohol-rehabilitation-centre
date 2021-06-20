a = 1

def add_a():
    global a
    a = a+1

def print_a():
    print(a)

if __name__ == '__main__':
    add_a()
    print_a()


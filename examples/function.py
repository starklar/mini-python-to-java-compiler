def foobar():
    True
    print(1 + 2 + 3)
    return 1
#

def returnsTrue():
    True
    return True
#

returnsTrue()

foobar()

def stuff_inside(c):
    print(3)
    return c
#

print(stuff_inside(returnsTrue()))
i = returnsTrue()

stuff_inside(i)
stuff_inside(False)

def multi_args(a, b, c):
    if a == b:
        return a
    #
    return c
#

multi_args(1, 2, 5)

def func_calls_func():
    if returnsTrue():
        return True
    #
    return False
#

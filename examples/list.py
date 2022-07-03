a = ["1", 1, 1.0, True]
print(a)
b = ["F1rst", "2nd", "(Third!)"]
print(b)
c = [1]
print(c)
d = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
print(d)
e = [True, False, False, True, False]
print(e)
f = []
print(f)
g = [1.0, 99.99, 42.0, 6.9, 0.001]
print(g)

[].append("Cool ranch bro")

i = 1 + 1
j = 2
k = [i, j]

l = len([])

m = [1, 2, 3, 4, 5][2]
print(m)
m = [1, 2, 3, 4, 5][2 : 3]
print(m)
m = [1, 2, 3, 4, 5][1 : 3 : 2]
print(m)
m = [1, 2, 3, 4, 5][:3]
print(m)
m = [1, 2, 3, 4, 5][2:]
print(m)
m = [1, 2, 3, 4, 5][: 4 : 3]
print(m)
m = [1, 2, 3, 4, 5][ : : 2]
print(m)

["Hee-Ho", "Hee-Ho"].extend(["Hee-Ho"])

def foobar():
    return 1
#

p = ["Woah", 2].index(2)
["Left", "Right"].insert(1, "Middle")
["Left", "Right"].insert(i, "Middle")
["Left", "Right"].insert(foobar(), "Middle")

q = ["Pop"].pop()
q = ["Pop"].pop(0)

s = ["I CAN DO ANYTHING", "CHAOS CHAOS"].copy()
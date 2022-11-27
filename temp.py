a = [1,2,4]



b = [x for x in range(-10,11)]

c = [[x,a[x%3]*10**(x//3)]  for x in b]

# print(b)
print(c)
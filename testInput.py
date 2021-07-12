from sys import exit
x = input("Give me a number => ")
if x == "":
    print ("try again")
    exit()
else:
    print (x)
    y = int(x)
    print (y*y)
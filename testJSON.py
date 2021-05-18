class myClass:
    def __init__(self, given, surname, age):
        self._given = given
        self._surname = surname
        self._age = age
        
    def getage(self):
        return self._age
        
myc1 = myClass('John', 'Gouk', 66)
myc2 = myClass('Fred', 'Walsh', 106)

mylist = []
mylist.append(myc1)
mylist.append(myc2)
for mc in mylist:
    print("Name: {} Surname: {} Age: {}".format(mc._given, mc._surname, mc._age))

class A():
    def __init__(self):
        self.param1 = 10
        self.param2 = None

    def get(self):
        print(self.param1, self.param2)

 
class B(A):
    def __init__(self,):
        self.param2 = 20


a = A()
b = B()
a.get()
b.get()

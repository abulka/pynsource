x = 10
SETTINGS = 'something'

class Customer:
    def __init__(self, restaurant):
        self.restaurant: Restaurant = restaurant
        self.fred: Fred
        self.xx: Mary = None

class Employee:
    def __init__(self, restaurant):
        self.restaurant: Restaurant = restaurant

class Boss(Employee):
    salary = 1000
    reputation = 'good'
    
def test():
    pass

def main():
    pass


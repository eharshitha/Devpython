while True:
    x = int(input("Enter a number: "))
    y = int(input("Enter another number: "))
    z = input("Enter equation: ")
    def calculate(n1,n2,e):
        if e == "+":
            return n1+n2
        elif e == "-":
            return n1-n2
        elif e == "*":
            return n1*n2
        elif e == "/":
            return n1/n2
        else:
            return "Error"
    print(calculate(x,y,z))
    a = input("Again?[y/n]")
    if a.lower() == "n":
        print("Thank you for your time")
        break
    elif a.lower() == "y":
        pass

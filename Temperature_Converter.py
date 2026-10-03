while True:
    print("Welcome to Temperature converter")
    x = input("Enter a measurement[C/F/K]: ")
    y = input("Enter a new measurement[C/F/K]: ")
    n = int(input("Enter a number: "))


    def convert(x,y,n):
        if x == "Celsius" or x == "C" :
            if y == "Celsius" or y == "C" :
                return n
            elif y == "Fahrenheit" or y == "F":
                return (n*9/5)+32
            elif y == "Kelvin" or y == "K":
                return n+273.15
            else:
                return "ERROR! ERROR! ERROR!"
        elif x == "Fahrenheit" or x == "F" :
            if y == "Celsius" or y == "C" :
                return (n - 32) * 5/9
            elif y == "Fahrenheit" or y == "F":
                return n
            elif y == "Kelvin" or y == "K":
                return (n - 32) * 5/9 + 273.15
            else:
                return "ERROR! ERROR! ERROR!"
        elif x == "Kelvin" or x == "K" :
            if y == "Celsius" or y == "C" :
                return n - 273.15
            elif y == "Fahrenheit" or y == "F":
                return (n - 273.15) * 9/5 + 32
            elif y == "Kelvin" or y == "K":
                return n
            else:
                return "ERROR! ERROR! ERROR!"
        else:
            return "ERROR! ERROR! ERROR!"


    print(convert(x.capitalize(),y.capitalize(),n))
    z = input("Again? [Y/N]: ")
    if z == "Y" or z == "y":
        pass
    elif z == "N" or z == "n":
        break

while True:
    x = input("Enter a word: ")
    if 2 % len(x) == 0:
            print("It has a even number of letters")
    elif 2 % len(x) != 0:
            print("It has a odd number of letters")
    a = input("Again? [y/n]: ").lower()
    if a == "y":
        pass
    elif a == "n":
        break
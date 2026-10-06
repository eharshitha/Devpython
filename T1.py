# imports
import random

# Starting & Difficulty
while True:
    print("Welcome to the Guess the number game")
    print("1. Easy (1 - 100), (10 - Lives)")
    print("2. Medium (1 - 500), (20 - Lives)")
    print("3. Hard (1 - 1000), (50 - Lives)")
    while True:
        try:
            D = int(input("Choose your difficulty[1,2,3]: "))
            if D not in (1, 2, 3):
                print("Please choose 1, 2, or 3!")
                continue
        except ValueError:
            print("Please enter a number!")
            continue
        break

    # Variables
    if D == 1:
        x = random.randint(1,100)
        L = 10
        maximum = 100
    elif D == 2:
        x = random.randint(1,500)
        L = 20
        maximum = 500
    elif D == 3:
        x = random.randint(1,1000)
        L = 50
        maximum = 1000
    previous_distance = None


    A = 0

    # define function
    def print_lives_attempts():
        print("Lives: ", L)
        print("Attempts: ", A)

    def lost():
        return L <= 0

    # input loop
    while L > 0:
        try:
            G = int(input(f"Guess the number between 1 and {maximum}: "))

            if G < 1 or G > maximum:
                print(f"Please choose between 1 and {maximum}!")
                continue

        except ValueError:
            print("Please enter a number!")
            continue
        A += 1

        # Hint
        if A == 3:
            if x % 2 == 0:
                print("Hint: The number is even!")
            else:
                print("Hint: The number is odd!")

        # Hot or cold hint
        current_distance = abs(G - x)
        if previous_distance is None:
            print("No previous guess to compare!")

        elif current_distance < previous_distance:
            print("🔥 You are getting closer!")

        else:
            print("❄️ You are getting farther away!")
        previous_distance = current_distance

    # Answer loop
        if G == x:
            print("You got it!")
            print_lives_attempts()
            break

        elif G > x:
            print("Too high!")
            L -= 1
            print_lives_attempts()

        elif G < x:
            print("Too low!")
            L -= 1
            print_lives_attempts()

    # lose
    if lost():
        print_lives_attempts()
        print("You lost!")

    # Play again loop
    while True:
        a = input("Again?: ")

        if a.lower() == "y":
            break
        elif a.lower() == "n":
            print("Goodbye!")
            exit()
        else:
            print("Please enter y or n")
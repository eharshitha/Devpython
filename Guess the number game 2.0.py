# imports
import random

# variables
hi_score = {
    "Easy": None,
    "Medium": None,
    "Hard": None,
}
points = 0
games_played = 0
games_won = 0
games_lost = 0
hi_score_file = "highscores(Guess the number game 2.0).txt"

# load highscore
def load_highscores():
    try:
        with open(hi_score_file, "r") as file:
            for line in file:
                difficulty, score = line.strip().split(":")

                if score != "None":
                    hi_score[difficulty] = int(score)

    except FileNotFoundError:
        pass


load_highscores()
# Functions
def print_lives_attempts():
    print("Lives:", L)
    print("Attempts:", A)

def print_highscore(d):
    print("High score:", hi_score[d])

def print_points():
    print("Points:", points)

def lost():
    return L <= 0


def save_highscores():
    with open(hi_score_file, "w") as file:
        for difficulty, score in hi_score.items():
            file.write(f"{difficulty}:{score}\n")

# Starting & Difficulty
while True:
    print("\nWelcome to the Guess the number game")
    print("1. Easy (1 - 100), (10 - Lives)")
    print("2. Medium (1 - 500), (20 - Lives)")
    print("3. Hard (1 - 1000), (50 - Lives)")
    games_played += 1

    while True:
        try:
            D = int(input("\nChoose your difficulty[1,2,3]: "))

            if D not in (1, 2, 3):
                print("Please choose 1, 2, or 3!")
                continue

        except ValueError:
            print("Please enter a number!")
            continue

        break

    # Variables
    if D == 1:
        x = random.randint(1, 100)
        L = 10
        maximum = 100

    elif D == 2:
        x = random.randint(1, 500)
        L = 20
        maximum = 500

    elif D == 3:
        x = random.randint(1, 1000)
        L = 50
        maximum = 1000

    previous_distance = None
    A = 0
    guesses = []
    hints_left = 3

    # Difficulty name
    if D == 1:
        difficulty = "Easy"
    elif D == 2:
        difficulty = "Medium"
    elif D == 3:
        difficulty = "Hard"



    # Input loop
    while L > 0:

        user_input = input(
            f"Guess the number between 1 and {maximum} "
            f"(or type 'hint'): "
        )

        # Hint system
        if user_input.lower() == "hint":

            if hints_left <= 0:
                print("❌ You have no hints left!")

            else:
                points -= 20
                hints_left -= 1

                print(f"💡 Hints remaining: {hints_left}")

                # Random hint
                hint_type = random.randint(1, 3)

                if hint_type == 1:
                    if x % 2 == 0:
                        print("💡 Hint: The number is EVEN!")
                    else:
                        print("💡 Hint: The number is ODD!")

                elif hint_type == 2:
                    middle = maximum // 2

                    if x <= middle:
                        print(f"💡 Hint: The number is {middle} or LOWER!")
                    else:
                        print(f"💡 Hint: The number is HIGHER than {middle}!")

                elif hint_type == 3:
                    if x % 5 == 0:
                        print("💡 Hint: The number is divisible by 5!")
                    else:
                        print("💡 Hint: The number is NOT divisible by 5!")

            continue

        # Convert input to number
        try:
            G = int(user_input)

            if G < 1 or G > maximum:
                print(f"Please choose between 1 and {maximum}!")
                continue

        except ValueError:
            print("Please enter a number or type 'hint'!")
            continue

        A += 1
        guesses.append(G)

        # Win
        if G == x:
            games_won += 1
            print("🎉 You got it!")
            points += 100
            points += L * 10

            print("Your guesses:", guesses)
            print_points()

            # High score
            if hi_score[difficulty] is None or A < hi_score[difficulty]:
                hi_score[difficulty] = A
                save_highscores()
                print("🏆 New high score!")

            print_lives_attempts()
            print_highscore(difficulty)

            break

        # Hot or cold hint
        current_distance = abs(G - x)

        if previous_distance is None:
            print("No previous guess to compare!")

        elif current_distance < previous_distance:
            print("🔥 You are getting closer!")

        else:
            print("❄️ You are getting farther away!")

        previous_distance = current_distance

        # Too high / too low
        if G > x:
            print("Too high!")
            points -= 5
            L -= 1
            print_lives_attempts()

        elif G < x:
            print("Too low!")
            points -= 5
            L -= 1
            print_lives_attempts()

    # Lose
    if lost():
        print_lives_attempts()
        print("You lost!")
        print("The number was:", x)
        print("Your guesses:", guesses)
        games_lost  += 1

    # Play again
    while True:
        a = input("\nAgain? (y/n): ")

        if a.lower() == "y":
            break

        elif a.lower() == "n":
            win_rate = (games_won / games_played) * 100

            print("\n📊 STATISTICS")
            print("Games played:", games_played)
            print("Games won:", games_won)
            print("Games lost:", games_lost)
            print(f"Win rate:{win_rate:.2f}%" )

            print("Goodbye!")
            exit()

        else:
            print("Please enter y or n!")
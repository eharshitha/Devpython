import random

def number_guessing_game():
    print("🎮 Welcome to the Number Guessing Game!")
    print("I'm thinking of a number between 1 and 100.")

    number = random.randint(1, 100)
    attempts = 7

    while attempts > 0:
        try:
            guess = int(input(f"\nEnter your guess ({attempts} attempts left): "))
        except ValueError:
            print("❌ Please enter a valid number.")
            continue

        if guess == number:
            print("🎉 Congratulations! You guessed the number!")
            break
        elif guess < number:
            print("⬆️ Too low!")
        else:
            print("⬇️ Too high!")

        attempts -= 1

    if attempts == 0:
        print(f"\n💀 Game Over! The number was {number}.")

    play_again = input("\nDo you want to play again? (y/n): ").lower()
    if play_again == 'y':
        number_guessing_game()
    else:
        print("👋 Thanks for playing!")

number_guessing_game()

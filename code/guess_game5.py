import random

class GuessGame:
    def __init__(self, guess: int = 5):
        self.guess = guess
        self.correct_number = random.randint(1, 10)

    def start(self):
        print("Welcome to the Number Guessing Game")

        while self.guess > 0:
            try:
                user_guess = int(input("Guess a number betweem 1 and 10: "))
                if user_guess < 1 or user_guess > 10:
                    print("Please enter a number between 1 and 10!")
                    continue
            except ValueError:
                print("Invalid input! Please enter a number between 1 and 10")
                continue

            if user_guess == self.correct_number:
                print("Congratulations! You guessed correctly.")
                return
            elif user_guess > self.correct_number:
                self.guess -= 1
                print(f"Too high! You have {self.guess} guesses left.")
            else:
                self.guess -= 1
                print(f"Too low! You have {self.guess} guesses left.")

        print(f"Out of attempts! The correct number was {self.correct_number}.")


if __name__ == "__main__":
    game = GuessGame(guess=5)
    game.start()
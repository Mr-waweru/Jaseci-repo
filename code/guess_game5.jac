"""A Number Guessing Game (Fixed)"""

import random;

walker GuessGame {
    has guess: int = 5;

    can start with entry {
        print("Welcome to the Number Guessing Game!");

        # Make a new turn node (the place where the secret number is stored)
        next = root ++> turn();
        # Move (visit) into the node so the guessing can begin
        visit next;
    }

    can process_guess with turn entry {
        while self.guess > 0 {
            let user_guess = int(input(f"Guess a number between 1 and 10: "));

            if user_guess < 1 or user_guess > 10 {
                print("Please enter a number between 1 and 10!");
            }

            if user_guess == here.correct_number {
                print("Congratulations! You guessed correctly!");
                return;
            } elif user_guess > here.correct_number {
                self.guess -= 1;
                print(f"Too high! You have {self.guess} guesses left!");
            } else {
                self.guess -= 1;
                print(f"Too low! You have {self.guess} guesses left!");
            }
        }

        print(f"Out of attempts! The correct number was {here.correct_number}!");
    }
}

node turn {
    has correct_number: int = random.randint(1, 10);
}

# Run in CLI mode
with entry: __main__ {
    root spawn GuessGame();
}

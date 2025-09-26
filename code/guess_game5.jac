"""A Number Guessing Game (Fixed)"""

import random;

walker GuessGame {
    has attempts: int = 10;

    can start with entry {
        print("Welcome to the Number Guessing Game!");

        # Create a turn node attached to root
        root ++> turn();

        # Visit the newly created turn node
        visit [--> turn];
    }

    can process_guess with turn entry {
        while self.attempts > 0 {
            let user_guess = int(input(f"Guess a number between 1 and 10: "));

            if user_guess == here.correct_number {
                print("Congratulations! You guessed correctly.");
                return;
            } elif user_guess > here.correct_number {
                self.attempts -= 1;
                print(f"Too high! You have {self.attempts} attempts left.");
            } else {
                self.attempts -= 1;
                print(f"Too low! You have {self.attempts} attempts left.");
            }
        }

        print(f"Out of attempts! The correct number was {here.correct_number}.");
    }
}

node turn {
    has correct_number: int = random.randint(1, 10);
}

# Run in CLI mode
with entry: __main__ {
    root spawn GuessGame();
}

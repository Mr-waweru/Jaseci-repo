"""AI-Enhanced Number Guessing Game with byLLM (fixed)"""

import random;
import os;
import from dotenv { load_dotenv }
import from byllm.llm { Model }

# LLM backend using Gemini
glob llm = Model(model_name="gemini/gemini-2.0-flash", verbose=False);

"""Provide a fun hint if guess is incorrect"""
def give_hint(guess: int, correct_number: int) -> str by llm();

walker GuessGame {
    has guess: int = 5;

    can start with entry {
        print("Welcome to the AI-Enhanced Guessing Game!");
        print("I'm thinking of a number between 1 and 10...");
        next = root ++> turn();
        visit next;
    }

    can process_guess with turn entry {
        while self.guess > 0 {
            let user_guess = int(input("Your guess: "));

            if user_guess == here.correct_number {
                print("Congratulations! You guessed it right!");
                return;
            } else {
                self.guess -= 1;

                if self.guess > 0 {
                    let hint = give_hint(user_guess, here.correct_number);
                    if user_guess > here.correct_number {
                        print(f"Too high! ({self.guess} attempts left)");
                    } else {
                        print(f"Too low! ({self.guess} attempts left)");
                    } 
                    print(f"Hint: {hint}");
                }
            }
        }
        print(f"Out of attempts! The correct number was {here.correct_number}.");
    }
}

node turn {
    has correct_number: int = random.randint(1, 10);
}

with entry: __main__ {
    root spawn GuessGame();
}
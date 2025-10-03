"""A Number Guessing Game (Fixed)"""

import random;

walker GuessGame {
    has guess: int = 5;

    # see implementations in guess_game5.impl.jac)
    can start with `root entry;
    can process_guess with turn entry;
}

node turn {
    has correct_number: int = random.randint(1, 10);
}

# Run in CLI mode
with entry:__main__ {
    root spawn GuessGame();
}
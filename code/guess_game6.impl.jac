"""implementations of guess_game6.jac (Fixed)"""

impl GuessGame.start {
    # load environment (API keys)
    load_dotenv();

    print("Welcome to the AI-Enhanced Guessing Game!");
    print("I'm thinking of a number between 1 and 10...");

    next = root ++> turn();
    visit next;
}

impl GuessGame.process_guess {
    while self.guess > 0 {
        let user_guess = int(input("Your guess: "));

        if user_guess < 1 or user_guess > 10 {
            print("Please enter a number between 1 and 10!");
        } else {
            if user_guess == here.correct_number {
                print("Congratulations! You guessed it right!");
                disengage;
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
                } else {
                    print(f"Out of attempts! The correct number was {here.correct_number}.");
                    disengage;
                    return;
                }
            }
        }
    }
}

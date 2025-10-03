"""implementations of guess_game5.jac (Fixed)"""

impl GuessGame.start {
    print("Welcome to the Number Guessing Game!");
    # Make a new turn node (the place where the secret number is stored)
    next = root ++> turn();
    # Move (visit) into the node so the guessing can begin
    visit next;
}

impl GuessGame.process_guess {
    while self.guess > 0 {
        let user_guess = int(input(f"Guess a number between 1 and 10: "));

        if user_guess < 1 or user_guess > 10 {
            print("Please enter a number between 1 and 10!");
        } else {
            if user_guess == here.correct_number {
                print("Congratulations! You guessed correctly!");
                disengage;
                return;
            } elif user_guess > here.correct_number {
                self.guess -= 1;
                print(f"Too high! You have {self.guess} guesses left!");
            } else {
                self.guess -= 1;
                print(f"Too low! You have {self.guess} guesses left!");
            }

            if self.guess <= 0 {
                print(f"Out of attempts! The correct number was {here.correct_number}!");
                disengage;
                return;
            }
        }
    }
}

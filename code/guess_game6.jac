"""AI-Enhanced Number Guessing Game with byLLM (Fixed)"""

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

    # interface only: implementations live in .impl.jac
    can start with `root entry;
    can process_guess with turn entry;
}

node turn {
    has correct_number: int = random.randint(1, 10);
}

with entry: __main__ {
    root spawn GuessGame();
}
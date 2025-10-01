# Assignments & Projects

This folder contains the Jac and Python source files used in the BCS-OUK Gen AI seminar.

## Files included

* `guess_game5.jac` — A fixed number-guessing game (step 5). The walker and abilities were implemented and corrected so the game runs, handles guesses, and reports results.
* `guess_game6.jac` — An AI-enhanced guessing game that uses `byllm` to generate playful hints via an LLM. The file demonstrates how to call an LLM from Jac.
* `mental_health_buddy.jac` — A Jac mental health buddy that prompts the user for their mood; on negative moods, it requests a short joke and encouragement from an LLM.
* `requirements.txt` — Requirements dependencies.
* `.env` — Contains API keys (e.g., GEMINI_API_KEY, GROQ_API_KEY, OPENAI_API_KEY). **This file should never be committed** — see `.gitignore`.

## Getting started

Prerequisites (WSL / Ubuntu recommended):

1. Install Python 3 and virtualenv/venv support:

   ```bash
   sudo apt update
   sudo apt install python3 python3-venv python3-pip
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt  # or: pip install byllm python-dotenv
   ```
2. Create a `.env` in this directory with keys (example):

   ```env
   GEMINI_API_KEY=your_gemini_key
   ```
3. For Jac files that use `byllm`, ensure `byllm` is installed in the active venv:

   ```bash
   pip install byllm python-dotenv
   ```

## Usage

### Run Jac guessing games

From this folder inside WSL and with the venv activated:

```bash
# run guess_game5 (non-LLM)
jac guess_game5.jac

# run AI-enhanced guess game (uses byllm)
jac guess_game6.jac
```

### Expected behaviour

* `guess_game5.jac`: simple CLI guessing — prompts and handles guesses.
* `guess_game6.jac`: on incorrect guesses, calls the LLM to generate a hint; ensure `.env` key is valid and loaded in your shell `export GEMINI_API_KEY="your_api_key_here"` or available to Jac.
* `mental_health_buddy.jac`: prompts for mood; if negative, requests a joke + encouragement from the model and prints the result.


Example:
 - Demonstration using guess_game6.jac
```
Welcome to the AI-Enhanced Guessing Game!
I'm thinking of a number between 1 and 10...
Your guess: 1
Too low! (4 attempts left)
Hint: Not quite! Think higher... like the number of legs a spider has!

Your guess: 8
Congratulations! You guessed it right!

```

- Demonstration using mental_health_buddy1.jac
```
How are you feeling today? good
That’s wonderful! Keep enjoying your good mood!
```
```
How are you feeling today? angry
I’m sorry you’re feeling that way. Let me cheer you up...
Here's something for you:

Why did the tomato turn red? Because it saw the salad dressing!

Hey, I know you're feeling angry right now, and that's okay. It's a valid emotion. Just remember to take a deep breath, and don't let that anger control you. You're strong, capable, and you've got this! You can work through whatever's making you mad.

```
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("⚠️ GEMINI_API_KEY not found. Add it to your .env file.")

# Configure Gemini
genai.configure(api_key=api_key)

# Pick a model
model = genai.GenerativeModel("gemini-1.5-flash")

def cheer_up(mood: str) -> str:
    """Ask Gemini for a supportive joke and encouragement"""
    prompt = f"""
    The user is feeling {mood}.
    Please respond with:
    1. A light-hearted, clean joke.
    2. A short encouraging message.
    """
    response = model.generate_content(prompt)
    return response.text

def main():
    mood = input("💙 How are you feeling today? ")

    if mood.lower() in ["sad", "tired", "angry", "stressed", "anxious", "lonely"]:
        print("🤖 I’m sorry you’re feeling that way. Let me cheer you up...\n")
        reply = cheer_up(mood)
        print("✨ Here's something for you:\n")
        print(reply)
    else:
        print(f"🌞 That’s wonderful! Keep enjoying your {mood} mood!")

if __name__ == "__main__":
    main()

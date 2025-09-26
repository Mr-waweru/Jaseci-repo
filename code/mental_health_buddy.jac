"""AI Mental Health Buddy using Groq (Free API)"""

import from byllm.llm { Model }
import os;
import from dotenv { load_dotenv }

# Python interop: load API key



# Attach Groq model (LLaMA 3)
glob llm = Model(
    model_name="groq/llama3-70b-8192",   # free Groq LLaMA 3 model
    api_key=os.getenv("GROQ_API_KEY"),
    verbose=False
);

"""Ask AI for a supportive joke + encouragement"""
def cheer_up(mood: str) -> str by llm();

walker MentalHealthBuddy {
    can start with entry {
        let mood = input("💙 How are you feeling today? ");

        if mood in ["sad", "tired", "angry", "stressed", "anxious", "lonely"] {
            print("🤖 I’m sorry you’re feeling that way. Let me cheer you up...");
            let response = cheer_up(mood);
            print("✨ Here's something for you:\n");
            print(response);
        } else {
            print(f"🌞 That’s wonderful! Keep enjoying your {mood} mood!");
        }
    }
}

with entry: __main__ {
    root spawn MentalHealthBuddy();
}

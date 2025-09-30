"""Using Gemini API"""

import from byllm.llm { Model }
import from dotenv { load_dotenv }
import os;

# Attach Gemini model
glob llm = Model(
    model_name="gemini/gemini-2.0-flash",
    api_key=os.getenv("GEMINI_API_KEY"),
    verbose=False
);

"""Ask AI for a supportive joke + encouragement"""
def cheer_up(mood: str) -> str by llm();

walker MentalHealthBuddy {
    can start with entry {
        let mood = input("How are you feeling today? ");

        if mood in ["sad", "tired", "angry", "stressed", "anxious", "lonely"] {
            print("I’m sorry you’re feeling that way. Let me cheer you up...");
            let response = cheer_up(mood);
            print("Here's something for you:\n");
            print(response);
        } else {
            print(f"That’s wonderful! Keep enjoying your {mood} mood!");
        }
    }
}

with entry: __main__ {
    root spawn MentalHealthBuddy();
}

"""Using Gemini API (Interface)"""

import from byllm.llm { Model }
import from dotenv { load_dotenv }
import os;

# Attach Gemini model (reads GEMINI_API_KEY from env)
glob llm = Model(
    model_name="gemini/gemini-2.0-flash",
    api_key=os.getenv("GEMINI_API_KEY"),
    verbose=False
);

"""Ask AI for a supportive joke + encouragement"""
def cheer_up(mood: str) -> str by llm();

walker MentalHealthBuddy {
    # interface only: implementation in .impl.jac
    can start with `root entry;
}

with entry: __main__ {
    root spawn MentalHealthBuddy();
}
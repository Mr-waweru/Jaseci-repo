# import google.generativeai as genai
# import os
# from dotenv import load_dotenv

# load_dotenv()
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# model = genai.GenerativeModel("gemini-2.0-flash")
# response = model.generate_content("Hello Gemini, test connection.")
# print(response.text)

# import os
# from dotenv import load_dotenv
# load_dotenv()
# print(os.getenv("GROQ_API_KEY"))

# from google import genai

# client = genai.Client()

# response = client.models.generate_content(
#     model="gemini-2.5-flash",
#     contents="Explain how AI works in a few words",
# )

# print(response.text)


import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

for m in genai.list_models():
    print(m.name)


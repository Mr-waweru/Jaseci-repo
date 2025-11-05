from langchain_google_genai import GoogleGenerativeAIEmbeddings
emb = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
vec = emb.embed_query("hello world")
print("len(vec)=", len(vec))

import google.generativeai as genai

API_KEY = "YOUR_GEMINI_API_KEY"

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")
response = model.generate_content("Say 'API key works!' in exactly those words.")

print("✅ Success:", response.text)
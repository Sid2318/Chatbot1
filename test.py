import google.generativeai as genai

genai.configure(api_key="AIzaSyD3IHgDTHiHU3QffVML_P2qBXkQN8Zd-mY")

models = genai.list_models()
for model in models:
    print(model.name)

from openai import OpenAI

# Lecture de la clé API et de l'ID d'organisation
with open('key.txt', 'r') as file:
    secret_key = file.read().strip()

with open('organization.txt', 'r') as file:
    organization_id = file.read().strip()

# Initialisation du client OpenAI
client = OpenAI(api_key=secret_key)

# Création d'une requête avec streaming
stream = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Say this is a test"}],
    stream=True
)

# Lecture du flux de données
for chunk in stream:
    if hasattr(chunk.choices[0].delta, "content") and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")

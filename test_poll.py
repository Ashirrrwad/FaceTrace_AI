import requests
prompt = "Professional forensic portrait of a 48 year old man, mugshot"
url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?seed=123&width=512&height=512&nologo=True"
response = requests.get(url)
print(f"Pollinations Status: {response.status_code}")

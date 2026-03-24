import requests

def get_llama_response(message):
    try:
        response = requests.post("http://localhost:8001/generate-response", json={"message": message})
        data = response.json()
        return data.get("response", "No response.")
    except Exception as e:
        return f"Error: {str(e)}"

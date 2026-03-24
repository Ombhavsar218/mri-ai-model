from flask import Flask, request, jsonify
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

app = Flask(__name__)

model_name = "meta-llama/Llama-2-7b-chat-hf"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16, device_map="auto")

@app.route("/generate-response", methods=["POST"])
def generate_response():
    data = request.get_json()
    user_input = data.get("message")
    if not user_input:
        return jsonify({"response": "Please provide a message."})

    prompt = f"Doctor: {user_input}\nAssistant:"
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    outputs = model.generate(**inputs, max_new_tokens=150, pad_token_id=tokenizer.eos_token_id)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True).split("Assistant:")[-1].strip()

    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(port=8001)

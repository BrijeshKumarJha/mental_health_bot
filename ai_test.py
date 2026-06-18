from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model_name = "microsoft/DialoGPT-small"
print(f"Loading {model_name} please wait...")
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

print("Success! The AI is ready. Type 'quit' to exit.\n")
while True:
    user_input = input(">> You: ")
    if user_input.lower() == 'quit':
        break
    new_user_input_ids = tokenizer.encode(user_input + tokenizer.eos_token, return_tensors='pt')
    bot_output_ids = model.generate(
        new_user_input_ids,
        max_length=100,
        pad_token_id=tokenizer.eos_token_id
    )
    bot_reply = tokenizer.decode(bot_output_ids[:, new_user_input_ids.shape[-1]:][0], skip_special_tokens=True)
    print(f">> Bot: {bot_reply}")
    
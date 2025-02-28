from transformers import GPT2Tokenizer, AutoModelForCausalLM, GPT2Model, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained('gpt2-large')
model = AutoModelForCausalLM.from_pretrained('gpt2-large')
prompt = "Replace me by any text you'd like."

input_ids = tokenizer([prompt], return_tensors='pt')#.input_ids

output = model.generate(**input_ids, max_new_tokens=100, do_sample=True)

gen_text = tokenizer.batch_decode(output)[0]

print(gen_text)
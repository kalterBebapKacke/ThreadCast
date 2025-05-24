from transformers import GPT2Tokenizer, GPT2LMHeadModel
import torch

# Load pre-trained tokenizer and model
tokenizer = GPT2Tokenizer.from_pretrained("gpt2-large")
model = GPT2LMHeadModel.from_pretrained("gpt2-large")

# Put model in evaluation mode
model.eval()

# Encode input prompt
story = '"So when I first moved out, I was living alone in a kind of sketchy area. One night I got super paranoid , decided to get a home security system. And once it was installed… man, I was OBSESSED. Didn’t matter if I was home, out, taking a nap, or just watching TV — that alarm was ON 24/7. One day while I was at work, I started getting weird notifications from the app: Front door opened Motion detected in the living room Alarm disarmed Alarm armed again All of that happened while I was sitting at my desk, clearly not at home. I totally freaked out. I rearmed the alarm from my phone, called the security company, , asked them to send the police immediately. I was panicking hard. I left work , rushed home… , when I got there, there were police officers everywhere, waiting for burglars to come out of my apartment. I opened the door , they went in to check. After a few minutes, one of them comes back out , says: Well… this is strange. It looks like the burglars didn’t steal anything, but they absolutely trashed the place. I walked in with them ,... yeah, turns out the mess was just how I had left the place — underwear everywhere, a 4-day-old breakfast on the table, clothes on the floor. They asked if I wanted to file a report, , I was like…Uhh... maybe another day. Later, the security company told me the system had glitched , replayed actions from 30 minutes earlier as if they were happening live — hence the chaos. Moral of the story: maybe clean your apartment once in a while. You never know when youll accidentally SWAT yourself.'
prompt = f'"{story}" This is a story, please rewrite this story so that there are no abbreviations and format the text so that it is easily readable. Only return the story.'
inputs = tokenizer.encode(prompt, return_tensors="pt")

# Generate output
outputs = model.generate(
    inputs,
    max_length=1024,
    num_return_sequences=1,
    no_repeat_ngram_size=2,
    do_sample=True,
    top_k=50,
    top_p=0.95,
    temperature=0.9,
    pad_token_id=tokenizer.eos_token_id
)

# Decode and print
generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(generated_text)
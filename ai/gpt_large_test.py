from transformers import GPT2Tokenizer, AutoModelForCausalLM, GPT2Model, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained('gpt2-large')
model = AutoModelForCausalLM.from_pretrained('gpt2-large')

test_story = 'Earlier in the day, I told my bf that I was going to make Mapo Tofu, a dish he’s never had before. It is one I like a lot. He told me he’s never had tofu before so I was excited for him to try it. Since we have different cultures and different taste, I told him ahead of time that if he didn’t end up liking it, he can order out. Not that it matters much, but he’s white and I’m Asian. When I was making the food, he comes into the kitchen and tells me “Tacobell seems nice right now.” To which, I tell him I want him to at least eat some of the food I’m making. When I actually made the food, he seemed sure that he wasn’t gonna like it as he told me, “I’ll just try a bite of your bowl.” And I responded “Why don’t you just get a bowl for yourself?” He responds with, “I told really eat Tofu.” I was confused because I thought he told me he’s never tried it before. When he took a bite, he said, “It’s good, I just don’t like the texture of tofu.” So I ate my bowl by myself while he prepared the dogs food. When I’m about to clean up, he asks me, “Are you mad I didn’t like it?” I said “No, I’m not mad, I’m just disappointed. I made this for us.” He said “Atleast I tired it. You’re making me feel bad, fine I’ll just eat it.” I was thrown aback because I don’t want him to feel forced to eat something he doesn’t like. So I responded with “No it’s fine, you can get tacobell. I’ll just pack this for my sister and I’s lunch”. He then said, “I’ll just eat it, you’re making me feel guilty”, to which I just shrugged. We then got into a long argument with him saying he expected me to comfort him when he expressed himself feeling guilty after the way I acted/ my tone of voice. He said he felt like I was guilty tripping him. I felt like I am not responsible for him feeling that way, just the same way I don’t blame him for me feeling disappointed. I just don’t know what more there was to say. I told him he’s free to get take out, and that I wasn’t mad at him for not liking my dish. Maybe I did have a bad tone, but it might be because I was disappointed. Please help me because I have no idea if I was in the wrong or not.'
prompt = f"'{test_story}' Based on this story create a new story implementing elements to make it more interesting"

input_ids = tokenizer([prompt], return_tensors='pt')#.input_ids

output = model.generate(**input_ids, max_new_tokens=100, do_sample=True)

gen_text = tokenizer.batch_decode(output)[0]

print(gen_text)

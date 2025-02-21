from gpt4all import GPT4All

def model():
    model = GPT4All("Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf")
    return model

def message(message_:str, title:str, tokens:int=2048):
    model_ = model()
    with model_.chat_session():
        text = model_.generate(f"{message_}  Please rewrite this text, so that it is family friendly. Also rewrite any insults and make it readable for a text-to-speech ai, so convert any short forms like '18 Male' or AITA for 'Am I the Asshole' into a full text.", max_tokens=tokens)
        title = model_.generate(f"{title}  Please rewrite this title, so that it is family friendly and attention grabbing as an Video title. Also rewrite any insults and make it readable for a text-to-speech ai, so convert any short forms like '18 Male' or AITA for 'Am I the Asshole' into a full word. Please only give me the title", max_tokens=tokens)
    del model_
    return text, title


if __name__ == '__main__':
    print('test')
    for i, x in enumerate(['a', 'b']):
        print(i)
        print(x)
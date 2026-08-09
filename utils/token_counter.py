from transformers import AutoTokenizer

def get_tokenizer(model_name):
    return AutoTokenizer.from_pretrained(model_name)


def tokenizer_length(text, tokenizer):
    return len(tokenizer.encode(text, add_special_tokens=False))


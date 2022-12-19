import string
from typing import List


class PromptHandler:
    def __init__(
        self,
        sets: List[str] = ["stopwords", "punkt"],
    ):
        for set_ in sets:
            nltk.download(set_)

        self.stop_words = set(stopwords.words("english"))

    def __call__(self, prompt: str) -> List[str]:
        word_tokens = word_tokenize(prompt)

        filtered_words = []
        for w in word_tokens:
            if (
                w not in self.stop_words
                and w not in string.punctuation
                and w not in filtered_words
            ):
                filtered_words.append(w)

        return filtered_words


try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize

    prompt_handler = PromptHandler()

except ImportError:
    print("nltk not found, skipping prompt handler")


if __name__ == "__main__":
    prompt = "Hello, how are you? Mr. Smith went to the store."
    print(prompt_handler(prompt))

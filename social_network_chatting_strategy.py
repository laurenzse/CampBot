import random
import re

HASHTAG_PROB = 0.3
EIN_1_REPLACEMENT_PROB = 0.6

EIN_1_WORDS = ["ein", "eine", "einen", "einem", "einer"]

AVERAGE_WORD_LENGTH = 6

class SocialNetworkChattingStrategy:

    def __init__(self):
        pass

    def will_send_message(self, bot, args, **kwargs):
        if args[1] is not None:
            args[1] = self.style_message(args[1])

    def has_sent_message(self, bot, *args, **kwargs):
        pass

    def style_message(self, message):
        words = message.split()

        for index, word in enumerate(words):
            # do not add # to the first word in a sentence
            if not self.is_first_word_in_sentence(index, words) \
                    and word[0].isalpha() and word[0].isupper() and random.uniform(0, 1) < self.hashtag_probability(word):

                word = "#{}".format(word)

            if random.uniform(0, 1) < EIN_1_REPLACEMENT_PROB:
                if word.lower() in EIN_1_WORDS:
                    word = "1"
                # elif "ein" in word:
                #     word = word.replace("ein", "1")

            words[index] = word

        styled = " ".join(words)
        return styled

    @staticmethod
    def hashtag_probability(word):
        if len(word) < AVERAGE_WORD_LENGTH:
            return HASHTAG_PROB
        else:
            return (HASHTAG_PROB + (len(word) - AVERAGE_WORD_LENGTH) * 0.05) % 1

    @staticmethod
    def is_first_word_in_sentence(index, words):
        if index == 0:
            return True
        return re.match('.*[?.!]$', words[index - 1]) is not None


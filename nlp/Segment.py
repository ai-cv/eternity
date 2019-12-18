import jieba


class Segment:

    def __init__(self):
        self.stop_words = []
        with open("../data/stop_words_line.txt", encoding="utf-8") as st:
            self.stop_words = st.readline().split(" ")

    def cut(self, line):
        return self.delete_stop_words(jieba.cut(line))

    def delete_stop_words(self, words):
        new_words = []
        for word in words:
            if word not in self.stop_words:
                new_words.append(word)
        return " ".join(new_words)

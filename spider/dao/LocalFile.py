class LocalFile:

    def save(self, line):
        if len(line) > 1:
            file = open("../test/data/train_test.txt", "a", encoding="utf-8")
            file.write(line + "\n")
            file.close()


if __name__ == '__main__':
    localFile = LocalFile()
    localFile.save("a")

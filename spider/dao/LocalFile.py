class LocalFile:

    def save(self, line):
        file = open("../test/data/train_test.txt", "a+")
        file.write(line + "\n")
        file.close()


if __name__ == '__main__':
    localFile = LocalFile()
    localFile.save("aaaaaaaaa")
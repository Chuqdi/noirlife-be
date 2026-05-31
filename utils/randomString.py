import random, string


class GenerateRandomString(object):
    @staticmethod
    def randomAlhanumeric(length):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))
    @staticmethod
    def randomStringGenerator(length):
        letter = ""
        array =[]
        for i in range(length):
            o =intg(array)
            array.append(str(o))
        out = letter.join(array)
        return out
    # @staticmethod
    # def randomStringGenerator(length):
    #     letter = ""
    #     array =[]
    #     for i in range(length):
    #         array.append(random.choice(string.ascii_lowercase))
    #     out = letter.join(array)
    #     return out


def intg(al):
    v=random.randrange(0, 10, 2)
    if v in al:
        intg(al)
    else:
        return v

class ExpressionTokenizer:

    def tokenize(expression, acceptSpace = False):
        tokens = []
        token = ''
        for char in expression:
            if char == '(' or char == ')':
                if token != '':
                    tokens.append(token)
                token = ''
                tokens.append(char)
                continue
            if char == '\'' or char == '\"':
                acceptSpace = not acceptSpace
            if char == ' ' and acceptSpace == False:
                if token != '':
                    tokens.append(token)
                token = ''
                continue
            else:
                token = token + char
        if token != '':
            tokens.append(token)
        return tokens
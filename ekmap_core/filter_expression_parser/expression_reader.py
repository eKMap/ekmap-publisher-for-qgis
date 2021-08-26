class ExpressionReader:

    priorityComparision = ['=']
    andOrComparision = ['OR']
    operations = []
    operations.extend(priorityComparision)
    operations.extend(andOrComparision)

    def read(expression):
        lst = ExpressionReader.__split(expression)
        #lst = ExpressionReader.__parsePriorityExpression(lst, ExpressionReader.priorityComparision)
        #lst = ExpressionReader.__parseExpression(lst)
        return lst

    def __split(expression):
        lst = []
        chars = ''
        acceptSpace = False
        for char in expression:
            if char == '(' or char == ')':
                if chars != '':
                    lst.append(chars)
                chars = ''
                lst.append(char)
                continue
            if char == '\'' or char == '\"':
                acceptSpace = not acceptSpace
            if char == ' ' and acceptSpace == False:
                if chars != '':
                    lst.append(chars)
                chars = ''
                continue
            else:
                chars = chars + char
        if chars != '':
            lst.append(chars)
        return lst

    def __parsePriorityExpression(lst, operations):
        newLst = []
        for i in range(0, len(lst) - 1):
            if lst[i] in operations:
                arguments = []
                arguments.append(lst[i-1])
                operation = lst[i]
                arguments.append(lst[i+1])
                dataDriven = ExpressionReader.toDataDrivenStyle(operation, arguments)
                if dataDriven is None:
                    return None
                newLst.append(dataDriven)
            elif lst[i] in ExpressionReader.operations:
                newLst.append(lst[i])
        return newLst

    def __parseExpression(lst):
        if lst is None:
            return None
        while len(lst) > 1:
            arguments = []
            arguments.append(lst.pop(0))
            operation = lst.pop(0)
            arguments.append(lst.pop(0))

            dataDriven = ExpressionReader.toDataDrivenStyle(operation, arguments)
            if dataDriven is None:
                return None
            lst.insert(0, dataDriven)
        return lst

    def toDataDrivenStyle(operation, arguments):
        if operation == '=':
            return '[\"==\",[\"get\",\"' + arguments[0] + '\"],' + arguments[1] + ']'
        if operation == 'OR':
            return '[\"any\",' + arguments[0] + ',' + arguments[1] + ']'
        return None

# subset = 'loaiDatHT = \'CAN\' OR loaiDatHT = \'COC\' OR loaiDatHT = \'CQP\' OR loaiDatHT = \'DBV\' OR loaiDatHT = \'DCK\' OR loaiDatHT = \'DCH\' OR loaiDatHT = \'DDT\' OR loaiDatHT = \'DGD\' OR loaiDatHT = \'DKH\' OR loaiDatHT = \'DNL\' OR loaiDatHT = \'DSH\' OR loaiDatHT = \'DSN\' OR loaiDatHT = \'DTS\' OR loaiDatHT = \'DTT\' OR loaiDatHT = \'DVH\' OR loaiDatHT = \'DXH\' OR loaiDatHT = \'DYT\' OR loaiDatHT = \'SKC\' OR loaiDatHT = \'SKK\' OR loaiDatHT = \'SKN\' OR loaiDatHT = \'SKX\' OR loaiDatHT = \'TIN\' OR loaiDatHT = \'TMD\' OR loaiDatHT = \'TON\' OR loaiDatHT = \'TSC\' OR loaiDatHT = \'TSN\' OR loaiDatHT = \'SKX\' OR loaiDatHT = \'DRA\' OR loaiDatHT = \'NTD\''
# print(ExpressionReader.read(subset))
testIn = '\"loaiDatHT\" in (\'DGT\')'
print(ExpressionReader.read(testIn))
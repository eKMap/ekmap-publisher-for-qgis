EUQ_PATTERN = '(.*) = (.*)'
IN_PATTERN = '(.*) in (.*)'
NOT_NULL_PATTERN = "(.*) is not null"

import re

class FilterParser():

    def parse(filterExpression):
        if re.match(EUQ_PATTERN, filterExpression):
            return FilterParser._parseEuq(filterExpression)
        elif re.match(IN_PATTERN, filterExpression):
            return FilterParser._parseIn(filterExpression)
        elif re.match(NOT_NULL_PATTERN, filterExpression):
            return FilterParser._parseNotNull(filterExpression)
        else:
            return None

    def _parseNotNull(filterExperssion):
        property = filterExperssion.split(" ")[0].strip().strip("\"")
        return [
            "!=",
            [
                "get",
                property
            ],
            None
        ]

    def _parseEuq(filterExpression):
        filterObj = {}
        # Filter có dạng "{Tên trường} = {Giá trị}"
        # Tạm thời hỗ trợ type Equal
        filterType = "="
        filterExps = filterExpression.split(filterType) # filterExpression.split(" ")
        if len(filterExps) != 2:
            return None
        filterObj["property"] = filterExps.pop(0).replace("\"","").strip()
        filterObj["type"] = filterType #filterExps.pop(0)

        # Giá trị có thể có khoảng trắng ở giữa
        # Bỏ đi dấu nháy ở đầu
        filterObj["value"] = " ".join(filterExps).replace("'","").strip()
        return [
            "==",
            [
                "get",
                filterObj["property"]
            ],
            filterObj["value"]
        ]
    
    def _parseIn(filterExpression):
        # Filter có dạng "{Tên trường} in ({Giá trị 1}, {Giá trị 2}, ... {Giá trị n})"
        # Tạm thời hỗ trợ type Equal
        filterType = " in "
        filterExps = filterExpression.split(filterType) # filterExpression.split(" ")
        if len(filterExps) != 2:
            return None
        property = filterExps[0].replace("\"","").strip()

        # Giá trị có thể có khoảng trắng ở giữa
        # Bỏ đi dấu nháy ở đầu
        values = filterExps[1].strip().strip('(').strip(')').replace("\'","").split(',')
        return [
            "in",
            [
                "get",
                property
            ],
            [
                "literal",
                values
            ]
        ]
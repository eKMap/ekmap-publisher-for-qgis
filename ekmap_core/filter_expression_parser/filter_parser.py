
class FilterParser():

    def parse(filterExpression):
        filterObj = {}
        # Filter có dạng "{Tên trường} {Filter} {Giá trị}"
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
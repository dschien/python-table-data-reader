from table_data_reader import OpenpyxlTableHandler


class TableWriter(OpenpyxlTableHandler):

    def __init__(self, workbook_path=None, worksheet=None):
        self.worksheet = worksheet
        self.workbook = workbook_path

    def update_table(self, data) -> None:
        """
        iterate over all cells, if the variable name is identical, then overwrite all cells defined in a record
        :param data:
        :return:
        """

        def update_row_visitor():

            self.table_visitor(self.workbook, self.worksheet, update_row_visitor)

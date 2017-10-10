class DBException(Exception):
    pass

class ReferenceException(DBException):
    def __init__(self, violated_column):
        DBException.__init__(self, "Reference violation of {}".format(violated_column))

class NoRowException(DBException):
    def __init__(self):
        DBException.__init__(self, "Row not found")

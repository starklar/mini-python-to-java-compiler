class TAC(object):
    """
    An object that represents a single TAC instruction.
    """
    def __init__(self, result, operator=None, left_operand=None, right_operand=None):
        self.result = result
        self.operator = operator
        self.left_operand = left_operand
        self.right_operand = right_operand
    
    def print_indented(self, string):
        print("    {}".format(string))

    def __str__(self):
        if self.operator is None:
            return "{} <- {}".format(self.result, self.left_operand)
        elif self.operator in ["and", "or", "==", "!=", "+", "-", "*", "/", "%", "**", "//", ">", "<", ">=", "<="]:
            if self.right_operand is not None:
                return "{} <- {} {} {}".format(self.result, self.left_operand, self.operator, self.right_operand)
            else:
                return "{} <- {} {}".format(self.result, self.operator, self.left_operand)
        elif self.operator == "fdef":
            return "func-def {} {}".format(self.left_operand, self.right_operand)
        elif self.operator == "if":
            return "if {}".format(self.left_operand)
        elif self.operator == "else-if":
            return "else-if {}".format(self.left_operand)
        elif self.operator == "else":
            return "else"
        elif self.operator == "while":
            return "while {}".format(self.left_operand)
        elif self.operator == "end-label":
            return "end"
        elif self.operator == "print":
            return "print {}".format(self.left_operand or "")
        elif self.operator == "return":
            return "return {}".format(self.left_operand or "")
        elif self.operator == "fcall":
            return "{} <- func-call {} {}".format(self.result, self.left_operand, self.right_operand)
        elif self.operator == "index":
            return "{} <- index {} {}".format(self.result, self.left_operand, self.right_operand)
        elif self.operator == "slice":
            start = self.right_operand[0]
            end = self.right_operand[1]
            step = self.right_operand[2]
            return "{} <- slice {} [{}:{}:{}]".format(self.result, self.left_operand, start or "", end or "", step or "")
        elif self.operator == "mcall":
            return "{} <- method-call {} {}".format(self.result, self.left_operand, self.right_operand)
        else:
            return "{} <- {} {} {}".format(self.result, self.operator, self.left_operand, self.right_operand)
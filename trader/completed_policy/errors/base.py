class CompletedPolicy(Exception):
    def __init__(self):
        Exception.__init__(self)
    def __str__(self):
        return "some error in completed-policy"

class UndefinedCompletedPolicyID(CompletedPolicy):
    def __init__(self):
        CompletedPolicy.__init__(self)
    def __str__(self):
        return "undefined completed-policy ID"

class UseForbiddenCompletedPolicyID(CompletedPolicy):
    def __init__(self):
        CompletedPolicy.__init__(self)
    def __str__(self):
        return "the completed-policy class defined by its id is forbidden to use"

class MethodIsNotImplemented(CompletedPolicy):
    def __init__(self):
        CompletedPolicy.__init__(self)
    def __str__(self):
        return "some method is not implemented in the completed-policy class instance"

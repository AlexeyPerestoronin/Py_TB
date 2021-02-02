# brief: presents some exception in completed-policy
class CompletedPolicy(Exception):
    def __init__(self):
        Exception.__init__(self)
    def __str__(self):
        return "some error in completed-policy"

# brief: exception of undefined completed-policy ID
class UndefinedCompletedPolicyID(CompletedPolicy):
    def __init__(self):
        CompletedPolicy.__init__(self)
    def __str__(self):
        return "undefined completed-policy ID"

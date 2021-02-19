import trader.completed_policy as trader_cp
import trader.completed_policy.errors as error

# brief: identifies completed-policy-class by its ID
# param: id - target identificator
# return: instance of identified completed-policy-class
def DefineCompletePolicy(id):
    if trader_cp.BaseCS.GetID() == id:
        raise error.UseForbiddenCompletedPolicyID()
    elif trader_cp.InfinityCP.GetID() == id:
        return trader_cp.InfinityCP()
    else:
        raise error.UndefinedCompletedPolicyID()

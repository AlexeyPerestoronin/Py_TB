import trader.completed_policy as t_cp
import trader.completed_policy.const.errors as t_cp_errors

# brief: identifies completed-policy-class by its ID
# param: id - target identificator
# return: instance of identified completed-policy-class
def DefineCompletePolicy(id):
    if t_cp.FixedCompletedStrategy.GetID() == id:
        return t_cp.FixedCompletedStrategy()
    else:
        raise t_cp_errors.UndefinedCompletedPolicyID()

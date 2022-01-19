def g_F_bound1(model, f, t):
    return model.g_F[f, t] <= cap_non_re[0]
model.g_F_bound_const1 = Constraint(F, T, rule=g_F_bound1)
#############################################################
# CIS510 MultiAgent Systems Final Project Code
# Adib Mosharrof, Trevor Bergstrom
# MILP File Runs the CPLEX solver
#############################################################

import math
from itertools import combinations
import cplex
import copy
import random

class Milp:
    number_resources = None
    feasible_paths = []
    number_targets = None

    def __init__(self, gp, number_resources):
        self.feasible_paths = gp.feasible_paths
        self.number_resources = number_resources
        self.number_targets = gp.grid_size * gp.grid_size
        self.play_grid = gp.grid
        self.path_combs = self.get_path_combinations()
        self.num_x = len(self.path_combs)
        self.num_y = self.number_targets
        self.num_z = self.number_targets
        self.index_paths = self.convert_paths()
        self.payoff_mat = self.generate_payoffs()
        self.M_var = 1000.0

    def print_strats(self):
        comb = self.get_path_combinations()
        for i in range(len(comb)):
            print("Combination #" + str(i))
            for j in range(len(comb[i])):
                print("For defender #" + str(j))
                print(comb[i][j])
                print("\n")
            print("\n")

    def get_path_combinations(self):
        return list(combinations(self.feasible_paths, self.number_resources))

    def convert_paths(self):
        indexed_paths = []
        combs = self.get_path_combinations()

        for i in range(len(combs)): #each combination of paths
            path_comb = []
            for j in range(len(combs[i])): #each defender resource has a path
                def_path = []
                for k in range(len(combs[i][j])):
                    x = combs[i][j][k].x
                    y = combs[i][j][k].y
                    idx  = int((math.sqrt(self.number_targets) * y) + x)
                    def_path.append(idx)
                path_comb.append(def_path)
            indexed_paths.append(path_comb)

        return indexed_paths;

    def generate_payoffs(self):
        payoff_mat = []

        for i in range(len(self.play_grid)):
            for j in range(len(self.play_grid[i])):
                payoff_mat.append(self.play_grid[i][j].animal_density)
        return payoff_mat;

    def get_obj(self):
        # objective function is to maximize vdef, but we need to fill in zeroes for all x's, z's, and y's as well as vatt

        my_obj = []
        for i in range(self.num_z + self.num_y + self.num_x):
            my_obj.append(0.0)

        my_obj.append(1.0)
        my_obj.append(0.0)

        return my_obj;

    def get_ub(self):
        # All upper bounds for the x's, y's, and z's are 1. Vdef and Vatt are cplex.inf

        my_ub = []

        for i in range(self.num_z + self.num_y + self.num_x):
            my_ub.append(1.0)

        my_ub.append(cplex.infinity)
        my_ub.append(cplex.infinity)

        return my_ub;

    def get_lb(self):
        # All lower bounds for the x's, y's, and z's are 0. Vdef and Vatt are neg cplex.inf

        my_lb = []

        for i in range(self.num_z + self.num_y + self.num_x):
            my_lb.append(0.0)

        my_lb.append(-1 * cplex.infinity)
        my_lb.append(-1 * cplex.infinity)

        return my_lb;

    def get_ctypes(self):
        # C_types: "I" is an integer value, "C" is continious non integer value. All Z's are C, everything else is a I

        my_ctypes = ""

        for i in range(self.num_z):
            my_ctypes += "I"

        for i in range(self.num_y + self.num_x + 2):
            my_ctypes += "C"

        return my_ctypes;

    def get_col_names(self):
        # columns like z(i), y(i), x(i), vdef, vatt

        col_names = []

        for i in range(self.num_z):
            col_names.append("z" + str(i+1))

        for i in range(self.num_y):
            col_names.append("y" + str(i+1))

        for i in range(self.num_x):
            col_names.append("x" + str(i+1))

        col_names.append("v_def")
        col_names.append("v_att")

        return col_names;

    def get_rhs(self):

        my_rhs = []
        # the first row is the sum of the z's
        my_rhs.append(1.0)

        # the next row is the x's which equal the number of defender resources
        #my_rhs.append(float(self.number_resources))

        my_rhs.append(1.0)

        # next rows will encompas all the y's which in the form y1 + x1...xm = 0
        for i in range(self.number_targets):
            my_rhs.append(0.0)

        # next we'll do the defender's utility constraint set, # constraints should be # of targets

        for i in range(self.number_targets):
            my_rhs.append( self.M_var + float((-1 * self.payoff_mat[i])))

        # next we need the attacker's strategy constraint set, same as number of targets:
        for i in range(self.number_targets):
            my_rhs.append(self.payoff_mat[i]) # Uatt_uncovered

        # next is attacker utility constraint set:
        for i in range(self.number_targets):
            my_rhs.append(self.M_var + self.payoff_mat[i])

        return my_rhs;

    def get_row_names(self):
        #cplex needs row names. We need figure out how many rows
       # there's the y values, defender's utility, attacker's strategy, and attackers strategy constraints. Then we have our sum of x's and sum of z's

        num_rows = (4 * self.number_targets) + 2
        my_row_names = []
        for i in range(num_rows):
            my_row_names.append("r" + str(i))

        return my_row_names;

    def get_sense(self):
        # cplex uses the sense to designate the inequality/ equality sign of each constraint. These are E,G,L. Must return string

        my_sense = ""

        my_sense += "E" # sum of z must be exactly 1

        my_sense += "E" # sum of all the x's must be an equality? <----------------- !!! Check this !!! <--------------------

        # y constraints are next. These are also equals
        for i in range(self.num_y):
            my_sense += "E"

        # next up are the defender's utility constraints.
        for i in range(self.number_targets):
            my_sense += "L"

        # next we need the attacker strategy constraints
        for i in range(self.number_targets):
            my_sense += "G"

        # lastly we have the attacker's utility constraints
        for i in range(self.number_targets):
            my_sense += "L"

        return my_sense;

    def get_rows(self):
        ''' this function needs to list all the rows in the following format:
        [ [ [var_names], [var_coeffecients] ], ..............]
        '''

        rows_list = []
        z_list = []
        z_coef = []
        x_list = []
        x_coef = []

        # the z constaint is the sum of all z, with a 1.0 coef for all
        for i in range(self.num_z):
            z_list.append("z" + str(i+1))
            z_coef.append(1.0)

        rows_list.append([z_list, z_coef])

        for i in range(self.num_x):
            x_list.append("x" + str(i+1))
            x_coef.append(1.0)

        rows_list.append([x_list, x_coef])


        y_list = []
        y_coef = []

        # next we need to deal with our y vars...
        for i in range(self.num_y):
            y_list.append("y" + str(i+1))
            y_coef.append(1.0)

            x_list = self.populate_y_rows(i)

            for j in range(len(x_list)):
                y_list.append(x_list[j])
                y_coef.append(-1.0)

            rows_list.append([copy.deepcopy(y_list), copy.deepcopy(y_coef)])
            y_list.clear()
            y_coef.clear()

        # next deal with the defender's utility constraints
        def_util_vars = []
        def_util_coef = []

        for i in range(self.number_targets):
            def_util_vars = (["v_def", ("y" + str(i+1)), ("z" + str(i+1))])
            def_util_coef = ([1.0, float(((-1 * self.payoff_mat[i]) - self.payoff_mat[i])), self.M_var])

            rows_list.append([copy.deepcopy(def_util_vars), copy.deepcopy(def_util_coef)])
            def_util_vars.clear()
            def_util_coef.clear()

         # next deal with the attacker's strategy constraints
        att_strat_vars = []
        att_strat_coef = []

        for i in range(self.number_targets):
            att_strat_vars = (["v_att", ("y" + str(i+1))])
            att_strat_coef = ([1.0, float((self.payoff_mat[i] - (-1 * self.payoff_mat[i])))])

            rows_list.append([copy.deepcopy(att_strat_vars), copy.deepcopy(att_strat_coef)])
            att_strat_vars.clear()
            att_strat_coef.clear()

        # next deal with the attacker's utility constraints
        att_util_vars = []
        att_util_coef = []

        for i in range(self.number_targets):
            att_util_vars = (["v_att", ("y" + str(i+1)), ("z" + str(i+1))])
            att_util_coef = ([1.0, float((self.payoff_mat[i] - (-1 * self.payoff_mat[i]))), self.M_var])

            rows_list.append([copy.deepcopy(att_util_vars), copy.deepcopy(att_util_coef)])
            att_util_vars.clear()
            att_util_coef.clear()

        return rows_list;

    def populate_y_rows(self, y_number):
        # give the y number and search all the path combinations for the y, if its found append to a list of x's
        x_list = []
        for i in range(len(self.index_paths)): # now we are searching though each path combo
            is_y = False
            for j in range(len(self.index_paths[i])): #search each path in the combo
                for k in range(len(self.index_paths[i][j])): # search though each path
                    if self.index_paths[i][j][k] == y_number:
                        is_y = True
            if is_y == True:
                x_list.append("x" + str(i+1))

        return x_list;

    def run_cplex(self):
        '''
        Needed for cplex:
            objective function
            upper bounds
            lower bounds
            c_types
            column_names
            right hand sides
            rows
            row names
            sense
        '''
        my_obj = self.get_obj()

        my_ub = self.get_ub()

        my_lb = self.get_lb()

        my_ctypes = self.get_ctypes()

        my_col_names = self.get_col_names()

        my_rhs = self.get_rhs()

        my_row_names = self.get_row_names()

        my_sense = self.get_sense()

        my_rows = self.get_rows()
       # set up cplex

        prob = cplex.Cplex()
        prob.objective.set_sense(prob.objective.sense.maximize)
        prob.variables.add(obj=my_obj, lb=my_lb, ub=my_ub, types=my_ctypes, names=my_col_names)
        prob.linear_constraints.add(lin_expr=my_rows, senses=my_sense, rhs=my_rhs, names=my_row_names)
        prob.solve()

        print("Solution status = " + str(prob.solution.get_status()) + ":")
        print(str(prob.solution.status[prob.solution.get_status()]))
        sol_val = ("Solution value = " + str(prob.solution.get_objective_value()))
        print(sol_val)

        numcols = prob.variables.get_num()
        numrows = prob.linear_constraints.get_num()

        slack = prob.solution.get_linear_slacks()
        x = prob.solution.get_values()

        x_val_list = []
        sol_idx = []
        for j in range(numcols):
            if my_col_names[j][0] == 'x' and x[j] != 0.0:
                x_val = (my_col_names[j] + " = " + str(x[j]))
                print(x_val)
                x_val_list.append(x_val)
                sol_idx.append(j)

        print("")
        return x_val_list, sol_val, sol_idx;

    def get_idx_paths(self):
        return self.index_paths;

    def print_all(self):
        print(self.get_obj())
        print(self.get_ub())
        print(self.get_lb())
        print(self.get_ctypes())
        print(self.get_col_names())
        rhs = self.get_rhs()
        print(rhs)
        print(str(len(rhs)))
        print(self.get_row_names())
        print(self.get_sense())
        print(self.get_rows())

    def print_problem(self):
        my_obj = self.get_obj()

        my_ub = self.get_ub()

        my_lb = self.get_lb()

        my_ctypes = self.get_ctypes()

        my_col_names = self.get_col_names()

        my_rhs = self.get_rhs()

        my_row_names = self.get_row_names()

        my_sense = self.get_sense()

        my_rows = self.get_rows()
        #print("rows len = " + str(len(my_rows)))
        #for i in range(len(my_rows)):
            #print(my_rows[i])

        obj_state = "Objective Statement: maximize "
        for i in range(len(my_obj)):
            if my_obj[i] != 0.0:
                obj_state += my_col_names[i]

        print(obj_state)

        for i in range(len(my_col_names)):
            cons = ""
            cons += str(my_lb[i])
            cons += " < "
            cons += str(my_col_names[i])
            cons += " < "
            cons += str(my_ub[i])
            cons += ", "

            if my_ctypes[i] == "I":
                cons += "Integers"
            else:
                cons += "mixed numbers"

            print(cons)

        for i in range(len(my_row_names)):
            cons = ""
            cons += str(my_row_names[i])
            cons += ": "

            for j in range(len(my_rows[i][0])):
                cons += "("
                cons += str(my_rows[i][1][j])
                cons += ")"
                cons += str(my_rows[i][0][j])
                if j != (len(my_rows[i][0]) - 1):
                    cons += " + "

            if my_sense[i] == "E":
                cons += " = "
            elif my_sense[i] == "G":
                cons += " > "
            else:
                cons += " < "

            cons += str(my_rhs[i])

            print(cons)

    def select_baseline(self):
        num_paths = len(self.index_paths)

        path_idx = random.randint(0, num_paths-1)

        new_path_list = [self.index_paths[path_idx]]

        self.index_paths = new_path_list

    def start(self, baseline):

        if baseline == True:
            self.select_baseline()

        x_vals = self.run_cplex()

        return x_vals;

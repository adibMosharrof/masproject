##############################################################
# CIS510 Final Project
# Adib Mosharrof, Trevor Bergstrom
# This is the main file. use --help for use options.
##############################################################

import grid
import milp as milp_file
import copy as dc
import sys
import csv

class Program:
    def init(self, grid_sz, num_resources, max_len, c_grid, st_pt, out_file, baseline):
        gp = grid.GeneratePaths()

        gp.init_grid(grid_sz, max_len, c_grid)
        gp.generate_starting_point(st_pt)
        gp.generate_routes(0, gp.starting_node, [])
        gp.print_paths(gp.feasible_paths)
        milp = milp_file.Milp(gp, num_resources)
        solutions, sol_val, sol_idx = milp.start(baseline)
        indexed_paths = milp.get_idx_paths()

        p_grid = gp.gen_print_grid()
        start = gp.gen_print_start()
        print_results(out_file, solutions, indexed_paths, p_grid, start, max_len, num_resources, sol_val, sol_idx)

def print_results(out_file, solutions, paths, print_grid, start_point, max_len, num_resources, sol_val, sol_idx):
    f = open(out_file, "w+")

    f.write("#########################################################\n")
    f.write("Build with params: \nNumber of defender resources: %d\nMax Path Length: %d\n" % (num_resources, max_len))
    f.write("Using a start point of x: %d, y: %d\n" % (start_point[0], start_point[1]))
    f.write("This is the grid used:\n")

    for i in range(len(print_grid)):
        g_string = ""
        for j in range(len(print_grid[i])):
            g_string += "["
            g_string += str(print_grid[i][j])
            g_string += "]"
        f.write(g_string + "\n")

    f.write("These are the feasible paths: \n")

    for i in range(len(paths)):
        f.write("Strategy #" + str(i+1) + "\n")
        for j in range(len(paths[i])):
            f.write("\tPath for defender resource #" + str(j+1) + ":")
            f.write(str(paths[i][j]) + "\n")


    f.write("<-------------------------------------------------->\n")

    f.write("Best defender's utility: " + str(sol_val) +"\n")
    f.write("This is the strategy:\n")
    for i in range(len(solutions)):
        f.write(solutions[i] + "\n")

    f.close()

def get_grid_size():

    grid_size = int(input ("Please enter the desired grid size "))

    return grid_size;

def get_params(grid_size):
    num_defender = int(input("Please now enter the desired number of defender resources "))
    max_len = int(input("Please enter the maximum path len "))

    starting_point = []
    good_sp = False

    print("Please enter the starting point value")
    while good_sp == False:
        x_pt = int(input("Enter x value: "))
        y_pt = int(input("Enter y value: "))

        if x_pt > grid_size-1 or x_pt < 0:
            print("Bad x value. Try again.")

        elif y_pt > grid_size-1 or y_pt < 0:
            print("Bad y value. Try again.")

        else:
            starting_point.append(x_pt)
            starting_point.append(y_pt)
            good_sp = True

    return num_defender, max_len, starting_point;

def get_grid(grid_size):

    grid = []
    row_list = []

    for i in range(grid_size):
        while len(row_list) != grid_size:
            row = input("Please enter row #" + str(i) + " ")
            row_list = row.split()

            for j in range(len(row_list)):
                row_list[j] = int(row_list[j])

            print(row_list)
            if len(row_list) != grid_size:
                print("Not enough elements in the row. Please input a row of size " + str(grid_size))

        grid.append(dc.deepcopy(row_list))
        row_list.clear()

    return grid;

def get_csv_grid(in_file):
    payoff_mat = []
    num_cols = 0
    with open(in_file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            num_cols = 0
            for i in range(len(row)):
                row[i] = int(row[i])
                num_cols += 1
            payoff_mat.append(row)

    if num_cols != len(payoff_mat):
        print("Non matching dimensions in csv file. Exiting...")
        exit()

    return payoff_mat, len(payoff_mat);

if __name__ == '__main__':

    grid_size = 5
    num_defender = 1
    c_grid = []
    start_pt = []
    max_len = 6
    run_baseline = False

    if len(sys.argv) > 1:
        if sys.argv[1] == "-cp":
            grid_size = get_grid_size()
            num_defender, max_len, start_pt = get_params(grid_size)
        elif sys.argv[1] == "-cg":
            grid_size = get_grid_size()
            num_defender, max_len, start_pt = get_params(grid_size)

            correct_grid = False

            while correct_grid == False:
                c_grid = get_grid(grid_size)
                print(c_grid)

                correct_grid_in = input("Does this grid look correct?: [y/n] ")

                if correct_grid_in == "y":
                    correct_grid = True
                else:
                    print("Ok... let's try that again")
        elif sys.argv[1] == "-csv":
            in_file = input("Please enter a input grid file name ")

            c_grid, grid_size = get_csv_grid(in_file)
            num_defender, max_len, start_pt = get_params(grid_size)

        elif sys.argv[1] == "-bl":
            in_file = input("Please enter a input grid file name ")

            c_grid, grid_size = get_csv_grid(in_file)
            num_defender, max_len, start_pt = get_params(grid_size)
            run_baseline = True

        elif sys.argv[1] == "-help":
            print("Usage options:")
            print("[-cp] - Custom Parameters: User will be prompted to enter the parameters of the problem. A Random animal density grid will be generated.")
            print("[-cg] - Custom Grid: User will be prompted to enter the parameters of the problem, and a custom grid.")
            print("[-csv] - User will be prompted to enter a file name containing a custom grid. User will need to supply necessary parameters")
            print("[-bl] - A baseline run on a csv file will be executed. Defenders select a random path combination")
            print("[no flags] - Random grid will be generated, with preset parameters.")
            print("[-help] - Flag options will be displayed.")
            exit()
        else:
            print("Incorrect usage. Use -help for options.")
    else:
        print("Running with random values")

    out_file = input("Please enter and output text file name to save your results ")

    program = Program()
    program.init(grid_size, num_defender, max_len, c_grid, start_pt, out_file, run_baseline)
    print("Please check the output file for results and problem overview")

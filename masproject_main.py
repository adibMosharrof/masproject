import grid
import milp as milp_file

class Program:
    def init(self):
        gp = grid.GeneratePaths()


        gp.init_grid()
        gp.generate_starting_point()
        gp.generate_routes(0, gp.starting_node, [])
        gp.print_paths(gp.feasible_paths)
        milp = milp_file.Milp(gp, 2)
        #milp = milp_file.Milp(gp.feasible_paths, 2, gp.grid_size)
        milp.start()

if __name__ == '__main__':
    program = Program()
    program.init()

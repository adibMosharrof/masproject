import random
import collections
import sys
import copy

class Cell:
    x = 0
    y = 0
    animal_density = 0
    has_been_visited = False

    def __init__(self, x, y, animal_density):
        self.x = x
        self.y = y
        self.animal_density = animal_density

    def __str__(self):
        return "X: %s, Y:%s, AnimalDensity:%s, HasBeenVisited:%s" % (self.x, self.y, self.animal_density, self.has_been_visited)

    def __repr__(self):
        return "(X:%s, Y:%s) " % (self.x, self.y)

    def __hash__(self):
        return hash(str(self))

    def __eq__(self,other):
        return self.x == other.x and self.y == other.y


class GeneratePaths:
    grid = []
    starting_node = None
    max_route_length = 6
    feasible_paths = []
    grid_size = 5

    def init_grid(self):
        for i in range(self.grid_size):
            row = []
            for j in range(self.grid_size):
                row.append(Cell(i,j, random.randint(1,10)))
            self.grid.append(row)

    def generate_starting_point(self):
        starting_x = random.randint(0,self.grid_size-1)
        starting_y = random.randint(0,self.grid_size-1)
        #self.starting_node = self.grid[starting_x][starting_y]
        self.starting_node = self.grid[0][0]

    def generate_routes(self, depth, node, path):
        #add current node to path and mark it as visited
        node.has_been_visited = True
        path.append(node)

        #check if we have come to the starting node again
        #this means that a route has been created
        if self.does_starting_node_exist_twice_in_path(path):
            if self.does_path_cover_same_cells(path, self.feasible_paths) is False:
                self.feasible_paths.append(copy.deepcopy(path))
        elif depth < self.max_route_length:
            #get adjacent nodes that are not in the path being generated
            nodes_to_expand = self.get_nodes_to_expand(node, path)
            for next_node in nodes_to_expand:
                #increase depth by expanding a node
                self.generate_routes(depth+1, next_node, path )

        #remove the current node to track back and find more paths
        path.pop()
        #mark it as not visited, so that it can be reused to generate a different path
        node.has_been_visited = False

    def get_nodes_to_expand(self, node, path):
        nodes_to_expand = []
        #left_node
        self.add_node_to_expansion_list(node.x-1,node.y, nodes_to_expand, path)
        #right_node
        self.add_node_to_expansion_list(node.x+1,node.y, nodes_to_expand, path)
        #top_node
        self.add_node_to_expansion_list(node.x,node.y+1, nodes_to_expand, path)
        #bottom_node
        self.add_node_to_expansion_list(node.x,node.y-1, nodes_to_expand, path)
        return nodes_to_expand

    def add_node_to_expansion_list(self, x, y, nodes_to_expand, path):
        if x<0 or y <0 or x is self.grid_size or y is self.grid_size:
            return
        cell = self.grid[x][y]
        if cell is not self.starting_node:
            if cell in path:
                return
        nodes_to_expand.append(cell)

    def does_path_cover_same_cells(self, path, feasible_paths):
      for p in feasible_paths:
        if collections.Counter(p) == collections.Counter(path):
          return True
      return False

    def does_starting_node_exist_twice_in_path(self, path):
        return path.count(self.starting_node) is 2

    def print_paths(self, paths):
        if type(paths[0]) is list:
            for path in paths:
                self.print_paths(path)
        else:
            grid = []
            for i in range(self.grid_size):
                row = []
                for j in range(self.grid_size):
                    row.append('.')
                grid.append(row)
            for point in paths:
                grid[point.x][point.y] = 'x'
            output = ""
            for i in range(self.grid_size):
                row = ""
                for j in range(self.grid_size):
                    row += grid[i][j]
                output = row + '\n'+ output
            print(output+"\n")



# if __name__ == '__main__':
#     gp = GeneratePaths()
#     gp.init_grid()
#
#     gp.generate_starting_point()
#     print('starting node', gp.starting_node)
#     gp.generate_routes(0, gp.starting_node, [])
#     print('Num of feasible paths', len(gp.feasible_paths))
#     gp.print_paths(gp.feasible_paths)



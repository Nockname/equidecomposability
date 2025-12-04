from convexpart import ConvexPart
import math
import random
import matplotlib.pyplot as plt
from utilities import CCW, find_line_intersection
from constants import PRECISION

def slope_and_intercept(p1, p2):
    slope = (p2[1] - p1[1]) / (p2[0] - p1[0] + 1e-9)
    y_intercept = p1[1] - slope * p1[0]
    return slope, y_intercept

# general random triangles with fixed area
def create_triangle(area):

    base = random.gammavariate(5, 50) + 20
    height = 2 * area / base
    
    A = (0, 0)
    B = (base, 0)
    C = (random.random() * base, height)
    
    information = {
        "type": "axis-aligned-triangle",
        "base": base,
        "height": height,
        "peak_x_coord": C[0]
    }
    
    return Shape([A, B, C], information=information)

def create_pair_of_triangles(area):
    triangle1 = create_triangle(area)
    triangle2 = create_triangle(area)
    # ratio = triangle1.information["base"] / triangle2.information["base"]

    # ensure triangle 1 has smaller base than triangle 2
    if triangle1.information["base"] > triangle2.information["base"]:
        triangle1, triangle2 = triangle2, triangle1
    max_base = triangle2.information["base"]
    
    return triangle1, triangle2

# returns if P is in the closure of a triangle
def in_triangle(triangle, P):
    A, B, C = triangle

    ab = CCW(A, B, P)
    bc = CCW(B, C, P)
    ca = CCW(C, A, P)

    if ab == 0 or bc == 0 or ca == 0:
        return True

    return (ab == bc and bc == ca)
        
class Shape:
    
    def __init__(self, points, rotation = 0, translation = (0, 0), information = None):
        
        self.parts = [ConvexPart(points, rotation, translation)]
        
        self.cuts = []
        for i in range(len(points)):
            p1 = points[i]
            p2 = points[(i + 1) % len(points)]
            self.cuts.append(slope_and_intercept(p1, p2))
            
        self.information = information
        
    # rotates parts, which is list of indices of parts to rotate
    def rotate(self, parts, angle):
        for i in parts:
            self.parts[i].rotate(angle)
    
    # translates parts, which is list of indices of parts to translate
    def translate(self, parts, dx, dy):
        for i in parts:
            self.parts[i].translate(dx, dy)
      
    # cuts shape along line  
    def cut(self, line):
        
        slope, y_intercept = slope_and_intercept(line[0], line[1])
        if not all(abs(slope - m) > PRECISION or abs(y_intercept - b) > PRECISION for m, b in self.cuts):
            return
        
        self.cuts.append((slope, y_intercept))
        new_parts = []   
            
        for part in self.parts:     
            result = part.intersect_transformed_with_line(line)
            if result is False:
                new_parts.append(part)
                continue
            
            part1, part2 = result
            new_parts.append(part1)
            new_parts.append(part2)
            
        self.parts = new_parts
    
    # visualizes the shape
    def visualize(self, transformed = True, amount = 1):
        
        plt.figure(figsize=(8, 8))
        
        for i, part in enumerate(self.parts):
            
            if transformed:
                points = part.get_transformed_points(amount)
            else:
                points = part.points
        
            
            polygon = plt.Polygon(points, alpha=0.3, label=f"Part {i+1}")
            color = plt.cm.tab10(i % 10)  # Use a colormap to assign colors based on part index
            polygon = plt.Polygon(points, alpha=0.3, label=f"Part {i+1}", color=color)
            plt.gca().add_patch(polygon)
            
            points.append(points[0])  # close the polygon
            x, y = zip(*points)
            plt.plot(x, y)
            
        plt.legend()
        plt.grid(True)
        plt.axis("equal")
        plt.title("Shape Visualization")
        plt.show()
        
    # returns the indices of all parts whose transformed center point is inside the given triangle
    def parts_inside_triangle(self, triangle):
        inside_parts = []
        for i, part in enumerate(self.parts):
            transformed_points = part.get_transformed_points()
            center_point = (sum(x for x, y in transformed_points) / len(transformed_points),
                            sum(y for x, y in transformed_points) / len(transformed_points))
            
            if in_triangle(triangle, center_point):
                inside_parts.append(i)
        
        return inside_parts
        
    # assumes triangle is axis-aligned with base on x-axis, vertex at origin, height upwards
    def triangle_to_rectangle(self, extra_information = False):
        
        if self.information["type"] != "axis-aligned-triangle":
            raise ValueError("Triangle must be axis-aligned with base on x-axis and vertex at origin")
        
        height = self.information["height"]
        base = self.information["base"]
        peak_x_coord = self.information["peak_x_coord"]
        
        cut1 = ((0, height / 2), (base, height / 2))
        cut2 = ((peak_x_coord, height / 2), (peak_x_coord, height))
        
        self.cut(cut1)
        self.cut(cut2)
        
        left_parts = self.parts_inside_triangle([
            (0, height / 2),
            (peak_x_coord, height / 2), 
            (peak_x_coord, height + 1)
        ])
        self.rotate(left_parts, -math.pi)
        self.translate(left_parts, peak_x_coord, height)
        
        right_parts = self.parts_inside_triangle([
            (base + 1, height / 2),
            (peak_x_coord, height / 2),
            (peak_x_coord, height + 1)
        ])
        self.rotate(right_parts, -math.pi)
        self.translate(right_parts, (base + peak_x_coord), height)
        
        self.information = {
            "type": "rectangle",
            "width": base,
            "height": height / 2
        }
                
        if extra_information:
            return base, height / 2, peak_x_coord
        return base, height / 2
    
    def cut_rectangle_to_rectangle_once(self, target_width):
        
        if self.information["type"] != "rectangle":
            raise ValueError("Shape must be a rectangle")
        
        width = self.information["width"]
        height = self.information["height"]
        
        if width >= target_width:
            return
        
        target_height = (height * width) / target_width
        cut1 = ((0, height), (target_width, 0))
        
        line2 = ((-1, target_height), (width, target_height))
        intersection = find_line_intersection(cut1, line2)
        cut2 = ((-1, target_height), (intersection[0] + 0.1, intersection[1]))
        
        self.cut(cut1)
        self.cut(cut2)
        
        left_parts = self.parts_inside_triangle([
            (0, height),
            (0, target_height),
            intersection
        ])
        self.translate(left_parts, width, -target_height)

        
        right_parts = self.parts_inside_triangle([
            (0, height),
            (width, height),
            find_line_intersection(cut1, ((width + 1, 0), (width + 1, height + 1)))
        ]) 
        self.translate(right_parts, target_width - width, target_height - height)
        
        self.information = {
            "type": "rectangle",
            "width": target_width,
            "height": target_height
        }
            
    # assumes target_width > width
    # rectangle is the outline of the rectangle to be transformed
    # first point is bottom-left, then counter-clockwise
    def rectangle_to_fixed_width_rectangle(self, target_width):
        
        if self.information["type"] != "rectangle":
            raise ValueError("Shape must be a rectangle")
                
        width = self.information["width"]
        height = self.information["height"]
        
        if width >= target_width:
            raise ValueError("Target width must be greater than current width")
        
        while self.information["width"] < target_width / 2:
            self.cut_rectangle_to_rectangle_once(self.information["width"] * 1.5)

        self.cut_rectangle_to_rectangle_once(target_width)
    
    # assume first triangle has smaller base than second triangle
    def triangle_to_triangle(self, target_triangle):
        
        if self.information["type"] != "axis-aligned-triangle" or target_triangle.information["type"] != "axis-aligned-triangle":
            raise ValueError("Both shapes must be axis-aligned triangles")
        
        if self.information["base"] > target_triangle.information["base"]:
            raise ValueError("Source triangle must have smaller base than target triangle")
        
        target_base, target_height, target_peak_x = target_triangle.information["base"], target_triangle.information["height"], target_triangle.information["peak_x_coord"]
        self.triangle_to_rectangle()
        self.rectangle_to_fixed_width_rectangle(target_base)
        
        # cut rectangle to triangle
        cut1 = ((0, 0), (target_peak_x / 2, target_height / 2))
        cut2 = ((target_peak_x/2 + target_base/2, target_height / 2), (target_base, 0))
        
        self.cut(cut1)
        self.cut(cut2)
        
        left_parts = self.parts_inside_triangle([
            (0, 0),
            (0, target_height / 2),
            (target_peak_x / 2, target_height / 2)
        ])
        self.rotate(left_parts, -math.pi)
        self.translate(left_parts, target_peak_x, target_height)
        
        right_parts = self.parts_inside_triangle([
            (target_base/2 + target_peak_x/2, target_height / 2),
            (target_base, target_height / 2),
            (target_base, 0)
        ])
        self.translate(right_parts, -(target_base + target_peak_x), -target_height)
        self.rotate(right_parts, -math.pi)
            
        return self
    
if __name__ == '__main__':

    initial_triangle, target_triangle = create_pair_of_triangles(area=10000)
    initial_triangle.visualize(transformed=False)
    target_triangle.visualize(transformed=False)
    
    initial_triangle.triangle_to_triangle(target_triangle)
    initial_triangle.visualize(transformed=False)
    initial_triangle.visualize(transformed=True)
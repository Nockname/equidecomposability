from constants import PRECISION
from utilities import do_line_segments_intersect, find_line_intersection
import math

class ConvexPart:
    def __init__(self, points, rotation=0, translation=(0,0)):
        # in counter-clockwise order
        self.points = points 
        
        # the transformation done to the part
        # rotation around the origin in radians, followed by translation (x, y)
        self.rotation = rotation
        self.translation = translation
        
        self.remove_duplicate_points()
    
    def remove_duplicate_points(self):
        unique_points = []
        for p in self.points:
            if len(unique_points) == 0 or math.dist(p, unique_points[-1]) > PRECISION:
                unique_points.append(p)
        self.points = unique_points
    
    # find if the simple polygon intersects with the given line [(point1, point2)]
    # if so, return the two resulting polygons after the cut    
    def intersect_with_line(self, line):
        
        intersections = []
        
        for i in range(len(self.points)):
            p1 = self.points[i]
            p2 = self.points[(i + 1) % len(self.points)]

            if do_line_segments_intersect((p1, p2), line, PRECISION=PRECISION):
                intersection_point = find_line_intersection((p1, p2), line)
                if all(math.dist(intersection_point, pt) > PRECISION for _, pt in intersections):
                    intersections.append((i, intersection_point))
        
        if len(intersections) != 2:
            return False

        (i1, intersection1), (i2, intersection2) = intersections
        
        new_points1 =  self.points[:i1 + 1] + [intersection1] + [intersection2] + self.points[i2 + 1:]
        new_points2 = [intersection1] + self.points[i1 + 1:i2 + 1] + [intersection2]
        
        part1 = ConvexPart(new_points1, self.rotation, self.translation)
        part2 = ConvexPart(new_points2, self.rotation, self.translation)
        
        return part1, part2
    
    
    # apply rotation and translation to the points
    # ammount: 0 = no transform, 1 = full transform of applying rotation then translation
    # centers of mass are linearly interpolated between amount = 0 and amount = 1
    # amount between 0 and 1 is used for animation purposes
    def transform(self, points, ammount = 1):
        
        # rotate around center of mass
        cos_r = math.cos(self.rotation * ammount)
        sin_r = math.sin(self.rotation * ammount)
        
        # compute center of mass of original points
        cx = sum(x for x, y in points) / len(points)
        cy = sum(y for x, y in points) / len(points)
        
        # compute where center of mass should be at ammount=1
        cx_rot = cx * math.cos(self.rotation) - cy * math.sin(self.rotation)
        cy_rot = cx * math.sin(self.rotation) + cy * math.cos(self.rotation)
        cx_final = cx_rot + self.translation[0]
        cy_final = cy_rot + self.translation[1]
        
        # interpolate center of mass position
        cx_interp = cx + (cx_final - cx) * ammount
        cy_interp = cy + (cy_final - cy) * ammount
        
        transformed_points = []
        for (x, y) in points:
            # rotate around original center of mass
            x_centered = x - cx
            y_centered = y - cy
            x_rot = x_centered * cos_r - y_centered * sin_r
            y_rot = x_centered * sin_r + y_centered * cos_r
            # place at interpolated center position
            x_final = x_rot + cx_interp
            y_final = y_rot + cy_interp
            transformed_points.append((x_final, y_final))
        return transformed_points
    
    def inverse_transform(self, points):
        # apply inverse translation and rotation to the points
        cos_r = math.cos(-self.rotation)
        sin_r = math.sin(-self.rotation)
        
        inverse_transformed_points = []
        for (x, y) in points:
            x_trans = x - self.translation[0]
            y_trans = y - self.translation[1]
            x_rot = x_trans * cos_r - y_trans * sin_r
            y_rot = x_trans * sin_r + y_trans * cos_r
            inverse_transformed_points.append((x_rot, y_rot))
        return inverse_transformed_points
    
    def get_transformed_points(self, ammount = 1):
        return self.transform(self.points, ammount)
    
    def translate(self, dx, dy):
        self.translation = (self.translation[0] + dx, self.translation[1] + dy)
    
    # rotation in radians
    def rotate(self, angle):
        self.rotation += angle
        
        # update translation
        cos_r = math.cos(angle)
        sin_r = math.sin(angle)
        x_new = self.translation[0] * cos_r - self.translation[1] * sin_r
        y_new = self.translation[0] * sin_r + self.translation[1] * cos_r
        self.translation = (x_new, y_new)
    
    def intersect_transformed_with_line(self, line):
        # apply inverse transformation to the line
        inv_line = self.inverse_transform(line)
        return self.intersect_with_line(inv_line)
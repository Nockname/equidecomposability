from math import sqrt
from constants import PRECISION

def length(P, Q):
    return sqrt((P[0] - Q[0]) ** 2 + (P[1] - Q[1]) ** 2)

def CCW(A, B, C, PRECISION = 0.0):

    det = A[0] * (B[1] - C[1]) - B[0] * (A[1] - C[1]) + C[0] * (A[1] - B[1])

    if abs(A[0] - B[0]) <= PRECISION and abs(A[1] - B[1]) <= PRECISION:
        if abs(A[0] - C[0]) <= PRECISION and abs(A[1] - C[1]) <= PRECISION:
            return 0
        return 2

    if abs(det) > PRECISION:
        return int(det / abs(det))
    
    lAB = length(A, B)
    lBC = length(B, C)
    lAC = length(A, C)

    if lAC + lBC <= lAB + PRECISION:
        return 0

    if lAB + lBC <= lAC + PRECISION:
        return 2

    return -2

def do_line_segments_intersect(l1, l2, PRECISION = 0.0):
    
    # If three points are collinear
    
    if CCW(l1[0], l1[1], l2[0], PRECISION) == 0:
        return True
    if CCW(l1[0], l1[1], l2[1], PRECISION) == 0:
        return True

    if abs(CCW(l1[0], l1[1], l2[0], PRECISION)) == 2 or abs(CCW(l1[0], l1[1], l2[1], PRECISION)) == 2:
        return CCW(l1[0], l1[1], l2[0], PRECISION) == -CCW(l1[0], l1[1], l2[1], PRECISION)
    
    # No three points are collinear
    
    if CCW(l1[0], l1[1], l2[0], PRECISION) * CCW(l1[0], l1[1], l2[1], PRECISION) > 0:
        return False

    if CCW(l2[0], l2[1], l1[0], PRECISION) * CCW(l2[0], l2[1], l1[1], PRECISION) > 0:
        return False
    
    return True

def find_line_intersection(l1, l2):
    
    x1, y1 = l1[0]
    x2, y2 = l1[1]
    x3, y3 = l2[0]
    x4, y4 = l2[1]
    
    denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4) + 1e-15
    
    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denominator
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denominator
    
    return (px, py)

if __name__ == "__main__":
    
    pass
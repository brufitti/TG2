def single_trilateration(distances):
    x1,y1 =  1.20,  2.49
    x2,y2 = -2.49, -2.00
    x3,y3 =  2.00, -2.49
    
    d1 = distances[0]
    d2 = distances[1]
    d3 = distances[2]
    
    dr1 = x1**2 + y1**2 - d1**2
    dr2 = x2**2 + y2**2 - d2**2
    dr3 = x3**2 + y3**2 - d3**2
    
    x32,x21,x13 = x3-x2, x2-x1, x1-x3
    y32,y21,y13 = y3-y2, y2-y1, y1-y3
    
    x = (dr1 * y32 + dr2 * y13 + dr3 * y21)/(2.0*(x1*y32 + x2*y13 + x3*y21))
    y = (dr1 * x32 + dr2 * x13 + dr3 * x21)/(2.0*(y1*x32 + y2*x13 + y3*x21))
    point = [x,y]
    return point

def trilateration(d1_vec,d2_vec,d3_vec):
    points = []
    for idx in range(len(d1_vec)):
        distances = [d1_vec[idx],d2_vec[idx],d3_vec[idx]]
        point = single_trilateration(distances)
        points.append(point)
    return points

# # Test
# # [4.74056873169499, 1.4533688089768357, 3.1824857788144625]
# # [-1.0747966766357422, -1.6691217422485352]
# P1 = [ 1.20000,  2.49000, 0.75000]
# P2 = [-2.49000, -2.00000, 0.75000]
# P3 = [ 2.00000, -2.49000, 0.75000]
# refs = [P1, P2, P3]
# dists = [4.74056873169499, 1.4533688089768357, 3.1824857788144625]
# results  = (-1.0747966766357422, -1.6691217422485352)
# test = trilateration(refs, dists)
# print("Xt, Yt = ",test)
# print("X , Y  = ",results)
from math import cos, sin, radians
def calc_theta(Aa,dt,theta0):
    angular_speed = []
    As = []
    for idx in range(len(dt)):
        As.append(Aa[idx]*dt[idx])
    
    dtheta = []
    theta = [theta0]
    for idx in range(len(As)):
        dtheta = dt[idx]*(As[idx]+(dt[idx]*Aa[idx]))
        theta.append(theta[idx]+dtheta)
    return theta

def calc_componnents(module, orientation):
    dx = module*cos(radians(orientation))
    dy = module*sin(radians(orientation))
    return [dx,dy]
"""
Meyerhof method for square fondation
"""
from math import exp, pi, sqrt

from ..dmath import tan, cot
from .terzaghi import Terzaghi

class Meyerhof:
    """
    Provide methods to calculate meyerhof's calculations
    """
    def __init__(self, width_footing, depth_footing, water_depth=0):
        """
        calculate same as terzaghi and save
        """
        Terzaghi.water_level_correction(self, width_footing, depth_footing, water_depth)
        #Process same as terzaghi for water level correction

    @staticmethod
    def Nc(phi):
        if phi<1e-7:#checked for near value to 2+pi
            phi=1e-7
        return cot(phi)*(Meyerhof.Nq(phi)-1)

    @staticmethod
    def Nq(phi):
        return exp(pi*tan(phi))*(tan(45+phi/2))**2

    @staticmethod
    def Ny(phi):
        return (Meyerhof.Nq(phi)-1)*tan(1.4*phi)
    
    def capacity(self, cohesion, phi, gamma, length_footing, surchage=0): #, inclination_angle=0
        """
        Calcutate for provided depth
        """
        #Passive Earth pressure coff
        Kp = tan(45+ phi/2)**2
        #Shape factors
        sc = 1 + 0.2*Kp*self.width_footing/length_footing
        if phi < 10:
            sq = 1
        else:
            sq=1+0.1*Kp*self.width_footing/length_footing
        sy = sq
        #Depth factors
        dc = 1 +0.2*sqrt(Kp)*self.depth_footing/self.width_footing
        if phi < 10:
            dq = 1
        else:
            dq =1 +0.1*sqrt(Kp)*self.depth_footing/self.width_footing
        dy = dq
        c_term = cohesion*self.Nc(phi)*sc*dc
        q_term = surchage*self.Nq(phi)*sq*dq
        y_term = 0.5*gamma*9.81*self.width_footing*self.Ny(phi)*sy*dy
        return c_term+q_term*self.rw1+y_term*self.rw2

if __name__ == "__main__":
    import doctest
    doctest.testmod()

#Inclination factors
"""
ic = (1 - inclination_angle/90)**2
iq = ic
if phi == 0:
    iy = 0
else:
    iy = (1 - inclination_angle/phi)**2
"""
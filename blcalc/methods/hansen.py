"""
Hansen method for square fondation
"""
from ..dmath import tan, cot, sin
from math import exp, pi
from .terzaghi import Terzaghi
from .meyerhof import Meyerhof

class Hansen:
    """
    Provide methods to calculate hansen's calculations
    """
    def __init__(self, width_footing, depth_footing, water_depth=0):
        """
        calculate same as terzaghi and save
        """
        Terzaghi.water_level_correction(self, width_footing, depth_footing, water_depth)
        #Process same as terzaghi for water level correction

    @staticmethod
    def Nc(phi):
        return Meyerhof.Nc(phi)

    @staticmethod
    def Nq(phi):
        return Meyerhof.Nq(phi)

    @staticmethod
    def Ny(phi):
        return 1.5*(Hansen.Nq(phi)-1)*tan(phi)

    def shape_and_depth_factors(self, length_footing, phi):
        """
        Calculate and save shape and depth factors
        """
        self.sc=1+self.Nq(phi)/self.Nc(phi)*self.width_footing/length_footing
        self.sq=1+self.width_footing/length_footing*tan(phi)
        self.sy=1-0.4*self.width_footing/length_footing
        #depth corrections
        self.dc = 1 +0.4*self.width_footing/length_footing
        self.dq = 1 +2*tan(phi)*(1-sin(phi))**2 * self.depth_footing/self.width_footing
        self.dy=1

    def capacity(self, cohesion, phi, gamma, length_footing, surchage=0):
        """
        Calcutate for provided depth
        """
        self.shape_and_depth_factors(length_footing, phi)
        c_term = cohesion*self.Nc(phi)*self.sc*self.dc
        q_term = surchage*self.Nq(phi)*self.sq*self.dq
        y_term = 0.5*gamma*9.81*self.width_footing*self.Ny(phi)*self.sy*self.dy
        return c_term+q_term*self.rw1+y_term*self.rw2

if __name__ == "__main__":
    import doctest
    doctest.testmod()

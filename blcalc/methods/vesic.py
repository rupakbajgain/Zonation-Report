"""
Vesic method for square fondation
"""

from ..dmath import tan, cot
from math import exp, pi
from .meyerhof import Meyerhof
from .terzaghi import Terzaghi
from .hansen import Hansen

class Vesic:
    """
    Provide methods to calculate vesic's calculations
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
        return 2*(Vesic.Nq(phi)+1)*tan(phi)
    
    def capacity(self, cohesion, phi, gamma, length_footing, surchage=0):
        """
        Calcutate for provided depth
        """
        Hansen.shape_and_depth_factors(self, length_footing, phi)
        c_term = cohesion*self.Nc(phi)*self.sc*self.dc
        q_term = surchage*self.Nq(phi)*self.sq*self.dq
        y_term = 0.5*gamma*9.81*self.width_footing*self.Ny(phi)*self.sy*self.dy
        return c_term+q_term*self.rw1+y_term*self.rw2

if __name__ == "__main__":
    import doctest
    doctest.testmod()

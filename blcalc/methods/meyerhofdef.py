"""
Meyerhof deflection method
"""

class MeyerhofDeflection:
    """
    Meyerhof method
    """
    @staticmethod
    def capacity(n60, depth_footing, width_footing, water_depth=0.):
        """
        For 25mm
        """
        Rd = 1 + 0.33*depth_footing/width_footing
        if Rd>1.33:
            Rd=1.33
        b = water_depth-depth_footing
        if b<0:
            b=0
        Wy = 0.5+0.5*b/width_footing
        if Wy>1:
            Wy=1
        if width_footing<1.2:
            return 12.2*n60*Wy*Rd
        else:
            return 8.1*n60*((width_footing+0.3)/width_footing)**2*Wy*Rd
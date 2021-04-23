"""
Teng deflection method
"""

class TengDeflection:
    """
    Teng method
    """
    @staticmethod
    def capacity(n60, depth_footing, width_footing, water_depth=0.):
        """
        For 25mm
        """
        Rd = 1 + depth_footing/width_footing
        if Rd>2:
            Rd=2
        b = water_depth-depth_footing
        if b<0:
            b=0
        Wy = 0.5+0.5*b/width_footing
        if Wy>1:
            Wy=1
        return 35*(n60-3)*((width_footing+0.3)/(2*width_footing))**2*Wy*Rd
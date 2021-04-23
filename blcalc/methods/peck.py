"""
Peck method
"""

class Peck:
    """
    Peck method
    """
    @staticmethod
    def capacity(n60, depth_footing, width_footing, water_depth=0.):
        """
        For 25mm
        """
        Cw = 0.5 + 0.5*water_depth/(depth_footing+width_footing)
        return 10.25*Cw*n60
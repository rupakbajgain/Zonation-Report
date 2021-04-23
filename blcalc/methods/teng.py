"""
Teng method
"""
from .terzaghi import Terzaghi

class Teng:
    """
    Teng method
    """
    def __init__(self, depth_footing, width_footing, water_depth=0):
        Terzaghi.water_level_correction(self, width_footing, depth_footing, water_depth)
    
    def circular_capacity(self, N60):
        return 0.11*N60*N60*self.width_footing*self.rw2+0.33*(100+N60*N60)*self.depth_footing*self.rw1

    def strip_capacity(self, N60):
        return 0.167*N60*N60*self.width_footing*self.rw2+0.277*(100+N60*N60)*self.depth_footing*self.rw1
"""
Material, represents a single soil material,
assume every soil is saturated for now
"""
from enum import Enum
import copy

from .base import Base
from .soilproperty import SoilProperty

class MaterialData(Enum):
    """
    Soil material info
    """
    WaterDepth = 'WaterDepth'
    ID = 'ID' #For caching prupose, internal
    Location = 'Location'

def _group_index_correction(group_index):
    """
    The input group_index may not contain proper group_index as required by problem
    """
    if len(group_index)==1:
        #just to make sure 2 letter group_index is available
        group_index=group_index+group_index
    if not group_index[0] in ['S','M','G','C','P','O']:
        #cannot determine make it clay
        #@TODO add fail here
        group_index=group_index[1]+group_index[0]
    if not group_index[0] in ['S','M','G','C','P','O']:
        group_index='C'+group_index[1]#failed to determine type
    return group_index

# _clamp result between min and max values
def _clamp(value, amin, amax):
    if value<amin:
        return amin
    if value>amax:
        return amax
    return value

def _need_dil_correction(group_index):
    chk = group_index[0] in ['S','M','O'] or group_index[1] in ['S','M','O']
    if group_index[0] in ['G','C']:
        return False
    return chk

class Material(Base):
    """
    It is a single soil material for a layer,
    it takes SPT and other previously known material properties,
    and group_indexves the unknown by analytical formulas,
    this contains datas like surchage too
    """
    def is_clayey(self):
        """
        Check first letter and determine if soil is clayey
        """
        group_index = self._data[SoilProperty.GI]
        return group_index[0] not in ['S','G','M']

    def _get_n(self):
        """
        Get n_60 value
        """
        n_60 = self._data[SoilProperty.SPT_N]
        #Apply dilatracy correction
        if _need_dil_correction(self._data[SoilProperty.GI]) and n_60>15 and self._data[SoilProperty.depth] > self._data[SoilProperty.water_depth]:
            n_60 = 15 + 0.5 * (n_60 - 15)
        if self._data[SoilProperty.depth]<3:
            cr = 0.7
        elif self._data[SoilProperty.depth]<4:
            cr = 0.75
        elif self._data[SoilProperty.depth]<6:
            cr = 0.85
        elif self._data[SoilProperty.depth]<10:
            cr = 0.95
        else:
            cr = 1.
        n_60 = 0.55 * 1 * 1 * cr * n_60 /0.6
        #Apply overburden correction
        cor = 9.78*((1/self._data[SoilProperty.vertical_effective_stress])**0.5)
        if cor>1.7:
            cor=1.7
        n_60 = n_60*cor
        return n_60

    def _get_gamma(self):
        """
        Get value of gamma based on soil type
        """
        gamma = None
        if self.is_clayey():
            gamma = 16.8 + 0.15*self._data[SoilProperty.N60]
        else:
            gamma = 16 + 0.1 * self._data[SoilProperty.N60]
        #gamma=_clamp(gamma,10,2.8*9.81)#do we need this
        return gamma

    # Note: The unconfined compressive strength value is two times undrained shear strength. The
    # ultimate bearing capacity is approximately six times the undrained shear strength where C in
    # CNc is the undrained shear strength. The value of Nc is 5.14 and 5.7 respectively by
    # Meyerhof and Terzaghi.
    # BC Mapping Bhadra 4

    @staticmethod
    def qu(N60):
        """
        Determine Qu from N60
        """
        return 0.29 * N60**0.72 * 100

    def _get_cu(self):
        """
        Get cohesion of soil
        """
        c_undrained=0
        #group_index = self._data['GI']
        if self.is_clayey():
            c_undrained = self.qu(self._data[SoilProperty.N60])/2
            #c_undrained=_clamp(c_undrained, 10, 103)
        # Plaxis calculation needs very small c_undrained
        #if c_undrained<0.21:
        #    c_undrained = 0.21
        #use 0.2 as per plaxis recommendation
        return c_undrained#the cu is always 103 check with small value of n_60, some mistake maybe

    def _get_packing_state(self):
        """
        Get packing state table column
        """
        # Ok, first determining packing condition as per Table 2.4,
        s_phelp = [0,4,10,30,50]
        if self.is_clayey():
            s_phelp = [0,2,4,8,15,30]
        packing_case = 0 # Packing cases as per table
        for i,value in enumerate(s_phelp):
            if self._data[SoilProperty.N60]>value:
                packing_case=i
        return packing_case

    @staticmethod
    def phi(N60):
        """
        Determine phi from N60
        """
        return 27.1 + 0.3*N60 - 0.00054* N60**2

    def _get_phi(self):
        """
        Get phi of soil
        #Many tables are used need to be refactred
        """
        phi = self.phi(self._data[SoilProperty.N60])
        ### Ok let's remove for clay
        if self.is_clayey():
            phi=0 #very small value for plaxis:::@TODO 0.01
        return phi

    def _get_e(self):
        """
        Elasticity
        """
        group_index = self._data[SoilProperty.GI]
        n_60 = self._data[SoilProperty.N60]
        packing_case = self._data[SoilProperty.packing_case]
        elasticity=None
        if self.is_clayey():
            if packing_case==0:#15-40
                elasticity= (15+40)/2 * n_60 * 100
            elif packing_case==1:#40-80
                elasticity= (40+80)/2 * n_60 * 100
            else:#80-200
                elasticity= (80+200)/2 * n_60 * 100
        else:
            if group_index[1] in ['M','C','P','O']:#with fines
                elasticity= 5 * n_60 * 100
            else: #The OCR condition of cohesionless test cannot be determined, assume NC sand
                elasticity= 10 * n_60 * 100
        return elasticity

    def __init__(self, input_data):
        """
        Save only use later when required
        """
        Base.__init__(self)
        self._data = input_data
        self._data[SoilProperty.GI] = _group_index_correction(self._data[SoilProperty.GI])
        if SoilProperty.N60 not in self._data:
            self._data[SoilProperty.N60] = self._get_n()
        if SoilProperty.packing_case not in self._data:
            self._data[SoilProperty.packing_case] = self._get_packing_state()
        if SoilProperty.gamma not in self._data:
            self._data[SoilProperty.gamma] = self._get_gamma()
        #Check and adjust values of qu, cu and phi as necessary
        if SoilProperty.phi not in self._data and SoilProperty.cu not in self._data and SoilProperty.qu in self._data:
            group_index = self._data[SoilProperty.GI]
            if self.is_clayey() or group_index[0]=='M':
                self._data[SoilProperty.phi] = 0.
                self._data[SoilProperty.cu] = self._data[SoilProperty.qu] / 2
        if SoilProperty.cu not in self._data:
            self._data[SoilProperty.cu] = self._get_cu()
        if SoilProperty.phi not in self._data:
            self._data[SoilProperty.phi] = self._get_phi()
        if SoilProperty.elasticity not in self._data:
            self._data[SoilProperty.elasticity] = self._get_e()
        if SoilProperty.nu not in self._data:
            if self.is_clayey():
                self._data[SoilProperty.nu] = 0.45
            else:
                self._data[SoilProperty.nu] = 0.3
        #update data to this dict
        self.set(self._data)

class LayerSoil(Base):
    """
    Use to determine multiple layer of soil
    so include surchage info also
    """
    def __init__(self, data, water_depth=0,id=-1,location='Undefined'):
        super().__init__(self)
        self[MaterialData.WaterDepth] = water_depth
        self[MaterialData.ID] = id
        self[MaterialData.Location] = location
        self._data = data
        self._values = []
        prev_vertical_eff = 0.
        prev_total_eff = 0.
        prev_depth = 0.
        for layer in data:
            if SoilProperty.sat_unit_weight not in layer:
                layer[SoilProperty.sat_unit_weight]=9.81*(1+layer[SoilProperty.water_per])*layer[SoilProperty.G]/(1+layer[SoilProperty.water_per]*layer[SoilProperty.G])
            new_depth = layer[SoilProperty.depth]
            if new_depth<=water_depth:
                prev_vertical_eff += layer[SoilProperty.gamma]*9.81*(new_depth-prev_depth)
                prev_total_eff += layer[SoilProperty.gamma]*9.81*(new_depth-prev_depth)
            else:
                prev_vertical_eff += (layer[SoilProperty.sat_unit_weight]-9.81)*(new_depth-prev_depth)
                prev_total_eff += layer[SoilProperty.sat_unit_weight]*(new_depth-prev_depth)
            layer[SoilProperty.vertical_effective_stress] = prev_vertical_eff
            layer[SoilProperty.total_effective_stress] = prev_total_eff
            layer[SoilProperty.water_depth] = water_depth
            layer[SoilProperty.thickness] = new_depth-prev_depth
            prev_depth=new_depth
            #create material
            mat = Material(layer)
            res = mat.get()
            self._values.append(res)

    def get_avg_N(self, depth=0.):
        Ns = []# N values
        depths = []#depth total values
        row_start=0
        while self._values[row_start][SoilProperty.depth]<depth/2:
            row_start+=1
        row_end = row_start
        end_row = len(self._values)-1
        if (self._values[end_row][SoilProperty.depth]<2*depth):
          self._values[end_row][SoilProperty.depth]=2*depth
        while self._values[row_end][SoilProperty.depth]<2*depth:
            row_end+=1
        if row_start==row_end:
            return self._values[row_end][SoilProperty.N60]
        if row_start==0:
            depths.append(0.)
        else:
            depths.append(self._values[row_start-1][SoilProperty.depth])
        for data in self._values[row_start:row_end]:
            Ns.append(data[SoilProperty.N60])
            depths.append(data[SoilProperty.depth])
        total_ns = 0.
        total_depth = 0.
        for (row, N_value) in enumerate(Ns):
            thickness = depths[row+1]-depths[row]
            total_ns += N_value*thickness
            total_depth += thickness
        return total_ns/total_depth

    def get(self, depth=None):
        """
        Return soil material at givel depth
        if no depth is given returns all saved materials
        """
        if depth is None:#Return all
            return self._values

        if depth<self._values[0][SoilProperty.depth]:
            mat = copy.copy(self._values[0])
            mat[SoilProperty.depth]=depth
            if depth<=mat[SoilProperty.water_depth]:
                mat[SoilProperty.vertical_effective_stress] =  mat[SoilProperty.gamma]*9.81*depth
                mat[SoilProperty.total_effective_stress] = mat[SoilProperty.gamma]*9.81*depth
            else:
                mat[SoilProperty.vertical_effective_stress] =  (mat[SoilProperty.sat_unit_weight]-9.81)*depth
                mat[SoilProperty.vertical_effective_stress] =  mat[SoilProperty.sat_unit_weight]*depth
            return mat
        size = len(self._values)
        if depth>self._values[size-1][SoilProperty.depth]:
            mat = copy.copy(self._values[size-1])
            if depth<=mat[SoilProperty.water_depth]:
                mat[SoilProperty.vertical_effective_stress] +=  (mat[SoilProperty.gamma]*9.81)*(depth - mat[SoilProperty.depth])
                mat[SoilProperty.total_effective_stress] += mat[SoilProperty.gamma]*9.81*(depth - mat[SoilProperty.depth])
            else:
                mat[SoilProperty.vertical_effective_stress] +=  (mat[SoilProperty.sat_unit_weight]-9.81)*(depth - mat[SoilProperty.depth])
                mat[SoilProperty.vertical_effective_stress] +=  mat[SoilProperty.sat_unit_weight]*(depth - mat[SoilProperty.depth])
            mat[SoilProperty.depth]=depth
            return mat
        row=0
        while self._values[row][SoilProperty.depth]<depth:
            row+=1
        mat = copy.copy(self._values[row])
        if depth<=mat[SoilProperty.water_depth]:
            mat[SoilProperty.vertical_effective_stress] -=  (mat[SoilProperty.gamma]*9.81)*(mat[SoilProperty.depth]-depth)
            mat[SoilProperty.total_effective_stress] -= mat[SoilProperty.gamma]*9.81*(mat[SoilProperty.depth]-depth)
        else:
            mat[SoilProperty.vertical_effective_stress] -=  (mat[SoilProperty.sat_unit_weight]-9.81)*(mat[SoilProperty.depth]-depth)
            mat[SoilProperty.vertical_effective_stress] -=  mat[SoilProperty.sat_unit_weight]*(mat[SoilProperty.depth]-depth)
        mat[SoilProperty.depth]=depth
        return mat

if __name__ == "__main__":
    import doctest
    doctest.testmod()

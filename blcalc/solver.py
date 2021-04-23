"""
Apply appropriate method based on data provided
"""

from enum import Enum
from .assembly import AssemblyType
from .footing import FootingType, FootingData
from .material import MaterialData
from .methods.terzaghi import Terzaghi
from .methods.meyerhof import Meyerhof
from .methods.hansen import Hansen
from .methods.vesic import Vesic
from .methods.teng import Teng
from .methods.liquifaction import Liquifaction
from .methods.peck import Peck
from .methods.tengdef import TengDeflection
from .methods.meyerhofdef import MeyerhofDeflection
from .soilproperty import SoilProperty

class Methods(str, Enum):
    """
    Supported solution methods
    """
    Terzaghi = 'Terzaghi'
    Meyerhof = 'Meyerhof'
    Hansen = 'Hansen'
    Bowels = 'Bowels'
    Vesic = 'Vesic'
    Teng = 'Teng'
    Liquifaction = 'Liquifaction'
    Plaxis = 'Plaxis'
    Peck = 'Peck'
    TengDeflection = 'TengDeflection'
    MeyerhofDeflection = 'MeyerhofDeflection'
    PlaxisShear = 'PlaxisShear'

FOS = 3

class Solver:
    """
    Apply appropriate method based on data provided
    """
    def __init__(self, assembly):
        """
        init solver
        """
        self._footing = assembly[AssemblyType.Footing]
        self._soilLayer = assembly[AssemblyType.SoilLayer]

    def calc_terzaghi(self):
        """
        Calculate based on terzaghi method
        """
        terzaghi = Terzaghi(
                    self._footing[FootingData.Width],
                    self._footing[FootingData.Depth],
                    self._soilLayer[MaterialData.WaterDepth]
                )
        footing_type = self._footing[FootingData.Type]
        mat = self._soilLayer.get(self._footing[FootingData.Depth])
        if footing_type==FootingType.Circular:
            return (terzaghi.circular_capacity(
                        mat[SoilProperty.cu],
                        mat[SoilProperty.phi],
                        mat[SoilProperty.gamma],
                        mat[SoilProperty.total_effective_stress]
                    ) - mat[SoilProperty.total_effective_stress])/ FOS
        elif footing_type==FootingType.Square:
            return (terzaghi.square_capacity(
                        mat[SoilProperty.cu],
                        mat[SoilProperty.phi],
                        mat[SoilProperty.gamma],
                        mat[SoilProperty.total_effective_stress]
                    ) - mat[SoilProperty.total_effective_stress])/ FOS
        return (terzaghi.strip_capacity(
                        mat[SoilProperty.cu],
                        mat[SoilProperty.phi],
                        mat[SoilProperty.gamma],
                        mat[SoilProperty.total_effective_stress]
                    ) - mat[SoilProperty.total_effective_stress])/ FOS

    def calc_meyerhoff(self):
        meyerhof = Meyerhof(
                    self._footing[FootingData.Width],
                    self._footing[FootingData.Depth],
                    self._soilLayer[MaterialData.WaterDepth]
                )
        mat = self._soilLayer.get(self._footing[FootingData.Depth])
        return (meyerhof.capacity(
                    mat[SoilProperty.cu],
                    mat[SoilProperty.phi],
                    mat[SoilProperty.gamma],
                    self._footing[FootingData.Length],
                    mat[SoilProperty.total_effective_stress]
                ) - mat[SoilProperty.total_effective_stress])/ FOS

    def calc_hansen(self):
        hansen = Hansen(
                    self._footing[FootingData.Width],
                    self._footing[FootingData.Depth],
                    self._soilLayer[MaterialData.WaterDepth]
                )
        mat = self._soilLayer.get(self._footing[FootingData.Depth])
        return (hansen.capacity(
                    mat[SoilProperty.cu],
                    mat[SoilProperty.phi],
                    mat[SoilProperty.gamma],
                    self._footing[FootingData.Length],
                    mat[SoilProperty.total_effective_stress]
                ) - mat[SoilProperty.total_effective_stress])/ FOS

    def calc_vesic(self):
        vesic = Vesic(
                    self._footing[FootingData.Width],
                    self._footing[FootingData.Depth],
                    self._soilLayer[MaterialData.WaterDepth]
                )
        mat = self._soilLayer.get(self._footing[FootingData.Depth])
        return (vesic.capacity(
                    mat[SoilProperty.cu],
                    mat[SoilProperty.phi],
                    mat[SoilProperty.gamma],
                    self._footing[FootingData.Length],
                    mat[SoilProperty.total_effective_stress]
                ) - mat[SoilProperty.total_effective_stress])/ FOS

    def calc_IS(self):
        avg_N60 = self._soilLayer.get_avg_N(self._footing[FootingData.Depth])
        return IS.capacity(
            avg_N60,
            self._footing[FootingData.Depth],
            self._footing[FootingData.Width]
        )

    def calc_peck(self):
        avg_N60 = self._soilLayer.get_avg_N(self._footing[FootingData.Depth])
        return Peck.capacity(
            avg_N60,
            self._footing[FootingData.Depth],
            self._footing[FootingData.Width],
            self._soilLayer[MaterialData.WaterDepth]
        )

    def calc_tengdef(self):
        avg_N60 = self._soilLayer.get_avg_N(self._footing[FootingData.Depth])
        return TengDeflection.capacity(
            avg_N60,
            self._footing[FootingData.Depth],
            self._footing[FootingData.Width],
            self._soilLayer[MaterialData.WaterDepth]
        )

    def calc_meyerofdeff(self):
        avg_N60 = self._soilLayer.get_avg_N(self._footing[FootingData.Depth])
        return MeyerhofDeflection.capacity(
            avg_N60,
            self._footing[FootingData.Depth],
            self._footing[FootingData.Width],
            self._soilLayer[MaterialData.WaterDepth]
        )

    def calc_bowels(self):
        return self.calc_meyerofdeff()*1.5

    def calc_teng(self):
        avg_N60 = self._soilLayer.get_avg_N(self._footing[FootingData.Depth])
        teng =  Teng(
            self._footing[FootingData.Depth],
            self._footing[FootingData.Width],
            self._soilLayer[MaterialData.WaterDepth]
        )
        footing_type = self._footing[FootingData.Type]
        if footing_type==FootingType.Circular or footing_type==FootingType.Square:
            return teng.circular_capacity(avg_N60)
        else:
            return teng.strip_capacity(avg_N60)
    
    def calc_lpi(self):
        return Liquifaction.LPI(self._soilLayer)

    def calc_plaxis(self):
        from .methods.plaxis import Plaxis
        return Plaxis.calculate(self._soilLayer,self._footing[FootingData.Depth])

    def run(self, methods=Methods): #all method if not selected
        """
        Run selected method based on method
        """
        results = {}
        for method in methods:
            if method == Methods.Terzaghi:
                results[method] = self.calc_terzaghi()
            elif method == Methods.Meyerhof:
                results[method] = self.calc_meyerhoff()
            elif method == Methods.Hansen:
                results[method] = self.calc_hansen()
            elif method == Methods.Bowels:
                results[method] = self.calc_bowels()
            elif method == Methods.Vesic:
                results[method] = self.calc_vesic()
            elif method == Methods.Teng:
                results[method] = self.calc_teng()
            elif method == Methods.Liquifaction:
                results[method] = self.calc_lpi()
            elif method == Methods.Plaxis:
                res = self.calc_plaxis()
                results[method] = res[0]
                #mat = self._soilLayer.get(self._footing[FootingData.Depth])
                results[Methods.PlaxisShear] = res[1]
                #(res[1]-mat[SoilProperty.total_effective_stress])/FOS
            elif method == Methods.Peck:
                results[method] = self.calc_peck()
            elif method == Methods.TengDeflection:
                results[method] = self.calc_tengdef()
            elif method == Methods.MeyerhofDeflection:
                results[method] = self.calc_meyerofdeff()
            else:
                pass
        return results

if __name__ == "__main__":
    import doctest
    doctest.testmod()

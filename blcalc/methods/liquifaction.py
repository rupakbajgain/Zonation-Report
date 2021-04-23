"""
Teng method
"""
import math
from ..soilproperty import SoilProperty

#do as per provided excel
class Liquifaction:
    """
    Teng method
    """
    @staticmethod
    def LPI(lay):
        datas = lay.get()
        lpi = 0.
        for  i in range(len(datas)):
            data = datas[i]
            FC = data[SoilProperty.FC]
            delN1 = math.exp(1.63+(9.7/(FC+0.01))-(15.7/(FC+0.01))*(15.7/(FC+0.01)))
            N1cs = data[SoilProperty.N60] + delN1
            MSF = 0.8758
            Csigma = 1/(18.9-2.55*math.sqrt(N1cs))
            if Csigma>0.3:
                Csigma = 0.3
            Ksigma = 1-Csigma*math.log(data[SoilProperty.vertical_effective_stress]/100)
            if Ksigma>1.1:
                Ksigma = 1.1
            CRR = math.exp((N1cs/14.1)+(N1cs/126)**2-(N1cs/23.6)**3+(N1cs/25.4)**3-2.8/1)*(MSF*Ksigma)
            a_g = 0.183
            SRF = math.exp(-1.012-1.126*math.sin(data[SoilProperty.depth]/11.73+5.133)+8*(0.106+0.118*math.sin(data[SoilProperty.depth]/11.28+5.142)))
            CSR = 0.65*(data[SoilProperty.total_effective_stress]/data[SoilProperty.vertical_effective_stress])*a_g*SRF
            FS = CRR / CSR
            if FS > 1.2:
                Fz = 0.
            elif FS < 0.95:
                Fz = 1-FS
            else:
                Fz = 2e6*math.exp(-18.427*FS)
            Wz = 10 - data[SoilProperty.depth]/2
            lpi += Fz * Wz * data[SoilProperty.thickness]
        return lpi

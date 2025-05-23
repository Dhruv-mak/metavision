# MetaInterp3D
import numpy as np
from scipy import interpolate

def interp(matrix,insert):
    #insert = # new added slices for each interval
    high_res_matrix = np.zeros((insert*(matrix.shape[0]-1)+matrix.shape[0],matrix.shape[1], matrix.shape[2]))
    x = np.linspace(1, matrix.shape[0], matrix.shape[0])
    x_new = np.linspace(1, matrix.shape[0], high_res_matrix.shape[0])
    for ii in range(high_res_matrix.shape[1]):
        for ij in range(high_res_matrix.shape[2]):
            f = interpolate.interp1d(x, matrix[:, ii, ij])
            high_res_matrix[:, ii, ij] = f(x_new)
    return high_res_matrix

class MetaInterp3D:
    def __init__(self,matrix,insert):
        self.matrix=matrix
        self.insert = insert
        
    def interp(self):
        high_res_matrix = np.zeros((self.insert*(self.matrix.shape[0]-1)+self.matrix.shape[0],self.matrix.shape[1], self.matrix.shape[2]))
        x = np.linspace(1, self.matrix.shape[0], self.matrix.shape[0])
        x_new = np.linspace(1, self.matrix.shape[0], high_res_matrix.shape[0])
        for ii in range(high_res_matrix.shape[1]):
            for ij in range(high_res_matrix.shape[2]):
                f = interpolate.interp1d(x, self.matrix[:, ii, ij])
                high_res_matrix[:, ii, ij] = f(x_new)
        return high_res_matrix
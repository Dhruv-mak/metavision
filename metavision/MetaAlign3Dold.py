# MetaAlign3D module
import sys
import numpy as np
import pandas as pd
import cv2
import os
from .MetaNorm3D import *

def image_size(data):
    x_size_list = []
    y_size_list = []
    for i in range(len(data.tissue_id.unique())):
        data_temp = data[data['tissue_id'] == (i+1)]
        
        cnt_x = 0
        cnt_y = 0

        # list to hold visited values
        visited_x = []
        visited_y = []

        # loop for counting the unique
        x_values = np.around(data_temp['x'].to_numpy(), 0)
        y_values = np.around(data_temp['y'].to_numpy(), 0)

        for i in range(len(x_values)):
            if x_values[i] not in visited_x: 
                visited_x.append(x_values[i])
                cnt_x += 1
            if y_values[i] not in visited_y: 
                visited_y.append(y_values[i])
                cnt_y += 1

        x_size_temp = ((cnt_x*1.1 + 9) // 10) * 10
        y_size_temp = ((cnt_y*1.1 + 9) // 10) * 10
        
        x_size_list.append(x_size_temp)
        y_size_list.append(y_size_temp)
        
    x_size = int(max(x_size_list))
    y_size = int(max(y_size_list))
    return x_size,y_size
    
def create_slice(df_all,slice_number, col='result', reverse = False):
    nslice = len(df_all.tissue_id.unique())
    if reverse:
        df_temp = df_all[df_all['tissue_id'] == nslice-slice_number]
    else:
        df_temp = df_all[df_all['tissue_id'] == (slice_number+1)]
    cnt_x = 0
    cnt_y = 0

    # list to hold visited values
    visited_x = []
    visited_y = []

    # loop for counting the unique
    x_values = np.around(df_temp['x'].to_numpy(), 0)
    y_values = np.around(df_temp['y'].to_numpy(), 0)
    
    for i in range(len(x_values)):
        if x_values[i] not in visited_x: 
            visited_x.append(x_values[i])
            cnt_x += 1
        if y_values[i] not in visited_y: 
            visited_y.append(y_values[i])
            cnt_y += 1

    #print("No.of.unique values :", cnt_x)
    #print("No.of.unique values :", cnt_y)

    visited_x = np.array(visited_x)
    visited_y = np.array(visited_y)

    sort_x_inds = visited_x.argsort()
    sort_y_inds = visited_y.argsort()

    visited_x = visited_x[sort_x_inds]
    visited_y = visited_y[sort_y_inds]
    
#     print(visited_x, "\n")
#     print(visited_y, "\n")

    reshaped_matrix = np.zeros((cnt_x, cnt_y))
    for ii, vi in enumerate(eval(f"df_temp[col].to_numpy()")):
        if not np.isnan(vi):
            x_ind = find_nearest(visited_x, x_values[ii])
            y_ind = find_nearest(visited_y, y_values[ii])
            reshaped_matrix[x_ind, y_ind] = vi
        else:
            continue
    return reshaped_matrix

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

def create_compound_matrix(data,col='result',reverse=False):
    x_size, y_size = image_size(data)
    nslice = len(data.tissue_id.unique())
    matrix = np.zeros((nslice, x_size, y_size))
    for ii in range(matrix.shape[0]):
        data_temp = create_slice(data, ii,col=col, reverse=reverse)
        x_vals = int((x_size - data_temp.shape[0])/2) 
        y_vals = int((y_size - data_temp.shape[1])/2) #find the (x,y) of the start vertex, '/2' means put the slice in the center
        #matrix[ii, int(x_vals/2):int(x_vals/2)+data_temp.shape[0], int(y_vals/2):int(y_vals/2)+data_temp.shape[1]] = data_temp
        matrix[ii, x_vals:x_vals+data_temp.shape[0], y_vals:y_vals+data_temp.shape[1]] = data_temp
    return matrix

def motionCorr_apply_maldi(ref_image, moving_image):
    cv_img_1 = cv2.convertScaleAbs(ref_image, alpha=255/ref_image.max())
    cv_img_2 = cv2.convertScaleAbs(moving_image, alpha=255/moving_image.max())
    # Find size of image1
    sz = cv_img_2.shape

    # Define the motion model
    warp_mode = cv2.MOTION_EUCLIDEAN
    warp_matrix = np.eye(2, 3, dtype=np.float32)
    
    # Specify the number of iterations.
    number_of_iterations = 5000;
    # Specify the threshold of the increment
    # in the correlation coefficient between two iterations
    termination_eps = 1e-10;
    
    # Define termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, number_of_iterations,  termination_eps)

    # Run the ECC algorithm. The results are stored in warp_matrix.
    try:
        (cc, warp_matrix) = cv2.findTransformECC (cv_img_1,cv_img_2,warp_matrix, warp_mode, criteria)
    except cv2.error:
        return cv_img_2,warp_matrix

    # Use warpAffine for Translation, Euclidean and Affine
    im2_aligned = cv2.warpAffine(moving_image, warp_matrix, (sz[1],sz[0]), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP);
    return im2_aligned,warp_matrix

def alignment_warp_matrix(moving_image, warp_matrix):
    cv_img_2 = cv2.convertScaleAbs(moving_image, alpha=255/moving_image.max())
    sz = cv_img_2.shape
    im_aligned = cv2.warpAffine(moving_image, warp_matrix, (sz[1],sz[0]), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
    
    return im_aligned

def calculate_warp_matrix(ref_matrix):
    matrix_corrected = np.zeros((ref_matrix.shape))
    matrix_corrected[0] = ref_matrix[0]
    warp_matrix_all = np.zeros((matrix_corrected.shape[0] - 1, 2, 3))
    for ii in range(matrix_corrected.shape[0] - 1):
        matrix_corrected[ii + 1], warp_matrix_all[ii] = motionCorr_apply_maldi(
            matrix_corrected[ii], ref_matrix[ii + 1])
    np.save('./warpmatrix/warp_matrix_all', warp_matrix_all)
    return warp_matrix_all

def get_warp_matrix(df,ref_compound,first_feature,reverse):
    if not os.path.exists('./warpmatrix/warp_matrix_all.npy'):

        meta_norm = MetaNorm3D(df, ref_compound, first_feature=first_feature)

        ## totalsum normalization
        norm_df = meta_norm.totalsum_norm()

        ## section normalization
        data = meta_norm.section_norm()

        # MetaAlign3D
        meta_align = MetaAlign3D(data)

        ## manual slices fitting and create compound matrix
        compound_matrix = meta_align.create_compound_matrix(reverse=reverse)

        ## get warp matrix with reference compound first 
        warp_matrix = meta_align.calculate_warp_matrix()

    else:
        print('Warp Matrix already existed.')
        pass
        

def seq_align(matrix, warp_matrix_all):
    matrix_corrected = np.zeros((matrix.shape))
    matrix_corrected[0] = matrix[0]
    for ii in range(matrix_corrected.shape[0]-1):
        matrix_corrected[ii+1] = alignment_warp_matrix(matrix[ii+1],warp_matrix_all[ii]) 
    return matrix_corrected


class MetaAlign3D:
    def __init__(self,data):
        self.data = data
        self.matrix=None
        self.warp_matrix_all=None
        
    def create_compound_matrix(self,col='result',reverse=False):
        x_size, y_size = image_size(self.data)
        nslice = len(self.data.tissue_id.unique())
        self.matrix = np.zeros((nslice, x_size, y_size))
        for ii in range(self.matrix.shape[0]):
            data_temp = create_slice(self.data, ii,col=col,reverse=reverse)
            x_vals = int((x_size - data_temp.shape[0])/2) 
            y_vals = int((y_size - data_temp.shape[1])/2) #find the (x,y) of the start vertex, '/2' means put the slice in the center
            self.matrix[ii, x_vals:x_vals+data_temp.shape[0], y_vals:y_vals+data_temp.shape[1]] = data_temp
        return self.matrix
    
    def calculate_warp_matrix(self):
        matrix_corrected = np.zeros((self.matrix.shape))
        matrix_corrected[0] = self.matrix[0]
        self.warp_matrix_all = np.zeros((matrix_corrected.shape[0] - 1, 2, 3))
        for ii in range(matrix_corrected.shape[0] - 1):
            matrix_corrected[ii + 1], self.warp_matrix_all[ii] = motionCorr_apply_maldi(
                matrix_corrected[ii], self.matrix[ii + 1])
        if not os.path.exists('./warpmatrix/'):
            os.makedirs('./warpmatrix/')
        np.save('./warpmatrix/warp_matrix_all', self.warp_matrix_all)
        return self.warp_matrix_all
    
    def seq_align(self):
        try:
            base_path = os.path.join(sys._MEIPASS , 'config')
        except Exception:
            base_path = 'visionApp/MetaVision3D/warpmatrix'
        self.warp_matrix_file = os.path.join(base_path, 'warp_matrix_all.npy')
        if os.path.exists(self.warp_matrix_file):
            self.warp_matrix_all = np.load(self.warp_matrix_file)
        # if os.path.exists('./warpmatrix/warp_matrix_all.npy'):
        #     self.warp_matrix_all = np.load('./warpmatrix/warp_matrix_all.npy')
        else:
             raise ValueError("Warp matrix is not available. Please run get_warp_matrix() with reference compound first.")
        matrix_corrected = np.zeros((self.matrix.shape))
        matrix_corrected[0] = self.matrix[0]
        for ii in range(matrix_corrected.shape[0]-1):
            matrix_corrected[ii+1] = alignment_warp_matrix(self.matrix[ii+1],self.warp_matrix_all[ii]) 
        return matrix_corrected
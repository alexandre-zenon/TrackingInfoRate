import numpy as np
import pandas as pd
#from idtxl.estimators_jidt import JidtKraskovCMI
import knncmi as k

k_cst = 2 #  number of nearest neighbours considered
settings = {'kraskov_k': k_cst}

def shift_elements(arr, num, fill_value):
    result = np.empty_like(arr)
    if num > 0:
        result[:num] = fill_value
        result[num:] = arr[:-num]
    elif num < 0:
        result[num:] = fill_value
        result[:num] = arr[-num:]
    else:
        result[:] = arr
    return result

def construct_shifted_array(inputs,order,lag):
    # inputs must be a list of variable
    # orders are listed in correspondence with variables
    if (not type(order) is list):
        order = [order]
    for idx,input in enumerate(inputs):
        if (idx==0):
            i = np.transpose(np.array([shift_elements(input, lag, np.NAN)]))
        else:
            i = np.append(i, np.transpose(np.array([shift_elements(input, lag, np.NAN)])), axis=1)
        for o in range(order[idx] - 1):
            i = np.append(i, np.transpose(np.array([shift_elements(input, lag + o + 1, np.NAN)])), axis=1)
    return i

def compute_FB(inputs,output,order,vmd):
    outputArray = construct_shifted_array([output],order[-1]-1,1)
    outputArrayVMD = construct_shifted_array([output],order[-1],vmd)
    inputArray = construct_shifted_array(inputs,order[0:-1],vmd)
    ix1 = np.where(np.isnan(outputArrayVMD))[0][-1] + 1
    ix2 = np.where(np.isnan(inputArray))[0][-1] + 1
    ix = np.maximum(ix1,ix2)

    df = pd.DataFrame(np.concatenate((np.array([output[ix:],]).T,inputArray[ix:,:],outputArray[ix:,:],outputArrayVMD[ix:,:]),axis=1))
    input_nc = inputArray.shape[1]
    total_nc = df.shape[1]
    input_list = list(range(1,input_nc+1))
    output_list = list(range(input_nc+1, total_nc))
    return k.cmi([0],input_list,output_list,k_cst,df)
    # estimator = JidtKraskovCMI(settings)
    # return estimator.estimate(output[ix:],inputArray[ix:,:],np.append(outputArray[ix:,:],outputArrayVMD[ix:,:],axis=1))

def compute_total_info(inputs,output,order,vmd):
    inputArray = construct_shifted_array(inputs,list(np.array(order[0:-1])-1),1)
    inputArrayVMD = construct_shifted_array(inputs, order[0:-1], vmd)
    ix1 = np.where(np.isnan(inputArrayVMD))[0][-1] + 1
    ix2 = np.where(np.isnan(inputArray))[0][-1] + 1
    ix = np.maximum(ix1,ix2)

    df = pd.DataFrame(
        np.concatenate((np.array([output[ix:], ]).T, inputArray[ix:, :], inputArrayVMD[ix:, :]),
                       axis=1))
    total_nc = df.shape[1]
    total_list = list(range(1, total_nc))
    return k.cmi([0], total_list, [], k_cst, df)
# encoding: utf-8
"""
 @author: Xin Zhang
 @contact: 2250271011@email.szu.edu.cn
 @time: 2022/10/28 21:47
 @name: 
 @desc:
"""
import pickle
from joblib import Parallel, delayed
from tqdm import tqdm
from data_pipeline.mne_reader import MNEReader
from utils.my_tools import file_scanf
import numpy as np
from pre_processing.difference import trial_average

parallel_jobs = 6


def ziyan_read(file_path):
    # read labels and stimulus from .Markers file which created by Ziyan He
    with open(file_path) as f:
        stim = []
        y = []
        for line in f.readlines():
            if line.strip().startswith('Stimulus'):
                line = line.strip().split(',')
                classes = int(line[1][-2:])  # 'S 17'
                time = int(line[2].strip())  # ' 39958'
                stim.append(time)
                y.append(classes)
    return stim, y


def thread_read_write(x, y, pkl_filename):
    """Writes and dumps the processed pkl file for each stimulus(or called subject).
    [time, channels=127], y
    """
    assert np.shape(x) == (2000, 127)
    with open(pkl_filename + '.pkl', 'wb') as file:
        pickle.dump(x, file)
        pickle.dump(y, file)


def go_through(label_filenames, pkl_path):
    edf_reader = MNEReader(filetype='edf', method='manual', resample=None, length=2000)

    for f in tqdm(label_filenames, desc=' Total', position=0, leave=True, colour='YELLOW', ncols=80):
        stim, y = ziyan_read(f)  # [frame_point], [class]
        x = edf_reader.get_set(file_path=f.replace('.Markers', '.edf'), stim_list=stim)
        assert len(x) == len(y)
        assert np.shape(x[0]) == (2000, 127)

        x = np.reshape(x, (len(x)*2000, 127))
        x = trial_average(x, axis=0)
        x = np.reshape(x, (-1, 2000, 127))

        name = f.split('/')[-1].replace('.Markers', '')
        Parallel(n_jobs=parallel_jobs)(
            delayed(thread_read_write)(x[i], y[i], pkl_path + name+'_' + str(i) + '_' + str(stim[i])+'_'+str(y[i]))
            for i in tqdm(range(len(y)), desc=' write '+name, position=1, leave=False, colour='WHITE', ncols=80))


if __name__ == "__main__":
    path = 'E:/Datasets/SZFace2/EEG'
    # path = '../../../../Datasets/SZFace2/EEG'
    label_filenames = file_scanf(path, endswith='.Markers')
    go_through(label_filenames, pkl_path=path+'/pkl_ave/')







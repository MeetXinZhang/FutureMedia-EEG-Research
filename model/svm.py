# -*- coding: utf-8 -*-
"""
 @author: Xin Zhang
 @contact: 2250271011@email.szu.edu.cn
 @time: 2023/3/10 17:22
 @desc:
"""

from utils.my_tools import file_scanf2
from sklearn.svm import LinearSVC
import pickle
import numpy as np
import matplotlib.pyplot as plt


def sk_svm():
    svm = LinearSVC(fit_intercept=True, C=0.1, dual=True, max_iter=5000)
    return svm


if __name__ == '__main__':
    path = '../../../Datasets/CVPR2021-02785/pkl_spec_from_2048'
    file_names = file_scanf2(path, contains=['1000-1-00', '1000-1-01', '1000-1-02', '1000-1-03', '1000-1-04',
                                             '1000-1-05', '1000-1-06', '1000-1-07', '1000-1-08', '1000-1-09'],
                             endswith='.pkl')

    # path = '../../../Datasets/CVPR2021-02785/pkl_pca_lda_from_spec'
    # filenames = file_scanf2(path, contains=['1000-1'], endswith='.pkl')
    np.random.shuffle(file_names)
    total = len(file_names)
    from pre_process.lda import pca_dataset

    data_set, labels = pca_dataset(file_names)

    svm = sk_svm()

    # train_svm_x = []  # [b 3780]
    # train_svm_y = []
    # for i, file in enumerate(filenames[0:int(total*0.7)]):
    #     with open(file, 'rb') as f:
    #         x = pickle.load(f)  # [39,]
    #         y = int(pickle.load(f))  # [1,]
    #         train_svm_x.append(x)
    #         train_svm_y.append(y)
    # train_svm_x = np.array(train_svm_x)
    # train_svm_y = np.array(train_svm_y)
    # print(np.shape(train_svm_x), np.shape(train_svm_y))
    # svm.fit(train_svm_x, train_svm_y)
    #
    # print("\nSVM model: Y = w0 + w1*x1 + w2*x2")  # 分类超平面模型
    # print('截距: w0={}'.format(svm.intercept_))  # w0: 截距, YouCans
    # print('系数: w1={}'.format(svm.coef_))  # w1,w2: 系数, XUPT
    #
    # test_svm_x = []  # [b 3780]
    # test_svm_y = []
    # for i, file in enumerate(filenames[int(total * 0.7):]):
    #     with open(file, 'rb') as f:
    #         x = pickle.load(f)  # [39,]
    #         y = int(pickle.load(f))  # [1,]
    #         test_svm_x.append(x)
    #         test_svm_y.append(y)
    # test_svm_x = np.array(test_svm_x)
    # test_svm_y = np.array(test_svm_y)
    #
    # print('\n分类准确度：{:.4f}'.format(svm.score(test_svm_x, test_svm_y)))  # 对训练集的分类准确度

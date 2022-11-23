# encoding: utf-8
"""
@author: Xin Zhang
@contact: zhangxin@szbl.ac.cn
@time: 12/5/21 9:02 PM
@desc:
"""
import os
import torch
import torch.nn.functional as F
from torch.utils.tensorboard import SummaryWriter
import time
from data_pipeline.dataset_szu import SZUDataset, collate_
from model.eeg_net import EEGNet
# from model.field_flow import FieldFlow
# from model.lrp_manager import ignite_relprop, generate_visualization
# from utils.weight_init import get_state_dict

# torch.cuda.set_device(6)
batch_size = 32
n_epoch = 2000

id_experiment = '_2000e03l-set1-4-EEGNet'
t_experiment = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())

# ../../Datasets/pkl_ave
# E:/Datasets/CVPR2021-02785/pkl
# E:/Datasets/SZFace2/EEG/pkl_ave
dataset = SZUDataset(path='../../Datasets/pkl_ave', contains='subject1', endswith='.pkl')
total_x = dataset.__len__()
print(total_x, ' link start !!!!!!')
loader = torch.utils.data.DataLoader(dataset, collate_fn=collate_, batch_size=batch_size, num_workers=4,
                                     prefetch_factor=2, shuffle=True, drop_last=True)

# ff = FieldFlow(dim=96, num_heads=6, mlp_dilator=2, qkv_bias=False, drop_rate=0.2, attn_drop_rate=0.2,
#                t=500, n_signals=127, n_classes=40).cuda()
# ff.load_state_dict(get_state_dict('log/checkpoint/2022-11-04-15-59-42_1000e03l-pre.pkl',
#                                   map_location='cuda:0', exclude=['arc_margin.weight']))
ff = EEGNet(classes_num=40, drop_out=0.25).cuda()

optimizer = torch.optim.AdamW(ff.parameters(), lr=0.0003, betas=(0.9, 0.98), eps=1e-9)
# optimizer = NoamOpt(model_size=40, factor=1, warmup=8000,
#                     optimizer=torch.optim.Adam(ff.parameters(), lr=0, betas=(0.9, 0.98), eps=1e-9))

# ----- Testing code start ----- Use following to test code without load data -----
# _x = torch.ones(3, 500, 127).unsqueeze(1).cuda()  # [batch_size, 1, time_step, channels]
# _y = torch.tensor([1, 0, 1], dtype=torch.long).cuda()
# optimizer.zero_grad()
# _logits = ff(_x)  # [bs, 40]
# _loss = F.cross_entropy(_logits, _y)
# _loss.backward()
# optimizer.step()
# del _x, _y, _logits, _loss
# _cam = ignite_relprop(model=ff, _x=_x[0].unsqueeze(0), index=_y[0])  # [1, 1, 500, 128]
# generate_visualization(_x[0].squeeze(), _cam.squeeze())
# ----- Testing code end-----------------------------------------------------------

summary = SummaryWriter(log_dir='./log/'+t_experiment+id_experiment+'/')
if __name__ == '__main__':
    step = 0
    global_step = 0
    for epoch in range(1, n_epoch + 1):
        for x, label in loader:
            #  [b, 1, 500, 127], [b]
            if x is None and label is None:
                step += 1
                global_step += 1
                continue

            x = x.cuda()
            label = label.cuda()
            ff.train()
            # if step % 2 == 0:
            optimizer.zero_grad()  # clean grad per 2 step, to double the batch_size

            y = ff(x)  # [bs, 40]
            loss = F.cross_entropy(y, label)
            loss.backward()
            optimizer.step()
            lr = optimizer.param_groups[0]['lr']

            step += 1
            global_step += 1
            if step % 1 == 0:
                corrects = (torch.argmax(y, dim=1).data == label.data)
                accuracy = corrects.cpu().int().sum().numpy() / batch_size
                print('epoch:{}/{} step:{}/{} global_step:{} '
                      'loss={:.5f} acc={:.3f} lr={}'.format(epoch, n_epoch, step,
                                                            int(10*((total_x/batch_size)+0.5)/10), global_step,
                                                            loss, accuracy, lr))
                summary.add_scalar(tag='TrainLoss', scalar_value=loss, global_step=global_step)
                summary.add_scalar(tag='TrainAcc', scalar_value=accuracy, global_step=global_step)
            del x, label, loss, accuracy
            # if step % 10 == 0:
            #     cam = ignite_relprop(model=ff, x=x[0].unsqueeze(0), index=label[0])  # [1, 1, 512, 96]
            #     generate_visualization(x[0].squeeze(), cam.squeeze(),
            #                            save_name='S' + str(global_step) + '_C' + str(label[0].cpu().numpy()))

        step = 0
    # torch.save(ff.state_dict(), 'log/checkpoint/' + t_experiment + id_experiment + '.pkl')
    summary.flush()
    summary.close()
    print('done')

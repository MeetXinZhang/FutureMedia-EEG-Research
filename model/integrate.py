# encoding: utf-8
"""
@author: Xin Zhang
@contact: zhangxin@szbl.ac.cn
@time: 12/6/21 2:50 PM
@desc:
"""
from torch import nn
# from model._transformer_v0 import Encoder
from model .transformer import Encoder, EncoderLayer, MultiHeadedAttention, PositionWiseFeedForward, PositionalEncoding

import copy


# def use_torch_interface():
#     encoder_layer = nn.TransformerEncoderLayer(d_model=96, nhead=8, batch_first=True)
#     encoder = nn.TransformerEncoder(encoder_layer, num_layers=6)
#     return encoder

def make_transformer(N=6, d_model=512, d_ff=2048, h=8, dropout=0.1):
    """Helper: Construct a model from hyperparameters."""
    c = copy.deepcopy
    attn = MultiHeadedAttention(h, d_model)
    ff = PositionWiseFeedForward(d_model, d_ff, dropout)
    position = PositionalEncoding(d_model, dropout)
    model = TransformerModel(
        Encoder(EncoderLayer(d_model, c(attn), c(ff), dropout), N))
    # This was important from their code.
    # Initialize parameters with Glorot / fan_avg.
    for p in model.parameters():
        if p.dim() > 1:
            nn.init.xavier_uniform(p)
    return model


class TransformerModel(nn.Module):
    """
    A standard Encoder-Decoder architecture. Base for this and many
    other models.
    """

    def __init__(self, encoder):
        super(TransformerModel, self).__init__()
        self.encoder = encoder

    def forward(self, src, src_mask):
        "Take in and process masked src and target sequences."
        return self.encode(src, src_mask)

    def encode(self, src, src_mask):
        return self.encoder(src), src_mask


class EEGModel(nn.Module):
    def __init__(self):
        super(EEGModel, self).__init__()
        # Encoder of transformer
        # self.encoder = use_torch_interface()
        # self.encoder = Encoder(dim_in=96, n_head=8, time_step=512, dropout=0.3)
        self.encoder = make_transformer()
        # classifier
        self.den1 = nn.Linear(in_features=96, out_features=192)
        self.den2 = nn.Linear(in_features=192, out_features=96)
        self.den3 = nn.Linear(in_features=96, out_features=40)
        self.dropout = nn.Dropout(p=0.3)

    def forward(self, x):
        h1 = self.encoder(x, mask=None)  # [bs, time_step, 96]
        last_step = h1[:, -1, :]  # [bs, 96]

        h2 = self.den1(last_step)
        h2 = self.dropout(h2)
        h3 = self.den2(h2)
        h3 = self.dropout(h3)
        logits = self.den3(h3)
        return logits



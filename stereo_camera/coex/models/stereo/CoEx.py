from __future__ import print_function
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable

from .submodules.feature import Feature, FeatUp
from .submodules.utils import AttentionCostVolume
from .submodules.aggregation import Aggregation
from .submodules.regression import Regression
from .submodules.util_conv import BasicConv, Conv2x

import pdb


class CoEx(nn.Module):
    def __init__(self, cfg):
        super(CoEx, self).__init__()
        self.cfg = cfg
        self.type = self.cfg['backbone']['type']
        chans = self.cfg['backbone']['channels'][self.type]\

        self.D = int(self.cfg['max_disparity']/4)

        # set up the feature extraction first
        self.feature = Feature(self.cfg)
        self.up = FeatUp(self.cfg)

        self.corr_volume = cfg['corr_volume']
        if self.corr_volume:
            self.cost_volume = AttentionCostVolume(
                cfg['max_disparity'],
                chans[1]*2+self.cfg['spixel']['branch_channels'][1],
                chans[1]*2,
                1,
                weighted=cfg['matching_weighted'])
            matching_head = cfg['matching_head']
        else:
            self.cost_conv = BasicConv(
                chans[1]*2+self.cfg['spixel']['branch_channels'][1],
                chans[1]*2,
                kernel_size=3,
                padding=1,
                stride=1)
            self.cost_desc = nn.Conv2d(
                chans[1]*2,
                chans[1],
                kernel_size=1,
                padding=0,
                stride=1)
            matching_head = chans[1]*2

        self.cost_agg = Aggregation(
            cfg['backbone'],
            max_disparity=cfg['max_disparity'],
            matching_head=matching_head,
            gce=cfg['gce'],
            disp_strides=cfg['aggregation']['disp_strides'],
            channels=cfg['aggregation']['channels'],
            blocks_num=cfg['aggregation']['blocks_num'],
            spixel_branch_channels=cfg['spixel']['branch_channels'])
        self.regression = Regression(
            max_disparity=cfg['max_disparity'],
            top_k=cfg['regression']['top_k'])

        self.stem_2 = nn.Sequential(
            BasicConv(3, self.cfg['spixel']['branch_channels'][0], kernel_size=3, stride=2, padding=1),
            nn.Conv2d(self.cfg['spixel']['branch_channels'][0], self.cfg['spixel']['branch_channels'][0], 3, 1, 1, bias=False),
            nn.BatchNorm2d(self.cfg['spixel']['branch_channels'][0]), nn.ReLU()
            )
        self.stem_4 = nn.Sequential(
            BasicConv(self.cfg['spixel']['branch_channels'][0], self.cfg['spixel']['branch_channels'][1], kernel_size=3, stride=2, padding=1),
            nn.Conv2d(self.cfg['spixel']['branch_channels'][1], self.cfg['spixel']['branch_channels'][1], 3, 1, 1, bias=False),
            nn.BatchNorm2d(self.cfg['spixel']['branch_channels'][1]), nn.ReLU()
            )

        self.spx = nn.Sequential(nn.ConvTranspose2d(2*32, 9, kernel_size=4, stride=2, padding=1),)
        self.spx_2 = Conv2x(chans[1], 32, True)
        self.spx_4 = nn.Sequential(
            BasicConv(chans[1]*2+self.cfg['spixel']['branch_channels'][1], chans[1], kernel_size=3, stride=1, padding=1),
            nn.Conv2d(chans[1], chans[1], 3, 1, 1, bias=False),
            nn.BatchNorm2d(chans[1]), nn.ReLU()
            )

    def forward(self, imL, imR=None, u0=None, v0=None, training=False):
        if imR is not None:
            assert imL.shape == imR.shape
            imL = torch.cat([imL, imR], 0)

        # print(imL.shape)
        b, c, h, w = imL.shape
        v2, v = self.feature(imL)
        x2, y2 = v2.split(dim=0, split_size=b//2)

        v = self.up(v)
        x, y = [], []
        for v_ in v:
            x_, y_ = v_.split(dim=0, split_size=b//2)
            x.append(x_)
            y.append(y_)

        stem_2v = self.stem_2(imL)
        stem_4v = self.stem_4(stem_2v)
        stem_2x, stem_2y = stem_2v.split(dim=0, split_size=b//2)
        stem_4x, stem_4y = stem_4v.split(dim=0, split_size=b//2)

        x[0] = torch.cat((x[0], stem_4x), 1)
        y[0] = torch.cat((y[0], stem_4y), 1)

        # Cost volume processing

        if self.corr_volume:
            cost = (self.cost_volume(x[0], y[0]))[:, :, :-1]
        else:
            refimg_fea = self.cost_conv(x[0])
            targetimg_fea = self.cost_conv(y[0])
            refimg_fea = self.cost_desc(refimg_fea)
            targetimg_fea = self.cost_desc(targetimg_fea)

            cost = Variable(
                torch.FloatTensor(
                    refimg_fea.size()[0],
                    refimg_fea.size()[1]*2,
                    self.D, 
                    refimg_fea.size()[2], 
                    refimg_fea.size()[3]).zero_()).cuda()
            for i in range(self.D):
                if i > 0:
                    cost[:, :refimg_fea.size()[1], i, :, i:] = refimg_fea[:, :, :, i:]
                    cost[:, refimg_fea.size()[1]:, i, :, i:] = targetimg_fea[:, :, :, :-i]
                else:
                    cost[:, :refimg_fea.size()[1], i, :, :] = refimg_fea
                    cost[:, refimg_fea.size()[1]:, i, :, :] = targetimg_fea
            cost = cost.contiguous()

        cost = self.cost_agg(x, cost)

        # spixel guide comp
        xspx = self.spx_4(x[0])
        xspx = self.spx_2(xspx, stem_2x)
        spx_pred = self.spx(xspx)
        spx_pred = F.softmax(spx_pred, 1)
        # Regression
        disp_pred = self.regression(cost, spx_pred, training=training)
        if training:
            disp_pred.append(0)

        return disp_pred

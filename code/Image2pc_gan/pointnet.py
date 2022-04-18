# -*- coding: utf-8 -*-

import numpy as np


import torch
import torch.autograd as autograd
import torch.nn as nn
import torch.nn.functional as F

class STN3D(nn.Module):
	def __init__(self):
		super(STN3D, self).__init__()
		self.conv1 = nn.Conv1d(3, 64, 1)
		self.conv2 = nn.Conv1d(64, 128, 1)
		self.conv3 = nn.Conv1d(128, 1024, 1)
		self.fc1 = nn.Linear(1024, 512)
		self.fc2 = nn.Linear(512, 256)
		self.fc3 = nn.Linear(256, 9)
		self.bn1 = nn.BatchNorm1d(64)
		self.bn2 = nn.BatchNorm1d(128)
		self.bn3 = nn.BatchNorm1d(1024)
		self.bn4 = nn.BatchNorm1d(512)
		self.bn5 = nn.BatchNorm1d(256)


	def forward(self, x):
		batchsize = x.size()[0]
		x = F.relu(self.bn1(self.conv1(x)))
		x = F.relu(self.bn2(self.conv2(x)))
		x = F.relu(self.bn3(self.conv3(x)))
		x = torch.max(x, 2, keepdim=True)[0]
		x = x.view(-1, 1024)

		x = F.relu(self.bn4(self.fc1(x)))
		x = F.relu(self.bn5(self.fc2(x)))
		x = self.fc3(x)

		iden = autograd.Variable(torch.from_numpy(np.array([1,0,0,0,1,0,0,0,1]).astype(np.float32))).view(1,9).repeat(batchsize, 1)
		if x.is_cuda:
			iden = iden.cuda()
		x += iden
		x = x.view(-1, 3, 3)
		return x


class PointNetfeat(nn.Module):
	def __init__(self, global_feat=True):
		super(PointNetfeat, self).__init__()
		self.stn = STN3D()
		self.conv1 = nn.Conv1d(3, 64, 1)
		self.conv2 = nn.Conv1d(64, 128, 1)
		self.conv3 = nn.Conv1d(128, 1024, 1)
		self.bn1 = nn.BatchNorm1d(64)
		self.bn2 = nn.BatchNorm1d(128)
		self.bn3 = nn.BatchNorm1d(1024)
		self.global_feat = global_feat


	def forward(self, x):
		batchsize = x.size()[0]
		n_pts = x.size()[2]
		trans = self.stn(x)
		x = x.transpose(2, 1)
		x = torch.bmm(x, trans)
		x = x.transpose(2, 1)
		x = F.relu(self.bn1(self.conv1(x)))
		pointfeat = x
		x = F.relu(self.bn2(self.conv2(x)))
		x = self.bn3(self.conv3(x))
		x = torch.max(x, 2, keepdim=True)[0]
		x = x.view(-1, 1024)
		if self.global_feat:
			return x, trans
		else:
			x = x.view(-1, 1024, 1).repeat(1, 1, n_pts)
			return torch.cat([x, pointfeat], 1), trans


class PointNetCls(nn.Module):
	def __init__(self, k=1):
		super(PointNetCls, self).__init__()
		self.k = k
		self.feat = PointNetfeat(global_feat=True)
		self.fc1 = nn.Linear(1024, 512)
		self.fc2 = nn.Linear(512, 256)
		self.fc3 = nn.Linear(256, k)
		self.bn1 = nn.BatchNorm1d(512)
		self.bn2 = nn.BatchNorm1d(256)



	def forward(self, x): 
		if True:
			x = x.view(x.size()[0], 3, -1)        
		x, trans = self.feat(x)
		x = F.relu(self.bn1(self.fc1(x)))
		x = F.relu(self.bn2(self.fc2(x)))
		x = self.fc3(x)
        
		return torch.sigmoid(x).squeeze()



if __name__ == '__main__':

	sim_data = autograd.Variable(torch.randn(32, 3, 8000))
	# trans = STN3D()
	# out = trans(sim_data)
	# print('stn', out.size())

	# pointfeat = PointNetfeat(global_feat=True)
	# out, _ = pointfeat(sim_data)
	# print('global feat', out.size())

	# pointfeat = PointNetfeat(global_feat=False)
	# out, _ = pointfeat(sim_data)
	# print('point feat', out.size())

	cls = PointNetCls(k=1)
	out = cls(sim_data)
	print('class', out.size())

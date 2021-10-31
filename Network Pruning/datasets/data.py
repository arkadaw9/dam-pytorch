import os

import torch
import torch.utils.data as data
from torch.utils.data.sampler import SubsetRandomSampler
from torchvision import transforms, datasets
from torchvision.datasets import CIFAR10, CIFAR100, SVHN
from sklearn.model_selection import train_test_split
import numpy as np

class DataManager:
    def __init__(self, args):
        self.dataset_name = args.dataset
        self.batch_size = args.batch_size
        self.workers = args.workers
        self.valid_size = args.valid_size
        self.num_train = 0
        self.num_classes = {'c10': 10, 'c100': 100}[self.dataset_name]
        self.insize = {'c10': 32, 'c100': 32}[self.dataset_name]

    def prepare_data(self):
        print('... Preparing data ...')
        if self.dataset_name in ['c10', 'c100']:
            norm_mean = [0.49139968, 0.48215827, 0.44653124]
            norm_std = [0.24703233, 0.24348505, 0.26158768]
            norm_transform = transforms.Normalize(norm_mean, norm_std)
            train_transform = transforms.Compose([
                transforms.RandomCrop(32, padding=4),
                transforms.RandomHorizontalFlip(),
                transforms.ToTensor(),
                norm_transform
            ])
            val_transform = transforms.Compose([
                transforms.ToTensor(),
                norm_transform
            ])
            dataset_choice = {'c10': CIFAR10, 'c100': CIFAR100}[self.dataset_name]
            trainset = dataset_choice(root='./data', train=True, download=True,
                                            transform=train_transform)

            valset = dataset_choice(root='./data', train=True, download=True,
                                                transform=val_transform)

            testset = dataset_choice(root='./data', train=False, download=True,
                                                transform=val_transform)

        self.num_train = len(trainset)
        train_idx, val_idx = self.get_split()
        train_sampler = SubsetRandomSampler(train_idx)
        val_sampler = SubsetRandomSampler(val_idx)
        train_loader = data.DataLoader(trainset, self.batch_size, num_workers=self.workers,
                                       sampler=train_sampler, pin_memory=True)
        val_loader = data.DataLoader(valset, self.batch_size, num_workers=self.workers, sampler=val_sampler,
                                     pin_memory=True)
        test_loader = data.DataLoader(testset, self.batch_size, num_workers=self.workers, shuffle=False,
                                     pin_memory=False)
        return train_loader, val_loader, test_loader

    def get_split(self):
        if(os.path.exists(f'data_splits/{self.dataset_name}_train_idx.npy') and os.path.exists(f'data_splits/{self.dataset_name}_valid_idx.npy')):
            print('using fixed split')
            train_idx, valid_idx = np.load(f'data_splits/{self.dataset_name}_train_idx.npy'), np.load(f'data_splits/{self.dataset_name}_valid_idx.npy')
            print(len(train_idx),len(valid_idx))
        else:
            print('creating a split')
            indices = list(range(self.num_train))
            train_idx, valid_idx = train_test_split(indices, test_size=self.valid_size)
            np.save(f'data_splits/{self.dataset_name}_train_idx.npy',train_idx)
            np.save(f'data_splits/{self.dataset_name}_valid_idx.npy',valid_idx)
        return train_idx, valid_idx



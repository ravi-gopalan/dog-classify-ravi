# -*- coding: utf-8 -*-
from PIL import Image, ImageFile

import torch
from torchvision import datasets, transforms, models
import torch.nn as nn
from collections import OrderedDict

def check_device_type():
	if torch.cuda.is_available():
		device = torch.device('cuda')
	else:
		device = torch.device('cpu')
	return device
	
def load_transfer_learning_model(filepath, device):
	tf_inference_model = models.resnet50()
	
	classifier = nn.Sequential(\
		OrderedDict([\
			('fc1', nn.Linear(2048, 256)),\
			('relu', nn.ReLU()),\
			('drop',nn.Dropout(0.2)),\
			('fc2', nn.Linear(256, 133)),\
			('relu', nn.ReLU()),\
			('output', nn.LogSoftmax(dim=1))\
			]))

	tf_inference_model.fc = classifier
	tf_inference_model.load_state_dict(torch.load(filepath,map_location=device))
	return tf_inference_model
	

def predict_dog_breed(img_file_path):
	with open('dog_classes.csv', 'r') as f:
		dog_names = f.readlines()

	if torch.cuda.is_available():
		device = torch.device('cuda')
	else:
		device = torch.device('cpu')

	inference_model = load_transfer_learning_model('saved_models/transfer_resnet50.pt', device)
	inference_model.eval()
	
	transform = transforms.Compose([\
		transforms.Resize(256),\
		transforms.RandomResizedCrop(224),\
		transforms.ToTensor(),\
		transforms.Normalize(mean=[0.5,0.5,0.5],std=[0.5,0.5,0.5])])

	if torch.cuda.is_available():
		out_tensor = inference_model(torch.unsqueeze(transform(Image.open(img_file_path)).cuda(),0))
	else:
		out_tensor = inference_model(torch.unsqueeze(transform(Image.open(img_file_path)),0))

	_, index = torch.max(out_tensor, 1)
	#percentage = nn.functional.softmax(out_tensor, dim=1)[0] * 100
	breed = dog_names[index[0].item()]
	print('This is a {}'.format(breed))
	return breed
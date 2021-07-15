import argparse
from PIL import Image
import torchvision
import torch
import json
from torchvision import transforms as T
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models.detection.mask_rcnn import MaskRCNNPredictor
from torchvision.transforms import transforms
import matplotlib.pyplot as plt
import numpy as np
import torchvision.transforms.functional as F
import colorsys
import random
from classification.classification_utils import Classification_Helper
    
def random_colors(N, brightness=0.01):
    """
    Generate random colors.
    To get visually distinct colors, generate them in HSV space then
    convert to RGB.
    """
   
    hsv = [(i / N, 1, brightness) for i in range(N)]
    colors = list(map(lambda c: colorsys.hsv_to_rgb(*c), hsv))
    random.shuffle(colors)
    return colors


def get_instance_segmentation_model(num_classes):
    print('ENTRATOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO')
    # load an instance segmentation model pre-trained on COCO
    model = torchvision.models.detection.maskrcnn_resnet50_fpn(pretrained=True)

  
    # get the number of input features for the classifier
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    print(f'in_features: {in_features}')
    # replace the pre-trained head with a new one
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)

    # now get the number of input features for the mask classifier
    in_features_mask = model.roi_heads.mask_predictor.conv5_mask.in_channels
    print(f'in_features_mask: {in_features_mask}')
    hidden_layer = 256
    # and replace the mask predictor with a new one
    model.roi_heads.mask_predictor = MaskRCNNPredictor(in_features_mask,
                                                       hidden_layer,
                                                       num_classes)

    return model

def show_bboxes_and_masks(image, boxes, masks, colors, alpha=0.2):
    for i,mask, bbox in zip(range(len(masks)), masks, boxes):
        #define bbox
     
        plt.gca().add_patch(
            plt.Rectangle((bbox[0], bbox[1]),
            bbox[2] - bbox[0],
            bbox[3] - bbox[1], fill=False,
            edgecolor='blue', linewidth=2, alpha=0.9)
        )

        #define mask
        for c in range(3):
            image[:, :, c] = np.where(mask == 1,
                                    image[:, :, c] *
                                    (1 - alpha) + alpha * colors[i][c] * 255,
                                    image[:, :, c])
    plt.imshow(image)
    plt.show()


parser = argparse.ArgumentParser(description='Computer Vision pipeline')
parser.add_argument('-img', '--image', type=str,
                    help='path of the image to analyze', required=True)

args = parser.parse_args()
img_path = args.image


try:
    img = Image.open(img_path)
    transform = transforms.Compose([                       
    transforms.ToTensor()])
    img = transform(img)
except FileNotFoundError:
    print('Impossible to open the specified file. Check the name and try again.')


#now I can use my model to segment the image(for the moment we use a fully pretrained maskrcnn)
#model = torchvision.models.detection.maskrcnn_resnet50_fpn(pretrained=True)
model = get_instance_segmentation_model(102)
model.load_state_dict(torch.load('model.pt', map_location=torch.device('cpu'))['model_state_dict'])
model.eval()
prediction = model([img])

scores = prediction[0]['scores']
scores = scores > 0.6
scores = scores.nonzero()
num_objs = len(scores)


boxes = prediction[0]['boxes'][:num_objs,:]
labels = prediction[0]['labels'][:num_objs]
print(labels)
boxes = boxes.detach().numpy()
masks = prediction[0]['masks'][:num_objs,:,:]
masks = masks.detach().numpy().round()
masks = np.squeeze(masks)

img = img.detach().numpy()
img = np.swapaxes(img, 0,2)
img = np.swapaxes(img, 0,1)

show_bboxes_and_masks(img, boxes, masks, random_colors(num_objs))

#classification phase

#construct vector
#i load the dataset info
with open('dataset_processing/dataset_info_all_objs.json', 'r') as f:
    data = json.load(f)

with open('dataset_processing/mapping.json', 'r') as f:
    mapping = json.load(f)

num_objs = len(data['instances_per_obj'])
vector = np.zeros((1,num_objs))
labels = np.unique(labels) #-1 because labels start from 1 but array indexing from 0
idxs = []
for label in labels:
    for map in mapping:
        if mapping[map]['new_label'] == label:
            print(map)
            idxs.append(list(data['instances_per_obj']).index(map))
            print(list(data['instances_per_obj']).index(map))

vector[:,idxs] = 1
classification_helper = Classification_Helper()
predicted_room = classification_helper.predict_room(vector)

print(f'The predicted room is: {predicted_room}')






import random
import cv2
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import numpy as np

class Plotter():
    def plot_image(self, image):
        plt.imshow(image)
        plt.show()

    def plot_imgs_by_row(self, images: list, titles: list, num_imgs):
        f, axes = plt.subplots(1, num_imgs)

        for i, image, title in zip(range(num_imgs), images, titles):
            axes[i].set_title(title)
            axes[i].imshow(image)
        plt.show()

    def random_colors(self, num_objs):
        colors = [[random.randint(0, 255) for _ in range(3)] for _ in range(num_objs)]
        return colors

    def show_bboxes_and_masks(self, image, boxes, masks, labels, scores, output_file=None):
        image = np.copy(image)
        f, axarr = plt.subplots(1,2)
        alpha=0.5
        colors = self.random_colors(len(masks))

        axarr[0].set_title('Test image')
        axarr[0].imshow(image)

        
        for i,mask,box,label,score in zip(range(len(masks)), masks, boxes, labels, scores):
            
            #define bbox
            #(x1, y1) is top left
            #(x2,y2) is bottom right
        
            tl = 2  # line thickness
            c1, c2 = (int(box[0]), int(box[1])), (int(box[2]), int(box[3]))

            cv2.rectangle(image, c1, c2, colors[i], tl)
            # draw text
            display_txt = "%s: %.1f%%" % (label, 100 * score)
            tf = 1  # font thickness
            t_size = cv2.getTextSize(display_txt, 0, fontScale=tl / 3, thickness=tf)[0]
            c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
            cv2.rectangle(image, c1, c2, colors[i], -1)  # filled
            cv2.putText(image, display_txt, (c1[0], c1[1] - 2), 0, tl / 3, [225, 255, 255], thickness=tf,
                        lineType=cv2.LINE_AA)

            #define mask
            for c in range(3):
                image[:, :, c] = np.where(mask == 1,
                                        image[:, :, c] *
                                        (1 - alpha) + alpha * colors[i][c],
                                        image[:, :, c])
        
        
        axarr[1].set_title('Segmented image')
        axarr[1].imshow(image)
        plt.show()
        if output_file:
            plt.imsave(output_file, image)

    def plot_retrieval_results(query_img, similar_images: list, retrieval_method):
        #images are already sorted by similarity
        #we always plot first 5 results
        fig = plt.figure()
        fig.suptitle("Controlling subplot sizes with width_ratios and height_ratios")

        gs = GridSpec(3, 3, width_ratios=[1, 2], height_ratios=[4, 1])
        query_axis = fig.add_subplot(gs[0,1])
        query_axis.imshow(query_img)

        ax1 = fig.add_subplot(gs[1,0])
        ax1.imshow(similar_images[0])

        ax2 = fig.add_subplot(gs[1,1])
        ax2.imshow(similar_images[1])

        ax3 = fig.add_subplot(gs[1,2])
        ax3.imshow(similar_images[2])

        ax4 = fig.add_subplot(gs[2,0])
        ax4.imshow(similar_images[3])

        ax5 = fig.add_subplot(gs[2,1])
        ax5.imshow(similar_images[4])

        plt.show()
from imgaug import augmenters as iaa
import cv2
import numpy as np 
import os
from PIL import Image  
import shutil
from tqdm import tqdm

def copyFile(src, dest):
    try:
        shutil.copy(src, dest)
    except shutil.Error as e:
        print('Error: %s' % e)
    except IOError as e:
        print('Error: %s' % e.strerror)

def create_train_and_val_folders():
    num_train_samples = len(os.listdir('../train/'))
    num_valid_samples = len(os.listdir('../validation/'))
    print('Train images: {}, validation images: {}'.format(
        num_train_samples, num_valid_samples))
    train_images = sorted(os.listdir('../train/'))
    valid_images = sorted(os.listdir('../validation/'))
    labels_idxs = sorted(set([int(image.split('_')[1].split('.')[0])
                        for image in train_images]))

    if not os.path.exists('../data/train'):
        os.makedirs('../data/train')
    if not os.path.exists('../data/validation'):
        os.makedirs('../data/validation')
    for label_idx in labels_idxs:
        shutil.rmtree(os.path.join('../data/train', str(label_idx)))
        shutil.rmtree(os.path.join('../data/validation', str(label_idx)))
        os.makedirs(os.path.join('../data/train', str(label_idx)))
        os.makedirs(os.path.join('../data/validation', str(label_idx)))

    for image in tqdm(train_images):
        label_idx = image.split('_')[1].split('.')[0]
        old_path = os.path.join('../train/', image)
        new_path = os.path.join('../data/train', label_idx)
        copyFile(old_path, new_path)
    for image in tqdm(valid_images):
        label_idx = image.split('_')[1].split('.')[0]
        old_path = os.path.join('../validation/', image)
        new_path = os.path.join('../data/validation', label_idx)
        copyFile(old_path, new_path)

def crop_and_save_imgs(percent_cropped=0.1):
    for img_folder in sorted(os.listdir('../data/train')):
        img_folder_path = os.path.join('../data/train', img_folder)
        print('\n {}'.format(img_folder_path))
        for img_file in tqdm(sorted(os.listdir(img_folder_path))):
            img_file_path = os.path.join(img_folder_path, img_file)
            img_arr = cv2.imread(img_file_path)
            img_arr = iaa.Crop(px=(int(percent_cropped*img_arr.shape[0]),
                                    int(percent_cropped*img_arr.shape[1]),
                                    int(percent_cropped*img_arr.shape[0]),
                                    int(percent_cropped*img_arr.shape[1])),
                                keep_size=False).augment_image(img_arr)
            cv2.imwrite(img_file_path, img_arr)

    for img_folder in sorted(os.listdir('../data/validation')):
        img_folder_path = os.path.join('../data/validation', img_folder)
        print('\n {}'.format(img_folder_path))
        for img_file in tqdm(sorted(os.listdir(img_folder_path))):
            img_file_path = os.path.join(img_folder_path, img_file)
            img_arr = cv2.imread(img_file_path)
            img_arr = iaa.Crop(px=(int(percent_cropped*img_arr.shape[0]),
                                    int(percent_cropped*img_arr.shape[1]),
                                    int(percent_cropped*img_arr.shape[0]),
                                    int(percent_cropped*img_arr.shape[1])),
                                keep_size=False).augment_image(img_arr)
            cv2.imwrite(img_file_path, img_arr)


def convert_test_files_to_rgb(test_dir):
    num_test_samples = 12800  # test dataset
    for i in range(num_test_samples): 
        filename =test_dir + str(i+1) + ".jpg" 
        if not os.path.exists(filename):  
            print("Don't exist image ", i+1)  
            continue  
        with Image.open(filename) as image:  
            img = np.array(image)  
            if len(img.shape) != 3 or img.shape[2] != 3:  
                rgb_image = image.convert('RGB')  
                rgb_image.save(filename)  
                print("Transform succesfully image ", i+1)


def preprocess_test_imgs(test_dir, percent_cropped=0.1):
    aug_test_paths = ['../data/test/test12703_top_right/test12703_top_right',
                      '../data/test/test12703_top_left/test12703_top_left',
                      '../data/test/test12703_bottom_right/test12703_bottom_right',
                      '../data/test/test12703_bottom_left/test12703_bottom_left', 
                      '../data/test/test12703_center/test12703_center', 
                      '../data/test/test12703_flip/test12703_flip', 
                      '../data/test/test12703_top_right_flip/test12703_top_right_flip', 
                      '../data/test/test12703_top_left_flip/test12703_top_left_flip', 
                      '../data/test/test12703_bottom_right_flip/test12703_bottom_right_flip', 
                      '../data/test/test12703_bottom_left_flip/test12703_bottom_left_flip', 
                      '../data/test/test12703_center_flip/test12703_center_flip']
    for test_path in aug_test_paths:
        if not os.path.exists(test_path):
            os.makedirs(test_path)
            
    for img_fname in tqdm(sorted(os.listdir(test_dir))):
        img_fpath = os.path.join(test_dir, img_fname)
        img_top_right_fpath = os.path.join('../data/test/test12703_top_right/test12703_top_right', img_fname)
        img_top_left_fpath = os.path.join('../data/test/test12703_top_left/test12703_top_left', img_fname)
        img_bottom_right_fpath = os.path.join('../data/test/test12703_bottom_right/test12703_bottom_right', img_fname)
        img_bottom_left_fpath = os.path.join('../data/test/test12703_bottom_left/test12703_bottom_left', img_fname)
        img_center_fpath = os.path.join('../data/test/test12703_center/test12703_center', img_fname)

        img_flip_fpath = os.path.join('../data/test/test12703_flip/test12703_flip', img_fname)
        img_top_right_flip_fpath = os.path.join('../data/test/test12703_top_right_flip/test12703_top_right_flip', img_fname)
        img_top_left_flip_fpath = os.path.join('../data/test/test12703_top_left_flip/test12703_top_left_flip', img_fname)
        img_bottom_right_flip_fpath = os.path.join('../data/test/test12703_bottom_right_flip/test12703_bottom_right_flip', img_fname)
        img_bottom_left_flip_fpath = os.path.join('../data/test/test12703_bottom_left_flip/test12703_bottom_left_flip', img_fname)
        img_center_flip_fpath = os.path.join('../data/test/test12703_center_flip/test12703_center_flip', img_fname)

        img_arr = cv2.imread(img_fpath)
        flip_img_arr = iaa.Fliplr(1.0).augment_image(img_arr)
        cv2.imwrite(img_flip_fpath, flip_img_arr)

        mod_img_arr = iaa.Crop(px=(int(percent_cropped*img_arr.shape[0]),
                                    int(percent_cropped*img_arr.shape[1]),
                                    0,
                                    0),
                                keep_size=False).augment_image(img_arr)
        cv2.imwrite(img_top_right_fpath, mod_img_arr)
        mod_img_arr = iaa.Fliplr(1.0).augment_image(mod_img_arr)
        cv2.imwrite(img_top_right_flip_fpath, mod_img_arr)

        mod_img_arr = iaa.Crop(px=(int(percent_cropped*img_arr.shape[0]),
                                    0,
                                    0,
                                    int(percent_cropped*img_arr.shape[1])),
                                keep_size=False).augment_image(img_arr)
        cv2.imwrite(img_top_left_fpath, mod_img_arr)
        mod_img_arr = iaa.Fliplr(1.0).augment_image(mod_img_arr)
        cv2.imwrite(img_top_left_flip_fpath, mod_img_arr)

        mod_img_arr = iaa.Crop(px=(0,
                                   int(percent_cropped*img_arr.shape[1]),
                                   int(percent_cropped*img_arr.shape[0]),
                                   0),
                               keep_size=False).augment_image(img_arr)
        cv2.imwrite(img_bottom_right_fpath, mod_img_arr)
        mod_img_arr = iaa.Fliplr(1.0).augment_image(mod_img_arr)
        cv2.imwrite(img_bottom_right_flip_fpath, mod_img_arr)

        mod_img_arr = iaa.Crop(px=(0,
                                   0,
                                   int(percent_cropped*img_arr.shape[0]),
                                   int(percent_cropped*img_arr.shape[1])),
                               keep_size=False).augment_image(img_arr)
        cv2.imwrite(img_bottom_left_fpath, mod_img_arr)
        mod_img_arr = iaa.Fliplr(1.0).augment_image(mod_img_arr)
        cv2.imwrite(img_bottom_left_flip_fpath, mod_img_arr)

        mod_img_arr = iaa.Crop(px=(int(percent_cropped*img_arr.shape[0]),
                                   int(percent_cropped*img_arr.shape[1]),
                                   int(percent_cropped*img_arr.shape[0]),
                                   int(percent_cropped*img_arr.shape[1])),
                               keep_size=False).augment_image(img_arr)
        cv2.imwrite(img_center_fpath, mod_img_arr)
        mod_img_arr = iaa.Fliplr(1.0).augment_image(mod_img_arr)
        cv2.imwrite(img_center_flip_fpath, mod_img_arr)


if __name__=='__main__':
    create_train_and_val_folders()
    # crop_and_save_imgs(0.1)
    # convert_test_files_to_rgb('../data/test/test12703/test12703')
    # preprocess_test_imgs('../data/test/test12703/test12703')

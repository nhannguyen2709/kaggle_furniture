import gc
import numpy as np
import os
import pandas as pd

import tensorflow as tf
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

from keras.backend import tensorflow_backend as K
from keras.callbacks import ModelCheckpoint
from keras.layers import Dense, GlobalMaxPooling2D
from keras.models import Model
from keras.optimizers import Adam, SGD
from keras.preprocessing.image import ImageDataGenerator
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.utils import shuffle

from data import FurnituresDataset
from utils import build_densenet_201, get_image_paths_and_labels, MultiGPUModel
from keras_CLR import CyclicLR


x_from_train_images, y_from_train_images = get_image_paths_and_labels(
    data_dir='data/train/')

# k-fold cross-validation on train and validation images
batch_size = 32
epochs = 5
num_workers = 4
n_splits = 5
n_repeats = 2
num_gpus = 2
rskf = RepeatedStratifiedKFold(n_splits=n_splits, n_repeats=n_repeats, random_state=201)

fold = 0
for train_index, test_index in rskf.split(
        x_from_train_images, y_from_train_images):
    fold += 1
    x_train, x_valid = x_from_train_images[train_index], x_from_train_images[test_index]
    y_train, y_valid = y_from_train_images[train_index], y_from_train_images[test_index]
    print('Found {} images belonging to {} classes'.format(len(x_train), 128))
    print('Found {} images belonging to {} classes'.format(len(x_valid), 128))

    train_generator = FurnituresDataset(
        x_train, y_train, batch_size=batch_size)
    valid_generator = FurnituresDataset(
        x_valid, y_valid, batch_size=batch_size, shuffle=False)
    save_best = ModelCheckpoint(
        'checkpoint/densenet_201/fold{}.weights.best.hdf5'.format(fold),
        monitor='val_acc',
        verbose=1,
        save_best_only=True,
        mode='max')
    clr_triangular = CyclicLR(
        mode='exp_range',
        max_lr=1e-3,
        step_size=len(x_train) //
        batch_size *
        2)
    callbacks = [clr_triangular, save_best]

    ## multi-gpu train
    # base_model = build_densenet_201()
    # parallel_model = MultiGPUModel(base_model, gpus=num_gpus)
    # parallel_model.compile(optimizer=Adam(), loss='categorical_crossentropy', metrics=['acc'])
    # parallel_model.fit_generator(generator=train_generator,
    #                              epochs=epochs,
    #                              steps_per_epoch=1,
    #                              callbacks=callbacks,
    #                              validation_data=valid_generator,
    #                              workers=num_workers)

    # single-gpu train
    model = build_densenet_201()
    model.fit_generator(generator=train_generator,
                        epochs=epochs,
                        callbacks=callbacks,
                        validation_data=valid_generator,
                        workers=num_workers)
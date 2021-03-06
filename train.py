import argparse
import numpy as np
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

from keras.backend import tensorflow_backend as K
from keras.callbacks import ModelCheckpoint, ReduceLROnPlateau
from keras_EMA import ExponentialMovingAverage
from keras.models import load_model
from keras.optimizers import Adam, SGD
from keras import regularizers

from sklearn.utils.class_weight import compute_class_weight
from sklearn.model_selection import train_test_split

from data import AugmentedDataset, Dataset, get_image_paths_and_labels
from model_utils import build_xception, build_densenet_201, build_inception_v3, build_inception_resnet_v2

parser = argparse.ArgumentParser(
    description='Training')
parser.add_argument(
    '--batch-size',
    default=16,
    type=int,
    metavar='N',
    help='mini-batch size')
parser.add_argument(
    '--input-shape',
    nargs='+',
    type=int)
parser.add_argument(
    '--epochs',
    default=20,
    type=int,
    metavar='N',
    help='number of epochs when resuming')
parser.add_argument(
    '--resume',
    default='False',
    type=str,
    help='indicate whether to continue training')
parser.add_argument(
    '--model-name',
    type=str,
    help='model to be trained')
parser.add_argument(
    '--num-workers',
    default=4,
    type=int,
    metavar='N',
    help='maximum number of processes to spin up')
parser.add_argument(
    '--scheme',
    default='trainval',
    type=str)


def train(batch_size, input_shape,
          x_train, y_train,
          x_valid, y_valid,
          model_name, num_workers,
          resume):
    print('Found {} images belonging to {} classes'.format(len(x_train), 128))
    print('Found {} images belonging to {} classes'.format(len(x_valid), 128))
    train_generator = AugmentedDataset(
        x_train, y_train,
        batch_size=batch_size, input_shape=input_shape)
    valid_generator = FurnituresDatasetNoAugmentation(
        x_valid, y_valid,
        batch_size=batch_size, input_shape=input_shape)
    class_weight = compute_class_weight(
        'balanced', np.unique(y_train), y_train)
    class_weight_dict = dict.fromkeys(np.unique(y_train))
    for key in class_weight_dict.keys():
        class_weight_dict.update({key: class_weight[key]})


    filepath = 'checkpoint/{}/iter1.hdf5'.format(model_name)
    save_best = ModelCheckpoint(filepath=filepath,
                                verbose=1,
                                monitor='val_acc',
                                save_best_only=True,
                                mode='max')
    save_on_train_end = ModelCheckpoint(filepath=filepath,
                                        verbose=1,
                                        monitor='val_acc',
                                        period=args.epochs)
    reduce_lr = ReduceLROnPlateau(monitor='val_acc',
                                  factor=0.2,
                                  patience=2,
                                  verbose=1)
    callbacks = [save_best, save_on_train_end, reduce_lr]

    if resume == 'True':
        print('\nResume training from the last checkpoint')
        model = load_model(filepath)
        trainable_count = int(
            np.sum([K.count_params(p) for p in set(model.trainable_weights)]))
        print('Trainable params: {:,}'.format(trainable_count))
        model.fit_generator(generator=train_generator,
                            epochs=args.epochs,
                            callbacks=callbacks,
                            validation_data=valid_generator,
                            class_weight=class_weight_dict,
                            workers=num_workers)
    else:
        print('\nTrain the last Dense layer')
        if model_name == 'densenet_201':
            model = build_densenet_201()
        elif model_name == 'inception_v3':
            model = build_inception_v3()
        elif model_name == 'inception_resnet_v2':
            model = build_inception_resnet_v2()
        elif model_name == 'xception':
            model = build_xception()
        for layer in model.layers[:-1]:
            layer.trainable = False
            model.compile(optimizer=Adam(lr=0.001), loss='categorical_crossentropy',
                          metrics=['acc'])
        model.fit_generator(generator=train_generator,
                            epochs=5,
                            callbacks=callbacks,
                            validation_data=valid_generator,
                            class_weight=class_weight_dict,
                            workers=num_workers)
        K.clear_session()

        print("\nFine-tune the network")
        model = load_model(filepath)
        for layer in model.layers:
            layer.trainable = True
            if hasattr(layer, 'kernel_regularizer'):
                layer.kernel_regularizer = regularizers.l2(0.0001)
        trainable_count = int(
            np.sum([K.count_params(p) for p in set(model.trainable_weights)]))
        print('Trainable params: {:,}'.format(trainable_count))
        model.compile(optimizer=Adam(lr=3e-5),
                      loss='categorical_crossentropy',
                      metrics=['acc'])
        model.fit_generator(generator=train_generator,
                            epochs=30,
                            callbacks=callbacks,
                            validation_data=valid_generator,
                            class_weight=class_weight_dict,
                            workers=num_workers)
        K.clear_session()


if __name__ == '__main__':
    args = parser.parse_args()

    x_train, y_train = get_image_paths_and_labels(
        data_dir='data/train/')
    x_valid, y_valid = get_image_paths_and_labels(
        data_dir='data/validation/')
    merged_x = np.concatenate((x_train, x_valid))
    merged_y = np.concatenate((y_train, y_valid))
    x_train, x_valid, y_train, y_valid = train_test_split(merged_x, merged_y, test_size=0.01)

    train(args.batch_size, tuple(args.input_shape),
            x_train, y_train,
            x_valid, y_valid,
            args.model_name, args.num_workers,
            args.resume)
   
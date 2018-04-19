import numpy as np
import os

from keras.applications.inception_resnet_v2 import InceptionResNetV2
from keras.layers import Dense, GlobalMaxPooling2D
from keras.models import Model
from keras.optimizers import Adam, SGD
from keras.preprocessing.image import ImageDataGenerator

def evaluate_model_no_data_augmentation(valid_dir, input_shape, checkpoint_dir, base_model, model_name, num_workers):
    valid_datagen = ImageDataGenerator(
        rescale=1. / 255)
    valid_generator = valid_datagen.flow_from_directory(
        valid_dir,
        batch_size=64,
        target_size=input_shape,
        class_mode='categorical',
        shuffle=False)
    x = GlobalMaxPooling2D(name='max_pool')(base_model.layers[-1].output)
    x = Dense(128, activation='softmax', name='predictions')(x)
    model = Model(inputs=base_model.layers[0].input, outputs=x)

    model_checkpoint_dir = os.path.join(checkpoint_dir, model_name)
    if not os.path.exists(model_checkpoint_dir):
        os.makedirs(model_checkpoint_dir)

    weights_filenames = sorted(os.listdir(model_checkpoint_dir))
    for weights_filename in weights_filenames:
        model.load_weights(os.path.join(model_checkpoint_dir, weights_filename))
        model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['acc'])
        val_loss, val_acc = model.evaluate_generator(valid_generator, workers=num_workers)
        print(weights_filename, val_loss, val_acc)


def build_inception_resnet_v2(verbose=True):
    model = InceptionResNetV2(include_top=False)
    features = GlobalMaxPooling2D(name='max_pool')(model.layers[-1].output)
    output = Dense(128, activation='softmax', name='predictions')(features)
    model = Model(inputs=model.layers[0].input, outputs=output)
    finetuned_layers_names = [
        # 'conv2d_189',
        # 'conv2d_190',
        # 'conv2d_191',
        # 'conv2d_188',
        # 'block8_7_conv',
        # 'conv2d_191',
        # 'conv2d_193',
        # 'conv2d_194',
        # 'block8_8_conv',
        # 'conv2d_197',
        # 'conv2d_192',
        # 'conv2d_195',
        # 'conv2d_198',
        # 'conv2d_196',
        # 'conv2d_199',
        # 'block8_9_conv',
        # 'conv2d_201',
        # 'conv2d_202',
        # 'conv2d_200',
        # 'conv2d_203',
        # 'block8_10_conv',
        'conv_7b',
        'predictions']
    finetuned_layers = [model.get_layer(name=layer_name)
                        for layer_name in finetuned_layers_names]
    for layer in model.layers:
        if layer not in finetuned_layers:
            layer.trainable = False
    if verbose:
        model.summary()
    model.compile(optimizer=Adam(),  # SGD(momentum=0.9, nesterov=True)
                  loss='categorical_crossentropy',
                  metrics=['acc'])
    return model


def get_image_paths_and_labels(data_dir):
    x = []
    y = []
    for folder in sorted(os.listdir(data_dir)):
        class_path = os.path.join(data_dir, folder)
        for image_filename in sorted(os.listdir(class_path)):
            x.append(os.path.join(class_path, image_filename))
            y.append(int(folder) - 1)
    x = np.array(x)
    y = np.array(y)
    return x, y
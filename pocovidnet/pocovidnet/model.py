#POCOVID-Net model.
from tensorflow.keras.applications import VGG16
from tensorflow.keras.layers import (
    AveragePooling2D, Dense, Dropout, Flatten, Input, BatchNormalization, ReLU
)
from tensorflow.keras.models import Model
from pocovidnet.layers import global_average_pooling
from .utils import fix_layers


def get_model(
    input_size: tuple = (224, 224, 3),
    hidden_size: int = 64,
    dropout: float = 0.5,
    num_classes: int = 3,
    trainable_layers: int = 3
):

    # load the VGG16 network, ensuring the head FC layer sets are left off
    baseModel = VGG16(
        weights="imagenet",
        include_top=False,
        input_tensor=Input(shape=input_size)
    )
    # construct the head of the model that will be placed on top of the
    # the base model
    headModel = baseModel.output
    headModel = AveragePooling2D(pool_size=(4, 4))(headModel)
    headModel = Flatten(name="flatten")(headModel)
    headModel = Dense(hidden_size)(headModel)
    headModel = BatchNormalization()(headModel)
    headModel = ReLU()(headModel)
    headModel = Dropout(dropout)(headModel)
    headModel = Dense(num_classes, activation="softmax")(headModel)

    # place the head FC model on top of the base model
    model = Model(inputs=baseModel.input, outputs=headModel)

    model = fix_layers(model, num_flex_layers=trainable_layers)

    return model


def get_cam_model(
    input_size: tuple = (224, 224, 3),
    num_classes: int = 3,
    trainable_layers: int = 3
):
    """
    Get a VGG model that supports class activation maps

    Keyword Arguments:
        input_size {tuple} -- [Image size] (default: {(224, 224, 3)})
        num_classes {int} -- [Number of output classes] (default: {3})
        trainable_layers {int} -- [Number of trainable layers] (default: {3})

    Returns:
        tensorflow.keras.models object
    """

    # load the VGG16 network, ensuring the head FC layer sets are left off
    baseModel = VGG16(
        weights="imagenet",
        include_top=False,
        input_tensor=Input(shape=input_size)
    )
    headModel = baseModel.output
    headModel = global_average_pooling(headModel)
    headModel = Dense(num_classes, activation="softmax")(headModel)

    model = Model(inputs=baseModel.input, outputs=headModel)
    model = fix_layers(model, num_flex_layers=trainable_layers)

    return model

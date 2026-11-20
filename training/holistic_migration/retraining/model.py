"""The Phase 4 CNN-LSTM (face_train.build_model) with the input width as a parameter."""


def build_model(width, seed):
    import tensorflow as tf
    tf.keras.utils.set_random_seed(seed)
    layers = tf.keras.layers
    model = tf.keras.Sequential(name=f'w{width}_cnnlstm_c64-128_l128-64')
    model.add(layers.Input((30, width), dtype='float32'))
    for filters in [64, 128]:
        model.add(layers.Conv1D(filters, 3, padding='same', activation='relu'))
        model.add(layers.BatchNormalization())
    model.add(layers.MaxPooling1D(2))
    for units, sequences in [(128, True), (64, False)]:
        model.add(layers.LSTM(units, return_sequences=sequences))
        model.add(layers.Dropout(.4))
    model.add(layers.Dense(128, activation='relu'))
    model.add(layers.Dropout(.4))
    model.add(layers.Dense(50, activation='softmax'))
    model.compile(tf.keras.optimizers.Adam(.001), 'sparse_categorical_crossentropy', metrics=['accuracy'])
    return model

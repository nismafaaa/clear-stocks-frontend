import numpy as np
from keras.layers import Dense, Lambda, RepeatVector, Permute, Multiply, Conv1D, Dropout, Bidirectional, LSTM, Flatten, Input
from keras import backend as K
from keras.models import Model

# Constants SINGLE_ATTENTION_VECTOR, PERIOD, INPUT_DIMS, lstm_units should be defined by user

def attention_3d_block(inputs):
    input_dim = int(inputs.shape[2])
    a = Dense(input_dim, activation='softmax')(inputs)
    if SINGLE_ATTENTION_VECTOR:
        a = Lambda(lambda x: K.mean(x, axis=1), name='dim_reduction')(a)
        a = RepeatVector(input_dim)(a)
    a_probs = Permute((1, 2), name='attention_vec')(a)
    output_attention_mul = Multiply()([inputs, a_probs])
    return output_attention_mul

def attention_3d_block2(inputs, single_attention_vector=False):
    time_steps = inputs.shape[1]
    input_dim = inputs.shape[2]
    a = Permute((2, 1))(inputs)
    a = Dense(time_steps, activation='softmax')(a)
    if single_attention_vector:
        a = Lambda(lambda x: K.mean(x, axis=1))(a)
        a = RepeatVector(input_dim)(a)
    a_probs = Permute((2, 1))(a)
    output_attention_mul = Multiply()([inputs, a_probs])
    return output_attention_mul

def NormalizeMult(data):
    data = np.array(data)
    normalize = np.zeros((data.shape[1], 2), dtype='float64')
    for i in range(data.shape[1]):
        col = data[:, i]
        listlow, listhigh = np.percentile(col, [0, 100])
        normalize[i, 0] = listlow
        normalize[i, 1] = listhigh
        delta = listhigh - listlow
        if delta != 0:
            data[:, i] = (data[:, i] - listlow) / delta
    return data, normalize

def FNormalizeMult(data, normalize):
    data = np.array(data)
    for i in range(data.shape[1]):
        listlow = normalize[i, 0]
        listhigh = normalize[i, 1]
        delta = listhigh - listlow
        if delta != 0:
            data[:, i] = data[:, i] * delta + listlow
    return data

def attention_model():
    inputs = Input(shape=(PERIOD, INPUT_DIMS))
    x = Conv1D(filters=64, kernel_size=1, activation='relu')(inputs)
    x = Dropout(0.3)(x)
    lstm_out = Bidirectional(LSTM(lstm_units, return_sequences=True))(x)
    lstm_out = Dropout(0.3)(lstm_out)
    attention_mul = attention_3d_block2(lstm_out)
    attention_mul = Flatten()(attention_mul)
    output = Dense(1, activation='linear')(attention_mul)
    model = Model(inputs=[inputs], outputs=output)
    return model

def rolling_forecast(model, dataset, look_back, input_dims):
    preds = []
    current_window = dataset[:look_back].copy()

    for i in range(len(dataset) - look_back):
        x_input = current_window.reshape(1, look_back, input_dims)
        pred = model.predict(x_input, verbose=0)
        preds.append(pred[0][0])

        # Update window: remove the earliest data and add prediction
        new_row = np.zeros((1, input_dims))
        new_row[0, 0] = pred[0][0]

        if input_dims > 1:
            new_row[0, 1:] = dataset[i + look_back, 1:]

        current_window = np.append(current_window[1:], new_row, axis=0)

    # Add NaN in front, so the length is the same
    pad = np.full(look_back, np.nan)
    final_preds = np.concatenate([pad, preds])
    final_preds = final_preds.reshape(-1, 1)

    return final_preds

def create_dataset(dataset, look_back):
    dataX, dataY = [], []
    for i in range(len(dataset)-look_back-1):
        a = dataset[i:(i+look_back), :]
        dataX.append(a)
        dataY.append(dataset[i + look_back, :])
    TrainX = np.array(dataX)
    Train_Y = np.array(dataY)
    return TrainX, Train_Y

from tensorflow.keras.models import model_from_json

def load(path_to_model, path_to_weights): 
    with open(path_to_model, "r") as json_file:
        loaded_model_json = json_file.read()
    loaded_model = model_from_json(loaded_model_json)

    # Load model weights from HDF5 file
    loaded_model.load_weights(path_to_weights)

    # Compile the loaded model if needed
    loaded_model.compile(optimizer='adam', loss='mse')
    return loaded_model
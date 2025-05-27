import time


def self_improvement_loop(model, X_train, y_train, validation_data, update_interval, num_epochs):
    while True:
        print("Retraining model...")
        model.fit(X_train, y_train, epochs=num_epochs, validation_data=validation_data, verbose=1)
        
        loss, _ = model.evaluate(validation_data[0], validation_data[1])
        print(f"Validation Loss: {loss}")

        
        print(f"Waiting for {update_interval} seconds before next update...")
        time.sleep(update_interval)




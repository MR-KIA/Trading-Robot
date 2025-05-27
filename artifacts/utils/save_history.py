import sys

def save(model, X_train_reshaped, X_test_reshaped,y_train_reshaped,y_test_reshaped):
    # Save the current standard output and standard error streams
    original_stdout = sys.stdout
    original_stderr = sys.stderr

    # Specify the file path where you want to save the output
    output_file_path = 'training_output.txt'

    try:
        # Open the file in write mode
        with open(output_file_path, 'w') as f:
            # Redirect standard output and standard error to the file
            sys.stdout = f
            sys.stderr = f
            
            # Run your training code here
            history = model.fit(X_train_reshaped, y_train_reshaped, epochs=50, batch_size=32, validation_data=(X_test_reshaped, y_test_reshaped))
            
            # Restore the original standard output and standard error streams
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            
            # Optionally, print a message indicating that the output has been saved
            print(f"Training output saved to '{output_file_path}'")
            
    except Exception as e:
        # If an exception occurs, restore the original streams and re-raise the exception
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        raise e
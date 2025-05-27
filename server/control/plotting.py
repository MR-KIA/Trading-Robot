import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def plot_prediction_vs_truth(csv_file):
    data = pd.read_csv(csv_file)

    # Ensure the columns are numeric
    data['predicted'] = pd.to_numeric(data['predicted'], errors='coerce')
    data['truth'] = pd.to_numeric(data['truth'], errors='coerce')

    if 'predicted' not in data.columns or 'truth' not in data.columns:
        raise ValueError(
            "CSV file must contain 'predicted' and 'truth' columns")

    predicted_values = data['predicted'].values
    truth_values = data['truth'].values
    indices = np.arange(1, len(predicted_values) + 1)

    bar_width = 0.35
    fig, ax = plt.subplots(figsize=(10, 6))

    bars_predicted = ax.bar(indices - bar_width/2, predicted_values,
                            bar_width, label='Predicted', color='blue')
    bars_truth = ax.bar(indices + bar_width/2, truth_values,
                        bar_width, label='Truth', color='green')

    for i in range(len(predicted_values)):
        pred = predicted_values[i]
        truth = truth_values[i]
        idx = indices[i]
        difference = truth - pred
        mid = (idx - bar_width/2 + idx + bar_width/2) / 2

        line_x = [idx - bar_width/2, idx + bar_width/2]
        line_y = [pred, pred]
        ax.plot(line_x, line_y, 'k-')

        bracket_x = [mid, mid, mid]
        bracket_y = [pred, pred + difference/2, truth]
        ax.plot(bracket_x, bracket_y, 'k-')

        ax.text(mid, pred + difference/2,
                f'{difference:.2f}', ha='center', va='bottom')

    ax.set_xlabel('Index')
    ax.set_ylabel('Price Value')
    ax.set_title('Predicted vs Truth Values')
    ax.set_xticks(indices)
    ax.legend()

    plt.tight_layout()
    plt.show()

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import tensorflow as tf
from tensorflow.keras.models import load_model

def save_text_to_png(text, filename, title, output_dir):
    """Renders text into a clean PNG image using Matplotlib."""
    plt.figure(figsize=(12, 8))
    plt.text(0.01, 0.95, title, fontsize=16, fontweight='bold', family='monospace', verticalalignment='top')
    plt.text(0.01, 0.9, text, fontsize=11, family='monospace', verticalalignment='top')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, filename), dpi=150, bbox_inches='tight')
    plt.close()

def visualize_architecture(model_path, model_name, output_dir):
    """Prints model summary and saves it as a PNG image."""
    print(f"\n{'='*60}")
    print(f"ARCHITECTURE SUMMARY: {model_name}")
    print(f"{'='*60}")
    
    if not os.path.exists(model_path):
        print(f"Model file {model_path} not found.")
        return

    try:
        model = load_model(model_path, compile=False)
        
        # Capture summary string
        import io
        stream = io.StringIO()
        model.summary(print_fn=lambda x: stream.write(x + '\n'))
        summary_text = stream.getvalue()
        print(summary_text)
        
        # Save summary as PNG
        summary_filename = f"summary_{model_name.lower().replace('-', '_')}.png"
        save_text_to_png(summary_text, summary_filename, f"Model Architecture: {model_name}", output_dir)
        print(f"Summary PNG saved to: {summary_filename}")
        
    except Exception as e:
        print(f"Error loading model {model_name}: {e}")

def plot_error_pie_chart(pred_df, output_dir):
    """Pie chart showing distribution of prediction error ranges."""
    print("Generating Error Distribution Pie Chart...")
    
    # Calculate absolute error in cycles
    error = np.abs(pred_df['y_true'] - pred_df['ensemble_pred'])
    
    # Categorize error ranges (relative to actual value)
    rel_error = error / pred_df['y_true'].replace(0, 1) # Avoid division by zero
    
    ranges = [
        (rel_error <= 0.05).sum(),
        ((rel_error > 0.05) & (rel_error <= 0.15)).sum(),
        ((rel_error > 0.15) & (rel_error <= 0.30)).sum(),
        (rel_error > 0.30).sum()
    ]
    labels = ['Excellent (<5%)', 'Good (5-15%)', 'Fair (15-30%)', 'Poor (>30%)']
    colors = ['#4CAF50', '#8BC34A', '#FFC107', '#F44336']
    
    plt.figure(figsize=(10, 8))
    plt.pie(ranges, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors, 
            explode=(0.1, 0, 0, 0), shadow=True, textprops={'fontsize': 12})
    plt.title("Ensemble Prediction Accuracy Distribution", fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "accuracy_pie_chart.png"), dpi=150)
    plt.close()

def plot_radar_comparison(metrics_df, output_dir):
    """Radar chart comparing models across RMSE, MAE, and R2."""
    print("Generating Model Comparison Radar Chart...")
    
    # Select models and metrics
    # We want metrics where 'higher is better' for radar chart naturally, so we invert RMSE/MAE for display
    # or just use them as is but label clearly.
    
    categories = ['RMSE', 'MAE', 'R2_Test']
    models = metrics_df['Model'].unique()
    
    # Normalize metrics for better visualization on the same scale
    # (Optional: we can just plot them if the scales are similar enough)
    
    label_loc = np.linspace(start=0, stop=2 * np.pi, num=len(categories), endpoint=False)
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    
    for model_name in models:
        model_data = metrics_df[metrics_df['Model'] == model_name].iloc[0]
        values = [model_data['RMSE'], model_data['MAE'], model_data.get('R2_Test', 0)]
        
        # Close the loop
        values = values + [values[0]]
        locs = list(label_loc) + [label_loc[0]]
        
        ax.plot(locs, values, label=model_name, linewidth=2)
        ax.fill(locs, values, alpha=0.1)

    ax.set_xticks(label_loc)
    ax.set_xticklabels(categories, fontsize=12)
    ax.set_title("Model Performance Multi-Metric Comparison", fontsize=16, fontweight='bold', pad=30)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "model_performance_radar.png"), dpi=150)
    plt.close()

def plot_error_histogram(pred_df, output_dir):
    """Histogram showing distribution of residuals (errors)."""
    print("Generating Error Density Histogram...")
    
    residuals = pred_df['ensemble_pred'] - pred_df['y_true']
    
    plt.figure(figsize=(12, 6))
    sns.histplot(residuals, kde=True, color='#673AB7', bins=30)
    plt.axvline(x=0, color='red', linestyle='--')
    plt.title("Distribution of Prediction Residuals (Errors)", fontsize=14, fontweight='bold')
    plt.xlabel("Prediction Error (Predicted - Actual Cycles)")
    plt.ylabel("Frequency")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "error_distribution.png"), dpi=150)
    plt.close()

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    data_dir = os.path.join(base_dir, "data")
    output_dir = os.path.join(base_dir, "plots")
    
    if not os.path.exists(output_dir): os.makedirs(output_dir)

    # 1. Model Architectures
    models_to_check = {
        "LSTM": "best_lstm_model.h5",
        "GRU": "best_gru_model.h5",
        "CNN-LSTM": "best_cnn_lstm_model.h5"
    }
    
    for name, filename in models_to_check.items():
        visualize_architecture(os.path.join(data_dir, filename), name, output_dir)

    # 2. Result Visualizations
    metrics_path = os.path.join(data_dir, "model_metrics.csv")
    ensemble_path = os.path.join(data_dir, "ensemble_metrics.csv")
    preds_path = os.path.join(data_dir, "predictions.csv")
    
    if os.path.exists(metrics_path) and os.path.exists(preds_path):
        metrics_df = pd.read_csv(metrics_path)
        if os.path.exists(ensemble_path):
            ens_metrics = pd.read_csv(ensemble_path)
            metrics_df = pd.concat([metrics_df, ens_metrics], ignore_index=True).drop_duplicates('Model')
            
        pred_df = pd.read_csv(preds_path)
        
        plot_error_pie_chart(pred_df, output_dir)
        plot_radar_comparison(metrics_df, output_dir)
        plot_error_histogram(pred_df, output_dir)
        
        print(f"\nAdvanced visualizations successfully saved to: {output_dir}")
    else:
        print("Required metric/prediction files not found in 'data/' directory.")

if __name__ == "__main__":
    main()

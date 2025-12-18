#!/usr/bin/env python3
"""
View Training Registry - Display all logged training runs
"""

import sys
from pathlib import Path

# Add the model directory to Python path to enable imports
sys.path.insert(0, str(Path(__file__).parent))

from validation.training_registry import get_registry

def main():
    """Main function to display training registry"""
    
    print("="*80)
    print("STRAWBERRY DETECTION - TRAINING REGISTRY")
    print("="*80)
    
    # Get registry
    registry = get_registry()
    runs = registry.get_all_runs()
    
    if not runs:
        print("\nNo training runs found in registry.")
        print("\nTo start logging training runs, use:")
        print("python train_with_logging.py --experiment-name 'my_run'")
        return
    
    print(f"\nTotal training runs: {len(runs)}\n")
    
    # Display summary table
    print("-"*120)
    print(f"{'Date':<12} {'Run ID':<12} {'Experiment':<20} {'Model':<10} {'Batch':<6} {'Size':<6} {'Epochs':<8} {'mAP@50':<8} {'Time':<10} {'GPU':<20}")
    print("-"*120)
    
    for run in runs:
        date = run['date'].split()[0] if run.get('date') else 'N/A'
        run_id = run['run_id'][:8] if run.get('run_id') else 'N/A'
        experiment = run.get('experiment_name', 'N/A')[:18]
        model_arch = run.get('model_architecture', 'N/A')
        model_size = run.get('model_size', '')
        model = f"{model_arch}-{model_size}" if model_size else model_arch
        model = model[:9]  # Truncate to fit column
        batch = run.get('batch_size', 'N/A')
        size = run.get('image_size', 'N/A')
        epochs_completed = run.get('epochs_completed', '?')
        epochs_planned = run.get('epochs_planned', '?')
        epochs = f"{epochs_completed}/{epochs_planned}"
        val_map50 = run.get('val_map50', run.get('mAP50', 0.0))
        map50 = f"{val_map50:.3f}" if isinstance(val_map50, (int, float)) else 'N/A'
        training_time = run.get('training_time_minutes', 0.0)
        time_str = f"{training_time:.1f}m" if isinstance(training_time, (int, float)) else 'N/A'
        gpu_name = run.get('gpu_name', 'N/A')
        gpu = gpu_name.split('(')[0].strip()[:18] if gpu_name != 'N/A' else 'N/A'

        print(f"{date:<12} {run_id:<12} {experiment:<20} {model:<10} {batch:<6} {size:<6} {epochs:<8} {map50:<8} {time_str:<10} {gpu:<20}")
    
    print("-"*120)
    
    # Show detailed info for latest run
    if runs:
        latest_run = runs[0]  # Most recent (sorted by date descending)
        print(f"\n{'='*80}")
        print(f"LATEST RUN DETAILS: {latest_run.get('run_id', 'N/A')}")
        print(f"{'='*80}")

        print(f"\n📅 Date: {latest_run.get('date', 'N/A')}")
        print(f"🎯 Experiment: {latest_run.get('experiment_name', 'N/A')}")
        print(f"📊 Status: {latest_run.get('status', 'N/A')}")
        print(f"🏆 Best Epoch: {latest_run.get('best_epoch', 'N/A')}")
        
        print(f"\n📦 Dataset:")
        dataset_name = latest_run.get('dataset_name', 'N/A')
        dataset_size = latest_run.get('dataset_size', 'N/A')
        num_classes = latest_run.get('num_classes', 'N/A')
        class_names = latest_run.get('class_names', [])
        class_names_str = ', '.join(class_names) if class_names else 'N/A'
        print(f"   - Name: {dataset_name}")
        print(f"   - Size: {dataset_size} images")
        print(f"   - Classes: {num_classes} ({class_names_str})")

        print(f"\n🤖 Model:")
        model_arch = latest_run.get('model_architecture', 'N/A')
        model_size = latest_run.get('model_size', 'N/A')
        pretrained = latest_run.get('pretrained', 'N/A')
        print(f"   - Architecture: {model_arch}")
        print(f"   - Size: {model_size}")
        print(f"   - Pretrained: {pretrained}")

        print(f"\n⚙️  Hyperparameters:")
        batch_size = latest_run.get('batch_size', 'N/A')
        image_size = latest_run.get('image_size', 'N/A')
        epochs_completed = latest_run.get('epochs_completed', '?')
        epochs_planned = latest_run.get('epochs_planned', '?')
        learning_rate = latest_run.get('learning_rate', 'N/A')
        optimizer = latest_run.get('optimizer', 'N/A')
        weight_decay = latest_run.get('weight_decay', 'N/A')
        print(f"   - Batch Size: {batch_size}")
        print(f"   - Image Size: {image_size}x{image_size}")
        print(f"   - Epochs: {epochs_completed}/{epochs_planned}")
        print(f"   - Learning Rate: {learning_rate}")
        print(f"   - Optimizer: {optimizer}")
        print(f"   - Weight Decay: {weight_decay}")

        print(f"\n📈 Performance:")
        val_precision = latest_run.get('val_precision', latest_run.get('precision', 0.0))
        val_recall = latest_run.get('val_recall', latest_run.get('recall', 0.0))
        val_map50 = latest_run.get('val_map50', latest_run.get('mAP50', 0.0))
        val_map50_95 = latest_run.get('val_map50_95', latest_run.get('mAP50_95', 0.0))

        print(f"   - Precision: {val_precision:.3f}" if isinstance(val_precision, (int, float)) else f"   - Precision: N/A")
        print(f"   - Recall: {val_recall:.3f}" if isinstance(val_recall, (int, float)) else f"   - Recall: N/A")
        print(f"   - mAP@50: {val_map50:.3f}" if isinstance(val_map50, (int, float)) else f"   - mAP@50: N/A")
        print(f"   - mAP@50-95: {val_map50_95:.3f}" if isinstance(val_map50_95, (int, float)) else f"   - mAP@50-95: N/A")

        print(f"\n⏱️  Training:")
        training_time = latest_run.get('training_time_minutes', 'N/A')
        early_stopped = latest_run.get('early_stopped', 'N/A')
        print(f"   - Duration: {training_time} minutes" if isinstance(training_time, (int, float)) else f"   - Duration: {training_time}")
        print(f"   - Early Stopped: {early_stopped}")

        print(f"\n💻 System:")
        gpu_name = latest_run.get('gpu_name', 'N/A')
        gpu_memory = latest_run.get('gpu_memory_peak_gb', 'N/A')
        cpu_count = latest_run.get('cpu_count', 'N/A')
        ram_total = latest_run.get('ram_total_gb', 'N/A')
        python_version = latest_run.get('python_version', 'N/A')
        pytorch_version = latest_run.get('pytorch_version', 'N/A')
        cuda_version = latest_run.get('cuda_version', 'N/A')
        os_info = latest_run.get('os_info', 'N/A')
        print(f"   - GPU: {gpu_name}")
        print(f"   - Peak GPU Memory: {gpu_memory} GB" if isinstance(gpu_memory, (int, float)) else f"   - Peak GPU Memory: {gpu_memory}")
        print(f"   - CPU Cores: {cpu_count}")
        print(f"   - RAM: {ram_total} GB" if isinstance(ram_total, (int, float)) else f"   - RAM: {ram_total}")
        print(f"   - Python: {python_version}")
        print(f"   - PyTorch: {pytorch_version}")
        print(f"   - CUDA: {cuda_version}")
        print(f"   - OS: {os_info}")

        print(f"\n📁 Paths:")
        model_path = latest_run.get('model_path', 'N/A')
        results_path = latest_run.get('results_path', 'N/A')
        config_path = latest_run.get('config_path', 'N/A')
        print(f"   - Model: {model_path}")
        print(f"   - Results: {results_path}")
        print(f"   - Config: {config_path}")
    
    print(f"\n{'='*80}")
    print("REGISTRY FILES:")
    print(f"{'='*80}")
    print(f"JSON Registry: {registry.registry_path}")
    print(f"CSV History: model/training_history.csv")
    print(f"Markdown Summary: model/training_summary.md")
    print(f"\nTo export registry: python -c \"from training_registry import get_registry; get_registry().export_to_csv()\"")
    print(f"To generate summary: python -c \"from training_registry import get_registry; get_registry().generate_summary_table()\"")

if __name__ == '__main__':
    main()
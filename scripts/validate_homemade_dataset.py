#!/usr/bin/env python3
"""
Comprehensive validation of the mixed model on your homemade dataset
Tests performance, bias, and real-world applicability
"""

import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO
import json
import argparse
from datetime import datetime

class HomemadeDatasetValidator:
    def __init__(self, model_path, homemade_dataset_path, output_dir):
        self.model = YOLO(model_path)
        self.dataset_path = Path(homemade_dataset_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        print("🔍 Homemade Dataset Validation")
        print("=" * 60)
        print(f"Model: {Path(model_path).name}")
        print(f"Dataset: {self.dataset_path}")
        print("=" * 60)
    
    def analyze_dataset_characteristics(self):
        """Analyze characteristics of homemade dataset vs Kaggle dataset"""
        print("\n📊 DATASET CHARACTERISTICS ANALYSIS")
        print("-" * 50)
        
        # Count images in different splits
        splits = ['train', 'val', 'test']
        stats = {}
        
        for split in splits:
            split_path = self.dataset_path / split
            if split_path.exists():
                images = list(split_path.glob("*.jpg")) + list(split_path.glob("*.png"))
                labels = list((split_path / "labels").glob("*.txt")) if (split_path / "labels").exists() else []
                
                stats[split] = {
                    'images': len(images),
                    'labels': len(labels),
                    'label_coverage': len(labels)/len(images)*100 if images else 0
                }
                
                print(f"\n{split.title()} Split:")
                print(f"  📸 Images: {len(images)}")
                print(f"  🏷️  Labels: {len(labels)}")
                print(f"  📈 Label Coverage: {len(labels)/len(images)*100:.1f}%" if images else "  📈 Label Coverage: 0%")
        
        return stats
    
    def test_detection_performance(self, confidence_threshold=0.7):
        """Test detection performance on homemade dataset"""
        print(f"\n🎯 DETECTION PERFORMANCE TEST (conf={confidence_threshold})")
        print("-" * 50)
        
        results = {
            'total_images': 0,
            'images_with_detections': 0,
            'total_detections': 0,
            'avg_confidence': 0,
            'detection_rate': 0,
            'confidence_distribution': {'high': 0, 'medium': 0, 'low': 0},
            'per_image_stats': []
        }
        
        confidences = []
        
        # Test on all available splits
        for split in ['train', 'val', 'test']:
            split_path = self.dataset_path / split / 'images'
            if not split_path.exists():
                continue
                
            print(f"\n📂 Testing {split} split...")
            
            image_files = list(split_path.glob("*.jpg")) + list(split_path.glob("*.png"))
            
            for i, img_path in enumerate(image_files, 1):
                print(f"  Testing {i}/{len(image_files)}: {img_path.name}")
                
                # Run detection
                detection_results = self.model(img_path, conf=confidence_threshold, verbose=False)
                
                detections = []
                if detection_results[0].boxes is not None:
                    boxes = detection_results[0].boxes.xyxy.cpu().numpy()
                    confs = detection_results[0].boxes.conf.cpu().numpy()
                    
                    for box, conf in zip(boxes, confs):
                        if conf >= confidence_threshold:
                            detections.append({
                                'bbox': box.tolist(),
                                'confidence': float(conf)
                            })
                            confidences.append(float(conf))
                
                num_detections = len(detections)
                
                # Update statistics
                results['total_images'] += 1
                if num_detections > 0:
                    results['images_with_detections'] += 1
                    results['total_detections'] += num_detections
                
                # Categorize confidence
                for detection in detections:
                    conf = detection['confidence']
                    if conf >= 0.8:
                        results['confidence_distribution']['high'] += 1
                    elif conf >= 0.5:
                        results['confidence_distribution']['medium'] += 1
                    else:
                        results['confidence_distribution']['low'] += 1
                
                # Save visualization
                result_img = detection_results[0].plot()
                output_file = self.output_dir / f"validation_{split}_{img_path.name}"
                cv2.imwrite(str(output_file), result_img)
                
                # Per-image statistics
                results['per_image_stats'].append({
                    'filename': img_path.name,
                    'split': split,
                    'detections': num_detections,
                    'avg_confidence': np.mean([d['confidence'] for d in detections]) if detections else 0,
                    'has_detection': num_detections > 0
                })
                
                print(f"    {'✓' if num_detections > 0 else '✗'} {num_detections} detections")
        
        # Calculate final statistics
        if confidences:
            results['avg_confidence'] = np.mean(confidences)
        if results['total_images'] > 0:
            results['detection_rate'] = results['images_with_detections'] / results['total_images'] * 100
        
        return results
    
    def test_specific_bias_scenarios(self):
        """Test for specific bias scenarios"""
        print(f"\n🧪 BIAS SCENARIO TESTING")
        print("-" * 50)
        
        bias_tests = {
            'close_up': {'pattern': ['20_51', '19_39'], 'description': 'Close-up shots'},
            'medium_distance': {'pattern': ['19_59', '19_45'], 'description': 'Medium distance shots'},
            'single_berry': {'pattern': ['19_39', '19_41'], 'description': 'Single berry focus'},
            'multiple_berries': {'pattern': ['20_51'], 'description': 'Multiple berries'},
            'different_times': {'pattern': ['19_', '20_'], 'description': 'Different times of day'}
        }
        
        bias_results = {}
        
        for bias_type, test_config in bias_tests.items():
            print(f"\n📸 Testing {test_config['description']}...")
            
            matching_images = []
            for split in ['train', 'val', 'test']:
                split_path = self.dataset_path / split / 'images'
                if split_path.exists():
                    for pattern in test_config['pattern']:
                        matching_images.extend(list(split_path.glob(f"*{pattern}*.jpg")))
                        matching_images.extend(list(split_path.glob(f"*{pattern}*.png")))
            
            if not matching_images:
                print(f"  ℹ️  No images found for {bias_type}")
                continue
            
            print(f"  Found {len(matching_images)} matching images")
            
            # Test these specific images
            detections = 0
            total_confidence = 0
            images_with_detections = 0
            
            for img_path in matching_images:
                results = self.model(img_path, conf=0.5, verbose=False)
                
                if results[0].boxes is not None:
                    boxes = results[0].boxes.xyxy.cpu().numpy()
                    confs = results[0].boxes.conf.cpu().numpy()
                    
                    for box, conf in zip(boxes, confs):
                        if conf >= 0.5:
                            detections += 1
                            total_confidence += float(conf)
                            images_with_detections += 1
            
            bias_results[bias_type] = {
                'total_images': len(matching_images),
                'images_with_detections': images_with_detections,
                'total_detections': detections,
                'detection_rate': images_with_detections / len(matching_images) * 100 if matching_images else 0,
                'avg_confidence': total_confidence / detections if detections > 0 else 0
            }
            
            print(f"  🎯 Detection rate: {bias_results[bias_type]['detection_rate']:.1f}%")
            print(f"  💯 Average confidence: {bias_results[bias_type]['avg_confidence']*100:.1f}%")
        
        return bias_results
    
    def generate_validation_report(self, dataset_stats, detection_results, bias_results):
        """Generate comprehensive validation report"""
        print(f"\n📋 GENERATING VALIDATION REPORT")
        print("-" * 50)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'model_info': {
                'model_path': str(self.model.model_path),
                'dataset_path': str(self.dataset_path)
            },
            'dataset_characteristics': dataset_stats,
            'detection_performance': detection_results,
            'bias_analysis': bias_results,
            'recommendations': []
        }
        
        # Analysis and recommendations
        print("\n📊 ANALYSIS AND RECOMMENDATIONS")
        print("-" * 50)
        
        # Overall performance assessment
        if detection_results['detection_rate'] >= 80:
            print("✅ EXCELLENT: Detection rate ≥ 80%")
            report['recommendations'].append("Detection performance is excellent - ready for deployment")
        elif detection_results['detection_rate'] >= 70:
            print("✅ GOOD: Detection rate ≥ 70%")
            report['recommendations'].append("Detection performance is good - consider deployment")
        else:
            print("⚠️  NEEDS IMPROVEMENT: Detection rate < 70%")
            report['recommendations'].append("Detection performance needs improvement - consider more training data")
        
        # Confidence analysis
        if detection_results['avg_confidence'] >= 0.8:
            print("✅ HIGH CONFIDENCE: Average confidence ≥ 80%")
            report['recommendations'].append("High confidence detections - model is very certain")
        elif detection_results['avg_confidence'] >= 0.6:
            print("✅ GOOD CONFIDENCE: Average confidence ≥ 60%")
            report['recommendations'].append("Good confidence detections - model is reasonably certain")
        else:
            print("⚠️  LOW CONFIDENCE: Average confidence < 60%")
            report['recommendations'].append("Low confidence detections - consider adjusting confidence threshold")
        
        # Bias analysis
        bias_rates = [stats['detection_rate'] for stats in bias_results.values() if stats['total_images'] > 0]
        if bias_rates:
            max_variance = max(bias_rates) - min(bias_rates)
            if max_variance < 20:
                print("✅ LOW BIAS: Similar performance across conditions")
                report['recommendations'].append("Low bias detected - model generalizes well")
            elif max_variance < 40:
                print("⚠️  MODERATE BIAS: Some variation across conditions")
                report['recommendations'].append("Moderate bias detected - monitor performance in deployment")
            else:
                print("❌ HIGH BIAS: Significant variation across conditions")
                report['recommendations'].append("High bias detected - consider retraining with more diverse data")
        
        # Deployment readiness
        if detection_results['detection_rate'] >= 75 and detection_results['avg_confidence'] >= 0.7:
            print("🚀 DEPLOYMENT READY: Performance meets production standards")
            report['deployment_ready'] = True
            report['recommendations'].append("Model is ready for greenhouse deployment")
        else:
            print("🔧 NEEDS WORK: Performance below production standards")
            report['deployment_ready'] = False
            report['recommendations'].append("Model needs improvement before deployment")
        
        return report

def main():
    parser = argparse.ArgumentParser(description='Validate model on homemade dataset')
    parser.add_argument('--model', type=str, 
                       default='model/detection/mixed_conservative_v24/weights/best.pt',
                       help='Path to trained model')
    parser.add_argument('--data', type=str, 
                       default='model/dataset_homemade_labeled',
                       help='Path to homemade dataset')
    parser.add_argument('--output', type=str, 
                       default='homemade_validation_results',
                       help='Output directory for results')
    parser.add_argument('--conf', type=float, 
                       default=0.7,
                       help='Confidence threshold for detection')
    
    args = parser.parse_args()
    
    validator = HomemadeDatasetValidator(
        model_path=args.model,
        homemade_dataset_path=args.data,
        output_dir=args.output
    )
    
    print("🍓 HOMEMADE DATASET VALIDATION")
    print("=" * 60)
    print("Validating mixed model performance on your specific dataset")
    print("This ensures the model works well in YOUR greenhouse environment")
    print("=" * 60)
    
    # Run comprehensive validation
    dataset_stats = validator.analyze_dataset_characteristics()
    detection_results = validator.test_detection_performance(confidence_threshold=args.conf)
    bias_results = validator.test_specific_bias_scenarios()
    final_report = validator.generate_validation_report(dataset_stats, detection_results, bias_results)
    
    # Save final report
    report_file = Path(args.output) / 'homemade_validation_report.json'
    with open(report_file, 'w') as f:
        json.dump(final_report, f, indent=2)
    
    print(f"\n🎯 VALIDATION COMPLETE!")
    print("=" * 60)
    print(f"📊 Full report saved to: {report_file}")
    print(f"📸 Visualizations saved to: {args.output}/")
    
    if final_report.get('deployment_ready', False):
        print("🚀 MODEL IS READY FOR GREENHOUSE DEPLOYMENT!")
    else:
        print("🔧 MODEL NEEDS IMPROVEMENT BEFORE DEPLOYMENT")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
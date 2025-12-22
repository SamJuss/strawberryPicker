#!/usr/bin/env python3
"""
Analyze bounding box quality for individual strawberry detections
Checks position accuracy, size appropriateness, and coverage completeness
"""

import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO
import json
import argparse

class BoundingBoxQualityAnalyzer:
    def __init__(self, model_path, test_images_dir, output_dir):
        self.model = YOLO(model_path)
        self.test_path = Path(test_images_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        print("🔍 Bounding Box Quality Analysis")
        print("=" * 60)
        print(f"Model: {Path(model_path).name}")
        print(f"Test images: {self.test_path}")
        print("=" * 60)
    
    def analyze_bounding_box_quality(self, image_path, detection_results):
        """Analyze quality of individual bounding boxes"""
        
        img = cv2.imread(str(image_path))
        if img is None:
            return None
            
        h, w = img.shape[:2]
        
        quality_metrics = {
            'filename': image_path.name,
            'total_detections': 0,
            'individual_berries': [],
            'overall_assessment': {},
            'issues_found': []
        }
        
        if detection_results[0].boxes is not None:
            boxes = detection_results[0].boxes.xyxy.cpu().numpy()
            confidences = detection_results[0].boxes.conf.cpu().numpy()
            
            quality_metrics['total_detections'] = len(boxes)
            
            for i, (box, conf) in enumerate(zip(boxes, confidences)):
                berry_analysis = self.analyze_individual_berry(box, conf, w, h, i)
                quality_metrics['individual_berries'].append(berry_analysis)
        
        return quality_metrics
    
    def analyze_individual_berry(self, box, confidence, img_width, img_height, berry_id):
        """Analyze quality of individual berry bounding box"""
        
        x1, y1, x2, y2 = box
        
        # Convert to pixel coordinates
        x1_px = int(x1)
        y1_px = int(y1)
        x2_px = int(x2)
        y2_px = int(y2)
        
        # Calculate metrics
        box_width = x2_px - x1_px
        box_height = y2_px - y1_px
        box_area = box_width * box_height
        
        # Aspect ratio
        aspect_ratio = box_width / box_height if box_height > 0 else 0
        
        # Relative size (percentage of image)
        rel_width = box_width / img_width
        rel_height = box_height / img_height
        rel_area = box_area / (img_width * img_height)
        
        # Position analysis
        center_x = (x1_px + x2_px) / 2
        center_y = (y1_px + y2_px) / 2
        
        # Quality assessment
        quality_score = self.assess_bounding_box_quality(
            box_width, box_height, aspect_ratio, rel_area, confidence
        )
        
        return {
            'berry_id': berry_id,
            'bbox': [x1_px, y1_px, x2_px, y2_px],
            'confidence': float(confidence),
            'dimensions': {
                'width_px': box_width,
                'height_px': box_height,
                'area_px': box_area,
                'aspect_ratio': aspect_ratio
            },
            'relative_size': {
                'width_pct': rel_width * 100,
                'height_pct': rel_height * 100,
                'area_pct': rel_area * 100
            },
            'position': {
                'center_x': center_x,
                'center_y': center_y,
                'center_x_pct': center_x / img_width,
                'center_y_pct': center_y / img_height
            },
            'quality_score': quality_score,
            'quality_assessment': self.interpret_quality_score(quality_score)
        }
    
    def assess_bounding_box_quality(self, width, height, aspect_ratio, rel_area, confidence):
        """Calculate quality score for bounding box"""
        
        quality_score = 0
        
        # Confidence weight (40% of score)
        quality_score += confidence * 0.4
        
        # Size appropriateness (30% of score)
        # Typical strawberry aspect ratio: 0.8-1.2 (roughly circular/oval)
        if 0.6 <= aspect_ratio <= 1.4:
            quality_score += 0.15
        
        # Relative size appropriateness (20% of score)
        # Strawberry should be reasonable percentage of image (1-20%)
        if 1 <= rel_area * 100 <= 20:
            quality_score += 0.15
        elif 0.5 <= rel_area * 100 <= 30:
            quality_score += 0.10
        
        # Box size consistency (10% of score)
        # Box shouldn't be too small or too large relative to typical strawberry
        if width >= 20 and height >= 20:  # Minimum reasonable size
            quality_score += 0.05
        if width <= 800 and height <= 600:  # Not too large (assuming 640x480)
            quality_score += 0.05
        
        return quality_score
    
    def interpret_quality_score(self, score):
        """Interpret quality score into human-readable assessment"""
        
        if score >= 0.8:
            return "Excellent - Tight, well-positioned box"
        elif score >= 0.6:
            return "Good - Reasonably positioned box"
        elif score >= 0.4:
            return "Fair - Acceptable but could be improved"
        else:
            return "Poor - Likely mispositioned or incorrectly sized"
    
    def detect_common_bounding_box_issues(self, quality_metrics):
        """Detect common bounding box quality issues"""
        
        issues = []
        
        for berry in quality_metrics['individual_berries']:
            score = berry['quality_score']
            conf = berry['confidence']
            rel_area = berry['relative_size']['area_pct']
            aspect_ratio = berry['dimensions']['aspect_ratio']
            
            # Issue detection
            if score < 0.4:
                issues.append({
                    'type': 'poor_quality_box',
                    'berry_id': berry['berry_id'],
                    'description': f"Berry {berry['berry_id']}: Low quality score ({score:.2f})"
                })
            
            if conf < 0.7:
                issues.append({
                    'type': 'low_confidence',
                    'berry_id': berry['berry_id'],
                    'description': f"Berry {berry['berry_id']}: Low confidence ({conf:.2f})"
                })
            
            if rel_area > 30:
                issues.append({
                    'type': 'box_too_large',
                    'berry_id': berry['berry_id'],
                    'description': f"Berry {berry['berry_id']}: Box too large ({rel_area:.1f}% of image)"
                })
            
            if rel_area < 0.5:
                issues.append({
                    'type': 'box_too_small',
                    'berry_id': berry['berry_id'],
                    'description': f"Berry {berry['berry_id']}: Box too small ({rel_area:.1f}% of image)"
                })
            
            if aspect_ratio < 0.4 or aspect_ratio > 2.5:
                issues.append({
                    'type': 'extreme_aspect_ratio',
                    'berry_id': berry['berry_id'],
                    'description': f"Berry {berry['berry_id']}: Extreme aspect ratio ({aspect_ratio:.2f})"
                })
        
        return issues
    
    def generate_bounding_box_quality_report(self, test_images_dir):
        """Generate comprehensive bounding box quality report"""
        
        print("📊 GENERATING BOUNDING BOX QUALITY REPORT")
        print("=" * 60)
        
        test_path = Path(test_images_dir)
        image_files = list(test_path.glob("*.jpg")) + list(test_path.glob("*.png"))
        
        if not image_files:
            print("❌ No test images found")
            return None
        
        # Sample 20 images for detailed analysis
        sample_size = min(20, len(image_files))
        sample_images = image_files[:sample_size]
        
        print(f"Analyzing {sample_size} sample images...")
        
        all_results = []
        total_berries = 0
        quality_scores = []
        
        for i, img_path in enumerate(sample_images, 1):
            print(f"\n📸 Analyzing {i}/{sample_size}: {img_path.name}")
            
            # Run detection
            results = self.model(img_path, conf=0.5, verbose=False)
            
            # Analyze bounding box quality
            quality_metrics = self.analyze_bounding_box_quality(img_path, results)
            
            if quality_metrics:
                all_results.append(quality_metrics)
                total_berries += quality_metrics['total_detections']
                
                for berry in quality_metrics['individual_berries']:
                    quality_scores.append(berry['quality_score'])
                
                # Save visualization
                self.save_quality_visualization(img_path, results, quality_metrics)
                
                print(f"  📈 {quality_metrics['total_detections']} berries detected")
                if quality_metrics['individual_berries']:
                    avg_quality = np.mean([b['quality_score'] for b in quality_metrics['individual_berries']])
                    print(f"  💯 Average quality score: {avg_quality:.2f}")
        
        # Generate final report
        final_report = self.generate_final_report(all_results, total_berries, quality_scores)
        
        return final_report
    
    def save_quality_visualization(self, image_path, detection_results, quality_metrics):
        """Save visualization with bounding box quality indicators"""
        
        img = detection_results[0].plot()  # Base detection visualization
        
        # Add quality indicators
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        for i, berry in enumerate(quality_metrics['individual_berries']):
            x1, y1, x2, y2 = berry['bbox']
            quality = berry['quality_assessment']
            score = berry['quality_score']
            conf = berry['confidence']
            
            # Add quality indicator text
            text_y = y1 - 5 if y1 > 20 else y2 + 20
            cv2.putText(img, f"Q:{score:.2f}", (x1, text_y), font, 0.5, (0, 255, 0), 1)
            
            # Color code based on quality
            color = (0, 255, 0) if score >= 0.6 else (0, 255, 255) if score >= 0.4 else (0, 0, 255)
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        
        # Add overall quality info
        if quality_metrics['individual_berries']:
            avg_quality = np.mean([b['quality_score'] for b in quality_metrics['individual_berries']])
            cv2.putText(img, f"Avg Quality: {avg_quality:.2f}", (10, 30), font, 0.7, (255, 255, 255), 2)
        
        output_file = self.output_dir / f"bbox_quality_{image_path.name}"
        cv2.imwrite(str(output_file), img)
    
    def generate_final_report(self, all_results, total_berries, quality_scores):
        """Generate comprehensive final report"""
        
        print(f"\n📋 GENERATING FINAL BOUNDING BOX QUALITY REPORT")
        print("=" * 60)
        
        if not all_results:
            print("❌ No results to analyze")
            return None
        
        # Calculate statistics
        total_images = len(all_results)
        images_with_detections = sum(1 for r in all_results if r['total_detections'] > 0)
        avg_quality = np.mean(quality_scores) if quality_scores else 0
        
        # Issue analysis
        all_issues = []
        for result in all_results:
            issues = self.detect_common_bounding_box_issues(result)
            all_issues.extend(issues)
        
        # Quality distribution
        quality_distribution = {
            'excellent': sum(1 for score in quality_scores if score >= 0.8),
            'good': sum(1 for score in quality_scores if 0.6 <= score < 0.8),
            'fair': sum(1 for score in quality_scores if 0.4 <= score < 0.6),
            'poor': sum(1 for score in quality_scores if score < 0.4)
        }
        
        report = {
            'total_images_analyzed': total_images,
            'images_with_detections': images_with_detections,
            'total_individual_berries': total_berries,
            'average_quality_score': avg_quality,
            'quality_distribution': quality_distribution,
            'common_issues': all_issues,
            'overall_assessment': self.generate_overall_assessment(avg_quality, all_issues),
            'recommendations': self.generate_recommendations(avg_quality, all_issues)
        }
        
        return report
    
    def generate_overall_assessment(self, avg_quality, issues):
        """Generate overall bounding box quality assessment"""
        
        if avg_quality >= 0.7 and len(issues) < total_berries * 0.1:
            return "EXCELLENT - Bounding boxes are well-positioned and sized"
        elif avg_quality >= 0.5 and len(issues) < total_berries * 0.3:
            return "GOOD - Bounding boxes are reasonably accurate"
        elif avg_quality >= 0.3:
            return "FAIR - Some bounding box issues detected"
        else:
            return "POOR - Significant bounding box quality issues"
    
    def generate_recommendations(self, avg_quality, issues):
        """Generate recommendations based on quality analysis"""
        
        recommendations = []
        
        if avg_quality >= 0.7:
            recommendations.append("Bounding box quality is excellent - no action needed")
        elif avg_quality >= 0.5:
            recommendations.append("Bounding box quality is good - monitor performance")
        else:
            recommendations.append("Consider improving bounding box quality")
        
        # Issue-specific recommendations
        issue_types = [issue['type'] for issue in issues]
        
        if 'box_too_large' in issue_types:
            recommendations.append("Some boxes are too large - consider tighter bounding")
        
        if 'box_too_small' in issue_types:
            recommendations.append("Some boxes are too small - ensure complete coverage")
        
        if 'extreme_aspect_ratio' in issue_types:
            recommendations.append("Some boxes have extreme aspect ratios - check positioning")
        
        return recommendations

def main():
    parser = argparse.ArgumentParser(description='Analyze bounding box quality')
    parser.add_argument('--model', type=str, 
                       default='model/detection/mixed_conservative_v24/weights/best.pt',
                       help='Path to trained model')
    parser.add_argument('--data', type=str, 
                       default='model/dataset_homemade_labeled/test/images',
                       help='Path to test images')
    parser.add_argument('--output', type=str, 
                       default='bounding_box_quality_analysis',
                       help='Output directory for results')
    
    args = parser.parse_args()
    
    analyzer = BoundingBoxQualityAnalyzer(
        model_path=args.model,
        test_images_dir=args.data,
        output_dir=args.output
    )
    
    print("🔍 BOUNDING BOX QUALITY ANALYSIS")
    print("=" * 60)
    print("Analyzing individual strawberry bounding box quality")
    print("This checks position accuracy, size appropriateness, and coverage")
    print("=" * 60)
    
    # Run comprehensive analysis
    final_report = analyzer.generate_bounding_box_quality_report(args.data)
    
    if final_report:
        print(f"\n🎯 ANALYSIS COMPLETE!")
        print("=" * 60)
        print(f"📊 Full report saved to: {args.output}/")
        
        # Print key findings
        print(f"\n📈 KEY FINDINGS:")
        print(f"  📸 Images analyzed: {final_report['total_images_analyzed']}")
        print(f"  🍓 Individual berries detected: {final_report['total_individual_berries']}")
        print(f"  💯 Average quality score: {final_report['average_quality_score']:.2f}")
        print(f"  🎯 Overall assessment: {final_report['overall_assessment']}")
        
        if final_report['common_issues']:
            print(f"\n⚠️  ISSUES DETECTED: {len(final_report['common_issues'])}")
            for issue in final_report['common_issues'][:5]:  # Show first 5
                print(f"  - {issue['description']}")
        
        print(f"\n📋 RECOMMENDATIONS:")
        for rec in final_report['recommendations']:
            print(f"  - {rec}")
    
    print(f"\n🎯 ANALYSIS COMPLETE!")
    print("=" * 60)

if __name__ == '__main__':
    main()
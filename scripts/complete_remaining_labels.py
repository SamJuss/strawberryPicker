#!/usr/bin/env python3
"""
Help complete remaining labels efficiently
Shows which images still need labeling and provides guidance
"""

import os
from pathlib import Path
import subprocess

def show_remaining_images():
    """Show which images still need labeling"""
    
    print("🎯 COMPLETING REMAINING LABELS")
    print("=" * 60)
    
    dataset_path = Path("model/datasets/manual_labeled")
    total_remaining = 0
    
    for split in ['train', 'val', 'test']:
        images_path = dataset_path / split / 'images'
        labels_path = dataset_path / split / 'labels'
        
        if images_path.exists():
            images = list(images_path.glob('*.jpg')) + list(images_path.glob('*.png'))
            labels = list(labels_path.glob('*.txt')) if labels_path.exists() else []
            
            labeled_files = {f.stem for f in labels}
            unlabeled = [img for img in images if img.stem not in labeled_files]
            
            if unlabeled:
                print(f"\n{split.upper()} Split - {len(unlabeled)} images remaining:")
                print("-" * 40)
                
                # Show first few unlabeled images
                for i, img in enumerate(unlabeled[:10]):
                    print(f"  {i+1}. {img.name}")
                
                if len(unlabeled) > 10:
                    print(f"  ... and {len(unlabeled) - 10} more")
                
                total_remaining += len(unlabeled)
    
    print(f"\n📊 TOTAL REMAINING: {total_remaining} images")
    print("=" * 60)
    
    return total_remaining

def create_completion_guide():
    """Create a guide for completing remaining labels"""
    
    print("\n🚀 HOW TO COMPLETE REMAINING LABELS:")
    print("=" * 60)
    
    print("1. 🌐 Start the annotation tool:")
    print("   python3 scripts/label_images_web.py model/datasets/manual_labeled/train/images")
    print()
    
    print("2. 🎯 Focus on remaining images:")
    print("   - Start with TRAIN split (28 images remaining)")
    print("   - Then complete TEST split (6 images remaining)")
    print("   - VAL split is already 100% complete!")
    print()
    
    print("3. ⏰ Time estimation:")
    print("   - 28 training images: ~3-4 hours")
    print("   - 6 test images: ~45 minutes")
    print("   - Total: ~4-5 hours")
    print()
    
    print("4. 💡 Quality tips:")
    print("   - Maintain same quality as your completed labels")
    print("   - Take regular breaks to stay focused")
    print("   - Review your first few completed labels for consistency")
    print("   - Don't rush - quality over speed!")

def suggest_batch_approach():
    """Suggest a batch approach for completing labels"""
    
    print("\n📦 SUGGESTED BATCH APPROACH:")
    print("=" * 60)
    
    print("Option A: Complete in 2 sessions")
    print("  Session 1: 14 training images (~2 hours)")
    print("  Session 2: 14 training + 6 test images (~2.5 hours)")
    print()
    
    print("Option B: Complete in 3 sessions")
    print("  Session 1: 10 training images (~1.5 hours)")
    print("  Session 2: 10 training images (~1.5 hours)")
    print("  Session 3: 8 training + 6 test images (~1.5 hours)")
    print()
    
    print("Option C: Complete all at once")
    print("  Single session: 34 images (~4-5 hours)")
    print("  Take breaks every 10-15 images")

def show_quality_check():
    """Show how to check quality of completed labels"""
    
    print("\n🔍 QUALITY CHECK TOOLS:")
    print("=" * 60)
    
    print("After completing labels, run these commands:")
    print()
    print("1. Check labeling statistics:")
    print("   python3 scripts/get_labeling_stats.py --data model/datasets/manual_labeled")
    print()
    print("2. Visualize your labels:")
    print("   python3 scripts/visualize_manual_labels.py --data model/datasets/manual_labeled --output quality_check")
    print()
    print("3. Check for quality issues:")
    print("   python3 scripts/check_label_quality.py --data model/datasets/manual_labeled")

def main():
    """Main function to help complete remaining labels"""
    
    print("🎯 MANUAL ANNOTATION COMPLETION HELPER")
    print("=" * 60)
    print("You're doing great! Let's finish the remaining labels.")
    print("=" * 60)
    
    # Show remaining images
    remaining = show_remaining_images()
    
    if remaining == 0:
        print("\n🎉 ALL LABELS COMPLETE!")
        print("✅ You can proceed to training the new model.")
        return
    
    # Show completion guide
    create_completion_guide()
    
    # Suggest batch approach
    suggest_batch_approach()
    
    # Show quality check
    show_quality_check()
    
    print("\n" + "=" * 60)
    print("🎯 NEXT STEPS:")
    print("1. Start the annotation tool with the command above")
    print("2. Complete the remaining images with high quality")
    print("3. Run quality check tools when done")
    print("4. Train new model on your perfect manual labels")
    print("=" * 60)
    
    print(f"\n🚀 Ready to complete the final {remaining} images!")
    print("📝 Take your time - quality is more important than speed!")

if __name__ == '__main__':
    main()
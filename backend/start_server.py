#!/usr/bin/env python3
"""
Startup script for the Object Detection Analysis Tool backend
"""

import os
import sys
from pathlib import Path

def check_data_files():
    """Check if required data files exist"""
    data_dir = Path("data")
    required_files = [
        "embeddings_2d.npy",
        "annotations.json", 
        "mapping.json"
    ]
    
    missing_files = []
    for file in required_files:
        if not (data_dir / file).exists():
            missing_files.append(file)
            
    if missing_files:
        print("❌ Missing required data files:")
        for file in missing_files:
            print(f"   - data/{file}")
        print("\nPlease ensure these files exist before starting the server.")
        return False
        
    print("✅ All required data files found")
    return True

def check_images_directory():
    """Check if images directory exists"""
    images_dir = Path("data/images")
    if not images_dir.exists():
        print(f"⚠️  Images directory not found: {images_dir}")
        print("   Image cropping may not work properly.")
        return False
    else:
        image_count = len(list(images_dir.glob("*")))
        print(f"✅ Images directory found with {image_count} files")
        return True

def main():
    print("🚀 Starting Object Detection Analysis Tool Backend")
    print("=" * 50)
    
    # Check data files
    if not check_data_files():
        sys.exit(1)
        
    # Check images directory
    check_images_directory()
    
    print("\n📊 Loading data...")
    
    # Import and load data
    try:
        from services.data_loader import data_loader
        data_loader.load_all()
        print("✅ Data loaded successfully")
        
        # Print summary
        print(f"   - Embeddings: {data_loader.embeddings.shape}")
        print(f"   - Annotations: {len(data_loader.annotations['annotations'])}")
        print(f"   - Mapping: {len(data_loader.mapping)}")
        print(f"   - Classes: {len(data_loader.class_names)}")
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        sys.exit(1)
    
    print("\n🌐 Starting FastAPI server...")
    print("   Frontend URL: http://localhost:3000")
    print("   Backend URL:  http://localhost:8000")
    print("   API Docs:     http://localhost:8000/docs")
    print("\n" + "=" * 50)
    
    # Start the server
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
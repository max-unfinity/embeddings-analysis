from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
import io
from services.image_service import image_service

router = APIRouter()

@router.get("/crop/{annotation_id}")
async def get_cropped_image(annotation_id: int):
    """Get cropped image for a specific annotation"""
    try:
        # Get cropped image bytes
        image_bytes = image_service.crop_detection(annotation_id)
        
        if image_bytes is None:
            # Return placeholder if cropping fails
            image_bytes = image_service.create_placeholder_image()
            
        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(image_bytes),
            media_type="image/jpeg",
            headers={"Cache-Control": "max-age=3600"}  # Cache for 1 hour
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting cropped image: {str(e)}")

@router.get("/crop/{annotation_id}/info")
async def get_crop_info(annotation_id: int):
    """Get information about the crop for debugging"""
    try:
        from services.data_loader import data_loader
        
        annotation = data_loader.get_annotation_by_id(annotation_id)
        if not annotation:
            raise HTTPException(status_code=404, detail="Annotation not found")
            
        image_id = annotation.get('image_id')
        bbox = annotation.get('bbox')
        
        # Get image path info
        image_path = image_service.get_image_path(image_id)
        
        return {
            'annotation_id': annotation_id,
            'image_id': image_id,
            'bbox': bbox,
            'image_path': str(image_path) if image_path else None,
            'image_exists': image_path.exists() if image_path else False,
            'category_id': annotation.get('category_id')
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting crop info: {str(e)}")

@router.get("/images/check")
async def check_images_directory():
    """Check if images directory exists and list some files"""
    try:
        import os
        images_dir = image_service.images_dir
        
        if not images_dir.exists():
            return {
                'exists': False,
                'path': str(images_dir),
                'message': 'Images directory not found'
            }
            
        # List first 10 files
        files = list(images_dir.glob('*'))[:10]
        file_info = [
            {
                'name': f.name,
                'size': f.stat().st_size if f.is_file() else 0,
                'is_file': f.is_file()
            }
            for f in files
        ]
        
        return {
            'exists': True,
            'path': str(images_dir),
            'total_files': len(list(images_dir.glob('*'))),
            'sample_files': file_info
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking images directory: {str(e)}")
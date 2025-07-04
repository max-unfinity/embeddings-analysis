from fastapi import APIRouter, HTTPException
from typing import List
from models.data_models import RemoveRequest, RemoveResponse, ClassesResponse, HealthResponse
from services.data_loader import data_loader
from services.coco_service import coco_service

router = APIRouter()

@router.get("/classes", response_model=List[str])
async def get_classes():
    """Get list of available class names"""
    try:
        if not data_loader.annotations:
            data_loader.load_all()
            
        class_names = coco_service.get_category_names()
        return class_names
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading classes: {str(e)}")

@router.post("/remove", response_model=RemoveResponse)
async def remove_annotations(request: RemoveRequest):
    """Remove annotations by IDs"""
    try:
        if not request.annotation_ids:
            raise HTTPException(status_code=400, detail="No annotation IDs provided")
            
        result = coco_service.remove_annotations_by_ids(request.annotation_ids)
        
        return RemoveResponse(
            success=result['success'],
            removed_count=result['removed_count'],
            output_file=result['output_file']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing annotations: {str(e)}")

@router.get("/annotations/stats")
async def get_annotation_stats():
    """Get statistics about annotations"""
    try:
        if not data_loader.annotations:
            data_loader.load_all()
            
        stats = coco_service.get_annotation_stats()
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting annotation stats: {str(e)}")

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check health status of the API"""
    try:
        # Try to load data if not already loaded
        if not data_loader.embeddings or not data_loader.annotations or not data_loader.mapping:
            try:
                data_loader.load_all()
            except Exception:
                pass  # Don't fail health check if data can't be loaded
                
        return HealthResponse(
            status="healthy",
            embeddings_loaded=data_loader.embeddings is not None,
            annotations_loaded=data_loader.annotations is not None,
            mapping_loaded=data_loader.mapping is not None
        )
        
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            embeddings_loaded=False,
            annotations_loaded=False,
            mapping_loaded=False
        )

@router.post("/reload")
async def reload_data():
    """Reload all data files"""
    try:
        data_loader.load_all()
        
        return {
            'success': True,
            'message': 'Data reloaded successfully',
            'embeddings_shape': list(data_loader.embeddings.shape) if data_loader.embeddings is not None else None,
            'annotations_count': len(data_loader.annotations['annotations']) if data_loader.annotations else 0,
            'mapping_count': len(data_loader.mapping) if data_loader.mapping else 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reloading data: {str(e)}")

@router.get("/annotations/{annotation_id}")
async def get_annotation(annotation_id: int):
    """Get specific annotation by ID"""
    try:
        annotation = data_loader.get_annotation_by_id(annotation_id)
        if not annotation:
            raise HTTPException(status_code=404, detail="Annotation not found")
            
        return annotation
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting annotation: {str(e)}")
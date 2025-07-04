from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from models.data_models import EmbeddingPoint, SelectionRequest, SelectionResponse
from services.data_loader import data_loader

router = APIRouter()

@router.get("/embeddings", response_model=List[EmbeddingPoint])
async def get_embeddings(class_name: Optional[str] = Query(None, description="Filter by class name")):
    """Get all embedding points or filtered by class"""
    if data_loader.embeddings is None:
        # Try to load data if not already loaded
        data_loader.load_all()
        
    points = data_loader.get_embedding_points(class_filter=class_name)
    return points
        

@router.get("/embeddings/{class_name}", response_model=List[EmbeddingPoint])
async def get_embeddings_by_class(class_name: str):
    """Get embedding points filtered by specific class"""
    if data_loader.embeddings is None:
        data_loader.load_all()
        
    points = data_loader.get_embedding_points(class_filter=class_name)
    return points
        
@router.post("/selection", response_model=SelectionResponse)
async def get_selection(selection: SelectionRequest):
    """Get annotation IDs within the selection rectangle"""
    annotation_ids = data_loader.get_annotations_in_selection(
        selection.x_min, selection.x_max,
        selection.y_min, selection.y_max
    )
        
    return SelectionResponse(annotation_ids=annotation_ids)
        
@router.get("/embeddings/stats")
async def get_embedding_stats():
    """Get statistics about embeddings"""
    if data_loader.embeddings is None:
        data_loader.load_all()
        
    points = data_loader.get_embedding_points()
    
    # Calculate stats
    class_counts = {}
    for point in points:
        class_name = point['class_name']
        class_counts[class_name] = class_counts.get(class_name, 0) + 1
        
    total_points = len(points)
    
    return {
        'total_points': total_points,
        'class_counts': class_counts,
        'embedding_shape': list(data_loader.embeddings.shape) if data_loader.embeddings is not None else None
    }
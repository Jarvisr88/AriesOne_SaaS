"""
AI services for image analysis and processing.
"""
from typing import Dict, Any, List, Optional
import io
import asyncio
from PIL import Image
import logging
import numpy as np
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input, decode_predictions
from transformers import ViTImageProcessor, ViTForImageClassification
import torch
from .config import settings


class AIService:
    """Manages AI-powered image analysis."""
    
    def __init__(self):
        """Initialize AI service."""
        self.logger = logging.getLogger(__name__)
        
        # Initialize models
        self._init_models()
        
    def _init_models(self):
        """Initialize AI models."""
        try:
            # Classification model
            self.classifier = ResNet50(
                weights='imagenet',
                include_top=True
            )
            
            # Vision transformer
            self.vit_processor = ViTImageProcessor.from_pretrained(
                'google/vit-base-patch16-224'
            )
            self.vit_model = ViTForImageClassification.from_pretrained(
                'google/vit-base-patch16-224'
            )
            
            # Move to GPU if available
            if torch.cuda.is_available():
                self.vit_model = self.vit_model.to('cuda')
                
        except Exception as e:
            self.logger.error(f"Model initialization error: {str(e)}")
            raise
            
    async def analyze_image(
        self,
        image_data: bytes
    ) -> Dict[str, Any]:
        """Analyze image content.
        
        Args:
            image_data: Raw image data
            
        Returns:
            Analysis results
        """
        try:
            # Run analysis in thread pool
            result = await asyncio.to_thread(
                self._analyze_sync,
                image_data
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Analysis error: {str(e)}")
            return {}
            
    def _analyze_sync(
        self,
        image_data: bytes
    ) -> Dict[str, Any]:
        """Synchronous image analysis.
        
        Args:
            image_data: Raw image data
            
        Returns:
            Analysis results
        """
        # Open image
        image = Image.open(io.BytesIO(image_data))
        
        # Run ResNet classification
        resnet_results = self._classify_resnet(image)
        
        # Run ViT analysis
        vit_results = self._analyze_vit(image)
        
        return {
            "classification": resnet_results,
            "analysis": vit_results,
            "nsfw_score": vit_results.get("nsfw_score", 0),
            "quality_score": self._assess_quality(image)
        }
        
    def _classify_resnet(
        self,
        image: Image.Image
    ) -> List[Dict[str, Any]]:
        """Classify image with ResNet.
        
        Args:
            image: PIL image
            
        Returns:
            Classification results
        """
        # Prepare image
        img = image.convert('RGB')
        img = img.resize((224, 224))
        x = np.array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)
        
        # Get predictions
        preds = self.classifier.predict(x)
        results = decode_predictions(preds, top=5)[0]
        
        return [
            {
                "label": label,
                "confidence": float(score)
            }
            for _, label, score in results
        ]
        
    def _analyze_vit(
        self,
        image: Image.Image
    ) -> Dict[str, Any]:
        """Analyze image with Vision Transformer.
        
        Args:
            image: PIL image
            
        Returns:
            Analysis results
        """
        # Prepare image
        inputs = self.vit_processor(
            image,
            return_tensors="pt"
        )
        
        # Move to GPU if available
        if torch.cuda.is_available():
            inputs = {
                k: v.to('cuda')
                for k, v in inputs.items()
            }
            
        # Get predictions
        with torch.no_grad():
            outputs = self.vit_model(**inputs)
            probs = outputs.logits.softmax(-1)
            
        # Get top predictions
        top_probs, top_ids = probs[0].topk(5)
        
        results = [
            {
                "label": self.vit_model.config.id2label[id.item()],
                "confidence": prob.item()
            }
            for prob, id in zip(top_probs, top_ids)
        ]
        
        # Calculate NSFW score
        nsfw_score = self._calculate_nsfw_score(results)
        
        return {
            "vit_results": results,
            "nsfw_score": nsfw_score
        }
        
    def _calculate_nsfw_score(
        self,
        results: List[Dict[str, Any]]
    ) -> float:
        """Calculate NSFW probability score.
        
        Args:
            results: Classification results
            
        Returns:
            NSFW score (0-1)
        """
        nsfw_keywords = {
            'explicit', 'nude', 'adult',
            'nsfw', 'inappropriate'
        }
        
        score = 0.0
        for result in results:
            label = result['label'].lower()
            if any(kw in label for kw in nsfw_keywords):
                score = max(score, result['confidence'])
                
        return score
        
    def _assess_quality(
        self,
        image: Image.Image
    ) -> float:
        """Assess image quality.
        
        Args:
            image: PIL image
            
        Returns:
            Quality score (0-1)
        """
        try:
            # Convert to grayscale
            gray = image.convert('L')
            
            # Calculate metrics
            array = np.array(gray)
            
            # Sharpness
            laplacian = np.var(
                np.array(
                    Image.fromarray(array).filter(
                        Image.FIND_EDGES
                    )
                )
            )
            
            # Contrast
            contrast = array.std()
            
            # Normalize metrics
            sharpness = min(laplacian / 500.0, 1.0)
            contrast_score = min(contrast / 127.0, 1.0)
            
            # Combine scores
            return (sharpness + contrast_score) / 2.0
            
        except Exception as e:
            self.logger.error(f"Quality assessment error: {str(e)}")
            return 0.5

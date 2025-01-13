from datetime import datetime
from typing import List, Dict, Optional
import hashlib
import base64
from PIL import Image
import io
from fastapi import HTTPException, UploadFile
from app.core.config import Settings
from app.core.logging import logger
from app.models.pod import (
    ProofOfDelivery,
    Signature,
    DeliveryPhoto,
    CustomerFeedback,
    DeliveryException,
    DigitalReceipt
)
from app.services.storage.storage_service import StorageService
from app.services.location.location_service import LocationService

class ProofOfDeliveryService:
    def __init__(
        self,
        settings: Settings,
        storage_service: StorageService,
        location_service: LocationService
    ):
        self.settings = settings
        self.storage_service = storage_service
        self.location_service = location_service
        self.pod_rules = settings.pod.rules
        self.offline_queue = []

    async def capture_delivery_proof(
        self,
        delivery_id: str,
        proof_data: Dict,
        location: Dict,
        timestamp: datetime
    ) -> ProofOfDelivery:
        """
        Capture complete proof of delivery
        """
        try:
            # Verify location
            location_verified = await self.verify_delivery_location(
                delivery_id,
                location
            )

            if not location_verified:
                raise ValueError("Delivery location verification failed")

            # Process signature
            signature = await self.process_signature(
                proof_data.get('signature'),
                delivery_id
            )

            # Process photos
            photos = await self.process_photos(
                proof_data.get('photos', []),
                delivery_id
            )

            # Create POD record
            pod = await ProofOfDelivery.create(
                delivery_id=delivery_id,
                signature_id=signature.id if signature else None,
                photo_ids=[photo.id for photo in photos],
                location=location,
                timestamp=timestamp,
                status='completed',
                verification_hash=self.generate_verification_hash(
                    delivery_id,
                    timestamp,
                    location
                ),
                created_at=datetime.now()
            )

            # Generate digital receipt
            receipt = await self.generate_digital_receipt(pod)

            # Collect customer feedback
            if proof_data.get('feedback'):
                await self.collect_customer_feedback(
                    pod.id,
                    proof_data['feedback']
                )

            return pod

        except Exception as e:
            logger.error(f"Error capturing delivery proof: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error capturing delivery proof: {str(e)}"
            )

    async def process_signature(
        self,
        signature_data: Optional[Dict],
        delivery_id: str
    ) -> Optional[Signature]:
        """
        Process and store electronic signature
        """
        if not signature_data:
            return None

        try:
            # Validate signature data
            if not self.validate_signature_data(signature_data):
                raise ValueError("Invalid signature data")

            # Convert signature to standard format
            signature_image = self.convert_signature_to_image(
                signature_data['points']
            )

            # Store signature
            signature_path = await self.storage_service.store_signature(
                signature_image,
                delivery_id
            )

            # Create signature record
            signature = await Signature.create(
                delivery_id=delivery_id,
                signer_name=signature_data['signer_name'],
                signature_path=signature_path,
                timestamp=datetime.now(),
                created_at=datetime.now()
            )

            return signature

        except Exception as e:
            logger.error(f"Error processing signature: {str(e)}")
            raise

    async def process_photos(
        self,
        photos: List[UploadFile],
        delivery_id: str
    ) -> List[DeliveryPhoto]:
        """
        Process and store delivery photos
        """
        processed_photos = []

        try:
            for photo in photos:
                # Validate photo
                if not self.validate_photo(photo):
                    continue

                # Optimize photo
                optimized_photo = await self.optimize_photo(photo)

                # Store photo
                photo_path = await self.storage_service.store_photo(
                    optimized_photo,
                    delivery_id
                )

                # Create photo record
                photo_record = await DeliveryPhoto.create(
                    delivery_id=delivery_id,
                    photo_path=photo_path,
                    photo_type=photo.content_type,
                    timestamp=datetime.now(),
                    created_at=datetime.now()
                )

                processed_photos.append(photo_record)

            return processed_photos

        except Exception as e:
            logger.error(f"Error processing photos: {str(e)}")
            raise

    async def verify_delivery_location(
        self,
        delivery_id: str,
        location: Dict
    ) -> bool:
        """
        Verify delivery location against expected coordinates
        """
        try:
            # Get expected location
            expected_location = await self.location_service.get_delivery_location(
                delivery_id
            )

            # Calculate distance
            distance = self.location_service.calculate_distance(
                location,
                expected_location
            )

            # Verify within threshold
            return distance <= self.pod_rules.location_threshold

        except Exception as e:
            logger.error(f"Error verifying location: {str(e)}")
            return False

    async def handle_delivery_exception(
        self,
        delivery_id: str,
        exception_data: Dict
    ) -> DeliveryException:
        """
        Handle delivery exceptions
        """
        try:
            # Create exception record
            exception = await DeliveryException.create(
                delivery_id=delivery_id,
                exception_type=exception_data['type'],
                description=exception_data['description'],
                photos=[
                    await self.process_photos([photo], delivery_id)
                    for photo in exception_data.get('photos', [])
                ],
                location=exception_data['location'],
                timestamp=datetime.now(),
                status='pending',
                created_at=datetime.now()
            )

            # Notify relevant parties
            await self.notify_exception_handlers(exception)

            return exception

        except Exception as e:
            logger.error(f"Error handling delivery exception: {str(e)}")
            raise

    async def collect_customer_feedback(
        self,
        pod_id: str,
        feedback_data: Dict
    ) -> CustomerFeedback:
        """
        Collect and store customer feedback
        """
        try:
            # Create feedback record
            feedback = await CustomerFeedback.create(
                pod_id=pod_id,
                rating=feedback_data['rating'],
                comments=feedback_data.get('comments'),
                categories=feedback_data.get('categories', []),
                timestamp=datetime.now(),
                created_at=datetime.now()
            )

            # Process feedback for analytics
            await self.process_feedback_analytics(feedback)

            return feedback

        except Exception as e:
            logger.error(f"Error collecting feedback: {str(e)}")
            raise

    async def generate_digital_receipt(
        self,
        pod: ProofOfDelivery
    ) -> DigitalReceipt:
        """
        Generate digital receipt for delivery
        """
        try:
            # Get delivery details
            delivery_details = await self.get_delivery_details(pod.delivery_id)

            # Create receipt record
            receipt = await DigitalReceipt.create(
                pod_id=pod.id,
                delivery_id=pod.delivery_id,
                receipt_number=self.generate_receipt_number(),
                delivery_details=delivery_details,
                verification_code=self.generate_verification_code(pod),
                created_at=datetime.now()
            )

            # Store receipt
            receipt_path = await self.generate_receipt_document(receipt)
            await receipt.update(receipt_path=receipt_path)

            return receipt

        except Exception as e:
            logger.error(f"Error generating receipt: {str(e)}")
            raise

    def validate_signature_data(self, signature_data: Dict) -> bool:
        """
        Validate electronic signature data
        """
        required_fields = ['signer_name', 'points']
        return all(field in signature_data for field in required_fields)

    def validate_photo(self, photo: UploadFile) -> bool:
        """
        Validate delivery photo
        """
        allowed_types = ['image/jpeg', 'image/png']
        max_size = 10 * 1024 * 1024  # 10MB

        return (
            photo.content_type in allowed_types and
            photo.size <= max_size
        )

    async def optimize_photo(self, photo: UploadFile) -> bytes:
        """
        Optimize photo for storage
        """
        try:
            image = Image.open(io.BytesIO(await photo.read()))
            
            # Resize if too large
            max_size = (1920, 1080)
            image.thumbnail(max_size, Image.LANCZOS)

            # Optimize quality
            output = io.BytesIO()
            image.save(
                output,
                format=image.format,
                quality=85,
                optimize=True
            )

            return output.getvalue()

        except Exception as e:
            logger.error(f"Error optimizing photo: {str(e)}")
            raise

    def generate_verification_hash(
        self,
        delivery_id: str,
        timestamp: datetime,
        location: Dict
    ) -> str:
        """
        Generate verification hash for POD
        """
        data = f"{delivery_id}_{timestamp.isoformat()}_{str(location)}"
        return hashlib.sha256(data.encode()).hexdigest()

    def generate_receipt_number(self) -> str:
        """
        Generate unique receipt number
        """
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_suffix = base64.b32encode(os.urandom(3)).decode()
        return f"RCP{timestamp}{random_suffix}"

    def generate_verification_code(self, pod: ProofOfDelivery) -> str:
        """
        Generate verification code for digital receipt
        """
        data = f"{pod.id}_{pod.timestamp.isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:12]

    async def queue_offline_pod(
        self,
        delivery_id: str,
        proof_data: Dict
    ) -> None:
        """
        Queue POD data for offline capture
        """
        self.offline_queue.append({
            'delivery_id': delivery_id,
            'proof_data': proof_data,
            'timestamp': datetime.now()
        })

    async def sync_offline_pods(self) -> List[ProofOfDelivery]:
        """
        Sync queued offline PODs
        """
        synced_pods = []

        while self.offline_queue:
            pod_data = self.offline_queue.pop(0)
            try:
                pod = await self.capture_delivery_proof(
                    pod_data['delivery_id'],
                    pod_data['proof_data'],
                    pod_data.get('location'),
                    pod_data['timestamp']
                )
                synced_pods.append(pod)
            except Exception as e:
                logger.error(f"Error syncing offline POD: {str(e)}")
                self.offline_queue.append(pod_data)

        return synced_pods

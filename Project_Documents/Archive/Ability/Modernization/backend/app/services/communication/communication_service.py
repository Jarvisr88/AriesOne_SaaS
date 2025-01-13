from datetime import datetime
from typing import List, Dict, Optional
import aiohttp
from fastapi import HTTPException
from app.core.config import Settings
from app.core.logging import logger
from app.models.communication import (
    Notification,
    EmailTemplate,
    SMSTemplate,
    DeliveryUpdate,
    CustomerRating,
    NotificationPreference
)

class CommunicationService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.sms_provider = settings.communication.sms_provider
        self.email_provider = settings.communication.email_provider
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict:
        """
        Load notification templates
        """
        return {
            'email': {
                template.type: template
                for template in EmailTemplate.all()
            },
            'sms': {
                template.type: template
                for template in SMSTemplate.all()
            }
        }

    async def send_notification(
        self,
        customer_id: str,
        notification_type: str,
        data: Dict
    ) -> Notification:
        """
        Send notification based on customer preferences
        """
        try:
            # Get customer preferences
            preferences = await NotificationPreference.get(
                customer_id=customer_id
            )

            # Determine notification methods
            methods = self._determine_notification_methods(
                preferences,
                notification_type
            )

            notifications = []
            for method in methods:
                if method == 'sms':
                    notification = await self.send_sms(
                        customer_id,
                        notification_type,
                        data
                    )
                elif method == 'email':
                    notification = await self.send_email(
                        customer_id,
                        notification_type,
                        data
                    )

                notifications.append(notification)

            return notifications

        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            raise

    async def send_sms(
        self,
        customer_id: str,
        notification_type: str,
        data: Dict
    ) -> Notification:
        """
        Send SMS notification
        """
        try:
            # Get customer phone
            customer = await self._get_customer(customer_id)
            if not customer.phone:
                raise ValueError("Customer phone number not available")

            # Get template
            template = self.templates['sms'].get(notification_type)
            if not template:
                raise ValueError(f"SMS template not found: {notification_type}")

            # Prepare message
            message = template.render(data)

            # Send SMS
            response = await self._send_sms_with_provider(
                customer.phone,
                message
            )

            # Create notification record
            notification = await Notification.create(
                customer_id=customer_id,
                type=notification_type,
                method='sms',
                content=message,
                status='sent',
                provider_response=response,
                created_at=datetime.now()
            )

            return notification

        except Exception as e:
            logger.error(f"Error sending SMS: {str(e)}")
            raise

    async def send_email(
        self,
        customer_id: str,
        notification_type: str,
        data: Dict
    ) -> Notification:
        """
        Send email notification
        """
        try:
            # Get customer email
            customer = await self._get_customer(customer_id)
            if not customer.email:
                raise ValueError("Customer email not available")

            # Get template
            template = self.templates['email'].get(notification_type)
            if not template:
                raise ValueError(f"Email template not found: {notification_type}")

            # Prepare email
            subject = template.render_subject(data)
            body = template.render_body(data)

            # Send email
            response = await self._send_email_with_provider(
                customer.email,
                subject,
                body
            )

            # Create notification record
            notification = await Notification.create(
                customer_id=customer_id,
                type=notification_type,
                method='email',
                content={'subject': subject, 'body': body},
                status='sent',
                provider_response=response,
                created_at=datetime.now()
            )

            return notification

        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            raise

    async def update_delivery_status(
        self,
        delivery_id: str,
        status: str,
        details: Optional[Dict] = None
    ) -> DeliveryUpdate:
        """
        Send delivery status update
        """
        try:
            # Get delivery info
            delivery = await self._get_delivery(delivery_id)

            # Create update record
            update = await DeliveryUpdate.create(
                delivery_id=delivery_id,
                status=status,
                details=details,
                created_at=datetime.now()
            )

            # Send notification
            await self.send_notification(
                delivery.customer_id,
                f"delivery_{status}",
                {
                    'delivery_id': delivery_id,
                    'status': status,
                    'details': details,
                    'tracking_url': self._generate_tracking_url(delivery_id)
                }
            )

            return update

        except Exception as e:
            logger.error(f"Error updating delivery status: {str(e)}")
            raise

    async def collect_delivery_rating(
        self,
        delivery_id: str,
        rating_data: Dict
    ) -> CustomerRating:
        """
        Collect and process delivery rating
        """
        try:
            # Validate rating
            if not self._validate_rating(rating_data):
                raise ValueError("Invalid rating data")

            # Create rating record
            rating = await CustomerRating.create(
                delivery_id=delivery_id,
                rating=rating_data['rating'],
                feedback=rating_data.get('feedback'),
                categories=rating_data.get('categories', []),
                created_at=datetime.now()
            )

            # Process rating
            await self._process_rating(rating)

            # Send thank you notification
            delivery = await self._get_delivery(delivery_id)
            await self.send_notification(
                delivery.customer_id,
                'rating_received',
                {'delivery_id': delivery_id}
            )

            return rating

        except Exception as e:
            logger.error(f"Error collecting rating: {str(e)}")
            raise

    async def _send_sms_with_provider(
        self,
        phone: str,
        message: str
    ) -> Dict:
        """
        Send SMS using configured provider
        """
        async with aiohttp.ClientSession() as session:
            params = {
                'to': phone,
                'message': message,
                'key': self.sms_provider.api_key
            }
            
            async with session.post(
                self.sms_provider.base_url,
                json=params
            ) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=response.status,
                        detail="SMS sending failed"
                    )
                return await response.json()

    async def _send_email_with_provider(
        self,
        email: str,
        subject: str,
        body: str
    ) -> Dict:
        """
        Send email using configured provider
        """
        async with aiohttp.ClientSession() as session:
            params = {
                'to': email,
                'subject': subject,
                'body': body,
                'key': self.email_provider.api_key
            }
            
            async with session.post(
                self.email_provider.base_url,
                json=params
            ) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=response.status,
                        detail="Email sending failed"
                    )
                return await response.json()

    def _determine_notification_methods(
        self,
        preferences: NotificationPreference,
        notification_type: str
    ) -> List[str]:
        """
        Determine notification methods based on preferences
        """
        methods = []
        
        if preferences.sms_enabled and notification_type in preferences.sms_types:
            methods.append('sms')
            
        if preferences.email_enabled and notification_type in preferences.email_types:
            methods.append('email')
            
        return methods or ['email']  # Default to email if no preferences

    def _generate_tracking_url(self, delivery_id: str) -> str:
        """
        Generate tracking URL for delivery
        """
        base_url = self.settings.application.tracking_url
        return f"{base_url}/track/{delivery_id}"

    def _validate_rating(self, rating_data: Dict) -> bool:
        """
        Validate rating data
        """
        if 'rating' not in rating_data:
            return False
            
        rating = rating_data['rating']
        return isinstance(rating, int) and 1 <= rating <= 5

    async def _process_rating(self, rating: CustomerRating) -> None:
        """
        Process and analyze rating
        """
        # Update delivery metrics
        delivery = await self._get_delivery(rating.delivery_id)
        await self._update_delivery_metrics(delivery, rating)

        # Update driver metrics
        await self._update_driver_metrics(delivery.driver_id, rating)

        # Process feedback if rating is low
        if rating.rating <= 3:
            await self._process_low_rating(rating)

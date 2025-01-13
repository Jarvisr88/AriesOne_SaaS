from datetime import datetime, timedelta
from typing import List, Dict, Optional
from enum import Enum
from fastapi import HTTPException
from app.core.config import Settings
from app.core.logging import logger
from app.models.vendor import (
    Vendor,
    Contract,
    PriceHistory,
    QualityReport,
    DeliveryPerformance,
    Payment,
    VendorRating,
    Communication
)

class VendorStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    BLACKLISTED = "blacklisted"

class ContractStatus(Enum):
    DRAFT = "draft"
    NEGOTIATING = "negotiating"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"

class VendorManagementService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.performance_weights = settings.vendor.performance_weights
        self.rating_thresholds = settings.vendor.rating_thresholds

    async def calculate_vendor_performance(
        self,
        vendor_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """
        Calculate comprehensive vendor performance metrics
        """
        try:
            # Get vendor data
            vendor = await Vendor.get_or_none(id=vendor_id)
            if not vendor:
                raise HTTPException(
                    status_code=404,
                    detail=f"Vendor {vendor_id} not found"
                )

            # Calculate delivery performance
            delivery_metrics = await self.calculate_delivery_performance(
                vendor_id,
                start_date,
                end_date
            )

            # Calculate quality metrics
            quality_metrics = await self.calculate_quality_metrics(
                vendor_id,
                start_date,
                end_date
            )

            # Calculate price performance
            price_metrics = await self.calculate_price_performance(
                vendor_id,
                start_date,
                end_date
            )

            # Calculate payment compliance
            payment_metrics = await self.calculate_payment_metrics(
                vendor_id,
                start_date,
                end_date
            )

            # Calculate overall score
            overall_score = (
                delivery_metrics['score'] * self.performance_weights['delivery'] +
                quality_metrics['score'] * self.performance_weights['quality'] +
                price_metrics['score'] * self.performance_weights['price'] +
                payment_metrics['score'] * self.performance_weights['payment']
            )

            return {
                'vendor_id': vendor_id,
                'period': {
                    'start': start_date,
                    'end': end_date
                },
                'overall_score': overall_score,
                'delivery_performance': delivery_metrics,
                'quality_metrics': quality_metrics,
                'price_performance': price_metrics,
                'payment_metrics': payment_metrics,
                'rating': self.calculate_rating(overall_score)
            }

        except Exception as e:
            logger.error(f"Error calculating vendor performance: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error calculating vendor performance: {str(e)}"
            )

    async def manage_contracts(
        self,
        vendor_id: str,
        action: str,
        contract_data: Optional[Dict] = None
    ) -> Contract:
        """
        Manage vendor contracts
        """
        try:
            if action == "create":
                contract = await Contract.create(
                    vendor_id=vendor_id,
                    **contract_data,
                    status=ContractStatus.DRAFT.value,
                    created_at=datetime.now()
                )
            elif action == "update":
                contract = await Contract.get(
                    id=contract_data['contract_id'],
                    vendor_id=vendor_id
                )
                for key, value in contract_data.items():
                    setattr(contract, key, value)
                await contract.save()
            elif action == "terminate":
                contract = await Contract.get(
                    id=contract_data['contract_id'],
                    vendor_id=vendor_id
                )
                contract.status = ContractStatus.TERMINATED.value
                contract.termination_date = datetime.now()
                contract.termination_reason = contract_data.get('reason')
                await contract.save()

            return contract

        except Exception as e:
            logger.error(f"Error managing contract: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error managing contract: {str(e)}"
            )

    async def negotiate_prices(
        self,
        vendor_id: str,
        items: List[Dict]
    ) -> Dict:
        """
        Handle price negotiation process
        """
        try:
            negotiation_results = []
            
            for item in items:
                # Get price history
                price_history = await PriceHistory.filter(
                    vendor_id=vendor_id,
                    item_id=item['item_id']
                ).order_by('-effective_date')

                # Calculate target price
                market_price = await self.get_market_price(item['item_id'])
                volume_discount = self.calculate_volume_discount(
                    item['quantity']
                )
                target_price = market_price * (1 - volume_discount)

                # Compare with vendor's proposed price
                price_difference = (
                    (item['proposed_price'] - target_price) / target_price
                ) * 100

                negotiation_results.append({
                    'item_id': item['item_id'],
                    'current_price': price_history[0].price if price_history else None,
                    'proposed_price': item['proposed_price'],
                    'target_price': target_price,
                    'price_difference': price_difference,
                    'recommendation': self.get_price_recommendation(
                        price_difference
                    )
                })

            return {
                'vendor_id': vendor_id,
                'negotiation_date': datetime.now(),
                'results': negotiation_results
            }

        except Exception as e:
            logger.error(f"Error negotiating prices: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error negotiating prices: {str(e)}"
            )

    async def track_quality(
        self,
        vendor_id: str,
        report_data: Dict
    ) -> QualityReport:
        """
        Track vendor quality metrics
        """
        try:
            report = await QualityReport.create(
                vendor_id=vendor_id,
                **report_data,
                created_at=datetime.now()
            )

            # Update vendor rating
            await self.update_vendor_rating(vendor_id)

            return report

        except Exception as e:
            logger.error(f"Error tracking quality: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error tracking quality: {str(e)}"
            )

    async def track_delivery(
        self,
        vendor_id: str,
        delivery_data: Dict
    ) -> DeliveryPerformance:
        """
        Track delivery performance
        """
        try:
            delivery = await DeliveryPerformance.create(
                vendor_id=vendor_id,
                **delivery_data,
                created_at=datetime.now()
            )

            # Calculate delivery metrics
            on_time = delivery.actual_date <= delivery.expected_date
            delay_days = (
                (delivery.actual_date - delivery.expected_date).days
                if not on_time else 0
            )

            # Update delivery record
            delivery.on_time = on_time
            delivery.delay_days = delay_days
            await delivery.save()

            # Update vendor rating
            await self.update_vendor_rating(vendor_id)

            return delivery

        except Exception as e:
            logger.error(f"Error tracking delivery: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error tracking delivery: {str(e)}"
            )

    async def track_payment(
        self,
        vendor_id: str,
        payment_data: Dict
    ) -> Payment:
        """
        Track vendor payments
        """
        try:
            payment = await Payment.create(
                vendor_id=vendor_id,
                **payment_data,
                created_at=datetime.now()
            )

            # Calculate payment metrics
            if payment.status == 'completed':
                payment.processing_time = (
                    payment.completed_at - payment.created_at
                ).days
                await payment.save()

            return payment

        except Exception as e:
            logger.error(f"Error tracking payment: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error tracking payment: {str(e)}"
            )

    async def update_vendor_rating(
        self,
        vendor_id: str
    ) -> VendorRating:
        """
        Update vendor rating based on performance metrics
        """
        try:
            # Calculate performance metrics
            performance = await self.calculate_vendor_performance(
                vendor_id,
                datetime.now() - timedelta(days=365),
                datetime.now()
            )

            # Create or update rating
            rating, created = await VendorRating.get_or_create(
                vendor_id=vendor_id,
                defaults={
                    'score': performance['overall_score'],
                    'rating': performance['rating'],
                    'last_updated': datetime.now()
                }
            )

            if not created:
                rating.score = performance['overall_score']
                rating.rating = performance['rating']
                rating.last_updated = datetime.now()
                await rating.save()

            return rating

        except Exception as e:
            logger.error(f"Error updating vendor rating: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error updating vendor rating: {str(e)}"
            )

    async def manage_communication(
        self,
        vendor_id: str,
        message_data: Dict
    ) -> Communication:
        """
        Manage vendor communication
        """
        try:
            message = await Communication.create(
                vendor_id=vendor_id,
                **message_data,
                created_at=datetime.now()
            )

            # Send notification if urgent
            if message.priority == 'urgent':
                await self.notify_vendor(
                    vendor_id,
                    'urgent_message',
                    message.content
                )

            return message

        except Exception as e:
            logger.error(f"Error managing communication: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error managing communication: {str(e)}"
            )

    async def calculate_delivery_performance(
        self,
        vendor_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """
        Calculate delivery performance metrics
        """
        deliveries = await DeliveryPerformance.filter(
            vendor_id=vendor_id,
            created_at__gte=start_date,
            created_at__lte=end_date
        )

        total_deliveries = len(deliveries)
        if total_deliveries == 0:
            return {
                'score': 0,
                'on_time_rate': 0,
                'average_delay': 0,
                'total_deliveries': 0
            }

        on_time_deliveries = sum(1 for d in deliveries if d.on_time)
        total_delay = sum(d.delay_days for d in deliveries if not d.on_time)

        return {
            'score': (on_time_deliveries / total_deliveries) * 100,
            'on_time_rate': (on_time_deliveries / total_deliveries) * 100,
            'average_delay': total_delay / (total_deliveries - on_time_deliveries) if total_deliveries > on_time_deliveries else 0,
            'total_deliveries': total_deliveries
        }

    async def calculate_quality_metrics(
        self,
        vendor_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """
        Calculate quality metrics
        """
        reports = await QualityReport.filter(
            vendor_id=vendor_id,
            created_at__gte=start_date,
            created_at__lte=end_date
        )

        total_reports = len(reports)
        if total_reports == 0:
            return {
                'score': 0,
                'defect_rate': 0,
                'return_rate': 0,
                'total_inspections': 0
            }

        total_defects = sum(r.defect_count for r in reports)
        total_returns = sum(r.return_count for r in reports)
        total_items = sum(r.inspection_quantity for r in reports)

        return {
            'score': ((total_items - total_defects) / total_items) * 100,
            'defect_rate': (total_defects / total_items) * 100,
            'return_rate': (total_returns / total_items) * 100,
            'total_inspections': total_reports
        }

    async def calculate_price_performance(
        self,
        vendor_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """
        Calculate price performance metrics
        """
        price_history = await PriceHistory.filter(
            vendor_id=vendor_id,
            effective_date__gte=start_date,
            effective_date__lte=end_date
        )

        if not price_history:
            return {
                'score': 0,
                'price_variance': 0,
                'market_difference': 0,
                'total_items': 0
            }

        price_variances = []
        market_differences = []

        for price in price_history:
            market_price = await self.get_market_price(price.item_id)
            
            if market_price > 0:
                market_diff = ((price.price - market_price) / market_price) * 100
                market_differences.append(market_diff)

            if price.previous_price:
                variance = ((price.price - price.previous_price) / price.previous_price) * 100
                price_variances.append(variance)

        avg_market_diff = sum(market_differences) / len(market_differences) if market_differences else 0
        score = 100 - abs(avg_market_diff)  # Higher score for prices closer to market

        return {
            'score': max(0, min(score, 100)),  # Clamp between 0 and 100
            'price_variance': sum(price_variances) / len(price_variances) if price_variances else 0,
            'market_difference': avg_market_diff,
            'total_items': len(price_history)
        }

    async def calculate_payment_metrics(
        self,
        vendor_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """
        Calculate payment compliance metrics
        """
        payments = await Payment.filter(
            vendor_id=vendor_id,
            created_at__gte=start_date,
            created_at__lte=end_date,
            status='completed'
        )

        total_payments = len(payments)
        if total_payments == 0:
            return {
                'score': 0,
                'average_processing_time': 0,
                'on_time_payment_rate': 0,
                'total_payments': 0
            }

        on_time_payments = sum(1 for p in payments if p.processing_time <= p.expected_processing_time)
        total_processing_time = sum(p.processing_time for p in payments)

        return {
            'score': (on_time_payments / total_payments) * 100,
            'average_processing_time': total_processing_time / total_payments,
            'on_time_payment_rate': (on_time_payments / total_payments) * 100,
            'total_payments': total_payments
        }

    def calculate_rating(self, score: float) -> str:
        """
        Calculate vendor rating based on score
        """
        if score >= self.rating_thresholds['excellent']:
            return 'A'
        elif score >= self.rating_thresholds['good']:
            return 'B'
        elif score >= self.rating_thresholds['fair']:
            return 'C'
        elif score >= self.rating_thresholds['poor']:
            return 'D'
        else:
            return 'F'

    def get_price_recommendation(self, price_difference: float) -> str:
        """
        Get price negotiation recommendation
        """
        if price_difference <= -10:
            return "Accept - Price significantly below target"
        elif price_difference <= 0:
            return "Accept - Price below target"
        elif price_difference <= 5:
            return "Consider - Price slightly above target"
        elif price_difference <= 15:
            return "Negotiate - Price moderately above target"
        else:
            return "Reject - Price significantly above target"

    def calculate_volume_discount(self, quantity: int) -> float:
        """
        Calculate volume discount percentage
        """
        if quantity >= 1000:
            return 0.15
        elif quantity >= 500:
            return 0.10
        elif quantity >= 100:
            return 0.05
        else:
            return 0

from typing import Dict, List, Optional, Union
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel
import httpx
import logging
import pandas as pd
from fastapi import HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import json
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReportFormat(str, Enum):
    JSON = "json"
    CSV = "csv"
    EXCEL = "excel"
    PDF = "pdf"

class ReportType(str, Enum):
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    CLINICAL = "clinical"
    COMPLIANCE = "compliance"
    CUSTOM = "custom"

class ReportPeriod(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"

class ReportRequest(BaseModel):
    report_type: ReportType
    period: ReportPeriod
    start_date: date
    end_date: date
    filters: Optional[Dict] = None
    format: ReportFormat = ReportFormat.JSON
    include_charts: bool = False

class ReportingSystemIntegration:
    def __init__(self, db_url: str, api_base_url: str, api_key: str):
        # Database setup
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)

        # API configuration
        self.api_base_url = api_base_url
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    async def generate_report(self, request: ReportRequest) -> Dict:
        """Generate a report based on the request parameters"""
        try:
            # Get data from appropriate sources
            raw_data = await self._gather_report_data(request)

            # Process and format the data
            processed_data = self._process_report_data(raw_data, request)

            # Generate charts if requested
            if request.include_charts:
                charts = self._generate_charts(processed_data, request)
                processed_data["charts"] = charts

            # Format the report
            formatted_report = self._format_report(processed_data, request.format)

            # Track report generation
            from services.analytics_service import analytics_service
            await analytics_service.track_action(
                action=UserAction(
                    timestamp=datetime.utcnow(),
                    component="reporting",
                    action="generate_report",
                    data={
                        "report_type": request.report_type,
                        "period": request.period,
                        "format": request.format
                    }
                )
            )

            return formatted_report

        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate report: {str(e)}"
            )

    async def _gather_report_data(self, request: ReportRequest) -> Dict:
        """Gather data from various sources for the report"""
        data = {}
        
        if request.report_type == ReportType.FINANCIAL:
            data["transactions"] = await self._get_billing_data(request)
            data["revenue"] = await self._get_revenue_data(request)
            
        elif request.report_type == ReportType.OPERATIONAL:
            data["patients"] = await self._get_patient_data(request)
            data["providers"] = await self._get_provider_data(request)
            
        elif request.report_type == ReportType.CLINICAL:
            data["treatments"] = await self._get_treatment_data(request)
            data["outcomes"] = await self._get_outcome_data(request)
            
        elif request.report_type == ReportType.COMPLIANCE:
            data["audits"] = await self._get_audit_data(request)
            data["incidents"] = await self._get_incident_data(request)

        return data

    async def _get_billing_data(self, request: ReportRequest) -> List[Dict]:
        """Get billing data from the billing system"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base_url}/billing/transactions",
                    headers=self.headers,
                    params={
                        "start_date": request.start_date.isoformat(),
                        "end_date": request.end_date.isoformat(),
                        **request.filters or {}
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to get billing data: {e}")
            raise

    def _process_report_data(self, raw_data: Dict, request: ReportRequest) -> Dict:
        """Process raw data into report format"""
        processed_data = {"metadata": {
            "report_type": request.report_type,
            "period": request.period,
            "start_date": request.start_date.isoformat(),
            "end_date": request.end_date.isoformat(),
            "generated_at": datetime.utcnow().isoformat()
        }}

        # Convert raw data to pandas DataFrames for processing
        dfs = {}
        for key, data in raw_data.items():
            if data:
                dfs[key] = pd.DataFrame(data)

        # Process based on report type
        if request.report_type == ReportType.FINANCIAL:
            processed_data.update(self._process_financial_data(dfs))
        elif request.report_type == ReportType.OPERATIONAL:
            processed_data.update(self._process_operational_data(dfs))
        elif request.report_type == ReportType.CLINICAL:
            processed_data.update(self._process_clinical_data(dfs))
        elif request.report_type == ReportType.COMPLIANCE:
            processed_data.update(self._process_compliance_data(dfs))

        return processed_data

    def _process_financial_data(self, dfs: Dict[str, pd.DataFrame]) -> Dict:
        """Process financial data"""
        result = {}
        
        if "transactions" in dfs:
            df = dfs["transactions"]
            result["summary"] = {
                "total_revenue": float(df["amount"].sum()),
                "average_transaction": float(df["amount"].mean()),
                "transaction_count": len(df),
                "payment_methods": df["payment_method"].value_counts().to_dict()
            }
            
            result["trends"] = {
                "daily_revenue": df.groupby("date")["amount"].sum().to_dict(),
                "status_distribution": df["status"].value_counts().to_dict()
            }

        return result

    def _generate_charts(self, data: Dict, request: ReportRequest) -> Dict:
        """Generate charts for the report"""
        charts = {}
        
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns
            
            if request.report_type == ReportType.FINANCIAL:
                # Revenue trend chart
                if "trends" in data and "daily_revenue" in data["trends"]:
                    plt.figure(figsize=(10, 6))
                    dates = list(data["trends"]["daily_revenue"].keys())
                    revenues = list(data["trends"]["daily_revenue"].values())
                    plt.plot(dates, revenues)
                    plt.title("Daily Revenue Trend")
                    plt.xlabel("Date")
                    plt.ylabel("Revenue")
                    plt.xticks(rotation=45)
                    
                    # Save to bytes
                    import io
                    buf = io.BytesIO()
                    plt.savefig(buf, format='png')
                    buf.seek(0)
                    import base64
                    charts["revenue_trend"] = base64.b64encode(buf.read()).decode()
                    plt.close()

        except Exception as e:
            logger.error(f"Failed to generate charts: {e}")
            # Continue without charts if there's an error
            pass

        return charts

    def _format_report(self, data: Dict, format: ReportFormat) -> Union[Dict, bytes]:
        """Format the report in the requested format"""
        if format == ReportFormat.JSON:
            return data
        
        elif format == ReportFormat.CSV:
            # Convert nested dict to flat CSV
            df = pd.json_normalize(data)
            return df.to_csv(index=False)
        
        elif format == ReportFormat.EXCEL:
            # Create Excel file with multiple sheets
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                for key, value in data.items():
                    if isinstance(value, (dict, list)):
                        df = pd.DataFrame(value)
                        df.to_excel(writer, sheet_name=key, index=False)
            return output.getvalue()
        
        elif format == ReportFormat.PDF:
            # Generate PDF report
            # This would require additional PDF generation library
            raise NotImplementedError("PDF format not yet implemented")

    async def schedule_report(
        self,
        request: ReportRequest,
        schedule: Dict
    ) -> Dict:
        """Schedule a report for periodic generation"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_base_url}/reports/schedule",
                    headers=self.headers,
                    json={
                        "report_request": request.dict(),
                        "schedule": schedule
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to schedule report: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to schedule report: {str(e)}"
            )

    async def get_scheduled_reports(self) -> List[Dict]:
        """Get list of scheduled reports"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base_url}/reports/schedule",
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to get scheduled reports: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get scheduled reports: {str(e)}"
            )

# Initialize global reporting service
reporting_system = ReportingSystemIntegration(
    db_url="postgresql://user:password@localhost/reporting_db",
    api_base_url="https://api.reporting.com/v1",
    api_key="your-api-key"
)

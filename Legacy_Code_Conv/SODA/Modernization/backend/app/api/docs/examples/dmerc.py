"""DMERC API examples."""

from datetime import datetime, timezone
from uuid import UUID

DMERC_FORM_CREATE = {
    "form_type": "CMN",
    "patient_id": "PAT123456",
    "organization_id": "234e5678-e89b-12d3-a456-426614174000",
    "notes": "Initial CMN for oxygen therapy",
    "metadata": {
        "diagnosis": "COPD",
        "prescribing_physician": "Dr. Jane Smith",
        "oxygen_flow_rate": "2L/min",
        "frequency": "continuous"
    }
}

DMERC_FORM_RESPONSE = {
    "id": "456e7890-e89b-12d3-a456-426614174000",
    "form_number": "CMN-2025-0001",
    "form_type": "CMN",
    "patient_id": "PAT123456",
    "organization_id": "234e5678-e89b-12d3-a456-426614174000",
    "status": "DRAFT",
    "notes": "Initial CMN for oxygen therapy",
    "metadata": {
        "diagnosis": "COPD",
        "prescribing_physician": "Dr. Jane Smith",
        "oxygen_flow_rate": "2L/min",
        "frequency": "continuous"
    },
    "created_at": "2025-01-12T18:44:05Z",
    "updated_at": None,
    "submitted_at": None,
    "approved_at": None,
    "denied_at": None,
    "expires_at": None,
    "created_by_id": "345e6789-e89b-12d3-a456-426614174000",
    "updated_by_id": None
}

DMERC_FORM_UPDATE = {
    "notes": "Updated oxygen flow rate",
    "metadata": {
        "diagnosis": "COPD",
        "prescribing_physician": "Dr. Jane Smith",
        "oxygen_flow_rate": "3L/min",
        "frequency": "continuous"
    }
}

DMERC_ATTACHMENT_RESPONSE = {
    "id": "567e8901-e89b-12d3-a456-426614174000",
    "form_id": "456e7890-e89b-12d3-a456-426614174000",
    "file_name": "prescription.pdf",
    "file_type": "application/pdf",
    "file_size": 1024576,
    "file_path": "uploads/2025/01/prescription.pdf",
    "metadata": {
        "content_type": "prescription",
        "pages": 2,
        "signed": True
    },
    "created_at": "2025-01-12T18:44:05Z",
    "uploaded_by_id": "345e6789-e89b-12d3-a456-426614174000"
}

DMERC_HISTORY_RESPONSE = {
    "id": "678e9012-e89b-12d3-a456-426614174000",
    "form_id": "456e7890-e89b-12d3-a456-426614174000",
    "action": "UPDATE",
    "changes": {
        "status": {
            "from": "DRAFT",
            "to": "SUBMITTED"
        },
        "metadata": {
            "oxygen_flow_rate": {
                "from": "2L/min",
                "to": "3L/min"
            }
        }
    },
    "created_at": "2025-01-12T18:44:05Z",
    "performed_by_id": "345e6789-e89b-12d3-a456-426614174000"
}

DMERC_FORM_WITH_DETAILS = {
    **DMERC_FORM_RESPONSE,
    "attachments": [DMERC_ATTACHMENT_RESPONSE],
    "history": [DMERC_HISTORY_RESPONSE]
}

DMERC_STATUS_UPDATE = {
    "notes": "Approved based on medical necessity"
}

DMERC_SEARCH_REQUEST = {
    "search_term": "COPD",
    "form_type": "CMN",
    "status": "SUBMITTED",
    "offset": 0,
    "limit": 10
}

DMERC_SEARCH_RESPONSE = {
    "forms": [DMERC_FORM_RESPONSE],
    "total": 1
}

examples = {
    "create_form": {
        "summary": "Create DMERC form",
        "description": "Create a new DMERC form with patient and medical information",
        "value": DMERC_FORM_CREATE
    },
    "form_response": {
        "summary": "DMERC form details",
        "description": "Detailed DMERC form information including metadata and timestamps",
        "value": DMERC_FORM_RESPONSE
    },
    "update_form": {
        "summary": "Update DMERC form",
        "description": "Update DMERC form details and metadata",
        "value": DMERC_FORM_UPDATE
    },
    "attachment": {
        "summary": "Form attachment",
        "description": "Attachment details including file information and metadata",
        "value": DMERC_ATTACHMENT_RESPONSE
    },
    "history": {
        "summary": "Form history",
        "description": "Historical record of form changes",
        "value": DMERC_HISTORY_RESPONSE
    },
    "form_with_details": {
        "summary": "Form with details",
        "description": "Complete form information including attachments and history",
        "value": DMERC_FORM_WITH_DETAILS
    },
    "status_update": {
        "summary": "Update form status",
        "description": "Update form status with notes",
        "value": DMERC_STATUS_UPDATE
    },
    "search_request": {
        "summary": "Search forms",
        "description": "Search DMERC forms with filters",
        "value": DMERC_SEARCH_REQUEST
    },
    "search_response": {
        "summary": "Search results",
        "description": "Paginated search results with total count",
        "value": DMERC_SEARCH_RESPONSE
    }
}

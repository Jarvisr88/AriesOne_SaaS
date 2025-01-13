from typing import List, Optional
from datetime import datetime
import strawberry
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info
from strawberry.file_uploads import Upload
from app.core.logging import logger
from app.services.forms import FormService
from app.schemas.forms import FormStatus, FormType
from app.core.analytics import analytics

@strawberry.type
class FormError:
    field: str
    message: str
    code: str

@strawberry.type
class FormField:
    name: str
    type: str
    label: str
    required: bool
    validation: Optional[str] = None
    options: Optional[List[str]] = None

@strawberry.type
class FormTemplate:
    id: str
    name: str
    type: str
    fields: List[FormField]
    created_at: datetime
    updated_at: datetime

@strawberry.type
class FormSubmission:
    id: str
    template_id: str
    status: str
    data: str
    errors: Optional[List[FormError]]
    created_at: datetime
    updated_at: datetime

@strawberry.type
class FormProgress:
    submission_id: str
    status: str
    progress: float
    message: Optional[str] = None

@strawberry.type
class Query:
    @strawberry.field
    async def form_template(self, info: Info, id: str) -> Optional[FormTemplate]:
        """Get form template by ID"""
        try:
            form_service = FormService(info.context["request"])
            template = await form_service.get_template(id)
            analytics.track_template_view(template.id)
            return template
        except Exception as e:
            logger.error(f"Error fetching form template: {e}")
            return None

    @strawberry.field
    async def form_templates(
        self,
        info: Info,
        type: Optional[str] = None,
        skip: int = 0,
        limit: int = 10
    ) -> List[FormTemplate]:
        """Get form templates"""
        try:
            form_service = FormService(info.context["request"])
            templates = await form_service.get_templates(type, skip, limit)
            analytics.track_template_list(type)
            return templates
        except Exception as e:
            logger.error(f"Error fetching form templates: {e}")
            return []

    @strawberry.field
    async def form_submission(
        self,
        info: Info,
        id: str
    ) -> Optional[FormSubmission]:
        """Get form submission by ID"""
        try:
            form_service = FormService(info.context["request"])
            submission = await form_service.get_submission(id)
            analytics.track_submission_view(submission.id)
            return submission
        except Exception as e:
            logger.error(f"Error fetching form submission: {e}")
            return None

    @strawberry.field
    async def form_submissions(
        self,
        info: Info,
        template_id: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 10
    ) -> List[FormSubmission]:
        """Get form submissions"""
        try:
            form_service = FormService(info.context["request"])
            submissions = await form_service.get_submissions(
                template_id,
                status,
                skip,
                limit
            )
            analytics.track_submission_list(template_id, status)
            return submissions
        except Exception as e:
            logger.error(f"Error fetching form submissions: {e}")
            return []

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_form_template(
        self,
        info: Info,
        name: str,
        type: str,
        fields: List[FormField]
    ) -> FormTemplate:
        """Create new form template"""
        try:
            form_service = FormService(info.context["request"])
            template = await form_service.create_template(name, type, fields)
            analytics.track_template_creation(template.id)
            return template
        except Exception as e:
            logger.error(f"Error creating form template: {e}")
            raise

    @strawberry.mutation
    async def update_form_template(
        self,
        info: Info,
        id: str,
        name: Optional[str] = None,
        fields: Optional[List[FormField]] = None
    ) -> FormTemplate:
        """Update form template"""
        try:
            form_service = FormService(info.context["request"])
            template = await form_service.update_template(id, name, fields)
            analytics.track_template_update(template.id)
            return template
        except Exception as e:
            logger.error(f"Error updating form template: {e}")
            raise

    @strawberry.mutation
    async def submit_form(
        self,
        info: Info,
        template_id: str,
        data: str,
        files: Optional[List[Upload]] = None
    ) -> FormSubmission:
        """Submit form data"""
        try:
            form_service = FormService(info.context["request"])
            submission = await form_service.submit_form(template_id, data, files)
            analytics.track_form_submission(submission.id)
            return submission
        except Exception as e:
            logger.error(f"Error submitting form: {e}")
            raise

    @strawberry.mutation
    async def update_form_submission(
        self,
        info: Info,
        id: str,
        status: str,
        data: Optional[str] = None
    ) -> FormSubmission:
        """Update form submission"""
        try:
            form_service = FormService(info.context["request"])
            submission = await form_service.update_submission(id, status, data)
            analytics.track_submission_update(submission.id)
            return submission
        except Exception as e:
            logger.error(f"Error updating form submission: {e}")
            raise

@strawberry.type
class Subscription:
    @strawberry.subscription
    async def form_progress(
        self,
        info: Info,
        submission_id: str
    ) -> FormProgress:
        """Subscribe to form submission progress"""
        try:
            form_service = FormService(info.context["request"])
            async for progress in form_service.track_progress(submission_id):
                analytics.track_progress_update(submission_id)
                yield FormProgress(
                    submission_id=submission_id,
                    status=progress.status,
                    progress=progress.progress,
                    message=progress.message
                )
        except Exception as e:
            logger.error(f"Error tracking form progress: {e}")
            raise

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription
)

graphql_app = GraphQLRouter(schema)

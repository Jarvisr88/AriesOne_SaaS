"""Submission service module."""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from ..models.submission import Submission, VoidMethod

class SubmissionService:
    """Service for handling submissions."""

    def __init__(self, db: Session):
        """Initialize the submission service."""
        self.db = db

    def create_submission(
        self,
        claim_number: str,
        metadata: Optional[dict] = None
    ) -> Submission:
        """Create a new submission."""
        submission = Submission(
            claim_number=claim_number,
            status='active',
            metadata=metadata
        )
        self.db.add(submission)
        self.db.commit()
        return submission

    def get_submission(self, submission_id: int) -> Optional[Submission]:
        """Get a submission by ID."""
        return self.db.query(Submission).filter(
            Submission.id == submission_id
        ).first()

    def get_submission_by_claim(self, claim_number: str) -> Optional[Submission]:
        """Get a submission by claim number."""
        return self.db.query(Submission).filter(
            Submission.claim_number == claim_number
        ).first()

    def void_submission(
        self,
        submission_id: int,
        void_method: VoidMethod,
        reason: str,
        replacement_id: Optional[int] = None
    ) -> Optional[Submission]:
        """Void a submission."""
        submission = self.get_submission(submission_id)
        if not submission or submission.status != 'active':
            return None

        # If this is a replacement, verify the replacement submission exists
        if void_method == VoidMethod.REPLACEMENT and replacement_id:
            replacement = self.get_submission(replacement_id)
            if not replacement or replacement.status != 'active':
                return None

        # Void the submission
        submission.void(void_method, reason, replacement_id)
        self.db.commit()
        return submission

    def get_active_submissions(self) -> List[Submission]:
        """Get all active submissions."""
        return self.db.query(Submission).filter(
            Submission.status == 'active'
        ).all()

    def get_voided_submissions(self) -> List[Submission]:
        """Get all voided submissions."""
        return self.db.query(Submission).filter(
            Submission.status == 'voided'
        ).all()

    def get_replacement_chain(self, submission_id: int) -> List[Submission]:
        """Get the chain of replacements for a submission."""
        submissions = []
        current = self.get_submission(submission_id)
        
        while current:
            submissions.append(current)
            if not current.replacement:
                break
            current = current.replacement

        return submissions

    def update_submission_metadata(
        self,
        submission_id: int,
        metadata: dict
    ) -> Optional[Submission]:
        """Update submission metadata."""
        submission = self.get_submission(submission_id)
        if not submission:
            return None

        submission.metadata = {
            **(submission.metadata or {}),
            **metadata
        }
        self.db.commit()
        return submission

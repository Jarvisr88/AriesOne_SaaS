from sqlalchemy.orm import Session
from models.cmn_request_search_criteria import CmnRequestSearchCriteria

def save_cmn_request_search_criteria(db: Session, criteria_data: dict):
    cmn_request_search_criteria = CmnRequestSearchCriteria(**criteria_data)
    db.add(cmn_request_search_criteria)
    db.commit()
    db.refresh(cmn_request_search_criteria)
    return cmn_request_search_criteria

from sqlalchemy.orm import Session
from models.cmn_request import CmnRequest

def save_cmn_request(db: Session, request_data: dict):
    cmn_request = CmnRequest(**request_data)
    db.add(cmn_request)
    db.commit()
    db.refresh(cmn_request)
    return cmn_request

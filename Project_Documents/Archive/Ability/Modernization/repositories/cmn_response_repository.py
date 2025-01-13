from sqlalchemy.orm import Session
from models.cmn_response import CmnResponse

def save_cmn_response(db: Session, response_data: dict):
    cmn_response = CmnResponse(**response_data)
    db.add(cmn_response)
    db.commit()
    db.refresh(cmn_response)
    return cmn_response

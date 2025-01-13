from sqlalchemy.orm import Session
from models.cmn_response_entry import CmnResponseEntry

def save_cmn_response_entry(db: Session, entry_data: dict):
    cmn_response_entry = CmnResponseEntry(**entry_data)
    db.add(cmn_response_entry)
    db.commit()
    db.refresh(cmn_response_entry)
    return cmn_response_entry

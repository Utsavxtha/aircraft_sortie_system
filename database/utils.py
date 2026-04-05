from database.connection import get_session, reset_session

def safe_delete(model_class, pk_field, pk_value):
    """Safely delete a record, resetting session on failure."""
    session = get_session()
    try:
        obj = session.query(model_class).filter(
            getattr(model_class, pk_field) == pk_value
        ).first()
        if obj is None:
            return False, "Record not found."
        session.delete(obj)
        session.commit()
        return True, "Deleted."
    except Exception as e:
        session.rollback()
        reset_session()
        return False, str(e)
import logging

logger = logging.getLogger(__name__)


def logInfo(p_message):
    logger.info(p_message)


def logError(p_message):
    logger.error(p_message)


def logDetail(p_log_id, p_message):
    v_message = f"[{p_log_id}] {p_message}"
    return {"id_log": p_log_id, "message": v_message}


def logGenerate(p_module):
    import uuid
    return f"{p_module}-{uuid.uuid4().hex[:8].upper()}"

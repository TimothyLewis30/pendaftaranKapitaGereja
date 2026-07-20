def removeEscapeCharacters(p_results):
    if isinstance(p_results, str):
        return p_results.replace('\\', '')
    elif isinstance(p_results, dict):
        return {k: removeEscapeCharacters(v) for k, v in p_results.items()}
    elif isinstance(p_results, list):
        return [removeEscapeCharacters(item) for item in p_results]
    return p_results


def responseJson(p_code, p_flag, p_message, p_results):
    return {
        "code": p_code,
        "status": p_flag,
        "message": p_message,
        "results": removeEscapeCharacters(p_results),
    }

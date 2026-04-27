# Response utilities
def format_response(data, message="Success"):
    return {"status": "success", "message": message, "data": data}


def add_parsed_ua(request):
    if hasattr(request, "parsed_ua"):
        return {"parsed_ua": request.parsed_ua}
    return {}

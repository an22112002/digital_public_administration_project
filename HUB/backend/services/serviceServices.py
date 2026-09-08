from backend.crud.servicesCrud import get_all_services, get_categories, get_services, set_service_active

def getAllServices():
    data = get_all_services()
    for row in data:
        row["serviceID"] = str(row["serviceID"])
    return data

def getServiceList(category: str | None = None, title: str | None = None):
    data = get_services(category=category, title=title)
    for row in data:
        row["serviceID"] = str(row["serviceID"])
    return data

def getCategories():
    return get_categories()

def setServiceActive(service_id: int, active: bool):
    return set_service_active(service_id, active)
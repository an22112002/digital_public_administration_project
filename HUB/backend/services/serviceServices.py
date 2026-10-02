from backend.crud.servicesCrud import get_all_services, get_categories, get_services, set_service_active,set_service_allow_mutil_push

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

def setServiceAllowMutilPush(service_id: int, action: bool):
    return set_service_allow_mutil_push(service_id, action)
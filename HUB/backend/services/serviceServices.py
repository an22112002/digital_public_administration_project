from database.index import db
from backend.crud.servicesCrud import get_active_services, get_categories

def getActiveServices():
    data = get_active_services()
    for row in data:
        row["serviceID"] = str(row["serviceID"])
    return data

def getCategories():
    return get_categories()
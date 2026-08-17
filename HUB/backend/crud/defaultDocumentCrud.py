from backend.models.serviceModels import DefaultDocumentImport

def insert_default_documents(
    cursor,
    documents: list[DefaultDocumentImport]
) -> None:
    """
    Insert danh sách default documents vào database.
    """

    if not documents:
        return

    sql = """
        INSERT INTO default_documents (
            serviceID,
            name,
            description,
            required,
            OCRtab
        )
        VALUES (
            %s, %s, %s, %s, %s
        )
    """

    values = [
        (
            document.serviceID,
            document.name,
            document.description,
            document.required,
            document.OCRtab
        )
        for document in documents
    ]

    cursor.executemany(sql, values)


def delete_all_default_documents(cursor) -> None:
    """
    Xóa toàn bộ dữ liệu trong bảng default_documents.
    """

    cursor.execute("""
        DELETE FROM default_documents
    """)
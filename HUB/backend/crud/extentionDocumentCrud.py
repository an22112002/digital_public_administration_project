from backend.models.serviceModels import ExtentionDocumentImport

def insert_extention_documents(
    cursor,
    documents: list[ExtentionDocumentImport]
) -> None:
    """
    Insert danh sách extention documents vào database.
    """

    if not documents:
        return

    sql = """
        INSERT INTO extention_documents (
            name,
            description,
            OCRtab
        )
        VALUES (
            %s, %s, %s
        )
    """

    values = [
        (
            document.name,
            document.description,
            document.OCRtab
        )
        for document in documents
    ]

    cursor.executemany(sql, values)


def delete_all_extention_documents(cursor) -> None:
    """
    Xóa toàn bộ dữ liệu trong bảng extention_documents.
    """

    cursor.execute("""
        DELETE FROM extention_documents
    """)

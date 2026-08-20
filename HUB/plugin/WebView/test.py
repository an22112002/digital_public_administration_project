from main import process_with_webview, DataProcess
import asyncio

async def main():
    url = "https://dichvucong.gov.vn/tim-kiem-thu-tuc-hanh-chinh?formalityId=019d2bfd-95fa-70ca-93fd-4cab11b87897&formalityCaseId=019db06b-1e13-773f-bd01-af4904294075"
    
    province = "Thành phố Hà Nội"
    commune = "Phường Ba Đình"

    data_auto_pass = {
        "province": province,
        "commune": commune,
        "button_send_documents_position": 1
    }

    paper_input = [
        {
            "name": "Bản chính hoặc bản sao có chứng thực hoặc bản sao điện tử được chứng thực từ bản chính của giấy chứng nhận quyền sở hữu, quyền sử dụng hoặc giấy tờ thay thế được pháp luật quy định đối với tài sản mà pháp luật quy định phải đăng ký quyền sở hữu, quyền sử dụng trong trường hợp giao dịch liên quan đến tài sản đó; trừ trường hợp người lập di chúc đang bị cái chết đe dọa đến tính mạng. Trường hợp nộp hồ sơ trực tiếp, người yêu cầu chứng thực có thể nộp bản sao kèm xuất trình bản chính để đối chiếu.",
            "file": r"D:\test\test.pdf"
        },
        {
            "name": "Dự thảo giao dịch",
            "file": r"D:\test\test2.pdf"
        },
        {
            "name": "CCCD",
            "file": r"D:\test\test3.pdf"
        },
    ]

    data_process = [
        DataProcess(task_name="auto_pass_select_service", data=data_auto_pass),
        DataProcess(task_name="insert_file_table", data=paper_input)
    ]
    asyncio.create_task(
        asyncio.to_thread(process_with_webview, url, data_process)
    )

if __name__ == "__main__":
    
    asyncio.run(main())
    print("gg")
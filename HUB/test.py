import asyncio

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn

from plugin.WebView.main import process_with_webview, DataProcess


app = FastAPI()


@app.websocket("/test-webview")
async def test_webview(websocket: WebSocket):
    await websocket.accept()

    print("[WS] connected")

    try:
        # =========================
        # Giả lập dữ liệu backend chuẩn bị
        # =========================

        url = (
            "https://dichvucong.gov.vn/"
            "tim-kiem-thu-tuc-hanh-chinh"
            "?formalityId=019d2bfd-95fa-70ca-93fd-4cab11b87897"
            "&formalityCaseId=019db06b-1e13-773f-bd01-af4904294075"
        )

        province = "Thành phố Hà Nội"
        commune = "Phường Ba Đình"

        data_auto_pass = {
            "province": province,
            "commune": commune,
            "button_send_documents_position": 1
        }

        paper_input = [
            {
                "name": "Giấy tờ 1",
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
            DataProcess(
                task_name="auto_pass_select_service",
                data=data_auto_pass
            ),
            DataProcess(
                task_name="insert_file_table",
                data=paper_input
            )
        ]

        # =========================
        # Báo client
        # =========================

        await websocket.send_json({
            "type": "webview",
            "status": "preparing"
        })

        print("[WS] starting webview")

        # =========================
        # Start WebView
        # =========================

        await asyncio.to_thread(
            process_with_webview,
            url,
            data_process
        )

        print("[WS] webview closed")

        await websocket.send_json({
            "type": "webview",
            "status": "closed"
        })

        # Giữ websocket sống để test tiếp
        while True:
            data = await websocket.receive_json()

            print("[WS] received:", data)

            if data.get("type") == "close":
                break

    except WebSocketDisconnect:
        print("[WS] client disconnected")

    except Exception as e:
        print("[WS] error:", e)

        try:
            await websocket.send_json({
                "type": "webview",
                "status": "error",
                "message": str(e)
            })
        except Exception:
            pass


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8001
    )
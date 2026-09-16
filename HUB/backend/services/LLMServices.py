import requests
import subprocess
from backend.config import open_settings
from backend.utils import image_to_base64

async def getLMStudioModels() -> list:
    """
    Lấy danh sách các mô hình LLM có sẵn từ LM Studio server.
    Returns:
        list: Danh sách các mô hình LLM có sẵn.
    """
    server_ip = "localhost"

    try:
        response = requests.get(f"http://{server_ip}:1234/api/v1/models", timeout=5)
        response.raise_for_status()  # Kiểm tra xem có lỗi HTTP không
        models = response.json().get("models", [])
        result = []
        for model in models:
            result.append(model.get("key", "Unknown"))
        return result
    except requests.RequestException as e:
        print(f"[LM Studio] Error occurred while fetching models: {e}")
        return []

async def checkLMStudioServerRunning(server_ip: str) -> bool:
    """
    Kiểm tra xem LM Studio server có đang chạy hay không.
    """
    request_url = f"http://{server_ip}:1234/api/v1/models"
    try:
        response = requests.get(request_url, timeout=5)
        if response.status_code == 200:
            return True
        else:
            print(f"[LM Studio] Server responded with status code: {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"[LM Studio] Error occurred while checking server: {e}")
        return False

async def loadLocalLMStudioModel():
    """
    CLI load local LM Studio model.
    """
    try:
        settings = await open_settings()
        llm_model = settings["settings"].get("LLM_model", "qwen3-vl-2b-instruct")
        gpu_use = settings["settings"].get("LLM_gpu_use", 1.0)
        context_length = settings["settings"].get("LLM_context_length", 8192)
        subprocess.run(
            ["lms", "load", llm_model, f"--gpu={gpu_use}", f"--context-length={context_length}"],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"[LM Studio] Error occurred while loading model: {e}")
        raise

async def unloadLocalLMStudioModel():
    """
    CLI unload local LM Studio model.
    """
    try:
        settings = await open_settings()
        llm_model = settings["settings"].get("LLM_model", "qwen3-vl-2b-instruct")
        subprocess.run(
            ["lms", "unload", llm_model],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"[LM Studio] Error occurred while unloading model: {e}")
        raise

async def runPromptInLMStudio(prompt: str, images: list, server_ip: str) -> str:
    """
    Gửi prompt đến LM Studio server và nhận phản hồi.
    """

    # Chuyển đổi hình ảnh sang base64
    images_data = []
    for image in images:
        data = image_to_base64(image, max_size=1600)
        images_data.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": "data:image/jpeg;base64," + data
                }
            }
        )
    # Gửi prompt và hình ảnh đến LM Studio server
    content = {
        "role": "user",
        "content": [{
            "type": "text",
            "text": prompt
        }]
    }
    if images_data:
        content["content"].extend(images_data)

    try:
        response = requests.post(
            f"http://{server_ip}:1234/v1/chat/completions",
            json={
                "model": "local-model",
                "messages": [content],
                "temperature": 0,
                "max_tokens": 512,
            },
            timeout=300,
        )

        response.raise_for_status()

        data = response.json()

        return data["choices"][0]["message"]["content"]
    except requests.RequestException as e:
        print(f"[LM Studio] Error occurred while sending prompt: {e}")
        raise
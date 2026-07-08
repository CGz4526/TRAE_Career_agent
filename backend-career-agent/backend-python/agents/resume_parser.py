"""简历解析 Agent —— 支持图片(PDF/PNG/JPG等)格式的简历OCR提取"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import io
import base64
from typing import Optional, Tuple
from PIL import Image
import pdfplumber
import fitz  # pymupdf
import httpx
from config import settings


def get_vision_model_name() -> str:
    """获取视觉 LLM 模型名称"""
    vision_model = os.getenv("LLM_VISION_MODEL", "")
    base_url = settings.llm_base_url

    if "deepseek" in base_url.lower():
        return vision_model or "deepseek-vl2"
    elif "ark" in base_url.lower() or "doubao" in base_url.lower():
        return vision_model or "doubao-vision-pro-32k"
    else:
        return vision_model or settings.llm_model


def extract_text_from_pdf(pdf_bytes: bytes) -> Tuple[str, bool]:
    """
    尝试从 PDF 中直接提取文字
    返回: (提取到的文字, 是否提取到足够内容)
    """
    try:
        print(f"开始提取 PDF 文字，文件大小: {len(pdf_bytes)} bytes")
        text_parts = []
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            print(f"PDF 页数: {len(pdf.pages)}")
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text_parts.append(t)
                    print(f"第 {page.page_number} 页提取到 {len(t)} 个字符")
        text = "\n".join(text_parts).strip()
        print(f"PDF 提取完成，总字符数: {len(text)}")
        return text, len(text) > 200
    except Exception as e:
        print(f"PDF 文字提取失败: {e}")
        return "", False


def pdf_to_images(pdf_bytes: bytes, max_pages: int = 5) -> list:
    """将 PDF 转为图片列表（用于扫描版 PDF 的 OCR）"""
    images = []
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        total = min(len(doc), max_pages)
        for i in range(total):
            page = doc[i]
            mat = fitz.Matrix(2, 2)  # 2x 缩放提高清晰度
            pix = page.get_pixmap(matrix=mat)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            images.append(buf.getvalue())
        doc.close()
    except Exception as e:
        print(f"PDF 转图片失败: {e}")
    return images


def image_to_base64(image_bytes: bytes) -> str:
    """图片转 base64"""
    return base64.b64encode(image_bytes).decode("utf-8")


async def ocr_image(image_bytes: bytes, mime_type: str = "image/png", prompt: str = "") -> str:
    """用视觉 LLM 对单张图片做 OCR（直接使用 httpx 调用 API）"""
    import json
    
    b64 = image_to_base64(image_bytes)
    model = get_vision_model_name()

    default_prompt = """请仔细识别这张简历图片中的所有文字内容，完整提取出来。

要求：
1. 准确识别所有文字，包括姓名、联系方式、教育背景、工作经历、项目经历、技能等
2. 保持原有的层级结构和段落顺序
3. 用清晰的 Markdown 格式输出（标题用 ##、列表用 - 等）
4. 不要遗漏任何内容
5. 不要添加额外的解释或说明，只输出识别到的简历内容本身"""

    headers = {
        "Authorization": f"Bearer {settings.llm_api_key}",
        "Content-Type": "application/json",
    }

    # 尝试多种端点和格式的组合
    endpoints_and_formats = [
        # 端点1: /v1/chat/completions + type: image_url
        ("/v1/chat/completions", {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt or default_prompt},
                        {"type": "image_url", "image_url": f"data:{mime_type};base64,{b64}"},
                    ],
                }
            ],
            "max_tokens": 4096,
            "temperature": 0.1,
        }),
        # 端点2: /chat/completions + type: image_url
        ("/chat/completions", {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt or default_prompt},
                        {"type": "image_url", "image_url": f"data:{mime_type};base64,{b64}"},
                    ],
                }
            ],
            "max_tokens": 4096,
            "temperature": 0.1,
        }),
        # 端点3: /v1/chat/completions + type: image (不是 image_url)
        ("/v1/chat/completions", {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt or default_prompt},
                        {"type": "image", "image": f"data:{mime_type};base64,{b64}"},
                    ],
                }
            ],
            "max_tokens": 4096,
            "temperature": 0.1,
        }),
    ]

    last_error = None
    for endpoint, payload in endpoints_and_formats:
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{settings.llm_base_url}{endpoint}",
                    json=payload,
                    headers=headers,
                )
                
                print(f"端点: {endpoint}, 状态码: {response.status_code}")
                print(f"响应: {response.text[:300]}")
                
                if response.status_code != 200:
                    last_error = f"{endpoint}: {response.status_code} - {response.text[:200]}"
                    continue
                
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            last_error = f"{endpoint}: {str(e)}"
            print(f"异常: {last_error}")
            continue

    raise Exception(f"所有格式都失败，最后错误: {last_error}")


async def ocr_jd_image(image_bytes: bytes, mime_type: str = "image/png") -> str:
    """用视觉 LLM 对岗位 JD 图片做 OCR 识别"""
    jd_prompt = """请仔细识别这张岗位招聘图片中的所有文字内容，完整提取出来。

要求：
1. 准确识别所有文字，包括岗位名称、岗位职责、任职要求、薪资福利、公司信息等
2. 保持原有的层级结构和段落顺序
3. 用清晰的 Markdown 格式输出（标题用 ##、列表用 - 等）
4. 不要遗漏任何内容
5. 不要添加额外的解释或说明，只输出识别到的招聘内容本身"""
    return await ocr_image(image_bytes, mime_type, jd_prompt)


def detect_file_type(filename: str, content: bytes) -> str:
    """检测文件类型：pdf / image"""
    name_lower = filename.lower()
    if name_lower.endswith(".pdf"):
        return "pdf"
    if name_lower.endswith((".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tiff")):
        return "image"
    # 通过文件头判断
    if content[:4] == b"%PDF":
        return "pdf"
    if content[:8] == b"\x89PNG\r\n\x1a\n":
        return "image"
    if content[:2] == b"\xff\xd8":
        return "image"
    return "unknown"


async def parse_resume_file(filename: str, content: bytes) -> dict:
    """
    解析简历文件（支持 PDF 和图片）

    Args:
        filename: 文件名
        content: 文件二进制内容

    Returns:
        dict: { text: 提取的简历文本, method: 解析方法(pdf_text/ocr/error), pages: 页数 }
    """
    print(f"\n=== 开始解析文件: {filename} ===")
    file_type = detect_file_type(filename, content)
    print(f"检测到文件类型: {file_type}")

    if file_type == "pdf":
        # 先尝试直接提取文字
        text, has_enough = extract_text_from_pdf(content)
        if has_enough:
            print(f"PDF 文字提取成功，使用 pdf_text 方法")
            return {
                "text": text,
                "method": "pdf_text",
                "pages": _count_pdf_pages(content),
            }
        
        # 文字版提取失败
        print(f"PDF 文字提取失败或内容不足，尝试 OCR...")
        images = pdf_to_images(content)
        if not images:
            return {"text": "", "method": "error", "pages": 0, "error": "无法解析 PDF 文件（可能是扫描版且当前 OCR 服务不可用）"}

        all_text = []
        for i, img_bytes in enumerate(images):
            try:
                print(f"正在 OCR 第 {i+1} 页...")
                page_text = await ocr_image(img_bytes, "image/png")
                all_text.append(f"--- 第 {i+1} 页 ---\n{page_text}")
            except Exception as e:
                print(f"OCR 失败: {e}")
                return {
                    "text": "",
                    "method": "error",
                    "pages": len(images),
                    "error": f"PDF OCR 识别失败：{str(e)}。当前视觉模型可能不支持图片识别，请确保 LLM_VISION_MODEL 配置正确。"
                }

        return {
            "text": "\n\n".join(all_text),
            "method": "ocr",
            "pages": len(images),
        }

    elif file_type == "image":
        # 图片直接 OCR
        print(f"开始图片 OCR...")
        ext = os.path.splitext(filename)[1].lower().lstrip(".")
        mime = f"image/{'jpeg' if ext == 'jpg' else ext}"
        try:
            text = await ocr_image(content, mime)
            print(f"图片 OCR 成功")
            return {
                "text": text,
                "method": "ocr",
                "pages": 1,
            }
        except Exception as e:
            print(f"图片 OCR 失败: {e}")
            return {
                "text": "",
                "method": "error",
                "pages": 1,
                "error": f"图片 OCR 识别失败：{str(e)}。当前视觉模型可能不支持图片识别，请确保 LLM_VISION_MODEL 配置正确。"
            }

    else:
        return {
            "text": "",
            "method": "error",
            "pages": 0,
            "error": f"不支持的文件类型: {filename}",
        }


def _count_pdf_pages(pdf_bytes: bytes) -> int:
    """统计 PDF 页数"""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        n = len(doc)
        doc.close()
        return n
    except:
        return 0

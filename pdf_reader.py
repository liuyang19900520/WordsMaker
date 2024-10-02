import fitz  # PyMuPDF
import base64
import requests
import json
from dotenv import load_dotenv
import os


load_dotenv()  # 加载 .env 文件
api_key = os.getenv('GOOGLE_API_KEY')  # 从 .env 文件获取 API 密钥
url = 'https://vision.googleapis.com/v1/images:annotate?key={}'.format(api_key)



def extract_images_from_pdf(pdf_path, start_page, end_page):
  doc = fitz.open(pdf_path)
  images = []
  for page_num in range(start_page - 1, end_page):
    page = doc.load_page(page_num)
    pix = page.get_pixmap()
    img_bytes = pix.tobytes("png")
    images.append(img_bytes)
  return images


def detect_text_with_api_key(image_bytes, api_key):
  """
  使用API密钥通过Google Cloud Vision API识别图像中的文本。

  :param image_bytes: 图像的字节数据。
  :param api_key: Google Cloud Vision API的API密钥。
  """
  url = 'https://vision.googleapis.com/v1/images:annotate?key={}'.format(api_key)
  encoded_image = base64.b64encode(image_bytes).decode('utf-8')
  payload = {
    "requests": [
      {
        "image": {
          "content": encoded_image
        },
        "features": [
          {
            "type": "TEXT_DETECTION"
          }
        ]
      }
    ]
  }
  headers = {'Content-Type': 'application/json'}
  response = requests.post(url, headers=headers, data=json.dumps(payload))
  result = response.json()

  # 检查是否有错误字段
  if 'error' in result:
    error_message = result['error']['message']
    print(f"Error: {error_message}")
    return None

  if 'responses' in result:
    for response in result['responses']:
      if 'textAnnotations' in response:
        # 第一个textAnnotations包含了整页的文本
        text_annotation = response['textAnnotations'][0]
      else:
        print("No text found.")
  else:
    print("Error in API response.")

  # 解析和打印结果
  texts = []
  if 'responses' in result and len(result['responses']) > 0:
    if 'textAnnotations' in result['responses'][0]:
      for annotation in result['responses'][0]['textAnnotations']:
        texts.append(annotation['description'])
  return texts

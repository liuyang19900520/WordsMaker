# 文件名：main.py
from pdf_reader import extract_images_from_pdf, detect_text_with_api_key
from words_collector import tokenize

from dotenv import load_dotenv
import os

load_dotenv()  # 加载 .env 文件
api_key = os.getenv('GOOGLE_API_KEY')  # 从 .env 文件获取 API 密钥

pdf_path = 'reading1000.pdf'  # 替换为你的PDF文件路径
output_path = 'test'

oulu_csv_path = 'oululist.csv'

pageTexts = []
images = extract_images_from_pdf(pdf_path, 131, 131)
for image_bytes in images:
  texts = detect_text_with_api_key(image_bytes, api_key)
  pageTextStr = ' '.join(texts)
  pageTexts.append(pageTextStr)
tokenize(' '.join(pageTexts), oulu_csv_path, output_path)




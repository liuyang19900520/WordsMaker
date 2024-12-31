# 文件名：main.py
from pdf_reader import extract_images_from_pdf, detect_text_with_api_key
from words_collector import tokenize
from dotenv import load_dotenv
import os

load_dotenv()  # 加载 .env 文件
api_key = os.getenv('GOOGLE_API_KEY')  # 从 .env 文件获取 API 密钥

# 需要检测的PDF文件，抽出扫描的单词
pdf_path = '19day.pdf'

pageTexts = []
images = extract_images_from_pdf(pdf_path, 1, 15)
for image_bytes in images:
  texts = detect_text_with_api_key(image_bytes, api_key)
  pageTextStr = ' '.join(texts)
  pageTexts.append(pageTextStr)

print("PDF文件单词扫描完成")

# 进行分词，分析
tokenize(' '.join(pageTexts))

from PyPDF2 import PdfReader, PdfWriter

def extract_pages(start_page, end_page, input_pdf, output_pdf):
    # 从1开始计数，转换为PyPDF2的0基索引
    start_page -= 1

    pdf_reader = PdfReader(input_pdf)
    pdf_writer = PdfWriter()

    # 提取特定的页面
    for page_num in range(start_page, min(end_page, len(pdf_reader.pages))):
        page = pdf_reader.pages[page_num]
        pdf_writer.add_page(page)

    # 写入到一个新的PDF文件
    with open(output_pdf, 'wb') as out:
        pdf_writer.write(out)

# 调用函数：提取第1页到第10页
extract_pages(64, 105, 'Japanese.pdf', 'paper2.pdf')

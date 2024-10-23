import time
import requests
import psycopg2

conn = psycopg2.connect(
  host="172.16.33.33",  # PostgreSQL服务器地址，例如"localhost"
  database="words",  # 数据库名称
  user="postgres",  # 数据库用户名
  password="postgres"  # 数据库密码
)

# 定义变量并将它们放入字典
category_dict = {
  "1": "0",
  "2": "133557195427064351",
  "3": "1721222268",
  "4": "1726467371"
}

# 创建游标对象
cur = conn.cursor()

cur.execute("TRUNCATE TABLE oulu")
conn.commit()  # 提交事务
def parse_cookie_string(cookie_string):
  # 使用 "; " 分隔每个 cookie 项
  cookies = cookie_string.split("; ")

  # 创建一个空字典来存储 cookie
  cookie_dict = {}

  # 遍历每个 cookie，将其拆分为键值对
  for cookie in cookies:
    # 分割键和值
    key, value = cookie.split("=", 1)  # 仅拆分第一个 "="，防止值中包含 "=" 时出错
    cookie_dict[key] = value

  return cookie_dict


# 测试数据
cookie_string = "_ga=GA1.1.794527447.1711241930; __utma=131758875.1355860809.1711238181.1711238181.1711238181.1; __utmz=131758875.1711238181.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); .AspNetCore.Session=CfDJ8K06SDLLKs1FpKlpqTRecpJyj0Vo%2Bslu51Lgn%2FpWVh4IJi1ozj%2BsGO1Farv5tP8FgomUdmSJDgJI2kxAVMcjHzAU6r%2FGQp5Jne2iidEkjDRayDukywfviXN9LmNND4cIzr0PZP6%2BwnuSSuiCpKC6Zn5BvuLfEOq%2BoKe3om%2F%2Fp9%2Fa; col_index=6; col_sort=desc; EudicWebSession=QYNeyJoYXNfb2xkX3Bhc3N3b3JkIjpmYWxzZSwidG9rZW4iOiJIMXlhaStBbVFFT2xjamdCbTBaQUIwaWhEcUk9IiwiZXhwaXJlaW4iOjEzMTQwMDAsInVzZXJpZCI6ImJkNWRjODJhLWJjMTYtMTFlZS1iYjNiLTAwNTA1Njg2OWFmNiIsInVzZXJuYW1lIjoi5YiY5rSLX3RWUzBJcTdaVEFGVCIsImNyZWF0aW9uX2RhdGUiOiIyMDI0LTAxLTI1VDIyOjQ3OjIyWiIsInJvbGVzIjpudWxsLCJvcGVuaWRfdHlwZSI6bnVsbCwib3BlbmlkX2Rlc2MiOm51bGwsInByb2ZpbGUiOnsibmlja25hbWUiOiLliJjmtIsiLCJlbWFpbCI6IiIsImdlbmRlciI6IuWlsyIsInBhc3N3b3JkIjpudWxsLCJ2b2NhYnVsYXJpZXMiOnsiZW4iOjYwNjl9fSwibGFzdF9wYXNzd29yZF9jaGFuZ2VkX2RhdGUiOiIxLzI2LzIwMjQgNjo0NzoyMiBBTSIsInJlZGlyZWN0X3VybCI6bnVsbH0%253d; _ga_6J9FB2R7F4=GS1.1.1727955588.6.1.1727955654.0.0.0"

# 使用函数解析cookie字符串
cookies = parse_cookie_string(cookie_string)
print(cookies)

# 原始URL的模板
url_template = "https://my.eudic.net/StudyList/WordsDataSource?=9&draw={draw}&columns%5B0%5D%5Bdata%5D=id&columns%5B0%5D%5Bname%5D=&columns%5B0%5D%5Bsearchable%5D=false&columns%5B0%5D%5Borderable%5D=false&columns%5B0%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B0%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B1%5D%5Bdata%5D=id&columns%5B1%5D%5Bname%5D=&columns%5B1%5D%5Bsearchable%5D=true&columns%5B1%5D%5Borderable%5D=false&columns%5B1%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B1%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B2%5D%5Bdata%5D=word&columns%5B2%5D%5Bname%5D=&columns%5B2%5D%5Bsearchable%5D=false&columns%5B2%5D%5Borderable%5D=true&columns%5B2%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B2%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B3%5D%5Bdata%5D=phon&columns%5B3%5D%5Bname%5D=&columns%5B3%5D%5Bsearchable%5D=true&columns%5B3%5D%5Borderable%5D=false&columns%5B3%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B3%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B4%5D%5Bdata%5D=exp&columns%5B4%5D%5Bname%5D=&columns%5B4%5D%5Bsearchable%5D=true&columns%5B4%5D%5Borderable%5D=false&columns%5B4%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B4%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B5%5D%5Bdata%5D=rating&columns%5B5%5D%5Bname%5D=&columns%5B5%5D%5Bsearchable%5D=false&columns%5B5%5D%5Borderable%5D=true&columns%5B5%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B5%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B6%5D%5Bdata%5D=addtime&columns%5B6%5D%5Bname%5D=&columns%5B6%5D%5Bsearchable%5D=false&columns%5B6%5D%5Borderable%5D=false&columns%5B6%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B6%5D%5Bsearch%5D%5Bregex%5D=false&order%5B0%5D%5Bcolumn%5D=6&order%5B0%5D%5Bdir%5D=desc&start={start}&length={length}&search%5Bvalue%5D=&search%5Bregex%5D=false&categoryid={category}&_=1727961507363"

# 使用 format() 方法替换 start 和 length
headers = {
  "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
  # 从浏览器复制的User-Agent
}

# 替换URL中的start和length
url = url_template.format(draw=1, start=0, length=1, category=-1)
# 发送请求
response = requests.get(url, headers=headers, cookies=cookies)
resp = response.json()
total_data = resp['recordsTotal']




# 循环通过key来调用值并打印
for key, value in category_dict.items():
  start = 0
  length = 500
  url = url_template.format(draw=1, start=start, length=length, category=value)
  response = requests.get(url, headers=headers, cookies=cookies)
  resp = response.json()
  total_data = resp['recordsTotal']

  # 计算总调用次数
  total_requests = total_data // length + (1 if total_data % length != 0 else 0)

  # 循环请求，每次获取 length 条数据
  for i in range(total_requests):
    # 设置start参数
    start = i * length
    draw = 2 + i
    # 替换URL中的start和length
    url = url_template.format(draw=draw, start=start, length=length, category=value)
    # 发送请求
    response = requests.get(url, headers=headers, cookies=cookies)

    # 输出响应内容或处理数据
    data = response.json()  # 假设返回JSON数据
    print(f"第 {i + 1} 次请求, 请求数据从 {start} 开始，共获取 {length} 条数据")
    # 从返回的数据中提取所需字段
    extracted_data = [
      {
        'uuid': item['uuid'],
        'exp': item['exp'],
        'rating': item['rating'],
        'addtime': item['addtime']
      }
      for item in data['data']
    ]

    # 将 extracted_data 转换为适合插入的元组列表
    records_to_insert = [(item['uuid'], item['exp'], item['rating'], item['addtime'], key) for item in extracted_data]

    # 插入数据到PostgreSQL表中，使用executemany进行批量插入
    cur.executemany("""
        INSERT INTO oulu (word, exp, rating, addTime,category)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (word)
        DO NOTHING
    """, records_to_insert)

    # 提交事务
    conn.commit()

    # 等待2秒再发起下一次请求
    time.sleep(2)

# 提交更改并关闭连接
cur.close()
conn.close()
response.close()

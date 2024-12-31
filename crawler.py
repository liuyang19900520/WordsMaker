# 文件名：fetch_and_insert.py

import time
import requests
import psycopg2


# 解析Cookie字符串的函数
def parse_cookie_string(cookie_string):
  cookies = cookie_string.split("; ")
  cookie_dict = {}
  for cookie in cookies:
    key, value = cookie.split("=", 1)
    cookie_dict[key] = value
  return cookie_dict


# 主函数，处理请求和插入
def fetch_and_insert_data():
  # 连接数据库
  conn = psycopg2.connect(
    host="172.16.33.33",
    database="words",
    user="postgres",
    password="postgres"
  )

  # 定义变量并将它们放入字典
  category_dict = {
    "1": "0",
    "2": "133557195427064351",
    "3": "1721222268",
    "4": "1726467371",
    "5": "133801326811757890",
    "6": "133801326642859934",
  }

  # 创建游标对象
  cur = conn.cursor()

  # 清空表
  cur.execute("TRUNCATE TABLE oulu")
  conn.commit()

  # Cookie字符串
  cookie_string = "_ga=GA1.1.794527447.1711241930; __utma=131758875.1355860809.1711238181.1711238181.1711238181.1; __utmz=131758875.1711238181.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); .AspNetCore.Session=CfDJ8K06SDLLKs1FpKlpqTRecpJyj0Vo%2Bslu51Lgn%2FpWVh4IJi1ozj%2BsGO1Farv5tP8FgomUdmSJDgJI2kxAVMcjHzAU6r%2FGQp5Jne2iidEkjDRayDukywfviXN9LmNND4cIzr0PZP6%2BwnuSSuiCpKC6Zn5BvuLfEOq%2BoKe3om%2F%2Fp9%2Fa; col_index=6; col_sort=desc; EudicWebSession=QYNeyJoYXNfb2xkX3Bhc3N3b3JkIjpmYWxzZSwidG9rZW4iOiJIMXlhaStBbVFFT2xjamdCbTBaQUIwaWhEcUk9IiwiZXhwaXJlaW4iOjEzMTQwMDAsInVzZXJpZCI6ImJkNWRjODJhLWJjMTYtMTFlZS1iYjNiLTAwNTA1Njg2OWFmNiIsInVzZXJuYW1lIjoi5YiY5rSLX3RWUzBJcTdaVEFGVCIsImNyZWF0aW9uX2RhdGUiOiIyMDI0LTAxLTI1VDIyOjQ3OjIyWiIsInJvbGVzIjpudWxsLCJvcGVuaWRfdHlwZSI6bnVsbCwib3BlbmlkX2Rlc2MiOm51bGwsInByb2ZpbGUiOnsibmlja25hbWUiOiLliJjmtIsiLCJlbWFpbCI6IiIsImdlbmRlciI6IuWlsyIsInBhc3N3b3JkIjpudWxsLCJ2b2NhYnVsYXJpZXMiOnsiZW4iOjYwNjl9fSwibGFzdF9wYXNzd29yZF9jaGFuZ2VkX2RhdGUiOiIxLzI2LzIwMjQgNjo0NzoyMiBBTSIsInJlZGlyZWN0X3VybCI6bnVsbH0%253d; _ga_6J9FB2R7F4=GS1.1.1727955588.6.1.1727955654.0.0.0"
  cookies = parse_cookie_string(cookie_string)

  # 请求头
  headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
  }

  # URL模板
  url_template = "https://my.eudic.net/StudyList/WordsDataSource?=9&draw={draw}&columns%5B0%5D%5Bdata%5D=id&columns%5B0%5D%5Bname%5D=&columns%5B0%5D%5Bsearchable%5D=false&columns%5B0%5D%5Borderable%5D=false&columns%5B0%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B0%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B1%5D%5Bdata%5D=id&columns%5B1%5D%5Bname%5D=&columns%5B1%5D%5Bsearchable%5D=true&columns%5B1%5D%5Borderable%5D=false&columns%5B1%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B1%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B2%5D%5Bdata%5D=word&columns%5B2%5D%5Bname%5D=&columns%5B2%5D%5Bsearchable%5D=false&columns%5B2%5D%5Borderable%5D=true&columns%5B2%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B2%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B3%5D%5Bdata%5D=phon&columns%5B3%5D%5Bname%5D=&columns%5B3%5D%5Bsearchable%5D=true&columns%5B3%5D%5Borderable%5D=false&columns%5B3%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B3%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B4%5D%5Bdata%5D=exp&columns%5B4%5D%5Bname%5D=&columns%5B4%5D%5Bsearchable%5D=true&columns%5B4%5D%5Borderable%5D=false&columns%5B4%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B4%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B5%5D%5Bdata%5D=rating&columns%5B5%5D%5Bname%5D=&columns%5B5%5D%5Bsearchable%5D=false&columns%5B5%5D%5Borderable%5D=true&columns%5B5%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B5%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B6%5D%5Bdata%5D=addtime&columns%5B6%5D%5Bname%5D=&columns%5B6%5D%5Bsearchable%5D=false&columns%5B6%5D%5Borderable%5D=false&columns%5B6%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B6%5D%5Bsearch%5D%5Bregex%5D=false&order%5B0%5D%5Bcolumn%5D=6&order%5B0%5D%5Bdir%5D=desc&start={start}&length={length}&search%5Bvalue%5D=&search%5Bregex%5D=false&categoryid={category}&_=1727961507363"

  print("爬虫开始")
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

    # 循环请求数据
    for i in range(total_requests):
      start = i * length
      draw = 2 + i
      url = url_template.format(draw=draw, start=start, length=length, category=value)
      response = requests.get(url, headers=headers, cookies=cookies)

      data = response.json()
      extracted_data = [
        {
          'uuid': item['uuid'],
          'exp': item['exp'],
          'rating': item['rating'],
          'addtime': item['addtime']
        }
        for item in data['data']
      ]

      records_to_insert = [(item['uuid'], item['exp'], item['rating'], item['addtime'], key) for item in extracted_data]

      # 批量插入数据
      cur.executemany("""
                INSERT INTO oulu (word, exp, rating, addTime, category)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (word)
                DO NOTHING
            """, records_to_insert)

      conn.commit()

      time.sleep(2)

  cur.close()
  conn.close()
  print("爬虫结束")


# 新的方法：从 oulu 表中抽取所有的 word，并返回为列表
def extract_all_words():
  # 连接数据库
  conn = psycopg2.connect(
    host="172.16.33.33",
    database="words",
    user="postgres",
    password="postgres"
  )

  # 创建游标对象
  cur = conn.cursor()

  # 查询所有 word
  cur.execute("SELECT word FROM oulu")

  # 获取所有结果
  words = cur.fetchall()

  # 提取word列并返回一个列表
  word_list = [word[0] for word in words]

  cur.close()
  conn.close()

  return word_list  # 返回包含所有 word 的列表


def get_oulu_count():
  # Cookie字符串
  cookie_string = "_ga=GA1.1.794527447.1711241930; __utma=131758875.1355860809.1711238181.1711238181.1711238181.1; __utmz=131758875.1711238181.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); .AspNetCore.Session=CfDJ8K06SDLLKs1FpKlpqTRecpJyj0Vo%2Bslu51Lgn%2FpWVh4IJi1ozj%2BsGO1Farv5tP8FgomUdmSJDgJI2kxAVMcjHzAU6r%2FGQp5Jne2iidEkjDRayDukywfviXN9LmNND4cIzr0PZP6%2BwnuSSuiCpKC6Zn5BvuLfEOq%2BoKe3om%2F%2Fp9%2Fa; col_index=6; col_sort=desc; EudicWebSession=QYNeyJoYXNfb2xkX3Bhc3N3b3JkIjpmYWxzZSwidG9rZW4iOiJIMXlhaStBbVFFT2xjamdCbTBaQUIwaWhEcUk9IiwiZXhwaXJlaW4iOjEzMTQwMDAsInVzZXJpZCI6ImJkNWRjODJhLWJjMTYtMTFlZS1iYjNiLTAwNTA1Njg2OWFmNiIsInVzZXJuYW1lIjoi5YiY5rSLX3RWUzBJcTdaVEFGVCIsImNyZWF0aW9uX2RhdGUiOiIyMDI0LTAxLTI1VDIyOjQ3OjIyWiIsInJvbGVzIjpudWxsLCJvcGVuaWRfdHlwZSI6bnVsbCwib3BlbmlkX2Rlc2MiOm51bGwsInByb2ZpbGUiOnsibmlja25hbWUiOiLliJjmtIsiLCJlbWFpbCI6IiIsImdlbmRlciI6IuWlsyIsInBhc3N3b3JkIjpudWxsLCJ2b2NhYnVsYXJpZXMiOnsiZW4iOjYwNjl9fSwibGFzdF9wYXNzd29yZF9jaGFuZ2VkX2RhdGUiOiIxLzI2LzIwMjQgNjo0NzoyMiBBTSIsInJlZGlyZWN0X3VybCI6bnVsbH0%253d; _ga_6J9FB2R7F4=GS1.1.1727955588.6.1.1727955654.0.0.0"
  cookies = parse_cookie_string(cookie_string)

  # 请求头
  headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
  }

  # URL模板
  url_template = "https://my.eudic.net/StudyList/WordsDataSource?=9&draw={draw}&columns%5B0%5D%5Bdata%5D=id&columns%5B0%5D%5Bname%5D=&columns%5B0%5D%5Bsearchable%5D=false&columns%5B0%5D%5Borderable%5D=false&columns%5B0%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B0%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B1%5D%5Bdata%5D=id&columns%5B1%5D%5Bname%5D=&columns%5B1%5D%5Bsearchable%5D=true&columns%5B1%5D%5Borderable%5D=false&columns%5B1%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B1%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B2%5D%5Bdata%5D=word&columns%5B2%5D%5Bname%5D=&columns%5B2%5D%5Bsearchable%5D=false&columns%5B2%5D%5Borderable%5D=true&columns%5B2%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B2%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B3%5D%5Bdata%5D=phon&columns%5B3%5D%5Bname%5D=&columns%5B3%5D%5Bsearchable%5D=true&columns%5B3%5D%5Borderable%5D=false&columns%5B3%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B3%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B4%5D%5Bdata%5D=exp&columns%5B4%5D%5Bname%5D=&columns%5B4%5D%5Bsearchable%5D=true&columns%5B4%5D%5Borderable%5D=false&columns%5B4%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B4%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B5%5D%5Bdata%5D=rating&columns%5B5%5D%5Bname%5D=&columns%5B5%5D%5Bsearchable%5D=false&columns%5B5%5D%5Borderable%5D=true&columns%5B5%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B5%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B6%5D%5Bdata%5D=addtime&columns%5B6%5D%5Bname%5D=&columns%5B6%5D%5Bsearchable%5D=false&columns%5B6%5D%5Borderable%5D=false&columns%5B6%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B6%5D%5Bsearch%5D%5Bregex%5D=false&order%5B0%5D%5Bcolumn%5D=6&order%5B0%5D%5Bdir%5D=desc&start={start}&length={length}&search%5Bvalue%5D=&search%5Bregex%5D=false&categoryid={category}&_=1727961507363"

  # 替换URL中的start和length
  url = url_template.format(draw=1, start=0, length=1, category=-1)
  # 发送请求
  response = requests.get(url, headers=headers, cookies=cookies)
  resp = response.json()
  total_data = resp['recordsTotal']

  return total_data


def markStars(word, star, cate):
  # Cookie字符串
  cookie_string = "_ga=GA1.1.794527447.1711241930; __utma=131758875.1355860809.1711238181.1711238181.1711238181.1; __utmz=131758875.1711238181.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); .AspNetCore.Session=CfDJ8K06SDLLKs1FpKlpqTRecpJyj0Vo%2Bslu51Lgn%2FpWVh4IJi1ozj%2BsGO1Farv5tP8FgomUdmSJDgJI2kxAVMcjHzAU6r%2FGQp5Jne2iidEkjDRayDukywfviXN9LmNND4cIzr0PZP6%2BwnuSSuiCpKC6Zn5BvuLfEOq%2BoKe3om%2F%2Fp9%2Fa; col_index=6; col_sort=desc; EudicWebSession=QYNeyJoYXNfb2xkX3Bhc3N3b3JkIjpmYWxzZSwidG9rZW4iOiJIMXlhaStBbVFFT2xjamdCbTBaQUIwaWhEcUk9IiwiZXhwaXJlaW4iOjEzMTQwMDAsInVzZXJpZCI6ImJkNWRjODJhLWJjMTYtMTFlZS1iYjNiLTAwNTA1Njg2OWFmNiIsInVzZXJuYW1lIjoi5YiY5rSLX3RWUzBJcTdaVEFGVCIsImNyZWF0aW9uX2RhdGUiOiIyMDI0LTAxLTI1VDIyOjQ3OjIyWiIsInJvbGVzIjpudWxsLCJvcGVuaWRfdHlwZSI6bnVsbCwib3BlbmlkX2Rlc2MiOm51bGwsInByb2ZpbGUiOnsibmlja25hbWUiOiLliJjmtIsiLCJlbWFpbCI6IiIsImdlbmRlciI6IuWlsyIsInBhc3N3b3JkIjpudWxsLCJ2b2NhYnVsYXJpZXMiOnsiZW4iOjYwNjl9fSwibGFzdF9wYXNzd29yZF9jaGFuZ2VkX2RhdGUiOiIxLzI2LzIwMjQgNjo0NzoyMiBBTSIsInJlZGlyZWN0X3VybCI6bnVsbH0%253d; _ga_6J9FB2R7F4=GS1.1.1727955588.6.1.1727955654.0.0.0"

  # 解析cookies
  cookies = parse_cookie_string(cookie_string)

  # 请求头
  headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
  }

  # 将参数word和star传入data字典
  data = {
    "oldcateid": -1,
    "newrating": star,  # star参数
    "uuid": word,  # word参数
    "oper": 'changerating'
  }

  # 将参数word和star传入data字典
  data2 = {
    "oldcateid": -1,
    "catename": cate,  # star参数
    "uuid": word,  # word参数
    "oper": 'moveword'
  }

  # URL
  url = 'https://my.eudic.net/StudyList/Edit'

  try:
    # 发送POST请求
    response = requests.post(url, headers=headers, cookies=cookies, data=data)
    response2 = requests.post(url, headers=headers, cookies=cookies, data=data2)

    # 检查请求是否成功
    response.raise_for_status()
    response2.raise_for_status()

    # 返回JSON响应
    resp = response.json()
    resp2 = response.json()
    return resp

  except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
    return None

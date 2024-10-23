from crawler import fetch_and_insert_data, extract_all_words, get_oulu_count, markStars


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
  cur.execute(
    "SELECT oulu.*, COALESCE(words.freq, 0) AS freq FROM oulu LEFT JOIN words ON oulu.word = words.word ORDER BY COALESCE(words.freq, 0) DESC;")

  # 获取所有结果
  words = cur.fetchall()

  # 遍历每一行，提取 word 和 freq 字段
  for word, freq in words:
    # 对 freq 字段进行修改，例如增加 1
    modified_freq = 1;

    if freq < 5: modified_freq = 1;
    if 5 <= freq < 10: modified_freq = 2;
    if 10 <= freq < 15: modified_freq = 3;
    if 15 <= freq < 20: modified_freq = 4;
    if freq >= 20: modified_freq = 5;

    markStars(word, modified_freq)

  # 关闭游标和连接
  cur.close()
  conn.close()

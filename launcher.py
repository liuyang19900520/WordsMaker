import psycopg2

from crawler import markStars

# fetch_and_insert_data()

## 连接数据库Ò
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
for index, row in enumerate(words):

  category_dict = {
    "1": "0",
    "2": "133557195427064351",
    "3": "1721222268",
    "4": "1726467371",
    "5": "133801326811757890",
    "6": "133801326642859934",
  }

  # 对 freq 字段进行修改，例如增加 1
  word = row[0]
  freq = row[-1]
  cate = category_dict[row[4]]
  rate = row[2]
  modified_freq = 1
  modified_cate = cate

  if freq < 5: modified_freq = 1;
  if 5 <= freq < 10: modified_freq = 2;
  if 10 <= freq < 15: modified_freq = 3;
  if 15 <= freq < 20: modified_freq = 4;
  if freq >= 20: modified_freq = 5;

  trimmed = word.strip()
  # 判断去掉前后空格后的字符串中是否还有空格
  if ' ' in trimmed:
    modified_cate = category_dict[6]
    if cate == '133557195427064351':
      modified_cate = category_dict[5]
  if rate != modified_freq or cate != modified_cate:
    print("设置rating开始====", word, index)
    markStars(word, modified_freq, cate)

print("设置rating结束")
# 关闭游标和连接
cur.close()
conn.close()

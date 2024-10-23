import psycopg2


def process_file_and_update_db(file_path):

  # 连接到PostgreSQL数据库
  conn = psycopg2.connect(
    host="172.16.33.33",  # PostgreSQL服务器地址，例如"localhost"
    database="words",  # 数据库名称
    user="postgres",  # 数据库用户名
    password="postgres"  # 数据库密码
  )

  # 创建游标对象
  cur = conn.cursor()

  # 读取txt文件中的数据
  with open(file_path, 'r') as file:
    for line in file:
      word, freq = line.strip().split(',')
      freq = int(freq)  # 将频率转换为整数

      # 插入数据到PostgreSQL的表中
      cur.execute("""
                        INSERT INTO words (word, freq)
                        VALUES (%s, %s)
                        ON CONFLICT (word)
                        DO UPDATE SET freq = words.freq + EXCLUDED.freq
                    """, (word, freq))

  # 提交更改并关闭连接
  conn.commit()
  cur.close()
  conn.close()

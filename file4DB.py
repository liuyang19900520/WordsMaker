import psycopg2
import boto3

# 创建DynamoDB资源
dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')  # 替换为你的AWS区域
table = dynamodb.Table('words')  # DynamoDB表名
# 连接到PostgreSQL数据库
conn = psycopg2.connect(
    host="172.16.33.33",      # PostgreSQL服务器地址，例如"localhost"
    database="words",    # 数据库名称
    user="postgres",      # 数据库用户名
    password="postgres"  # 数据库密码
)

# 创建游标对象
cur = conn.cursor()

# 读取txt文件中的数据
with open('testDB.txt', 'r') as file:
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

        # 更新 freq，如果不存在，插入新的记录
        response = table.update_item(
          Key={'word': word},
          UpdateExpression="""
                  SET freq = if_not_exists(freq, :start) + :val,
                      typ = if_not_exists(typ, :typ),
                      lvl = if_not_exists(lvl, :lvl)
              """,
          ExpressionAttributeValues={
            ':val': freq,
            ':start': 0,
            ':typ': '',
            ':lvl': ''
          },
          ReturnValues="UPDATED_NEW"
        )
# 提交更改并关闭连接
conn.commit()
cur.close()
conn.close()





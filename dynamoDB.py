import boto3
import time

def truncate():
  # 创建 DynamoDB 客户端
  dynamodb = boto3.client('dynamodb', region_name='ap-northeast-1')

  # DynamoDB 表名
  table_name = 'words'

  # 删除表
  dynamodb.delete_table(TableName=table_name)

  # 等待表被删除
  time.sleep(5)

  # 重新创建表 (确保与原表结构一致)
  dynamodb.create_table(
      TableName=table_name,
      KeySchema=[
          {
              'AttributeName': 'word',
              'KeyType': 'HASH'  # 分区键
          },
      ],
      AttributeDefinitions=[
          {
              'AttributeName': 'word',
              'AttributeType': 'S'  # 字符串类型
          },
      ],
      ProvisionedThroughput={
          'ReadCapacityUnits': 5,
          'WriteCapacityUnits': 5
      }
  )

  print("表已重新创建并清空所有数据。")



def process_file_and_update_db(file_path):
  # 创建 DynamoDB 客户端
  dynamodb = boto3.client('dynamodb', region_name='ap-northeast-1')

  # DynamoDB 表名
  table_name = 'words'

  # 读取txt文件中的数据
  with open(file_path, 'r') as file:
    for line in file:
      word, freq = line.strip().split(',')
      freq = int(freq)  # 将频率转换为整数

      # 更新DynamoDB中的数据
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




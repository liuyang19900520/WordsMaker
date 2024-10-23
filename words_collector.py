import string
import nltk
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus.reader.wordnet import NOUN, VERB, ADJ, ADV
from nltk.corpus import words
import spacy
from crawler import fetch_and_insert_data, extract_all_words, get_oulu_count
from file4DB import process_file_and_update_db
from datetime import datetime

nltk.download('words')
word_set = set(words.words())


def is_english_word(word):
  return word.lower() in word_set


def contains_digit(s):
  return any(char.isdigit() for char in s)


def is_blank(s):
  # 如果字符串为空或者每个字符都是空白字符，则返回True
  return not s or s.isspace()


def createDBFile(db_file, sorted_freq_dist):
  with open(db_file, 'w', encoding='utf-8') as file:
    for word, freq in sorted_freq_dist:
      if word not in list(string.ascii_lowercase) and not contains_digit(word) and not is_blank(
        word) and is_english_word(word):
        file.write(f"{word},{freq}\n")


def tokenize(text):
  # 确保已下载nltk的数据和模型
  nlp = spacy.load('en_core_web_sm')
  nltk.download('punkt')
  nltk.download('stopwords')
  nltk.download('averaged_perceptron_tagger')
  nltk.download('wordnet')

  doc = nlp(text)
  names = [ent.text.lower() for ent in doc.ents if ent.label_ == 'PERSON']

  # 分词
  tokens = word_tokenize(text)

  # 词形还原
  lemmatizer = WordNetLemmatizer()

  def get_wordnet_pos(tag):
    if tag.startswith('J'):
      return ADJ
    elif tag.startswith('V'):
      return VERB
    elif tag.startswith('N'):
      return NOUN
    elif tag.startswith('R'):
      return ADV
    else:
      return NOUN

  pos_tags = nltk.pos_tag(tokens)
  lemmas = [lemmatizer.lemmatize(token.lower(), get_wordnet_pos(pos_tag)) for token, pos_tag in pos_tags]

  # 分词并去除停用词和标点符号
  filtered_tokens = [lemma for lemma in lemmas if
                     lemma not in stopwords.words('english') + list(string.punctuation) + names]

  # 统计单词频率
  word_freq = nltk.FreqDist(filtered_tokens)
  sorted_freq_dist = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
  print("单词频率统计完成")

  current_time = datetime.now()
  formatted_time = current_time.strftime('%Y%m%d%H%M%S')
  createDBFile(formatted_time + 'Import.txt', sorted_freq_dist)
  print("创建DB导入file成功")

  process_file_and_update_db(formatted_time + 'Import.txt')
  print("频率DB创建成功")

  pgDBList = extract_all_words()
  ouluCount = get_oulu_count();

  if (len(pgDBList) != ouluCount):
    fetch_and_insert_data()

  ouluWordList = extract_all_words()
  abc = list(string.ascii_lowercase)
  exist_list = set(ouluWordList + abc)
  # 导出到txt文件
  with open(formatted_time + 'Upload.txt', 'w', encoding='utf-8') as file:
    for word, freq in sorted_freq_dist:
      if word not in exist_list and not contains_digit(word) and not is_blank(word) and is_english_word(word):
        file.write(f"{word}\n")

  print("导入欧路词典的txt文件创建成功")

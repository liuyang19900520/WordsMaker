import string
import nltk
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus.reader.wordnet import NOUN, VERB, ADJ, ADV
from nltk.corpus import words
import spacy

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
      if word and not contains_digit(word) and not is_blank(word) and is_english_word(word):
        file.write(f"{word},{freq}\n")


def tokenize(text, file_path, output_file):
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

  print("Word Frequencies:")
  print(word_freq.most_common())

  createDBFile(output_file + 'DB.txt',sorted_freq_dist)
  # 使用pandas读取CSV文件
  df = pd.read_csv(file_path)

  # 假设CSV文件中有一个名为"单词"的列，我们将提取这一列的数据
  # 如果您的列名不是"单词"，请将下面代码中的'单词'替换为您的列名
  words_column = '单词'
  words = df[words_column].tolist()
  abc = list(string.ascii_lowercase)
  exist_list = set(words + abc)

  # 导出到txt文件
  with open(output_file + '.txt', 'w', encoding='utf-8') as file:
    for word, freq in sorted_freq_dist:
      if word not in exist_list and not contains_digit(word) and not is_blank(word) and is_english_word(word):
        file.write(f"{word}\n")
  #
  # # 寻找常用的双词搭配（bigrams）
  # bigram_measures = BigramAssocMeasures()
  # finder = BigramCollocationFinder.from_words(tokens)
  # # 可以调整这里的频率阈值
  # finder.apply_freq_filter(2)  # 假设我们只关注至少出现2次的搭配
  # collocations = finder.nbest(bigram_measures.pmi, 3)  # 提取得分最高的3个搭配
  # print("\nCommon Collocations:")
  # print(collocations)

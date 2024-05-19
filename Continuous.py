import re
import json
from langdetect import detect
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk import pos_tag
import ast

# 如果没有安装nltk数据，则需要安装数据
nltk.download('punkt')  # 用于分词
nltk.download('averaged_perceptron_tagger')  # 用于POS标记

################# Function tools ################
#写几个工具函数，来简化流程
#前uuid<=17没有进行简化

def sentences_word_split(text):
    """
        将句子拆分成为一个个字符数组，形式为[[--],[--],[--],--]
    """
    text = re.split(r'[.!?]+', text)
    if len(text)>0 and text[len(text)-1]=='':
        text.pop()
    sentences=[]
    for sentence in text:
        if sentence[-1]=='!'or sentence[-1]=='.' or sentence[-1]=='?':
            sentence=sentence[:-1]
        elif sentence[0]==' ':
            sentence=sentence[1:]
        sentence=re.split(',|:| |;|-',sentence)
        sentences.append(sentence)
    
    return sentences

#################################################


def verify_response_limit(response_text, vars,type=0):
    """
        uuid 0
        type=0: return True/False
        type=1: word_count<=word_limit  return 1
                word_count>word_limit   return 1-(word_count-word_limit)/word_limit
                                        (-inf,1)
        不需要负值，负值全部算0
        （0，1）之间完成度高低
        超出多少以内（0，1）
        超出过多设置为0
    """
    word_limit = int(vars[0])
    word_count = len(response_text.split())
    meets_criteria = word_count <= word_limit
    if type==0:
        return meets_criteria
    else:
        if meets_criteria:
            return 1
        else:
            return 1-(word_count-word_limit)/word_limit


def verify_language(response_text, vars, type=0):
    """
        uuid 1
        return True/False
    """
    expected_language = vars[0]
    detected_language = detect(response_text)
    print(detected_language)
    language_map = {
        "English": "en",
        "Chinese": "zh-cn",
        "Spanish": "es",
        "French": "fr",
        "Japanese": "ja"
    }
    expected_language_code = language_map.get(expected_language, expected_language)
    
    return detected_language == expected_language_code

def verify_keywords(response_text, vars,type=0):
    """
        uuid 2
        only type=0: return True/False
    """
    keyword = vars[0]
    
    return keyword.lower() in response_text.lower()

def verify_sentence_word_limit1(response_text, vars, type=0):
    """
        uuid 3
        return True/False
    """
    sentence_number, word_limit = vars
    sentence_number, word_limit = int(sentence_number), int(word_limit)
    
    sentences = response_text.split('. ')
    if len(sentences) < sentence_number:
        return False
    else:
        selected_sentence = sentences[sentence_number - 1]
        word_count = len(selected_sentence.split())
        return word_count <= word_limit

    

def count_sentences_with_pos_nltk(response_text, vars, type=0):
    """
        uuid 4
        return True/False
    """
    # 将文本分成句子
    sentences = sent_tokenize(response_text)
    count_number, pos_type = vars 
    count_number = int(count_number)
    
    # 将词性列表映射到可能的POS标记
    pos_mapping = {
        "noun": ['NN', 'NNS', 'NNP', 'NNPS'],
        "adjective": ['JJ', 'JJR', 'JJS'],
        "verb": ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'],
        "adverb": ['RB', 'RBR', 'RBS'],
        "preposition": ['IN', 'TO']
    }

    count = 0

    # 遍历每个句子
    for sentence in sentences:
        # 分词
        words = word_tokenize(sentence)
        # 词性标记
        pos_tags = pos_tag(words)

        # 检查第一个词的词性
        first_word_pos = pos_tags[0][1]  # 获取第一个词的POS标记

        # 如果第一个词的词性在给定列表中，计数加1
        if first_word_pos in pos_mapping.get(pos_type, []):
            count += 1

    return count == count_number

def verify_mixed_sentence_constraints(response_text, vars, type=0):
    """
        uuid 5
        return True/False
    """
    sentence_number, word_limit, punctuation=vars
    sentence_number = int(sentence_number)
    word_limit = int(word_limit)
    sentences = re.split(r'(?<=[.!?])\s*', response_text)
    if len(sentences)>0 and sentences[len(sentences)-1]=='':
        sentences.pop()
    if sentence_number>len(sentences):
        return False
    selected_sentence = sentences[sentence_number - 1] if sentence_number <= len(sentences) else ''
    if selected_sentence[-1]=='!'or selected_sentence[-1]=='.' or selected_sentence[-1]=='?':
        selected_sentence=selected_sentence[:-1]
    selected_sentence=re.split(',|:| |;|-',selected_sentence)
    word_count = len(selected_sentence)
    if len(punctuation)>1:
        punctuation=re.split(',|:| |;|-',punctuation)
        ends_correctly=True
        if len(selected_sentence)<len(punctuation):
            ends_correctly=False
        else:
            for i in range(len(punctuation)):
                if selected_sentence[-1-len(punctuation)+1+i]!=punctuation[i]:
                    ends_correctly=False
                    break
    else:
        ends_correctly = selected_sentence[-1]==punctuation
    return word_count <= word_limit and ends_correctly

def verify_keyword_frequency1(response_text, vars, type=0):
    """
        uuid 6
        type=0: return True/False
        type=1: 1-abs(word_count-n)/n
    """
    word, n  = vars
    n = int(n)
    sentences = re.split(r'(?<=[.!?])\s*', response_text)
    word_count = 0
    for sentence in sentences:
        if len(sentence) > 0 and ( sentence[-1]=='!'or sentence[-1]=='.' or sentence[-1]=='?'):
            sentence=sentence[:-1]
        sentence=re.split(',|:| |;|-',sentence)
        word_count+=sentence.count(word)
    if type==0:
        return word_count == n
    else:
        return 1-abs(word_count-n)/n
    
def verify_letter_frequency(response_text, vars, type=0):
    """
        uuid 7
        type=0: return True/False
        type=1: 1-abs(letter_count-n)/n
    """
    letter, n = vars
    n = int(n)
    letter_count = 0
    for char in response_text:
        if char == letter:
            letter_count += 1
    if type==0:
        return letter_count == n
    else:
        return 1-abs(letter_count-n)/n

def verify_number_placeholders(response_text, vars, type=0):
    """
        uuid 8
        type=0: return True/False
        type=1: return 1-abs(count1-placeholder_count)/placeholder_count
        (In the case of equal quantities of '[[' and ']]')
    """
    placeholder_count = int(vars[0])
    
    count1=response_text.count('[[')
    count2=response_text.count(']]')
    if count1==count2:
        if type==0:
            return count1 == placeholder_count
        else:
            return 1-abs(count1-placeholder_count)/placeholder_count
    else:
        return False

def verify_json_format(response_text, vars, type=0):
    """
        uuid 9
        return True/False
    """
    try:
        json_object = json.loads(response_text)
        return True
    except ValueError as e:
        return False
    
def verify_highlighted_sections(response_text, number_of_sections,type=0):
    """
        uuid 10
        type=0: return True/False
        type=1: 1-(len(highlighted)/2 - number_of_sections)/number_of_sections
    """
    highlighted = response_text.split("*")
    number_of_sections = int(number_of_sections[0])
    if type==0:
        return len(highlighted)/2 >= number_of_sections
    else:
        if len(highlighted)/2 >= number_of_sections:
            return 1
        else:
            return 1-(len(highlighted)/2 - number_of_sections)/number_of_sections

def verify_repeat_prompt(response_text, vars, type=0):
    """
        uuid 11
        return True/False
    """
    prompt = vars[0]
    return response_text.startswith(prompt)

def verify_sentence_count(response_text, vars,type=0):
    """
        uuid 12
        type=0 return True/False
        type=1: 1-abs(len(sentences) - sentence_count)/sentence_count
    """
    sentences = re.split(r'(?<=[.!?])\s*', response_text)
    sentence_count = int(vars[0])
    if len(sentences)>0 and sentences[len(sentences)-1]=='':
        sentences.pop()
    if type==0:
        return len(sentences) == sentence_count
    else:
        return 1-abs(len(sentences) - sentence_count)/sentence_count

def verify_vocabulary_complexity(response_text, vars, type=0):
    """
        uuid 13
        return True/False
    """
    n, min_length = map(int, vars)
    # Regular expression to split sentences
    sentences = re.split(r'(?<=[.!?])\s*', response_text)

    if sentences and not sentences[-1]:
        sentences.pop()  # Remove empty string at the end

    word_count = 0
    # Split each sentence into words and count words with length >= min_length
    for sentence in sentences:
        words = re.split(r'[,:; \-\s]', sentence)  # Split by common delimiters
        for word in words:
            if len(word) >= min_length:
                word_count += 1
                if word_count >= n:  # If word count meets or exceeds 'n'
                    return True
    
    # If total word count with length >= min_length is less than 'n', return False
    return False

def verify_keyword_frequency2(response_text, vars, type=0):
    """
        uuid 14
        return True/False
    """
    keyword, n1, n2 = vars
    n1, n2 =  int(n1), int(n2)
    sentences = re.split(r'(?<=[.!?])\s*', response_text)
    word_count = 0
    for sentence in sentences:
        if len(sentence) > 0 and ( sentence[-1]=='!'or sentence[-1]=='.' or sentence[-1]=='?'):
            sentence=sentence[:-1]
        sentence=re.split(',|:| |;|-',sentence)
        word_count+=sentence.count(keyword)
    
    return n1 <= word_count <= n2

def verify_inclusion_of_keywords1(response_text, vars, type=0):
    """
        uuid 15
        type=0 return True/False
    """
    keyword_groups = vars
    
    # Convert response text to lowercase for case-insensitive comparison
    response_lower = response_text.lower()

    # Check each keyword group to ensure at least one keyword is present
    for group in keyword_groups:
        group_found = any(keyword.lower() in response_lower for keyword in group)
        if not group_found:
            return False  # If any group has no keywords in the text, return False
    
    return True


def verify_specific_punctuation1(response_text, min_exclamations, type=0):
    """
        uuid 16
        type=0 return True/False
        type=1
        exclamation_count > 0 return exclamation_count / min_exclamations
        exclamation_count == 0 return 0
    """
    # exclamation_count = response_text.count('!')
    # if type == 0:
    #     return exclamation_count >= min_exclamations
    # else:
    #     if exclamation_count == 0:
    #         return 0
    #     else:
    #         return exclamation_count / min_exclamations
    return True

def verify_specific_punctuation2(response_text, vars, type=0):
    """
        uuid 17
        return True/False
    """
    # sentence_interval, punctuation = vars
    # sentence_interval = int(sentence_interval)
    
    
    # sentences = re.split(r'[.!?]+', response_text)
    # if len(sentences)>0 and sentences[len(sentences)-1]=='':
    #     sentences.pop()
    # flag=True
    # count=0
    # word_count=0
    # for sentence in sentences:
    #     count+=1
    #     if sentence[-1]=='!'or sentence[-1]=='.' or sentence[-1]=='?':
    #         sentence=sentence[:-1]
    #     sentence=re.split(',|:| |;|-',sentence)
    #     print(sentence)
    #     for word in sentence:
    #         if word == punctuation:
    #             word_count+=1
    #         if len(sentence)>0:
    #             if word == sentence[len(sentence)-1] and count == sentence_interval:
    #                 if word_count < 1:
    #                     flag=False
    #                 count=0
    #                 word_count=0
    #         else:
    #             if count == sentence_interval:
    #                 if word_count < 1:
    #                     flag=False
    #                 count=0
    #                 word_count=0
    
    # return flag
    return True

def verify_end_punctuation(response_text, vars, type=0):
    """
        uuid 18
        return True/False
    """
    punctuation = vars[0]
    if len(response_text) > 0:
        # print(response_text[-1])
        # print(punctuation)
        return response_text[-1] == punctuation
    else:
        return False

def verify_paragraph_limit(response_text, vars, type=0):
    """
        uuid 19
        type=0 return True/False
        type=1
        abs(len(paragraphs)-paragraph_limit) <= 2 return exclamation_count / min_exclamations
        abs(len(paragraphs)-paragraph_limit) > 2 return 0
        感觉还是有点问题，比如\n\n\n....的情况
    """
    
    paragraph_limit = int(vars[0])
    paragraphs = response_text.split('\n\n')
    paragraphs = [p for p in paragraphs if p.strip()]
    
    if type == 0:
        return len(paragraphs) == paragraph_limit
    else:
        if abs(len(paragraphs)-paragraph_limit) <= 2:
            return 1-abs(len(paragraphs)-paragraph_limit) / paragraph_limit
        else:
            return 0

def verify_number_format(response_text, vars, type=0):
    """
        uuid 20
        type=0 return True/False
        type=1 return count / len(numbers)
    """
    decimal_places = int(vars[0])
    pattern = re.compile(r'\b\d+\.\d{' + str(decimal_places) + '}' + r'\b')
    numbers=re.findall(r'\b\d+\.\d+\b', response_text)
    count=0
    for number in numbers:
        if pattern.fullmatch(number):
            count+=1
    if type==0:
        return count==len(numbers)
    else:
        return count / len(numbers)

def verify_sentence_punctuation(response_text, vars, type=0):
    """
    验证每个段落是否都以指定标点符号结尾
    uuid 21
    return True/False
    """
    punctuation_mark = vars[0]
    # 删除首尾空白字符，并根据换行符分割文本
    paragraphs = response_text.strip().split('\n')
    
    # 用于检查是否每个段落都以给定符号结尾
    all_end_with_mark = True
    
    # 正则表达式用于匹配段落结尾的指定标点符号
    pattern = re.compile(rf'{re.escape(punctuation_mark)}\s*$')
    
    for paragraph in paragraphs:
        # 如果段落不以指定符号结尾，设置标志为False并退出循环
        if not pattern.search(paragraph):
            all_end_with_mark = False
            break
    
    return all_end_with_mark


def verify_sentence_complexity1(response_text, min_commas, type=0):
    """
    验证每个句子中逗号的数量是否达到要求
    uuid 22
    type=0: 返回 True/False
    type=1: 返回比例
    """
    # 确保 min_commas 是整数
    min_commas = int(min_commas[0])

    # 通过正则表达式分割句子
    sentences = re.split(r'[.!?]+', response_text.strip())

    # 如果最后一段是空的，则去掉
    if sentences and sentences[-1] == '':
        sentences.pop()

    # 计数符合条件的逗号数量
    total_commas = sum(sentence.count(',') for sentence in sentences)

    if type == 0:
        # 返回布尔值，表示是否满足逗号要求
        return all(sentence.count(',') >= min_commas for sentence in sentences)
    else:
        # 返回比例，代表满足条件的逗号数量与总的逗号数量的比率
        num_sentences_meeting_min = sum(1 for sentence in sentences if sentence.count(',') >= min_commas)
        if total_commas >= min_commas:
            return 1.0
        else:
            return num_sentences_meeting_min / len(sentences)
        

def verify_sentence_word_count(response_text, max_words, type=0):
    """
    验证每个句子的单词数量是否小于指定值
    uuid 23
    返回布尔值表示每个句子的单词数量是否少于max_words
    """
    # 确保 max_words 是整数
    max_words = int(max_words[0])
    # print(max_words)

    # 分割文本成句子
    sentences = re.split(r'[.!?]+', response_text.strip())

    # 如果最后一段是空的，则去掉
    if sentences and sentences[-1] == '':
        sentences.pop()

    # 检查每个句子的单词数量
    all_less_than_max = True

    for sentence in sentences:
        # 使用正则表达式来划分句子中的单词，并计数
        words = re.findall(r'\w+', sentence)
        word_count = len(words)

        if word_count >= max_words:
            all_less_than_max = False
            break
            
    return all_less_than_max

def verify_specific_punctuation3(response_text, vars, type=0):
    """
    检查文本中某个符号的出现次数
    uuid 24
    type=0: 返回 True/False 表示符号的出现次数是否与目标相符
    type=1: 返回相对精确度，越接近 1 表示越接近目标
    """
    # 确保 target_count 是整数
    punctuation_mark, target_count = vars
    target_count = int(target_count)

    # 使用正则表达式计算符号的出现次数
    punctuation_count = len(re.findall(re.escape(punctuation_mark), response_text))

    if type == 0:
        # 如果符号出现次数等于目标值，返回 True，否则返回 False
        return punctuation_count == target_count
    else:
        # 计算相对精确度，偏差越小，返回值越接近 1
        deviation = abs(punctuation_count - target_count)
        if deviation <= 2:
            return 1 - (deviation / target_count)
        else:
            return 0
        
def verify_vocabulary_range(response_text, unique_word_count, type=0):
    """
        uuid 25
        type=0 return True/False
        type=1 
        count > unique_word_count  return 1
        abs(count - unique_word_count)<=2   return 1-abs(count - unique_word_count)/unique_word_count
        abs(count - unique_word_count)>2    return 0
    """
    # sentences=sentences_word_split(response_text)
    # unique_word_count = int(unique_word_count[0])
    # print(sentences)
    # word_dict={}
    # for sentence in sentences:
    #     for word in sentence:
    #         if word not in word_dict:
    #             word_dict[word]=1
    #         else:
    #             word_dict[word]+=1
    # word_dict_filtered = {key: value for key, value in word_dict.items() if value == 1}
    # count = sum(1 for value in word_dict_filtered)
    
    # if type==0:
    #     return count >= unique_word_count
    # else:
    #     if count > unique_word_count:
    #         return 1
    #     else:
    #         if abs(count - unique_word_count)<=2:
    #             return 1-abs(count - unique_word_count)/unique_word_count
    #         else:
    #             return 0
    return True

def verify_inclusion_of_keywords2(response_text, vars, type=0):
    """
        This function checks if the response text includes at least 'VAR1' number of specified keywords.
        :param response_text: The text to check.
        :param vars: A dictionary with 'VAR1' (minimum number of keywords) and 'VAR2' (list of keywords).
        :return: True if the text contains at least 'VAR1' specified keywords, otherwise False.
    """
    # Extracting required values from vars
    required_count, keywords = vars
    required_count = int(required_count)
    keywords = ast.literal_eval(keywords)
    # print(keywords)
    # Ensure response text is case-insensitive
    response_lower = response_text.lower()

    # Count the number of specified keywords found in the response text
    found_count = 0
    for keyword in keywords:
        if keyword.lower() in response_lower:
            found_count += 1
            if found_count >= required_count:
                return True  # Enough keywords found

    return False  # Not enough keywords found

# def verify_inclusion_of_keywords2(response_text, vars, type=0):
#     """
#         uuid 26
#         type=0 return True/False
#         type=1 word_count / minimum_keywords
#     """
#     word_count=0
#     minimum_keywords, keywords = vars
#     minimum_keywords = int(minimum_keywords)
#     sentences = sentences_word_split(response_text)
#     for sentence in sentences:
#         for word in sentence :
#             for keyword in keywords:
#                 keyword_=re.split(' ',keyword)
#                 if len(keyword_)>1:
#                     if sentence.index(word)+len(keyword_)-1<=len(sentence)-1:
#                         flag=True
#                         for i in range(len(keyword_)):
#                             if sentence[sentence.index(word)+i]!=keyword_[i]:
#                                 flag=False
#                         if flag:
#                             word_count+=1
#                 else:
#                     if keyword.lower() == word:
#                         word_count+=1
#     if type == 0:  
#         return word_count == minimum_keywords
#     else:
#         return word_count / minimum_keywords
    
def verify_sentence_word_limit3(response_text, vars, type=0):
    """
        uuid 27
        return True/False
    """
    word_limit = int(vars[0])
    sentences = sentences_word_split(response_text)
    for sentence in sentences:
        if len(sentence)==word_limit:
            return False
    return True

def verify_sentence_complexity(response_text, vars, type=0):
    """
    验证每个句子的单词数是否在指定范围内
    uuid 28
    返回 True/False
    """
    # 确保输入值是整数
    min_words, max_words = vars
    min_words = int(min_words)
    max_words = int(max_words)

    # 使用正则表达式分割句子，并按空格分割单词
    sentences = re.split(r'[.!?]+', response_text.strip())
    if sentences and sentences[-1] == '':
        sentences.pop()

    # 检查每个句子的单词数
    for sentence in sentences:
        # 按空格分割单词，并去除首尾空白
        words = sentence.strip().split()

        # 如果单词数量不在指定范围内，返回 False
        if len(words) < min_words or len(words) > max_words:
            return False

    # 如果所有句子的单词数量都在范围内，返回 True
    return True

def verify_specific_structure(response_text, vars, type=0):
    """
        uuid 29
        return True/False
    """
    sentences = re.split(r'[.!?]+', response_text)
    if sentences[0].startswith('The sentiment of the sentence is'):
        return True
    else:
        return False

def verify_sentence_structure(response_text, vars, type=0):
    sentence_count = vars
    sentences = re.split(r'[.!?]+', response_text)
    sentences = [sentence.strip() for sentence in sentences if sentence.strip() != '']
    structures = set()
    for sentence in sentences:
        structure = ''.join(['D' if ch.isdigit() else 'L' if ch.isalpha() else ch for ch in sentence])
        structures.add(structure)
    return len(sentences) == sentence_count and len(structures) == sentence_count


def verify(answer,vars,uuid,type=0):
    match uuid:
        case 0:
            verify_func = verify_response_limit
        case 1:
            verify_func = verify_language
        case 2:
            verify_func = verify_keywords
        case 3:
            verify_func = verify_sentence_word_limit1
        case 4:
            verify_func = count_sentences_with_pos_nltk
        case 5:
            verify_func = verify_mixed_sentence_constraints
        case 6:
            verify_func = verify_keyword_frequency1
        case 7:
            verify_func = verify_letter_frequency
        case 8:
            verify_func = verify_number_placeholders
        case 9:
            verify_func = verify_json_format
        case 10:
            verify_func = verify_highlighted_sections
        case 11:
            verify_func = verify_repeat_prompt
        case 12:
            verify_func = verify_sentence_count
        case 13:
            verify_func = verify_vocabulary_complexity
        case 14:
            verify_func = verify_keyword_frequency2
        case 15:
            verify_func = verify_inclusion_of_keywords1
        case 16:
            verify_func = verify_specific_punctuation1
        case 17:
            verify_func = verify_specific_punctuation2
        case 18:
            verify_func = verify_end_punctuation
        case 19:
            verify_func = verify_paragraph_limit
        case 20:
            verify_func = verify_number_format
        case 21:
            verify_func = verify_sentence_punctuation
        case 22:
            verify_func = verify_sentence_complexity1
        case 23:
            verify_func = verify_sentence_word_count
        case 24:
            verify_func = verify_specific_punctuation3
        case 25:
            verify_func = verify_vocabulary_range
        case 26:
            verify_func = verify_inclusion_of_keywords2
        case 27:
            verify_func = verify_sentence_word_limit3
        case 28:
            verify_func = verify_sentence_complexity
        case 29:
            verify_func = verify_specific_structure
        case _:
            raise ValueError("Invalid UUID")
    return verify_func(answer, vars, type)
        
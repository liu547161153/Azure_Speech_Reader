import pickle
import re
import jieba
import numpy as np
from keras.models import load_model
from keras.preprocessing import sequence
import asyncio



class Sentiment:
    def __init__(self, model_path, word_dict_path):
        self.MAX_SENTENCE_LENGTH = 80
        self.model = load_model(model_path)
        with open(word_dict_path, 'rb') as handle:
            self.word2index = pickle.load(handle)
        self.label2word = {1: '喜好', 2: '悲伤', 3: '厌恶', 4: '愤怒', 5: '高兴', 0: '无情绪'}
        self.tts_emotions = {'喜好': 'gentle', '悲伤': 'depressed', '厌恶': 'disgruntled', '愤怒': 'angry',
                             '高兴': 'cheerful', '无情绪': None}

    def determine_final_emotion(self, top_3_emotions):
        # 先确定概率最高的情绪及其强度
        primary_emotion, primary_strength = top_3_emotions[0]

        # 调整强度基准值，以使强度值落在 0.5 到 2 的范围内
        primary_strength = 1.5 * primary_strength + 0.5

        # 考虑其他情绪对强度的影响
        for emotion, strength in top_3_emotions[1:]:
            if emotion in ['悲伤', '愤怒', '厌恶']:
                # 如果是消极情绪，降低强度
                primary_strength -= 0.2  # 调整值可根据需要修改
            elif emotion in ['喜好', '高兴']:
                # 如果是正面情绪，提高强度
                primary_strength += 0.2  # 调整值可根据需要修改

        # 确保强度值在 0.5 到 2 之间
        primary_strength = min(max(primary_strength, 0.5), 2)

        return primary_emotion, primary_strength

    def regex_filter(self, s_line):
        special_regex = re.compile(r"[a-zA-Z0-9\s]+")
        en_regex = re.compile(r"[.…{|}#$%&\'()*+,!-_./:~^;<=>?@★●，。]+")
        zn_regex = re.compile(r"[《》、，“”；～？！：（）【】]+")

        s_line = special_regex.sub(r"", s_line)
        s_line = en_regex.sub(r"", s_line)
        s_line = zn_regex.sub(r"", s_line)
        return s_line

    async def predict(self, sentence):
        xx = np.empty(1, dtype=list)
        sentence = self.regex_filter(sentence)
        words = jieba.cut(sentence)
        seq = []
        for word in words:
            if word in self.word2index:
                seq.append(self.word2index[word])
            else:
                seq.append(self.word2index['UNK'])
        xx[0] = seq
        xx = sequence.pad_sequences(xx, maxlen=self.MAX_SENTENCE_LENGTH)

        # 使用 run_in_executor 来运行同步的模型预测代码
        loop = asyncio.get_running_loop()
        x = await loop.run_in_executor(None, self.model.predict, xx)
        top_3_indices = np.argsort(x[0])[-3:][::-1]
        top_3_emotions = [(self.label2word[i], x[0][i]) for i in top_3_indices]

        final_emotion, emotion_strength = self.determine_final_emotion(top_3_emotions)
        tts_emotion = self.tts_emotions.get(final_emotion, None)

        return tts_emotion, emotion_strength * 2



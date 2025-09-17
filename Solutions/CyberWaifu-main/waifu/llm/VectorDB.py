import pandas as pd
import os
import ast
from scipy import spatial

class VectorDB:
    def __init__(self, embedding, save_path):#三个参数：embedding，保存路径，embedding模型
        self.save_path = save_path
        self.embedding = embedding
        self.chunks    = []


    def store(self, text: str | list):
        '''保存 vector'''
        if isinstance(text, str):#单个句子
            if text == '':#空句子
                return#不保存
            vector = self.embedding.embed_documents([text])#计算向量
            df = pd.DataFrame({"text": text, "embedding": vector})#保存到dataframe
        elif isinstance(text, list):#多个句子
            if len(text) == 0:#空句子列表
                return
            vector = self.embedding.embed_documents(text)#计算向量
            df = pd.DataFrame({"text": text, "embedding": vector})#保存到dataframe
        else:
            raise TypeError('text must be str or list')#句子类型错误
        df.to_csv(self.save_path, mode='a', header=not os.path.exists(self.save_path), index=False)#保存到csv文件


    def query(self, text: str, top_n: int, threshold: float = 0.7):
        if text == '':
            return ['']
        relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y)

        # Load embeddings data
        if not os.path.isfile(self.save_path):
            return ['']
        df = pd.read_csv(self.save_path)
        row = df.shape[0]
        top_n = min(top_n, row)
        df['embedding'] = df['embedding'].apply(ast.literal_eval)

        # Make query
        query_embedding = self.embedding.embed_query(text)
        strings_and_relatednesses = [
            (row["text"], relatedness_fn(query_embedding, row["embedding"]))
            for i, row in df.iterrows()
        ]

        # Rank
        strings_and_relatednesses.sort(key=lambda x: x[1], reverse=True)
        strings, relatednesses = zip(*strings_and_relatednesses)
        for i in range(len(relatednesses)):
            if relatednesses[i] < threshold:
                break
        return strings[:min(i+1, top_n)], relatednesses[:min(i+1, top_n)]
    
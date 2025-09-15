from waifu.llm.Brain import Brain
from waifu.llm.VectorDB import VectorDB
from waifu.llm.SentenceTransformer import STEmbedding
from langchain_community.chat_models import  ChatOpenAI
from langchain_community.embeddings import OpenAIEmbeddings
from typing import Any, List, Mapping, Optional
from langchain.schema import BaseMessage
import openai
import os

class GPT(Brain):
    def __init__(self, api_key: str,
                 name: str,
                 stream: bool=False,
                 callback=None,
                 model: str='grok-beta',
                 emb_Model: str='ep-20241116221815-66kt7',
                 EMB_API_KEY: str="e759cfd8-f7bc-43a0-9dc2-00cb154ac483",
                 proxy: str=''):


        self.llm = ChatOpenAI(openai_api_key=api_key,
                        model_name=model,
                        streaming=stream,
                        callbacks=[callback],
                        temperature=2)
        self.llm_nonstream = ChatOpenAI(openai_api_key=api_key,
                                        model_name=model,
                                        openai_api_base="https://api.x.ai/v1",)
        self.embedding = OpenAIEmbeddings(openai_api_key=EMB_API_KEY,
                                          model_name=emb_Model,
                                          openai_api_base="https://ark.cn-beijing.volces.com/api/v3"
                                          )
        # self.embedding = STEmbedding()
        self.vectordb = VectorDB(self.embedding, f'./memory/{name}.csv')
        if proxy != '':
            openai.proxy = proxy


    def think(self, messages: List[BaseMessage]):
        return self.llm(messages).content


    def think_nonstream(self, messages: List[BaseMessage]):
        return self.llm_nonstream(messages).content


    def store_memory(self, text: str | list):
        '''保存记忆 embedding'''
        self.vectordb.store(text)


    def extract_memory(self, text: str, top_n: int = 10):
        '''提取 top_n 条相关记忆'''
        return self.vectordb.query(text, top_n)
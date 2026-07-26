#imports
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
# imports for integrating chat history
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_classic.chains.history_aware_retriever import create_history_aware_retriever
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains import create_retrieval_chain


# import streamlit for session_id management to keep track of chat history for each user session
import streamlit as st

# import ChatGroq for using Groq LLM instead of Ollama and load the api key from .env file
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
# Load environment variables from .env file
load_dotenv()

from langchain_huggingface import HuggingFaceEmbeddings

import chromadb
from langchain_chroma import Chroma

from pydantic_parser import RecommendedRecipe
from langchain_core.output_parsers import PydanticOutputParser

import time
from langchain_core.callbacks import get_usage_metadata_callback
from database import log_request

class RAG:
    def __init__(self):
        self.embedding_model = HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5"
        )
        # define contextualise query prompt
        self.contextualize_q_system_prompt="""Given a chat history and the latest user question \
        which might reference context in the chat history, formulate a standalone question \
        which can be understood without the chat history. Do NOT answer the question, \
        just reformulate it if needed and otherwise return it as is."""
        self.contextualize_q_prompt=ChatPromptTemplate.from_messages(
            [
                ('system',self.contextualize_q_system_prompt),
                MessagesPlaceholder('chat_history'),
                ('human','{input}')
            ]
        )
        # define qa prompt
        self.qa_system_prompt="""
You are an AI Recipe Assistant.

Use ONLY the retrieved context to answer the user's question.

Rules:
- Do not make up recipes.
- Do not invent ingredients.
- If the answer is not in the context, say you don't know.
- Keep the answer concise.
- Use the retrieved context only.

Retrieved Context:
{context}

"""     # parser
        self.pydantic_parser=PydanticOutputParser(pydantic_object=RecommendedRecipe)
        
        self.qa_prompt=ChatPromptTemplate.from_messages(
            [
                ('system',self.qa_system_prompt),
                MessagesPlaceholder('chat_history'),
                ('human','{input}\n{format_instructions}')
            ]
        ).partial(format_instructions=self.pydantic_parser.get_format_instructions())
        
        # Automatically build everything
        self.load_retriever()
        self.build_chain()
        # store to keep track of chat history
        self.store={}
        
        # build initial chains with current selected model
        self.update_model()
        
    def load_retriever(self):
        self.vectorstore=Chroma(
        persist_directory='./recipe_db',
        embedding_function=self.embedding_model
        )
        
        self.retriever=self.vectorstore.as_retriever(search_type='mmr',
        search_kwargs={'k':5, 'lambda_mult': 0.5})
       
    # ill replace the build chain function with update_chain with currently instantiate the model and build chains with the selected model  from dropdown because the build_chain will use the model is was built and initialised previously on and will not take changes
    # def build_chain(self):
    #     # creation of chain which includes prompt and context
    #     # also create history aware retriever
    #     self.history_aware_retriever=create_history_aware_retriever(self.model,self.retriever,self.contextualize_q_prompt)
    #     # create qa chain
    #     self.qa_chain=create_stuff_documents_chain(self.model,self.qa_prompt,output_parser=self.pydantic_parser)
        
    #     # rag chain
    #     self.rag_chain=create_retrieval_chain(self.history_aware_retriever,self.qa_chain)
        
    #     # final chain
    #     self.chain=RunnableWithMessageHistory(
    #         self.rag_chain,
    #         self.get_session_history,
    #         input_messages_key='input',
    #         history_messages_key='chat_history',
    #         output_messages_key='answer'
    #     )
    
    def update_model(self):
        """" Call this function whenever the model cnages in the selection sidebar"""
        
        # re initialise chatgroq instance with the new model name
        self.model=ChatGroq(
            model=st.session_state['selected_model'],
            temperature=0
        )
        
        # rebuild all dependent chains with the new model
        self.history_aware_retriever=create_history_aware_retriever(self.model,self.retriever,self.contextualize_q_prompt)
        
        self.qa_chain=create_stuff_documents_chain(
            self.model,self.qa_prompt,output_parser=self.pydantic_parser
        )
        
        self.rag_chain=create_retrieval_chain(
            self.history_aware_retriever,self.qa_chain
        )
        
        self.chain = RunnableWithMessageHistory(
            self.rag_chain,
            self.get_session_history,
            input_messages_key='input',
            history_messages_key='chat_history',
            output_messages_key='answer'
        )
        
    def ask(self,query):

        start = time.perf_counter()

        with get_usage_metadata_callback() as cb:

            response = self.chain.invoke(
                {"input": query},
                {
                    "configurable": {
                        "session_id": st.session_state["session_id"]
                    }
                }
            )

        latency = (time.perf_counter() - start) * 1000

        # Extract usage
        model_name = list(cb.usage_metadata.keys())[0]

        usage = cb.usage_metadata[model_name]

        input_tokens = usage["input_tokens"]

        output_tokens = usage["output_tokens"]

        total_tokens = usage["total_tokens"]

        # Save to SQLite
        log_id = log_request(
            session_id=st.session_state["session_id"],
            model_name=model_name,
            user_query=query,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            latency_ms=latency
        )

        return {
            "answer": response["answer"],
            "log_id": log_id # in order to keep a track of the id to make changes later like adding feedback etc
        }
    
    # function to get_session_history 
    def get_session_history(self,session_id:str)->BaseChatMessageHistory:
        if session_id not in self.store:
            self.store[session_id]=ChatMessageHistory()
        return self.store[session_id]
    
    def clear(self):
        self.vectorstore = None
        self.retriever = None
        self.history_aware_retriever = None
        self.qa_chain = None
        self.rag_chain = None
        self.chain = None
        self.store.clear()
        
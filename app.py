import streamlit as st
from ragClass import RAG
# import to create table
from database import create_table
# import to get user feedback and update in the table
from database import update_feedback

# import sqlite3

# function to display the conversation messages
def display_messages():
    for message in st.session_state['messages']:
        role=message['role']
        if role=='assistant':
            with st.chat_message(role):
                result=message['content']
                st.title(result.RecipeName)
                st.caption(
                    f"{result.Cuisine} • {result.Course} • {result.Diet}"
                )

                col1, col2, col3 = st.columns(3)

                col1.metric("Prep", f"{result.PrepTime} min")
                col2.metric("Cook", f"{result.CookingTime} min")
                col3.metric("Servings", result.Servings)

                st.subheader("Ingredients")
                for ing in result.Ingredients:
                    st.write(f"• {ing}")

                st.subheader("Instructions")
                for i, step in enumerate(result.Instructions, 1):
                    st.write(f"{i}. {step}")

                st.info(result.Explanation)

                if result.MissingIngredients:
                    st.warning(
                        f"Missing ingredients: {result.MissingIngredients}"
                    )

                st.link_button("View Recipe", result.SourceURL)
        else:
            with st.chat_message(role):
                st.markdown(message['content'])

# callback or function to save feedback
def save_feedback():
    feedback=st.session_state['feedback']
    
    if feedback is None:
        return
    
    # because st.feedback return 1 for thunmbs up and 0 for thumbs down
    # so we convert them to up or down
    if feedback==1:
        value='up'
    else:
        value='down'
        
    update_feedback(
        st.session_state['last_log_id'],
        value
    )

def process_input():
    if prompt:=st.chat_input('Hello! Which recipe do you want?'):
        # dsiplay the user's input
        with st.chat_message('user'):
            st.markdown(prompt)
        # append it to the chat history
        st.session_state.messages.append({'role':'user','content':prompt})
        
        # get assistant's response
        response=st.session_state['assistant'].ask(prompt)
        
        result=response['answer']
        log_id=response['log_id']
        
        # save the log_id for later use
        st.session_state['last_log_id']=log_id
        # with st.chat_message('assistant'):
        #     st.markdown(response)
        with st.chat_message("assistant"):

            st.title(result.RecipeName)

            st.caption(
                f"{result.Cuisine} • {result.Course} • {result.Diet}"
            )

            col1, col2, col3 = st.columns(3)

            col1.metric("Prep", f"{result.PrepTime} min")
            col2.metric("Cook", f"{result.CookingTime} min")
            col3.metric("Servings", result.Servings)

            st.subheader("Ingredients")
            for ing in result.Ingredients:
                st.write(f"• {ing}")

            st.subheader("Instructions")
            for i, step in enumerate(result.Instructions, 1):
                st.write(f"{i}. {step}")

            st.info(result.Explanation)

            if result.MissingIngredients:
                st.warning(
                    f"Missing ingredients: {result.MissingIngredients}"
                )

            st.link_button("View Recipe", result.SourceURL)
            
            # add feedback widget
            st.feedback(
                'thumbs',
                key='feedback',
                on_change=save_feedback
            )
        # append to cht history
        st.session_state.messages.append({'role':'assistant','content':result,'log_id':log_id})


st.set_page_config(page_title='Indian Recipe RAG',layout='wide')  
create_table()  # to create the sql table once and checks whtehr it exists
st.title('Indian Recipe RAG')
        

import uuid
if 'session_id' not in st.session_state:
    st.session_state['session_id']=str(uuid.uuid4())
# st.write(f"Your session id is {st.session_state['session_id']}") # this is just for testing, in production you would not want to display session id to user

# initaiise sesssion state
if 'assistant' not in st.session_state:
    st.session_state['assistant']=RAG()
    st.session_state['messages']=[]
    # st.session_state['last_log_id']=
    
display_messages()
process_input()

#imports
import streamlit as st
import pandas as pd
import plotly_express as px

from database import (
    get_all_logs,
    get_avg_input_tokens,
    get_avg_output_tokens,
    get_avg_latency,
    get_feedback_counts,
    get_model_usage,
    get_total_requests
)

# page title
st.set_page_config(
    page_title='Analytics Dashboard',
    layout='wide'
)
st.title('📊 LLM Monitoring Dashboard')

# KPI cards to show metrics
st.subheader('📈 Overview')
col1,col2,col3,col4=st.columns(4)

with col1:
    st.metric(
        'Total Requests',
        get_total_requests()
    )
col2.metric(
    'Avg Latency',
    f'{get_avg_latency():.2f} ms'
)

col3.metric(
    'Avg Input Tokens',
    f'{get_avg_input_tokens():.0f}'
)

col4.metric(
    'Avg Output tokens',
    f'{get_avg_output_tokens():.0f}'
)

# load logs into a DataFrame to use in plotly
rows=get_all_logs()

columns=[
    'ID',
    'Timestamp',
    'Session',
    'Model',
    'Query',
    'Input Tokens',
    'Output Tokens',
    'Total Tokens',
    'Latency (ms)',
    'Feedback'
]

df=pd.DataFrame(rows,columns=columns)

recent = df.tail(20)

fig = px.line(
    recent,
    x="Timestamp",
    y="Latency (ms)",
    markers=True,
    title="Latency per Request"
)

st.plotly_chart(fig, use_container_width=True)

# charts
# 2columns left and right
left,right=st.columns(2)

with left:
    # chart 1 Token Usage Chart
    st.subheader('🪙 Token Usage')

    fig=px.bar(
        df,
        x='Total Tokens',
        # nbins=20
        orientation='h'
    )
    st.plotly_chart(fig,width='stretch')

    # latency chart
    st.subheader('⚡ Latency')

    fig=px.bar(
        df,
        x='Latency (ms)',
        # nbins=20
        orientation='h'
    )

    st.plotly_chart(fig,width='stretch')

with right:
    # model usage chart
    models=get_model_usage()

    model_df=pd.DataFrame(
        models,
        columns=['Models','Requests']
    )

    fig=px.bar(
        model_df,
        x='Requests',
        y='Models'
    )
    st.subheader("🤖 Model Usage")

    st.plotly_chart(fig,width='stretch')

    # feedback chart
    feedback=get_feedback_counts()

    if feedback:
        feedback_df=pd.DataFrame(
            feedback,
            columns=['Feedback','Count']
        )
        
        fig=px.pie(
            feedback_df,
            names='Feedback',
            values='Count',
            hole=0.5
        )
        st.subheader('👍 User Feedback')
        st.plotly_chart(fig,width='stretch')
    
# recent logs
with st.expander('Recent Requests'):
# st.subheader('📄 Recent Requests')
    st.dataframe(
        df[['Timestamp','Model','Query','Input Tokens','Output Tokens','Total Tokens','Latency (ms)','Feedback']],
        width='stretch'
    )
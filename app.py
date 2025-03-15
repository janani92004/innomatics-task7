import pymongo
import streamlit as st
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import MongoDBChatMessageHistory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate


mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
db = mongo_client["chat_memory"]
collection = db["conversations"]


chat_history = MongoDBChatMessageHistory(
    connection_string="mongodb://localhost:27017/",
    database_name="chat_memory",
    collection_name="conversations",
    session_id="user_123"  
)


memory = ConversationBufferMemory(chat_memory=chat_history, return_messages=True)

llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=GOOGLE API KEY)


prompt = PromptTemplate(
    input_variables=["history", "question"],
    template="You are a Data Science tutor. Answer based on previous conversation: {history}\n\nUser: {question}\nTutor:"
)

chain = LLMChain(llm=llm, prompt=prompt, memory=memory)


st.title("🤖 Conversational AI Data Science Tutor")
st.write("Ask me anything about **Data Science**, and I'll help you!")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_input("Ask a Data Science question:")

if user_input:
    try:
    
        response = chain.run({"history": memory.load_memory_variables({}), "question": user_input})

      
        chat_history.add_user_message(user_input)
        chat_history.add_ai_message(response)

       
        st.session_state.chat_history.append((user_input, response))

     
        for user_msg, bot_reply in st.session_state.chat_history:
            st.write(f"**You:** {user_msg}")
            st.write(f"**Tutor:** {bot_reply}")

    except Exception as e:
        st.error(f"⚠️ An error occurred: {e}")


if st.button("Reset Chat Memory"):
    chat_history.clear()
    st.session_state.chat_history = []
    st.success("✅ Chat memory cleared!")

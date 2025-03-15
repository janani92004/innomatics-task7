import pymongo
import streamlit as st
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import MongoDBChatMessageHistory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Load environment variables (API Key)

# MongoDB Connection
mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
db = mongo_client["chat_memory"]
collection = db["conversations"]

# Store chat history in MongoDB
chat_history = MongoDBChatMessageHistory(
    connection_string="mongodb://localhost:27017/",
    database_name="chat_memory",
    collection_name="conversations",
    session_id="user_123"  # Change for unique users
)

# Initialize Memory for Chat History
memory = ConversationBufferMemory(chat_memory=chat_history, return_messages=True)

# Initialize Gemini 1.5 Pro Model
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=GOOGLE API KEY)

# Define a simple conversational prompt
prompt = PromptTemplate(
    input_variables=["history", "question"],
    template="You are a Data Science tutor. Answer based on previous conversation: {history}\n\nUser: {question}\nTutor:"
)

# Create an LLM Chain (without retrieval)
chain = LLMChain(llm=llm, prompt=prompt, memory=memory)

# Streamlit UI
st.title("🤖 Conversational AI Data Science Tutor")
st.write("Ask me anything about **Data Science**, and I'll help you!")

# Session State for Chat History
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# User Input
user_input = st.text_input("Ask a Data Science question:")

if user_input:
    try:
        # Get AI Response
        response = chain.run({"history": memory.load_memory_variables({}), "question": user_input})

        # Store user query & response in MongoDB
        chat_history.add_user_message(user_input)
        chat_history.add_ai_message(response)

        # Save chat history in Streamlit session
        st.session_state.chat_history.append((user_input, response))

        # Display chat history
        for user_msg, bot_reply in st.session_state.chat_history:
            st.write(f"**You:** {user_msg}")
            st.write(f"**Tutor:** {bot_reply}")

    except Exception as e:
        st.error(f"⚠️ An error occurred: {e}")

# Reset Chat History Button
if st.button("Reset Chat Memory"):
    chat_history.clear()
    st.session_state.chat_history = []
    st.success("✅ Chat memory cleared!")

import streamlit as st
import ollama

st.set_page_config(page_title="Sovereign Hub", page_icon="🤖", layout="wide")
st.title("🤖 Pratham's Sovereign Intelligence Hub")
st.sidebar.success("Select a brain module above.")

# FIXED: Initializing chat memory as an empty list to avoid SyntaxError
if "messages" not in st.session_state:
    st.session_state.messages =

# Display conversation history
for msg in st.session_state.messages:
    with st.chat_message(msg['role']):
        st.write(msg['content'])

if prompt := st.chat_input("Command the Swarm..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    # Calls your local LLaMA 3.2 brain
    try:
        response = ollama.chat(model='llama3.2', messages=[{'role': ''content': prompt}])
        reply = response['message']['content']
    except Exception as e:
        reply = f"System Error: {e}. Check if 'ollama serve' is active."
        
    with st.chat_message("assistant"):
        st.write(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})

import os
import streamlit as st
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Load Together.ai API Key from .env
load_dotenv()
together_api_key = os.getenv("TOGETHER_API_KEY")  # Use this instead of OPENAI_API_KEY

# Initialize LangChain LLM using Together.ai endpoint
llm = ChatOpenAI(
    temperature=0.7,
    openai_api_key=together_api_key,
    openai_api_base="https://api.together.xyz/v1",
    model_name="meta-llama/Llama-3-8b-chat-hf"
)

# Prompt Template
recipe_prompt = PromptTemplate(
    input_variables=["ingredients"],
    template="""
You are a helpful recipe assistant.
Generate a step-by-step cooking recipe using the following ingredients: {ingredients}.
Ensure it is easy to follow, includes measurements, and give the name of the dish.
If the ingredients are too few, be creative!
"""
)

# LangChain Chain
recipe_chain = LLMChain(llm=llm, prompt=recipe_prompt)

# Streamlit UI
st.set_page_config(page_title="Smart Recipe Generator", page_icon="🍳", layout="centered")
st.title("🍳 Smart Recipe Generator")
st.markdown("Enter your available ingredients and get a delicious recipe!")

ingredients = st.text_area("📝 Ingredients (comma-separated)", placeholder="e.g. tomato, cheese, pasta, onion")

if st.button("Generate Recipe"):
    if ingredients.strip() == "":
        st.warning("Please enter at least one ingredient.")
    else:
        with st.spinner("Cooking up something delicious..."):
            response = recipe_chain.run(ingredients=ingredients)
            st.markdown("### 🍽️ Your Recipe:")
            st.success(response)
# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; font-size: 16px;'>"
    "Powered by <b>Mohit Sharma</b> ❤️"
    "</div>",
    unsafe_allow_html=True
)

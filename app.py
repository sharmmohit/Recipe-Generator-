import os
import streamlit as st
from fpdf import FPDF
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Load Together.ai API Key from .env
load_dotenv()
together_api_key = os.getenv("TOGETHER_API_KEY")

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

# Initialize recipe as a session state variable
if "recipe" not in st.session_state:
    st.session_state.recipe = ""

if st.button("Generate Recipe"):
    if ingredients.strip() == "":
        st.warning("Please enter at least one ingredient.")
    else:
        with st.spinner("Cooking up something delicious..."):
            response = recipe_chain.run(ingredients=ingredients)
            st.session_state.recipe = response
            st.markdown("### 🍽️ Your Recipe:")
            st.success(response)

# Function to generate PDF
def generate_pdf(recipe_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, recipe_text)
    pdf_path = "recipe.pdf"
    pdf.output(pdf_path)
    return pdf_path

# Show download button only if recipe was generated
if st.session_state.recipe:
    pdf_file = generate_pdf(st.session_state.recipe)
    with open(pdf_file, "rb") as f:
        st.download_button(
            label="📥 Download Recipe as PDF",
            data=f,
            file_name="recipe.pdf",
            mime="application/pdf"
        )

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; font-size: 16px;'>"
    "Powered by <b>Mohit Sharma</b> ❤️"
    "</div>",
    unsafe_allow_html=True
)

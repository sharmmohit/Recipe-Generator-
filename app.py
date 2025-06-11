import os
import streamlit as st
from fpdf import FPDF
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Load API Key
load_dotenv()
together_api_key = os.getenv("TOGETHER_API_KEY")

# Initialize LangChain LLM
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

# Streamlit App Config
st.set_page_config(page_title="Smart Recipe Generator", page_icon="🍳", layout="centered")
st.title("🍳 Smart Recipe Generator")
st.markdown("Enter your available ingredients and get a delicious recipe!")

# Initialize session history
if "history" not in st.session_state:
    st.session_state.history = []

# Text input
ingredients = st.text_area("📝 Ingredients (comma-separated)", placeholder="e.g. tomato, cheese, pasta, onion")

recipe = ""

# Generate recipe
if st.button("Generate Recipe"):
    if ingredients.strip() == "":
        st.warning("Please enter at least one ingredient.")
    else:
        with st.spinner("Cooking up something delicious..."):
            recipe = recipe_chain.run(ingredients=ingredients)
            st.success("✅ Recipe generated!")
            st.markdown("### 🍽️ Your Recipe:")
            st.markdown(recipe)

            # Add to history
            st.session_state.history.append({
                "ingredients": ingredients,
                "recipe": recipe
            })

# PDF generation function
def generate_pdf(recipe_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, recipe_text)
    pdf_path = "recipe.pdf"
    pdf.output(pdf_path)
    return pdf_path

# Show PDF download button if a recipe was generated
if recipe:
    pdf_file = generate_pdf(recipe)
    with open(pdf_file, "rb") as f:
        st.download_button(
            label="📥 Download Recipe as PDF",
            data=f,
            file_name="recipe.pdf",
            mime="application/pdf"
        )

# Display history
if st.session_state.history:
    st.markdown("## 🕘 Recipe History")
    for i, item in enumerate(reversed(st.session_state.history), 1):
        with st.expander(f"🔹 Recipe #{len(st.session_state.history) - i + 1} (Ingredients: {item['ingredients']})"):
            st.markdown(item["recipe"])

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; font-size: 16px;'>"
    "Powered by <b>Mohit Sharma</b> ❤️"
    "</div>",
    unsafe_allow_html=True
)

import os
import base64
import streamlit as st
from fpdf import FPDF
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Load API key
load_dotenv()
together_api_key = os.getenv("TOGETHER_API_KEY")

# Session state setup
if 'show_recipe' not in st.session_state:
    st.session_state.show_recipe = False
if 'generated_recipe' not in st.session_state:
    st.session_state.generated_recipe = ""
if 'ingredients' not in st.session_state:
    st.session_state.ingredients = ""

# Background styling
def set_bg(image_path):
    with open(image_path, "rb") as img:
        b64_img = base64.b64encode(img.read()).decode()
    st.markdown(
        f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background: url("data:image/png;base64,{b64_img}") no-repeat center center fixed;
            background-size: cover;
        }}
        [data-testid="stHeader"], [data-testid="stToolbar"] {{
            background: transparent;
        }}
        .title-container {{
            text-align: center;
            margin-bottom: 10px;
            padding: 5px 0;
        }}
        .title-container h1 {{
            font-size: 28px;
            color: white;
            margin-bottom: 5px;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
        }}
        .title-container p {{
            font-size: 16px;
            color: white;
            margin-top: 0;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        }}
        .input-container {{
            width: 280px;
            margin: 0 auto;
            text-align: center;
        }}
        .stTextArea > div > div > textarea {{
            background-color: rgba(255, 255, 255, 0.9) !important;
            color: black !important;
            border-radius: 8px !important;
            height: 40px !important;
            width: 100% !important;
            font-size: 13px !important;
            padding: 6px 10px !important;
            margin: 0 auto !important;
            resize: none !important;
        }}
        .stButton > button {{
            background-color: #ff7043;
            color: white;
            font-weight: bold;
            padding: 8px 20px;
            border-radius: 8px;
            font-size: 14px;
            margin: 10px auto;
            display: block;
            width: fit-content;
        }}
        .recipe-container {{
            background-color: transparent !important;
            padding: 15px;
            margin: 10px auto 20px auto !important;
            color: white !important;
            width: 85%;
            max-width: 800px;
        }}
        .stMarkdown {{
            background-color: transparent !important;
        }}
        .stMarkdown p, .stMarkdown li, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
            color: white !important;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
            margin-top: 5px !important;
            margin-bottom: 5px !important;
        }}
        .footer {{
            text-align: center;
            position: fixed;
            bottom: 15px;
            left: 0;
            width: 100%;
            color: white;
            font-size: 13px;
            text-shadow: 1px 1px 2px black;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Set page config
st.set_page_config(page_title="Smart Recipe Generator", layout="wide")
set_bg("images/bg.png")

def generate_recipe(ingredients):
    llm = ChatOpenAI(
        temperature=0.7,
        openai_api_key=together_api_key,
        openai_api_base="https://api.together.xyz/v1",
        model_name="meta-llama/Llama-3-8b-chat-hf"
    )
    prompt_template = PromptTemplate(
        input_variables=["ingredients"],
        template="""
        Generate a clear recipe with these sections:
        1. [Dish Name] (as ## heading)
        2. Ingredients (as bullet points)
        3. Instructions (as numbered steps)
        
        Use these ingredients: {ingredients}
        """
    )
    recipe_chain = LLMChain(llm=llm, prompt=prompt_template)
    return recipe_chain.run(ingredients=ingredients)

# Main Page
def main_page():
    st.markdown(
        """
        <div class="title-container">
            <h1>Smart Recipe Generator</h1>
            <p>Turn your ingredients into delicious meals</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    ingredients = st.text_area("Ingredients", placeholder="Enter ingredients (e.g., tomato, onion, pasta)", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("Generate Recipe"):
        if not ingredients.strip():
            st.warning("Please enter some ingredients.")
        else:
            st.session_state.ingredients = ingredients
            st.session_state.show_recipe = True
            st.experimental_rerun()

# Recipe Page
def recipe_page():
    with st.spinner("Generating your recipe..."):
        if not st.session_state.generated_recipe:
            st.session_state.generated_recipe = generate_recipe(st.session_state.ingredients)
    
    st.components.v1.html("<script>window.scrollTo(0, 0);</script>", height=0)

    st.markdown(
        """
        <div style="margin-top: -20px;">
            <div class="title-container">
                <h1>Your Generated Recipe</h1>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("""
        <div class="recipe-container">
    """, unsafe_allow_html=True)
    st.markdown(st.session_state.generated_recipe)
    st.markdown("</div>", unsafe_allow_html=True)

    col1, col2 = st.columns([1,1])
    with col1:
        def save_pdf(text):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, text)
            path = "recipe.pdf"
            pdf.output(path)
            return path

        pdf_file = save_pdf(st.session_state.generated_recipe)
        with open(pdf_file, "rb") as f:
            st.download_button("📥 Download PDF", f, file_name="recipe.pdf", mime="application/pdf")
    
    with col2:
        if st.button("← Generate Another Recipe"):
            st.session_state.show_recipe = False
            st.session_state.generated_recipe = ""
            st.experimental_rerun()

# Footer
st.markdown('<div class="footer">Powered by <b>Mohit Sharma</b> ❤️</div>', unsafe_allow_html=True)

# Page Routing
if st.session_state.show_recipe:
    recipe_page()
else:
    main_page()
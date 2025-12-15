import streamlit as st
import pandas as pd
from dotenv import load_dotenv, find_dotenv
import os
from openai import OpenAI


st.set_page_config(
    page_title="Coffee Shop AI Assistant",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)


def load_css(path: str):
    if os.path.exists(path):
        with open(path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("styles/coffee_theme.css")

load_dotenv(find_dotenv())
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

USE_AI = False
client = None

if OPENAI_KEY:
    try:
        client = OpenAI(api_key=OPENAI_KEY)
        USE_AI = True
    except Exception:
        USE_AI = False

@st.cache_data
def load_data():
    ingredients = pd.read_csv("data/ingredients.csv")
    inventory = pd.read_csv("data/inventory.csv")
    items = pd.read_csv("data/items.csv")
    orders = pd.read_csv("data/orders.csv")
    recipe = pd.read_csv("data/recipe.csv")
    rota = pd.read_csv("data/rota.csv")
    shift = pd.read_csv("data/shift.csv")
    staff = pd.read_csv("data/staff.csv")
    return ingredients, inventory, items, orders, recipe, rota, shift, staff

ingredients, inventory, items, orders, recipe, rota, shift, staff = load_data()
merged = orders.merge(items, on="item_id", how="left")

st.markdown("""
<div class="main-header">
    <h1>☕ Coffee Shop AI Assistant</h1>
    <p>Explore menu items and orders intelligently</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🎛 Control Panel")

    if USE_AI:
        st.success("✅ OpenAI Connected")
        st.caption(f"Key: {OPENAI_KEY[:8]}...")
    else:
        st.warning("⚠ OpenAI Disabled (No Key / Billing)")

    st.markdown("---")

    show_dataset = st.checkbox("📊 Show Dataset Explorer", False)
    use_ai = st.checkbox("🤖 Enable AI Answer", USE_AI)

    st.markdown("---")
    st.markdown("### 💡 Try asking:")
    st.markdown("""
    - Cold drinks  
    - Hot drinks  
    - Show all drinks  
    - Latte  
    """)


COLD_KEYWORDS = ["cold", "iced", "ice", "frappe"]
HOT_KEYWORDS = ["hot", "warm"]

def simple_chatbot(question: str):
    q = question.lower()

    if any(k in q for k in COLD_KEYWORDS):
        df = merged[merged["item_name"].str.contains("|".join(COLD_KEYWORDS), case=False, na=False)]
        return df[["item_name"]].drop_duplicates() if not df.empty else "❄ No cold drinks found."

    if any(k in q for k in HOT_KEYWORDS):
        df = merged[merged["item_name"].str.contains("|".join(HOT_KEYWORDS), case=False, na=False)]
        return df[["item_name"]].drop_duplicates() if not df.empty else "🔥 No hot drinks found."

    if "menu" in q or "drink" in q:
        return pd.DataFrame({"Available Drinks": merged["item_name"].unique()})

    results = merged[merged.apply(lambda r: q in str(r).lower(), axis=1)]
    return results if not results.empty else "❌ No matching results."


tab1, tab2 = st.tabs(["💬 Chatbot", "📊 Data Explorer"])


with tab1:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)

    query = st.text_input(
        "Ask something about the menu",
        placeholder="e.g. Show me cold drinks",
        label_visibility="collapsed"
    )

    col1, col2, col3, col4 = st.columns(4)
    if col1.button("🧊 Cold Drinks"):
        query = "cold drinks"
    if col2.button("☕ Hot Drinks"):
        query = "hot drinks"
    if col3.button("📜 Full Menu"):
        query = "show all drinks"
    if col4.button("🔄 Clear"):
        query = ""

    st.markdown("</div>", unsafe_allow_html=True)

    if query:
        st.markdown("### 🔍 Results")
        result = simple_chatbot(query)

        if isinstance(result, pd.DataFrame):
            st.dataframe(result, use_container_width=True)
        else:
            st.info(result)


        if use_ai and USE_AI:
            st.markdown("### 🤖 AI Explanation")

            try:
                prompt = f"""
You are a helpful coffee shop assistant.
Answer clearly and briefly using ONLY the dataset below.

DATA:
{merged.head(30).to_string()}

QUESTION:
{query}
"""

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a coffee shop AI assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3
                )

                st.markdown(
                    f"<div class='info-card'>{response.choices[0].message.content}</div>",
                    unsafe_allow_html=True
                )

            except Exception as e:
                st.error("❌ OpenAI Error. Check API key or billing.")


with tab2:
    if show_dataset:
        st.markdown("### 📋 Dataset Overview")

        t1, t2, t3 = st.tabs(["Orders", "Inventory", "Staff"])

        with t1:
            st.dataframe(merged.head(50), use_container_width=True)

        with t2:
            st.dataframe(inventory.head(50), use_container_width=True)

        with t3:
            st.dataframe(staff.head(50), use_container_width=True)
    else:
        st.info("Enable dataset view in the sidebar")


st.markdown("""
<hr>
<div style="text-align:center;color:#8B4513;">
    ☕ Coffee Shop AI Assistant — Streamlit App
</div>
""", unsafe_allow_html=True)

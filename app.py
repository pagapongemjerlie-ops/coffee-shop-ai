import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Coffee Shop Dashboard", page_icon="☕", layout="wide")

st.title("☕ Coffee Shop Analytics & Chatbot")

# ===============================
# LOAD DATA
# ===============================
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

# Merge orders with items
merged = orders.merge(items, on="item_id", how="left")

# ===============================
# SIDEBAR MENU
# ===============================
st.sidebar.title("📌 Navigation")
page = st.sidebar.radio("Go to:", ["Dashboard", "Orders Table", "Chatbot"])

# ===============================
# DASHBOARD PAGE
# ===============================
if page == "Dashboard":
    st.header("📊 Sales Dashboard")

    # Total Orders
    total_orders = len(orders)
    total_items = merged["item_name"].nunique()

    col1, col2 = st.columns(2)
    col1.metric("Total Orders", total_orders)
    col2.metric("Unique Items Sold", total_items)

    # ==========================
    # Bar Chart - Most Ordered Drinks
    # ==========================
    drink_counts = merged["item_name"].value_counts().reset_index()
    drink_counts.columns = ["Drink", "Count"]

    fig = px.bar(drink_counts, x="Drink", y="Count", title="Most Ordered Drinks")
    st.plotly_chart(fig, use_container_width=True)

# ===============================
# ORDERS TABLE PAGE
# ===============================
elif page == "Orders Table":
    st.header("📋 Orders Preview")
    st.write(merged.head(20))

# ===============================
# CHATBOT PAGE
# ===============================
elif page == "Chatbot":
    st.header("🤖 Open Chatbot")

    st.info("Click the button below to run the Coffee Shop Chatbot.")
    
    st.write("➡ Run this command in another terminal window:")
    st.code("streamlit run chatbot.py")

    st.success("Chatbot code is ready! Just run it separately.")

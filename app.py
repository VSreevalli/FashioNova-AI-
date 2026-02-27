import streamlit as st 
from PIL import Image
import io
import uuid
import random   
from urllib.parse import quote_plus, urlencode
from dotenv import load_dotenv
from groq import Groq
from model.image_generator import generate_image
import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()  # loads .env file

HF_TOKEN = os.getenv("HF_TOKEN")

hf_client = InferenceClient(
    provider="fal-ai",
    api_key=HF_TOKEN
)

# ==============================
# 🔐 Load API Keys
# ==============================
load_dotenv()
hf_token = os.getenv("HF_TOKEN")
hf_client = InferenceClient(api_key=hf_token)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ==============================
# 🎨 Page Config
# ==============================
st.set_page_config(page_title="FashioNova AI : AI Fashion Stylist", layout="wide")

# ==============================
# 💎 Top Split Layout
# ==============================
left_col, right_col = st.columns([1, 1])

with left_col:
    st.markdown("# 👗 FashioNova AI - AI Fashion Stylist")
    st.markdown("### Your Smart Personal Fashion Assistant ✨")
    st.write(
        "Welcome! Discover outfit ideas, get styling inspiration, "
        "and generate stunning fashion looks instantly. 💃🕺"
    )

    quotes = [
        "Fashion is the armor to survive the reality of everyday life.",
        "Style is a way to say who you are without speaking.",
        "Elegance is not standing out, but being remembered.",
        "Dress like you're already famous.",
        "Confidence is the best outfit. Rock it and own it."
    ]
    st.markdown("#### 💬 Fashion Quote")
    st.info(random.choice(quotes))

    tips = [
        "Balance your outfit — if your top is loose, go for fitted bottoms.",
        "Neutral colors are timeless and easy to mix and match.",
        "Accessories can completely transform a simple outfit.",
        "Confidence is your strongest style statement.",
        "Choose outfits based on occasion and comfort."
    ]
    st.markdown("#### 🌟 Fashion Tip")
    st.success(random.choice(tips))


with right_col:
    outfits = [
        {
            "title": "🌸 Casual Chic",
            "desc": "White oversized shirt + Blue straight jeans + White sneakers",
            "img": "https://images.unsplash.com/photo-1520975922284-8b456906c813?w=800"
        },
        {
            "title": "🖤 Evening Elegance",
            "desc": "Black midi dress + Heels + Minimal gold jewelry",
            "img": "https://images.unsplash.com/photo-1495121605193-b116b5b09a75?w=800"
        },
        {
            "title": "💼 Smart Office Look",
            "desc": "Beige blazer + Black trousers + Loafers",
            "img": "https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?w=800"
        }
    ]

    selected_outfit = random.choice(outfits)
    random_price = round(random.uniform(500, 5000), 2)

    st.markdown("## 💎 Outfit of the Day")
    st.image(selected_outfit["img"], width=700)
    st.markdown(f"### {selected_outfit['title']}")
    st.write(selected_outfit["desc"])
    st.markdown(f"**💰 Price:** ₹{random_price}")

st.divider()

# ==============================
# 📦 Session State Defaults
# ==============================
defaults = {
    "design_history": [],
    "chat_messages": [],
    "current_image": None,
    "last_prompt": None,
    "chat_generate_trigger": False,
    "shared_designs": {},
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ==============================
# 🔗 SHARE LINK VIEWER
# ==============================
query_params = st.query_params
if "share" in query_params:
    share_id = query_params["share"]
    if share_id in st.session_state.shared_designs:
        item = st.session_state.shared_designs[share_id]
        st.header("🔗 Shared Design")
        st.image(item["image"], width=700)
        st.markdown(f"**💰 Price:** ₹{item.get('price', 'N/A')}")
        st.code(item["prompt"])
        st.stop()

# ==============================
# 🖼 Display Design Function
# ==============================
def display_design(item, unique_key=""):
    image = item["image"]
    prompt = item["prompt"]
    links = item["links"]

    link_prices = item.get("link_prices", {})
    if not link_prices:
        link_prices = {name: round(random.uniform(500, 5000), 2) for name in links.keys()}
        item["link_prices"] = link_prices

    price = item.get("price", round(random.uniform(500, 5000), 2))

    col1, col2 = st.columns([2, 1])

    with col1:
        if isinstance(image, Image.Image):
            image = image.copy()
            image.thumbnail((1024, 1024), Image.LANCZOS)
        st.image(image, caption="Generated Design", use_column_width=True)
        st.markdown("### 📝 Prompt Used")
        st.code(prompt)
        st.markdown(f"**💰 Design Price:** ₹{price}")

    with col2:
        st.subheader("🛍 Similar Products")
        for name, link in links.items():
            st.markdown(f"**{name} — Price: ₹{link_prices[name]}**")
            st.markdown(f"[View Products]({link})")
            st.text_input("Copy Link", link, key=f"{unique_key}_{name}", disabled=True)
            st.markdown("---")

        buf = io.BytesIO()
        image.save(buf, format="PNG")
        st.download_button(
            "📥 Download Image",
            buf.getvalue(),
            f"{unique_key}.png",
            "image/png",
            key=f"download_{unique_key}"
        )

        if st.button("🔗 Generate Share Link", key=f"share_{unique_key}"):
            share_id = str(uuid.uuid4())
            st.session_state.shared_designs[share_id] = item
            share_url = f"?{urlencode({'share': share_id})}"
            st.success("Copy this link:")
            st.code(share_url)

# ==============================
# 🎨 Design Generator Inputs
# ==============================
col1, col2 = st.columns(2)
with col1:
    user_prompt = st.text_input("Describe your fashion idea")
    category = st.selectbox("Category", ["Women", "Men", "Girls", "Boys", "Other"])
    if category == "Other":
        category = st.text_input("Enter Custom Category")

    style = st.selectbox("Style", ["Casual", "Party", "Ethnic", "Formal", "Other"])
    if style == "Other":
        style = st.text_input("Enter Custom Style")

    fabric = st.selectbox("Fabric", ["Cotton", "Silk", "Denim", "Wool", "Other"])
    if fabric == "Other":
        fabric = st.text_input("Enter Custom Fabric")

    pattern = st.selectbox("Pattern", ["Solid", "Floral", "Striped", "Printed", "Other"])
    if pattern == "Other":
        pattern = st.text_input("Enter Custom Pattern")

with col2:
    occasion = st.selectbox("Occasion", ["College", "Office", "Wedding", "Party", "Other"])
    if occasion == "Other":
        occasion = st.text_input("Enter Custom Occasion")

    body_type = st.selectbox("Body Type", ["Slim", "Athletic", "Curvy", "Plus Size", "Other"])
    if body_type == "Other":
        body_type = st.text_input("Enter Custom Body Type")

    size = st.selectbox("Size", ["XS", "S", "M", "L", "XL", "Other"])
    if size == "Other":
        size = st.text_input("Enter Custom Size")

    color_name = st.selectbox(
        "Color Name",
        ["Red","Blue","Black","White","Pink","Green","Yellow",
         "Purple","Orange","Brown","Other"]
    )
    if color_name == "Other":
        color_name = st.text_input("Enter Custom Color Name")

    color_hex = st.color_picker("Pick Exact Color", "#ff69b4")
    budget_min, budget_max = st.slider("Budget Range (₹)", 500, 10000, (1000, 5000))

# ==============================
# 🎨 Generate Design Function (Improved Faces)
# ==============================
def generate_design_from_prompt(prompt_text):
    enhanced_prompt = f"""
    {prompt_text}
    High-resolution, ultra realistic full body fashion model, 1024x1024,
    perfect anatomy, centered, studio lighting,
    ultra realistic face, natural expression, symmetrical eyes, realistic hands, no extra limbs
    """
    with st.spinner("Generating design..."):
        try:
            images = [generate_image(enhanced_prompt) for _ in range(3)]
            image = images[0]
        except Exception as e:
            st.error(f"Error generating image: {e}")
            return

    price = round(random.uniform(1000, 5000), 2)
    links = {
        "Amazon": "https://www.amazon.in/s?k=" + quote_plus(enhanced_prompt),
        "Flipkart": "https://www.flipkart.com/search?q=" + quote_plus(enhanced_prompt),
        "Myntra": "https://www.myntra.com/search?q=" + quote_plus(enhanced_prompt),
    }

    item = {
        "prompt": enhanced_prompt,
        "image": image,
        "links": links,
        "price": price
    }
    st.session_state.design_history.append(item)
    st.session_state.current_image = image
    st.session_state.last_prompt = enhanced_prompt

# ==============================
# Main Buttons
# ==============================
if st.button("🎨 Generate Design") and user_prompt.strip():
    generate_design_from_prompt(user_prompt)

if st.session_state.last_prompt and st.button("🔄 Regenerate Last Design"):
    generate_design_from_prompt(st.session_state.last_prompt)

if st.session_state.design_history:
    display_design(st.session_state.design_history[-1], unique_key="main")

# ==============================
# Design History
# ==============================
st.subheader("📚 Design History")
for i, item in enumerate(reversed(st.session_state.design_history)):
    index = len(st.session_state.design_history) - 1 - i
    with st.expander(f"Design {index+1}"):
        display_design(item, unique_key=f"history_{index}")
        if st.button("❌ Delete This Design", key=f"delete_{index}"):
            st.session_state.design_history.pop(index)
            st.rerun()

if st.button("🗑 Clear Full Design History"):
    st.session_state.design_history = []
    st.session_state.current_image = None
    st.session_state.last_prompt = None
    st.rerun()

# ==============================
# 🤖 Sidebar Chatbot
# ==============================
with st.sidebar:
    st.markdown("## 🤖 AI Style Assistant")
    st.markdown("Your Personal Fashion Helper ✨")
    st.divider()
    st.markdown("### 💬 Chat With AI")

    chat_input = st.text_input("Ask for styling advice", key="chat_input")
    if st.button("▶ Send Suggestion"):
        if chat_input.strip():
            st.session_state.chat_messages.append({"role": "user", "content": chat_input})
            with st.spinner("AI is thinking..."):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=st.session_state.chat_messages,
                    temperature=0.7,
                )
                ai_reply = response.choices[0].message.content
                st.session_state.chat_messages.append({"role": "assistant", "content": ai_reply})

    st.sidebar.markdown("### 💬 Chat History")
    for msg in st.session_state.chat_messages:
        if msg["role"] == "user":
            st.sidebar.markdown(f"**🧑 You:** {msg['content']}")
        else:
            st.sidebar.markdown(f"**🤖 AI:** {msg['content']}")

    if st.session_state.chat_messages:
        last_ai_msg = st.session_state.chat_messages[-1]["content"]
        if st.button("🎨 Generate Dress From Suggestion"):
            generate_design_from_prompt(last_ai_msg)

    if st.sidebar.button("🗑 Clear Full Chat"):
        st.session_state.chat_messages = []
        st.rerun()
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from collections import Counter

st.set_page_config(
    page_title="RESTAURANT DATA ANALYSIS AND VISUALIZATION DASHBOARD",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton>button {
        background-color: #ff6b6b;
        color: white;
        border-radius: 10px;
        padding: 10px 24px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #ff5252;
    }
    h1 {
        color: #cb202d;
        text-align: center;
        padding: 20px;
        background: linear-gradient(90deg, #cb202d 0%, #ff6b6b 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    h2, h3 {
        color: #2c3e50;
    }
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv("zomato.csv")
    df.drop_duplicates(inplace=True)
    df.dropna(subset=["rate", "cuisines"], inplace=True)
    df = df[df["rate"].str.contains(r'\d', na=False)]
    df["rate"] = df["rate"].str.split("/").str[0].astype(float)
    df["approx_cost(for two people)"] = (
        df["approx_cost(for two people)"].str.replace(",", "").astype(float)
    )
    return df

df = load_data()

def categorize_sentiment(rating):
    if rating >= 4.0:
        return 'Positive'
    elif rating >= 3.0:
        return 'Neutral'
    else:
        return 'Negative'

df['sentiment'] = df['rate'].apply(categorize_sentiment)

st.title("🍽️ RESTAURANT DATA ANALYSIS AND VISUALIZATION DASHBOARD")



st.markdown("<p style='text-align: center; color: #7f8c8d; font-size: 14px;'>done with zomato dataset</p>", unsafe_allow_html=True)
st.markdown("---")

st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/7/75/Zomato_logo.png", use_container_width=True)
st.sidebar.header("🎯 Filters")
selected_location = st.sidebar.selectbox(
    "📍 Choose a Location", 
    sorted(df["location"].dropna().unique()),
    help="Select a location to filter the data"
)

st.sidebar.markdown("---")
min_rating = st.sidebar.slider(" Minimum Rating", 0.0, 5.0, 0.0, 0.5)
max_cost = st.sidebar.slider(" Maximum Cost (for two)", 0, int(df["approx_cost(for two people)"].max()), int(df["approx_cost(for two people)"].max()))

filtered_df = df[
    (df["location"] == selected_location) & 
    (df["rate"] >= min_rating) &
    (df["approx_cost(for two people)"] <= max_cost)
]

st.header(" Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(" Total Restaurants", filtered_df.shape[0])
with col2:
    st.metric(" Average Rating", f"{filtered_df['rate'].mean():.2f}")
with col3:
    st.metric(" Avg Cost (for 2)", f"₹{filtered_df['approx_cost(for two people)'].mean():.0f}")
with col4:
    online_pct = (filtered_df['online_order'] == 'Yes').sum() / len(filtered_df) * 100
    st.metric(" Online Orders", f"{online_pct:.1f}%")

st.markdown("---")

with st.expander(" Dataset Overview", expanded=False):
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Shape (rows, columns):**", filtered_df.shape)
        st.write("**Column Info:**")
        st.dataframe(pd.DataFrame({
            "Column": filtered_df.columns,
            "Data Type": filtered_df.dtypes.values,
            "Missing Values": filtered_df.isnull().sum().values
        }), use_container_width=True)
    
    with col2:
        st.write("**Summary Statistics (Numeric Columns):**")
        st.dataframe(filtered_df.describe(), use_container_width=True)

st.header(" Sample Data Preview")
sample_size = st.slider("Select number of rows to preview", 5, 50, 10)

preview_df = filtered_df.head(sample_size).copy()
cols = preview_df.columns.tolist()

if 'name' in cols and 'url' in cols:
    name_idx = cols.index('name')
    url_idx = cols.index('url')
     
    cols[name_idx], cols[url_idx] = cols[url_idx], cols[name_idx]
    preview_df = preview_df[cols]

st.dataframe(preview_df, use_container_width=True, height=400)

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader(" Top 10 Popular Cuisines")
    cuisines = filtered_df["cuisines"].dropna().str.split(", ")
    cuisine_list = [c for sub in cuisines for c in sub]
    cuisine_count = pd.Series(Counter(cuisine_list)).nlargest(10)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    cuisine_count.plot(kind="barh", ax=ax, color='#ff6b6b')
    ax.set_xlabel("Count", fontsize=12)
    ax.set_ylabel("Cuisine", fontsize=12)
    ax.set_title("Top 10 Cuisines", fontsize=14, fontweight='bold')
    plt.tight_layout()
    st.pyplot(fig)

with col2:
    st.subheader(" Rating Distribution")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(filtered_df["rate"], bins=20, kde=True, ax=ax, color='#4ecdc4')
    ax.set_xlabel("Rating", fontsize=12)
    ax.set_ylabel("Frequency", fontsize=12)
    ax.set_title("Distribution of Ratings", fontsize=14, fontweight='bold')
    plt.tight_layout()
    st.pyplot(fig)

st.markdown("---")

col3, col4 = st.columns(2)

with col3:
    st.subheader(" Online Order vs Ratings")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(x="online_order", y="rate", data=filtered_df, ax=ax, palette="Set2")
    ax.set_xlabel("Online Order Available", fontsize=12)
    ax.set_ylabel("Rating", fontsize=12)
    ax.set_title("Rating Comparison: Online vs Offline", fontsize=14, fontweight='bold')
    plt.tight_layout()
    st.pyplot(fig)

with col4:
    st.subheader(" Cost vs Rating")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(
        x="approx_cost(for two people)", y="rate", data=filtered_df, alpha=0.5, ax=ax, color='#ff6b6b'
    )
    ax.set_xlabel("Approximate Cost (for two)", fontsize=12)
    ax.set_ylabel("Rating", fontsize=12)
    ax.set_title("Cost vs Rating Analysis", fontsize=14, fontweight='bold')
    plt.tight_layout()
    st.pyplot(fig)

st.markdown("---")
col5, col6 = st.columns(2)

with col5:
    st.subheader(" Sentiment Distribution")
    sentiment_counts = filtered_df['sentiment'].value_counts()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sentiment_counts.plot(kind='pie', ax=ax, autopct='%1.1f%%', 
                          colors=['#90EE90', '#FFD700', '#FF6B6B'],
                          startangle=90)
    ax.set_ylabel('')
    ax.set_title('Restaurant Sentiment Breakdown', fontsize=14, fontweight='bold')
    plt.tight_layout()
    st.pyplot(fig)

with col6:
    st.subheader(" Sentiment by Location")
    sentiment_by_location = filtered_df.groupby(['location', 'sentiment']).size().unstack(fill_value=0)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sentiment_by_location.plot(kind='bar', ax=ax, stacked=True,
                               color=['#FF6B6B', '#FFD700', '#90EE90'])
    ax.set_xlabel('Location', fontsize=12)
    ax.set_ylabel('Number of Restaurants', fontsize=12)
    ax.set_title('Sentiment Distribution by Location', fontsize=14, fontweight='bold')
    ax.legend(title='Sentiment')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)

st.subheader(" Top 20 Restaurants and Their Cuisines")
top_rests = (
    filtered_df.sort_values('rate', ascending=False)
    .groupby("name")[["cuisines", "rate", "approx_cost(for two people)"]]
    .first()
    .reset_index()
    .head(20)
)
top_rests = top_rests.reset_index(drop=True)
top_rests.index = top_rests.index + 1
top_rests.columns = ["Restaurant Name", "Cuisines", "Rating", "Cost (for 2)"]
st.dataframe(top_rests, use_container_width=True)


st.markdown("---")
st.markdown("<p style='text-align: center; color: #95a5a6;'>please like this project</p>", unsafe_allow_html=True)


#streamlit run app.py
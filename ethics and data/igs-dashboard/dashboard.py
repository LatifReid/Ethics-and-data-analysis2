import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import nh3

st.title("IGS Dashboard: California Census Tracts")
st.markdown("Visualize social and economic indicators for low- and high-income neighborhoods.")

def login_to_api(username, password, api_url="http://localhost:8000/token"):
    try:
        response = requests.post(api_url, data={"username": username, "password": password}, timeout=5)
        response.raise_for_status()
        return response.json()["access_token"]
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API. Make sure FastAPI is running on http://localhost:8000")
        return None
    except requests.exceptions.Timeout:
        st.error("❌ API request timed out")
        return None
    except requests.RequestException as e:
        st.error(f"❌ Login failed: {str(e)}")
        return None

@st.cache_data
def fetch_api_data(token, api_url="http://localhost:8000/tracts/"):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(api_url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        for item in data:
            item["census_tract"] = nh3.clean(item["census_tract"])
        return pd.DataFrame(data)
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API. Make sure FastAPI is running on http://localhost:8000")
        return None
    except requests.exceptions.Timeout:
        st.error("❌ API request timed out")
        return None
    except requests.RequestException as e:
        st.error(f"❌ API error: {str(e)}")
        return None

# Login
st.sidebar.header("Login")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")
if st.sidebar.button("Login"):
    token = login_to_api(username, password)
    if token:
        st.session_state.token = token
        st.success("Login successful!")
    else:
        st.stop()

# Fetch data
if "token" not in st.session_state:
    st.warning("Please log in to access data.")
    st.stop()
df = fetch_api_data(st.session_state.token)
if df is None:
    st.stop()

# Data structure: List of unique census tracts
tract_list = sorted(list(df["census_tract"]))
st.write(f"Available Census Tracts: {tract_list}")

# Filters
st.sidebar.header("Filters")
selected_tract = st.sidebar.selectbox("Select Census Tract", ["All"] + tract_list)
min_inclusion = st.sidebar.slider("Minimum Inclusion Score", 0, 100, 0)
filtered_df = df[df["inclusion_score"] >= min_inclusion]
if selected_tract != "All":
    filtered_df = filtered_df[filtered_df["census_tract"] == selected_tract]

# Layout
col1, col2 = st.columns(2)
with col1:
    st.subheader("Census Tract Data")
    st.dataframe(filtered_df)
with col2:
    st.subheader("Inclusion vs. Growth")
    fig = px.scatter(filtered_df, x="inclusion_score", y="growth_score", color="census_tract")
    st.plotly_chart(fig)

# Income classification and analysis
st.subheader("Low-Income vs. High-Income Tracts Analysis")

# Define thresholds using list comprehension
median_inclusion = df["inclusion_score"].median()
low_income_tracts = [t for t in df.to_dict('records') if t["inclusion_score"] < median_inclusion]
high_income_tracts = [t for t in df.to_dict('records') if t["inclusion_score"] >= median_inclusion]

# Calculate average scores using list comprehension
def get_avg_scores(tracts_list, score_type):
    return sum([t[score_type] for t in tracts_list]) / len(tracts_list) if tracts_list else 0

avg_data = {
    "Income Group": ["Low-Income", "High-Income"],
    "Inclusion": [get_avg_scores(low_income_tracts, "inclusion_score"), 
                  get_avg_scores(high_income_tracts, "inclusion_score")],
    "Growth": [get_avg_scores(low_income_tracts, "growth_score"),
               get_avg_scores(high_income_tracts, "growth_score")],
    "Economy": [get_avg_scores(low_income_tracts, "economy_score"),
                get_avg_scores(high_income_tracts, "economy_score")],
    "Community": [get_avg_scores(low_income_tracts, "community_score"),
                  get_avg_scores(high_income_tracts, "community_score")]
}

avg_df = pd.DataFrame(avg_data)
fig_bar = px.bar(avg_df, x="Income Group", y=["Inclusion", "Growth", "Economy", "Community"],
                 title="Average IGS Scores: Low-Income vs. High-Income Tracts",
                 barmode="group", labels={"value": "Score", "variable": "Score Type"})
st.plotly_chart(fig_bar, use_container_width=True)

# Display statistics
st.write(f"**Low-Income Tracts:** {len(low_income_tracts)} | **High-Income Tracts:** {len(high_income_tracts)}")
st.dataframe(avg_df)
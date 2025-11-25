# Ethics-and-data-analysis2
Mini-Lab: Secure FastAPI with JWT Authentication and Streamlit Dashboard for IGS Data
Links to an external site.
Overview
Links to an external site.
In this mini-lab, you will build a secure FastAPI backend with JWT authentication, load Mastercard Inclusive Growth Score (IGS) data for 10 U.S. census tracts into a SQLite database, and create a Streamlit dashboard to visualize the data. You will practice data structures (lists, dictionaries, sets), address ethical considerations (bias, privacy), and complete five challenges. The lab concludes with deploying the application locally, creating a dashboard wireframe, and submitting a report with screenshots, source code, and a GitHub repository link via Canvas.

Learning Objectives:

Implement secure FastAPI endpoints with JWT authentication.
Load IGS data into a SQLite database using SQLAlchemy.
Build a Streamlit dashboard to display IGS data.
Apply data structures (lists, dictionaries, sets) in data processing.
Analyze data ethics (bias mitigation, privacy) using IGS.
Complete challenges for each application component.
Create a dashboard wireframe and document the process.
Prerequisites:

Python 3.8+, pip, git installed.
GitHub account and repository.
Access to https://inclusivegrowthscore.com/Links to an external site. (free account).
Basic understanding of Python, data structures, and web concepts.
Technologies Introduced
Links to an external site.
Mastercard Inclusive Growth Score (IGS): A dataset providing neighborhood-level social and economic insights, using aggregated, anonymized transaction data for ethical analysis.
SQLite: A lightweight, serverless database for storing structured data.
SQLAlchemy: A Python ORM library for secure database interactions, preventing SQL injection.
FastAPI: A high-performance web framework for building APIs with automatic OpenAPI documentation.
JWT (JSON Web Token): A secure method for authenticating API requests using encoded tokens.
python-jose: A Python library for generating and verifying JWTs.
passlib: A library for secure password hashing (used in JWT authentication).
Streamlit: A Python library for creating interactive web dashboards.
nh3: A library for sanitizing HTML to prevent XSS attacks.
python-dotenv: Loads environment variables to secure sensitive data.
Dataset: IGS Data for 10 Census Tracts
Links to an external site.
Source: Export IGS data from https://inclusivegrowthscore.com/Links to an external site. for 10 U.S. census tracts in California, balancing low-income and high-income neighborhoods.
Recommended Census Tracts (California):
Low-Income:
06037102107 (Los Angeles, Skid Row)
06065045117 (Riverside, low-income urban)
06059099251 (Orange County, Santa Ana)
06001400300 (Alameda, Oakland inner city)
06073008339 (San Diego, City Heights)
High-Income: 6. 06085511712 (Santa Clara, Palo Alto) 7. 06075010200 (San Francisco, Pacific Heights) 8. 06041110100 (Marin, Mill Valley) 9. 06013355102 (Contra Costa, Danville) 10. 06059062610 (Orange County, Newport Beach)
Data Format (hypothetical igs_data.csv):
census_tract,inclusion_score,growth_score,economy_score,community_score
06037102107,45,60,50,55
06065045117,48,58,47,60
06059099251,50,55,52,57
06001400300,42,62,49,58
06073008339,47,59,51,56
06085511712,85,75,80,82
06075010200,88,78,85,80
06041110100,90,80,87,83
06013355102,87,77,84,81
06059062610,92,82,89,85
Directory Structure
Links to an external site.
igs-dashboard/
├── dashboard.py         # Streamlit dashboard
├── main.py             # FastAPI backend with JWT
├── database.py         # SQLite setup
├── igs_data.csv        # IGS dataset
├── requirements.txt    # Dependencies
├── .env               # Environment variables
├── tests/
│   ├── __init__.py
│   ├── test_api.py    # Unit tests
├── .gitignore         # Git ignore file
Step-by-Step Instructions
Links to an external site.
Part 1: Project Setup
Links to an external site.
Create Directory Structure:

mkdir igs-dashboard && cd igs-dashboard
mkdir tests
touch dashboard.py main.py database.py requirements.txt .env igs_data.csv tests/__init__.py tests/test_api.py .gitignore
Set Up .gitignore:

.env
*.db
__pycache__/
*.pyc
Download IGS Data:

Sign up at https://inclusivegrowthscore.com/Links to an external site..
Export data for the 10 listed census tracts (or use the provided igs_data.csv sample).
Save as igs_data.csv.
Activity: Verify the CSV contains census_tract, inclusion_score, growth_score, economy_score, community_score.
Set Up Dependencies (requirements.txt):

streamlit==1.38.0
pandas==2.2.2
plotly==5.24.1
requests==2.32.3
fastapi==0.115.0
uvicorn==0.30.6
sqlalchemy==2.0.31
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.1
nh3==0.2.18
pytest==8.3.2
Install Dependencies:

pip install -r requirements.txt
Part 2: Import IGS Data into SQLite
Links to an external site.
Set Up SQLite Database (database.py):
from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
import nh3

Base = declarative_base()
engine = create_engine('sqlite:///igs_data.db')

class CensusTract(Base):
    __tablename__ = 'census_tracts'
    id = Column(Integer, primary_key=True)
    census_tract = Column(String, unique=True)
    inclusion_score = Column(Float)
    growth_score = Column(Float)
    economy_score = Column(Float)
    community_score = Column(Float)

Base.metadata.create_all(engine)

def init_db():
    df = pd.read_csv("igs_data.csv")
    with sessionmaker(bind=engine)() as session:
        existing_tracts = {row.census_tract for row in session.query(CensusTract.census_tract).all()}
        for _, row in df.iterrows():
            if row["census_tract"] not in existing_tracts:
                tract = CensusTract(
                    census_tract=nh3.clean(str(row["census_tract"])),
                    inclusion_score=row["inclusion_score"],
                    growth_score=row["growth_score"],
                    economy_score=row["economy_score"],
                    community_score=row["community_score"]
                )
                session.add(tract)
        session.commit()

def get_db():
    db = sessionmaker(bind=engine)()
    try:
        yield db
    finally:
        db.close()

init_db()
Explanation:
SQLite: Stores structured data in a lightweight, serverless database.
SQLAlchemy: Uses ORM to prevent SQL injection by mapping Python objects to database tables.
nh3: Sanitizes string inputs (e.g., census_tract) to prevent XSS.
Data Structure: Uses a set (existing_tracts) to check for duplicates efficiently.
Activity: Run database.py to create igs_data.db and verify data with:
from sqlalchemy.orm import sessionmaker
with sessionmaker(bind=engine)() as session:
    print([r.census_tract for r in session.query(CensusTract).all()])
Part 3: Implement Secure FastAPI with JWT Authentication
Links to an external site.
Set Up Environment Variables (.env):

JWT_SECRET_KEY=your-secure-secret-key-123
JWT_ALGORITHM=HS256
Explanation:
python-dotenv: Loads environment variables to secure sensitive data like JWT secrets.
JWT: A token-based authentication method encoding user data securely.
Activity: Generate a secure key (e.g., using openssl rand -hex 32) and save in .env.
Create FastAPI Backend (main.py):

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import List
import nh3
from database import CensusTract, get_db
from dotenv import load_dotenv
import os

load_dotenv()
app = FastAPI(title="IGS API")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class User(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class CensusTractModel(BaseModel):
    census_tract: str = Field(..., max_length=11)
    inclusion_score: float = Field(..., ge=0, le=100)
    growth_score: float = Field(..., ge=0, le=100)
    economy_score: float = Field(..., ge=0, le=100)
    community_score: float = Field(..., ge=0, le=100)

# Simulated user database (replace with real database in production)
users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": pwd_context.hash("securepassword123")
    }
}

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username not in users_db:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_db.get(form_data.username)
    if not user or not pwd_context.verify(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/tracts/", response_model=List[CensusTractModel])
async def get_tracts(current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    tracts = db.query(CensusTract).all()
    return [
        {
            "census_tract": nh3.clean(t.census_tract),
            "inclusion_score": t.inclusion_score,
            "growth_score": t.growth_score,
            "economy_score": t.economy_score,
            "community_score": t.community_score
        } for t in tracts
    ]
Explanation:
python-jose: Generates and verifies JWTs for secure authentication.
passlib: Hashes passwords securely using bcrypt.
Data Structure: Uses a dictionary (users_db) for user storage (simplified for demo).
Activity: Save main.py and run:
uvicorn main:app --reload --port 8000
Test at http://localhost:8000/docs with username admin, password securepassword123.
Step-by-Step JWT Implementation:

Step 1: Install python-jose[cryptography] and passlib[bcrypt].
Step 2: Create a user login endpoint (/token) to issue JWTs.
Step 3: Implement token verification using OAuth2PasswordBearer.
Step 4: Secure the /tracts/ endpoint with get_current_user.
Step 5: Test authentication in FastAPI docs using the /token endpoint to get a token, then use it for /tracts/.
Activity: Document the JWT flow (login → token → access) in your report.
Part 4: Build Streamlit Dashboard
Links to an external site.
Create Dashboard (dashboard.py):
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import nh3

st.title("IGS Dashboard: California Census Tracts")
st.markdown("Visualize social and economic indicators for low- and high-income neighborhoods.")

@st.cache_data
def login_to_api(username, password, api_url="http://localhost:8000/token"):
    try:
        response = requests.post(api_url, data={"username": username, "password": password})
        response.raise_for_status()
        return response.json()["access_token"]
    except requests.RequestException as e:
        st.error(f"Login failed: {str(e)}")
        return None

@st.cache_data
def fetch_api_data(token, api_url="http://localhost:8000/tracts/"):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        for item in data:
            item["census_tract"] = nh3.clean(item["census_tract"])
        return pd.DataFrame(data)
    except requests.RequestException as e:
        st.error(f"API error: {str(e)}")
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
Explanation:
Streamlit: Creates an interactive dashboard with login and data visualization.
Data Structure: Uses a sorted list (tract_list) for dropdown options.
Activity: Run:
streamlit run dashboard.py
Log in with admin/securepassword123 and verify data display.
Part 5: Data Ethics Insights
Links to an external site.
Bias in IGS Data:

Insight: IGS data may underrepresent transient populations (e.g., homeless) in low-income tracts, leading to biased Inclusion scores.
Mitigation: Supplement with public datasets (e.g., HUD homeless data).
Privacy Protection:

Insight: IGS uses aggregated, anonymized data, aligning with GDPR/CCPA, but risks re-identification if combined with other datasets.
Mitigation: Apply differential privacy to add noise to scores.
Transparency:

Insight: IGS clearly documents its methodology, fostering trust and enabling scrutiny.
Practice: Include a methodology section in your dashboard.
Fairness in Decision-Making:

Insight: Using IGS for investment decisions could favor high-income areas if not balanced with low-income data.
Mitigation: Use fairness metrics (e.g., equal representation of tracts).
Accountability:

Insight: Ethical oversight (e.g., Mastercard’s Data Responsibility Principles) ensures responsible use, unlike cases like Strava’s heatmap breach.
Practice: Establish an ethics review process for your app.
Activity: Reflect on these insights in your report, proposing one additional mitigation strategy.
Part 6: Dashboard Wireframe
Links to an external site.
Task: Design a wireframe for the Streamlit dashboard using pen/paper or tools like Figma.
Requirements:
Include login section (username, password).
Display a table of census tract data.
Show a scatter plot (Inclusion vs. Growth).
Add filters (census tract, minimum Inclusion score).
Include an ethics notice (e.g., “Data anonymized to protect privacy”).
Ethical Considerations:
Bias Mitigation: Balance low- and high-income tracts in visualizations.
Privacy: Avoid displaying raw identifiers; use aggregated metrics.
Activity: Sketch the wireframe and include it in your report.
Part 7: Challenges (Complete at Least One per Component)
Links to an external site.
Database (Set Operations):
Use a set to identify and remove duplicate census tracts from a second CSV file before inserting into the database. Update database.py to handle this.
FastAPI (Dictionary Processing):
Add an endpoint /tracts/{census_tract} to return a single tract’s data, storing results in a dictionary before returning.
Streamlit (List Comprehension):
Create a bar chart showing average scores for low-income vs. high-income tracts using list comprehension to filter tracts.
JWT Authentication:
Add a /users/me endpoint to return the current user’s username, secured with JWT.
Ethics Analysis:
Analyze the IGS dataset for potential socioeconomic bias (e.g., compare Inclusion scores for low- vs. high-income tracts) and propose a mitigation strategy.
Part 8: Local Deployment
Links to an external site.
Run FastAPI:
uvicorn main:app --reload --port 8000
Run Streamlit:
streamlit run dashboard.py
Test:
Log in with admin/securepassword123.
Verify data display, filters, and scatter plot.
Activity: Take screenshots of login, data table, and scatter plot.
Part 9: Unit Tests
Links to an external site.
Create Test File (tests/test_api.py):
from fastapi.testclient import TestClient
from main import app, create_access_token

client = TestClient(app)

def test_login_success():
    response = client.post("/token", data={"username": "admin", "password": "securepassword123"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_get_tracts_unauthorized():
    response = client.get("/tracts/")
    assert response.status_code == 401

def test_get_tracts_authorized():
    token = create_access_token({"sub": "admin"})
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/tracts/", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) > 0
Run Tests:
pytest tests/ -v --junitxml=pytest_report.xml
Part 10: Submission Requirements
Links to an external site.
Report (report.docx):
Content:
Introduction: Describe lab objectives and IGS dataset.
Dataset Import: Explain SQLite import with data structure usage.
FastAPI: Detail JWT authentication and endpoint security.
Streamlit: Describe dashboard features and visualizations.
Ethics: Discuss the five insights and your mitigation strategy.
Challenges: Describe completed challenges (at least one per component).
Wireframe: Include dashboard wireframe sketch.
Screenshots:
FastAPI docs with successful /token and /tracts/ requests.
Streamlit dashboard (login, data table, scatter plot).
Test results (pytest_report.xml).
Conclusion: Reflect on learnings about secure APIs and ethics.
GitHub Repository:
Push all code to a public GitHub repository.
Include README.md with setup and run instructions.
Activity: Commit and push:
git init
git add .
git commit -m "IGS dashboard with secure FastAPI and Streamlit"
git push origin main
Canvas Submission:
Submit report.docx, GitHub URL, pytest_report.xml, and wireframe sketch.

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
        csv_tracts = set()
        for _, row in df.iterrows():
            tract_id = nh3.clean(str(row["census_tract"]))
            if tract_id not in existing_tracts and tract_id not in csv_tracts:
                tract = CensusTract(
                    census_tract=tract_id,
                    inclusion_score=row["inclusion_score"],
                    growth_score=row["growth_score"],
                    economy_score=row["economy_score"],
                    community_score=row["community_score"]
                )
                session.add(tract)
                csv_tracts.add(tract_id)
        session.commit()

def get_db():
    db = sessionmaker(bind=engine)()
    try:
        yield db
    finally:
        db.close()

def remove_duplicates_from_csv(input_file, output_file=None):
    """
    Remove duplicate census tracts from a CSV file using set operations.
    Returns a DataFrame with unique tracts only.
    """
    df = pd.read_csv(input_file)
    seen_tracts = set()
    unique_rows = []
    
    for _, row in df.iterrows():
        tract_id = nh3.clean(str(row["census_tract"]))
        if tract_id not in seen_tracts:
            seen_tracts.add(tract_id)
            unique_rows.append(row)
    
    unique_df = pd.DataFrame(unique_rows)
    if output_file:
        unique_df.to_csv(output_file, index=False)
        print(f"Duplicates removed: {len(df)} rows → {len(unique_df)} rows")
    return unique_df
import wrds
import pandas as pd
import streamlit as st
import numpy as np
import os

@st.cache_resource
def get_wrds_connection():
    return wrds.Connection()

def load_cached_data(gvkey: str):
    """Try to load cached CSV from data_cache folder"""
    cache_file = os.path.join('data_cache', f"{gvkey}.csv")
    if os.path.exists(cache_file):
        try:
            df = pd.read_csv(cache_file, parse_dates=['datadate'])
            required_cols = ['current_ratio', 'debt_ratio', 'roe', 'gross_margin', 'net_margin', 'year']
            if all(col in df.columns for col in required_cols):
                return df
        except Exception as e:
            st.warning(f"Cache read failed: {e}")
    return None

@st.cache_data(ttl=3600)
def fetch_company_data(gvkey: str):
    # 1. Try local cache first
    cached_df = load_cached_data(gvkey)
    if cached_df is not None:
        return cached_df

    # 2. If no cache, connect to WRDS
    try:
        db = get_wrds_connection()
    except Exception as e:
        st.error(f"WRDS connection failed and no local cache available: {e}")
        return None

    sql = f"""
        SELECT 
            f.gvkey, f.datadate, f.fyear,
            f.indfmt, f.consol, f.popsrc, f.datafmt,
            n.sic,
            f.at, f.lt, f.lct, f.act, f.che, f.invt, f.rect,
            f.sale, f.cogs, f.oiadp, f.ni, f.ib
        FROM 
            comp.funda f
        LEFT JOIN 
            comp.namesd n ON f.gvkey = n.gvkey
        WHERE 
            f.gvkey = '{gvkey}'
    """
    try:
        df = db.raw_sql(sql)
    except Exception as e:
        st.error(f"Query failed: {e}")
        return None

    if df.empty:
        return None

    # Apply standard filters
    required_cols = ['indfmt', 'consol', 'popsrc', 'datafmt']
    for col in required_cols:
        if col not in df.columns:
            st.error(f"Column '{col}' missing from WRDS data.")
            return None

    df = df[
        (df['indfmt'] == 'INDL') & 
        (df['consol'] == 'C') & 
        (df['popsrc'] == 'D') & 
        (df['datafmt'] == 'STD')
    ].copy()

    if df.empty:
        st.warning("No data found after applying standard filters (INDL, C, D, STD).")
        return None

    # Date processing
    df['datadate'] = pd.to_datetime(df['datadate'], errors='coerce')
    df = df.dropna(subset=['datadate'])
    df.sort_values('datadate', inplace=True)
    df['year'] = df['fyear'].astype(int)

    # Numeric conversion
    num_cols = ['at', 'lt', 'lct', 'act', 'che', 'invt', 'rect', 'sale', 'cogs', 'oiadp', 'ni', 'ib']
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Calculate ratios
    df['current_ratio'] = df['act'] / df['lct'].replace(0, np.nan)
    df['quick_ratio'] = (df['act'] - df['invt']) / df['lct'].replace(0, np.nan)
    df['debt_ratio'] = df['lt'] / df['at'].replace(0, np.nan)
    equity = df['at'] - df['lt']
    df['roe'] = df['ni'] / equity.replace(0, np.nan)
    df['gross_margin'] = (df['sale'] - df['cogs']) / df['sale'].replace(0, np.nan)
    df['net_margin'] = df['ni'] / df['sale'].replace(0, np.nan)
    df['inventory_turnover'] = df['cogs'] / df['invt'].replace(0, np.nan)
    df['receivables_turnover'] = df['sale'] / df['rect'].replace(0, np.nan)

    return df

@st.cache_data(ttl=3600)
def get_latest_data_date(gvkey: str):
    df = fetch_company_data(gvkey)
    if df is not None and not df.empty:
        latest_date = df['datadate'].max()
        return latest_date.strftime('%Y-%m-%d')
    return "N/A"
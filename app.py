import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from streamlit_lottie import st_lottie

# ================================
# PAGE CONFIG
# ================================
st.set_page_config(page_title="AI Procurement Intelligence", layout="wide")

# ================================
# LOAD DATA
# ================================
@st.cache_data
def load_data():
    url = "https://drive.google.com/uc?export=download&id=1cqOruxB9MAJdKIVWGKKbDaLEl1LQ3hM4"
    return pd.read_csv(url)

df = load_data()

# ================================
# LOTTIE
# ================================
def load_lottie(url):
    return requests.get(url).json()

lottie_ai = load_lottie("https://assets2.lottiefiles.com/packages/lf20_kyu7xb1v.json")

# ================================
# INTENT SYSTEM
# ================================
INTENTS = {
    "spending": ["spend", "cost", "value"],
    "risk": ["risk", "fraud"],
    "supplier": ["supplier", "vendor"],
    "sector": ["sector"],
    "forecast": ["forecast", "trend"],
    "method": ["method", "procurement"]
}

def detect_intents(query):
    q = query.lower()
    return [i for i in INTENTS if any(w in q for w in INTENTS[i])] or ["general"]

# ================================
# SIDEBAR
# ================================
st.sidebar.title("AI Procurement System")
page = st.sidebar.radio("Navigation", ["Home", "Chat", "Dashboard", "About"])

# ================================
# HOME (UNCHANGED AS YOU WANTED)
# ================================
if page == "Home":

    col1, col2 = st.columns([2,1])

    with col1:
        st.title("AI Procurement Intelligence System")

        st.markdown("""
        ### 📊 System Capabilities

        #### 1. Spending & Contract Value Analysis
        - Total procurement spend by year, country, sector
        - Average contract values
        - Contract size distribution
        - Top contractors

        #### 2. Supplier / Vendor Analysis
        - Supplier concentration
        - Local vs international suppliers
        - Repeat suppliers
        - Supplier diversity

        #### 3. Procurement Method Analysis
        - Method distribution (ICB, NCB, Direct)
        - Trends over time
        - Value vs method correlation

        #### 4. Sector & Project Analysis
        - Sector-wise investment
        - Project-level spend tracking
        - Country-level activity

        #### 5. Timeline & Efficiency
        - Procurement duration
        - Delays & benchmarks

        #### 6. Geographic Analysis
        - Country-wise procurement
        - Supplier origin analysis

        #### 7. Risk & Compliance
        - High-risk contracts
        - Direct contracting risks
        - Supplier concentration risk

        #### 8. Forecasting
        - Growth trends
        - Future projections
        """)

    with col2:
        st_lottie(lottie_ai, height=300)

# ================================
# CHAT (IMPROVED ONLY)
# ================================
elif page == "Chat":

    st.title("💬 Chat with Procurement Agent")

    # ================= CHAT MEMORY =================
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # ================= HELPER FUNCTION =================
    def generate_response(intent):
        outputs = []

        if intent == "spending":
            data = df.groupby('year')['contract_value'].sum().reset_index()
            fig = px.line(data, x='year', y='contract_value',
                          title="Yearly Spending Trend", markers=True)
            outputs.append(("plot", fig))
            outputs.append(("table", data))

        elif intent == "risk":
            risk = df['risk_flag'].mean() * 100
            risk_table = df['risk_flag'].value_counts().reset_index()
            risk_table.columns = ['Risk Flag', 'Count']
            outputs.append(("text", f"Risk Percentage: {risk:.2f}%"))
            outputs.append(("table", risk_table))

        elif intent == "supplier":
            data = df['supplier_name'].value_counts().head(10).reset_index()
            data.columns = ['Supplier', 'Contracts']
            fig = px.bar(data, x='Contracts', y='Supplier',
                         orientation='h', title="Top Suppliers")
            outputs.append(("plot", fig))
            outputs.append(("table", data))

        elif intent == "sector":
            data = df.groupby('sector')['contract_value'].sum().reset_index()
            fig = px.bar(data, x='sector', y='contract_value',
                         color='sector', title="Sector Spending")
            outputs.append(("plot", fig))
            outputs.append(("table", data))

        elif intent == "forecast":
            data = df.groupby('year')['contract_value'].sum().reset_index()
            fig = px.line(data, x='year', y='contract_value',
                          title="Forecast Trend", line_shape='spline')
            outputs.append(("plot", fig))

        elif intent == "method":
            method = df['procurement_method'].value_counts().reset_index()
            method.columns = ['Method', 'Count']
            fig = px.pie(method, names='Method', values='Count', hole=0.4)
            outputs.append(("plot", fig))
            outputs.append(("table", method))

        else:
            outputs.append(("text", "Try a more specific query"))

        return outputs

    # ================= DISPLAY CHAT HISTORY =================
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            for item in msg["content"]:
                if item[0] == "text":
                    st.write(item[1])
                elif item[0] == "plot":
                    st.plotly_chart(item[1], use_container_width=True)
                elif item[0] == "table":
                    st.dataframe(item[1])

    # ================= INPUT =================
    st.markdown("""
### 💡 Suggested Queries (What you can explore)

#### 📊 Spending Analysis
- show spending trend → yearly procurement spending  
- total contract value → overall spending  
- spending by country → country comparison  

#### 🏢 Supplier Analysis
- top suppliers → biggest vendors  
- repeat suppliers → recurring vendors  
- supplier distribution → supplier spread  

#### ⚠️ Risk & Compliance
- risk analysis → % high-risk contracts  
- fraud detection → risky procurement  
- direct contracts risk → potential issues  

#### 🏗️ Sector Analysis
- sector spending → investment by sector  
- top sectors → most funded sectors  

#### 📈 Forecast & Trends
- forecast growth → future trend  
- yearly growth rate → spending changes  

#### 📑 Procurement Methods
- procurement method → distribution (ICB, NCB, Direct)  
- method comparison → usage analysis  
""")
    
    # ================= QUICK ACTION BUTTONS =================
    st.markdown("### ⚡ Quick Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📊 Show Spending"):
            st.session_state.quick_query = "show spending trend"

        if st.button("🏢 Top Suppliers"):
            st.session_state.quick_query = "supplier analysis"

    with col2:
        if st.button("⚠️ Risk Analysis"):
            st.session_state.quick_query = "risk analysis"

        if st.button("🏗️ Sector Spending"):
            st.session_state.quick_query = "sector spending"

    with col3:
        if st.button("📈 Forecast"):
            st.session_state.quick_query = "forecast growth"

        if st.button("📑 Methods"):
            st.session_state.quick_query = "procurement method"
    
    user_input = st.chat_input("Ask your question...")

    # Handle button click input
    if "quick_query" in st.session_state:
        user_input = st.session_state.quick_query
        del st.session_state.quick_query

    if user_input:
        # Show user message
        st.session_state.messages.append({
            "role": "user",
            "content": [("text", user_input)]
        })

        # Detect intent
        intents = detect_intents(user_input)

        # Generate response
        response_content = []
        for intent in intents:
            response_content.extend(generate_response(intent))

        # Save assistant response
        st.session_state.messages.append({
            "role": "assistant",
            "content": response_content
        })

        # Rerun to display instantly
        st.rerun()

# ================================
# DASHBOARD (ADVANCED - POWER BI STYLE)
# ================================
elif page == "Dashboard":

    st.title("📊 Advanced Procurement Dashboard")

    # ================= FILTERS =================
    st.sidebar.subheader("🔎 Filters")

    year_filter = st.sidebar.multiselect(
        "Select Year",
        options=sorted(df['year'].dropna().unique()),
        default=sorted(df['year'].dropna().unique())
    )

    sector_filter = st.sidebar.multiselect(
        "Select Sector",
        options=df['sector'].dropna().unique(),
        default=df['sector'].dropna().unique()
    )

    country_filter = st.sidebar.multiselect(
        "Select Country",
        options=df['country'].dropna().unique(),
        default=df['country'].dropna().unique()
    )

    # Apply filters
    filtered_df = df[
        (df['year'].isin(year_filter)) &
        (df['sector'].isin(sector_filter)) &
        (df['country'].isin(country_filter))
    ]

    # ================= KPI CARDS =================
    st.markdown("## 📌 Key Metrics")

    total_spend = filtered_df['contract_value'].sum()
    total_contracts = len(filtered_df)
    avg_contract = filtered_df['contract_value'].mean()
    risk_percent = filtered_df['risk_flag'].mean() * 100

    c1, c2, c3, c4 = st.columns(4)

# 💰 Total Spend (Blue Gradient)
    c1.markdown(f"""
    <div style='background: linear-gradient(135deg, #1f77b4, #4dabf7);
                padding:20px;border-radius:12px;color:white'>
            <h4>💰 Total Spend</h4>
        <h2>${total_spend:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

    # 📄 Total Contracts (Green)
    c2.markdown(f"""
    <div style='background: linear-gradient(135deg, #2ca02c, #69db7c);
                padding:20px;border-radius:12px;color:white'>
            <h4>📄 Total Contracts</h4>
        <h2>{total_contracts}</h2>
    </div>
    """, unsafe_allow_html=True)

    # 📊 Avg Contract (Orange)
    c3.markdown(f"""
    <div style='background: linear-gradient(135deg, #ff7f0e, #ffa94d);
                padding:20px;border-radius:12px;color:white'>
            <h4>📊 Avg Contract</h4>
        <h2>${avg_contract:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

    # ⚠️ Risk % (Red)
    c4.markdown(f"""
    <div style='background: linear-gradient(135deg, #d62728, #ff6b6b);
            padding:20px;border-radius:12px;color:white'>
        <h4>⚠️ Risk %</h4>
        <h2>{risk_percent:.2f}%</h2>
    </div>
    """, unsafe_allow_html=True)

    # ================= ROW 1 =================
    col1, col2 = st.columns(2)

    with col1:
        yearly = filtered_df.groupby('year')['contract_value'].sum().reset_index()
        fig1 = px.line(yearly, x='year', y='contract_value',
                       title="📈 Yearly Spending Trend",
                       markers=True)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        sector = filtered_df.groupby('sector')['contract_value'].sum().reset_index()
        fig2 = px.bar(sector, x='sector', y='contract_value',
                      title="🏗️ Sector-wise Spending",
                      color='sector')
        st.plotly_chart(fig2, use_container_width=True)

    # ================= ROW 2 =================
    col3, col4 = st.columns(2)

    with col3:
        country = filtered_df.groupby('country')['contract_value'].sum() \
            .sort_values(ascending=False).head(10).reset_index()

        fig3 = px.bar(country, x='contract_value', y='country',
                      orientation='h',
                      title="🌍 Top Countries by Spend")
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        method = filtered_df['procurement_method'].value_counts().reset_index()
        method.columns = ['method', 'count']

        fig4 = px.pie(method, names='method', values='count',
                      hole=0.5,
                      title="📑 Procurement Methods")
        fig4.update_traces(textinfo='percent+label')
        st.plotly_chart(fig4, use_container_width=True)

    # ================= ROW 3 =================
    col5, col6 = st.columns(2)

    with col5:
        supplier = filtered_df['supplier_name'].value_counts().head(10).reset_index()
        supplier.columns = ['supplier', 'count']

        fig5 = px.bar(supplier, x='count', y='supplier',
                      orientation='h',
                      title="🏢 Top Suppliers")
        st.plotly_chart(fig5, use_container_width=True)

    with col6:
        risk_data = filtered_df.groupby('sector')['risk_flag'].mean().reset_index()
        risk_data['risk_flag'] = risk_data['risk_flag'] * 100

        fig6 = px.bar(risk_data, x='sector', y='risk_flag',
                      title="⚠️ Risk by Sector (%)",
                      color='risk_flag')
        st.plotly_chart(fig6, use_container_width=True)

    st.divider()

    # ================= TABLE =================
    st.subheader("📋 Data Overview")
    st.dataframe(filtered_df.head(100))

# ================================
# ABOUT (UNCHANGED)
# ================================
elif page == "About":

    st.title("📘 Project Details")

    st.markdown("""
    ## 🔹 Phase 1: Data Pipeline
    - Collected ADB procurement dataset
    - Cleaned messy Excel data
    - Standardized columns
    - Created final CSV

    ## 🔹 Phase 2: Analytics Engine
    - Built functions for:
        - Spending
        - Supplier
        - Sector
        - Risk
        - Forecast

    ## 🔹 Phase 3: Agent System
    - Developed NLP-based intent detection
    - Multi-intent handling
    - Automated analysis routing

    ## 🔹 Phase 4: Streamlit UI
    - Interactive dashboard
    - Chat-based interface
    - Real-time insights

    ## 🚀 Technologies Used
    - Python
    - Pandas
    - Plotly
    - Streamlit

    ## 🎯 Goal
    To build an intelligent procurement decision system.

    ## 👨‍💻 Developed By
    Aditya Nandal
    """)
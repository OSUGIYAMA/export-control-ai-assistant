import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
import pandas as pd
import PyPDF2
import pdfplumber
import io
from datetime import datetime
from pathlib import Path

# Import custom modules
from knowledge_base import get_full_knowledge_base, get_ear_knowledge
from utils import (
    extract_contract_info,
    check_group_a_country,
    check_concern_country,
    search_eccn,
    check_entity_list,
    assess_risk_level,
    generate_action_items,
    load_eccn_json,
    search_eccn_json,
    get_eccn_by_number,
    get_eccn_categories_summary
)
from visualization import (
    create_country_chart_heatmap,
    create_world_map_restrictions,
    create_regulation_summary_chart,
    create_interactive_eccn_table,
    display_reference_data,
    create_entity_list_viewer
)
from rag_tools import (
    LicenseExceptionRAG,
    check_license_exception_with_rag
)

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Page config
st.set_page_config(
    page_title="US EAR Re-export Compliance Assistant",
    page_icon="🇺🇸",
    layout="wide"
)

# Enhanced Modern UI Design with Gradients and Animations
st.markdown("""
<style>
/* Enhanced Modern UI Design with Gradients and Animations */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* Global Styles - Modern Typography */
.stApp {
    background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%) !important;
    color: #1a202c !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}

body, p, span, div, h1, h2, h3, h4, h5, h6, label {
    color: #1a202c !important;
    font-family: 'Inter', sans-serif !important;
}

/* Main Header - Modern Gradient Design */
.main-header {
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-align: center;
    margin-bottom: 2.5rem;
    padding: 2rem 0;
    position: relative;
    letter-spacing: -0.02em;
    animation: fadeInDown 0.6s ease-out;
}

.main-header::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 100px;
    height: 4px;
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    border-radius: 2px;
}

/* Section Headers - Modern with Icon Support */
.section-header {
    font-size: 1.75rem;
    font-weight: 700;
    color: #2d3748 !important;
    margin-top: 2.5rem;
    margin-bottom: 1.5rem;
    padding: 1rem 1.5rem;
    background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
    border-left: 5px solid #667eea;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.section-header:hover {
    transform: translateX(5px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

/* Alert Boxes - Modern Cards with Shadows */
.warning-box {
    background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
    border-left: 5px solid #f59e0b;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1.5rem 0;
    color: #78350f !important;
    box-shadow: 0 4px 6px rgba(245, 158, 11, 0.1);
    animation: slideInLeft 0.4s ease-out;
}

.info-box {
    background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
    border-left: 5px solid #3b82f6;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1.5rem 0;
    color: #1e3a8a !important;
    box-shadow: 0 4px 6px rgba(59, 130, 246, 0.1);
    animation: slideInLeft 0.4s ease-out;
}

.success-box {
    background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
    border-left: 5px solid #10b981;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1.5rem 0;
    color: #064e3b !important;
    box-shadow: 0 4px 6px rgba(16, 185, 129, 0.1);
    animation: slideInLeft 0.4s ease-out;
}

.danger-box {
    background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
    border-left: 5px solid #ef4444;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1.5rem 0;
    color: #7f1d1d !important;
    box-shadow: 0 4px 6px rgba(239, 68, 68, 0.1);
    animation: slideInLeft 0.4s ease-out;
}

/* Buttons - Modern Gradient with Hover Effects */
.stButton>button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white !important;
    border: none;
    border-radius: 10px;
    padding: 0.75rem 2rem;
    font-weight: 600;
    font-size: 1rem;
    letter-spacing: 0.025em;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 6px rgba(102, 126, 234, 0.25);
    position: relative;
    overflow: hidden;
}

.stButton>button::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
    transition: left 0.5s;
}

.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 15px rgba(102, 126, 234, 0.4);
}

.stButton>button:hover::before {
    left: 100%;
}

.stButton>button:active {
    transform: translateY(0);
}

/* Input Fields - Modern with Focus Effects */
.stTextInput>div>div>input,
.stTextArea>div>div>textarea,
.stSelectbox>div>div>div {
    border-radius: 10px;
    border: 2px solid #e2e8f0;
    padding: 0.75rem 1rem;
    transition: all 0.3s ease;
    background-color: #ffffff;
    font-size: 0.95rem;
}

.stTextInput>div>div>input:focus,
.stTextArea>div>div>textarea:focus {
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    outline: none;
    transform: translateY(-1px);
}

/* Expander - Modern Card Design */
.streamlit-expanderHeader {
    background: linear-gradient(135deg, #ffffff 0%, #f7fafc 100%);
    border-radius: 10px;
    border: 2px solid #e2e8f0;
    font-weight: 600;
    padding: 1rem 1.5rem;
    transition: all 0.3s ease;
}

.streamlit-expanderHeader:hover {
    border-color: #667eea;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

/* Dataframe - Modern Table */
.stDataFrame {
    border: 2px solid #e2e8f0;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

/* Tabs - Modern Pills Design */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: transparent;
    border-bottom: none;
    padding: 0.5rem;
}

.stTabs [data-baseweb="tab"] {
    background-color: #f7fafc;
    border-radius: 10px;
    padding: 0.875rem 1.75rem;
    font-weight: 600;
    color: #64748b;
    border: 2px solid transparent;
    transition: all 0.3s ease;
}

.stTabs [data-baseweb="tab"]:hover {
    background-color: #e2e8f0;
    color: #475569;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white !important;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

/* Sidebar - Modern with Gradient */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%) !important;
    border-right: 2px solid #e2e8f0;
}

[data-testid="stSidebar"] * {
    color: #1a202c !important;
}

[data-testid="stSidebar"] .stMarkdown h2 {
    color: #667eea !important;
    font-weight: 700;
}

/* Metrics - Modern Cards with Gradients */
[data-testid="stMetricValue"] {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

[data-testid="stMetricLabel"] {
    font-size: 0.95rem;
    font-weight: 600;
    color: #64748b !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

[data-testid="stMetric"] {
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    border: 2px solid #e2e8f0;
    transition: all 0.3s ease;
}

[data-testid="stMetric"]:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    border-color: #667eea;
}

/* File Uploader - Modern Dashed Card */
[data-testid="stFileUploader"] {
    background: linear-gradient(135deg, #fafbfc 0%, #f3f4f6 100%);
    border: 3px dashed #cbd5e0;
    border-radius: 12px;
    padding: 2rem;
    transition: all 0.3s ease;
}

[data-testid="stFileUploader"]:hover {
    border-color: #667eea;
    background: linear-gradient(135deg, #f0f4ff 0%, #e0e7ff 100%);
}

/* Success/Info/Warning Messages - Enhanced */
.stSuccess {
    background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
    border-left: 5px solid #10b981;
    border-radius: 10px;
    color: #064e3b !important;
    box-shadow: 0 2px 8px rgba(16, 185, 129, 0.15);
}

.stInfo {
    background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
    border-left: 5px solid #3b82f6;
    border-radius: 10px;
    color: #1e3a8a !important;
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.15);
}

.stWarning {
    background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
    border-left: 5px solid #f59e0b;
    border-radius: 10px;
    color: #78350f !important;
    box-shadow: 0 2px 8px rgba(245, 158, 11, 0.15);
}

/* Animations */
@keyframes fadeInDown {
    from {
        opacity: 0;
        transform: translateY(-20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes slideInLeft {
    from {
        opacity: 0;
        transform: translateX(-20px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

@keyframes pulse {
    0%, 100% {
        opacity: 1;
    }
    50% {
        opacity: 0.8;
    }
}

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Modern Scrollbar */
::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}

::-webkit-scrollbar-track {
    background: #f1f5f9;
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 10px;
    transition: all 0.3s ease;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, #5568d3 0%, #653a8e 100%);
}

/* Download Button Enhancement */
.stDownloadButton>button {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white !important;
    border: none;
    border-radius: 10px;
    padding: 0.75rem 2rem;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4px 6px rgba(16, 185, 129, 0.25);
}

.stDownloadButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 15px rgba(16, 185, 129, 0.4);
}

/* Enhanced spacing */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1400px;
}

/* Status Cards */
.status-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1.5rem;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    transition: all 0.3s ease;
}

.status-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

.status-card-value {
    color: white;
    font-size: 2rem;
    font-weight: 800;
    margin-bottom: 0.5rem;
}

.status-card-label {
    color: rgba(255,255,255,0.9);
    font-size: 0.85rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}


</style>
""", unsafe_allow_html=True)

# Define functions before session state initialization
def load_sample_data():
    """サンプルデータを読み込む"""
    sample_data_dir = Path("sample_data")
    data = {}
    
    # ECCN リスト（CSV）
    eccn_path = sample_data_dir / "eccn_list.csv"
    if eccn_path.exists():
        data['eccn_csv'] = pd.read_csv(eccn_path)
    
    # ECCN リスト（JSON）- より詳細なデータ
    eccn_json_path = Path("eccnnumber.json")
    if eccn_json_path.exists():
        data['eccn_json'] = load_eccn_json(str(eccn_json_path))
        # 読み込み成功時のメッセージは後で表示
    
    # カントリーチャート（米国EAR）
    country_chart_path = Path("11_12_2025_country_chart_export.csv")
    if country_chart_path.exists():
        data['country_chart'] = pd.read_csv(country_chart_path)
    
    # カントリーグループ
    country_path = sample_data_dir / "country_groups.csv"
    if country_path.exists():
        data['countries'] = pd.read_csv(country_path)
    
    # エンティティリスト
    entity_path = sample_data_dir / "entity_list_sample.csv"
    if entity_path.exists():
        data['entities'] = pd.read_csv(entity_path)
    
    return data

# Initialize session state
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'extracted_info' not in st.session_state:
    st.session_state.extracted_info = None
if 'sample_data' not in st.session_state:
    st.session_state.sample_data = load_sample_data()

def extract_text_from_pdf(pdf_file):
    """PDFからテキストを抽出（pdfplumberを使用して精度向上）"""
    try:
        # pdfplumberを試す
        with pdfplumber.open(io.BytesIO(pdf_file.read())) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        # フォールバック: PyPDF2を使用
        st.warning(f"pdfplumberでの抽出に失敗しました。PyPDF2にフォールバックします: {str(e)}")
        pdf_file.seek(0)  # ファイルポインタを先頭に戻す
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.read()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text

def load_knowledge_base():
    """ガイドに基づくナレッジベースを構築"""
    return get_full_knowledge_base()

def analyze_contract_with_gpt(contract_text, knowledge_base):
    """Analyze contract with GPT (US EAR Re-export Regulations only)"""
    
    # Prepare ECCN database
    eccn_json = st.session_state.sample_data.get('eccn_json')
    eccn_data_text = ""
    if eccn_json and 'ccl_categories' in eccn_json:
        eccn_data_text = "\n[ECCN Number Database (Complete)]\n"
        for category in eccn_json['ccl_categories']:
            eccn_data_text += f"\n## Category {category.get('category_number', '')}: {category.get('title', '')}\n"
            for group in category.get('product_groups', []):
                eccn_data_text += f"\n### {group.get('group_title', '')}\n"
                for item in group.get('items', [])[:10]:  # Max 10 items from each group
                    eccn_data_text += f"- **{item.get('eccn', '')}**: {item.get('description', '')[:200]}...\n"
    
    # Prepare Country Chart data
    country_chart = st.session_state.sample_data.get('country_chart')
    country_chart_text = ""
    if country_chart is not None and not country_chart.empty:
        country_chart_text = "\n[Country Chart (Complete)]\n"
        country_chart_text += "Below is actual US EAR Country Chart data.\'X\'は許可が必要であることを示します。\n\n"
        # Include first ~30 countries (considering token limit)
        for idx, row in country_chart.head(30).iterrows():
            country_name = row.iloc[0]
            country_chart_text += f"\n**{country_name}**:\n"
            # Show only key regulation reason columns
            key_columns = ['NS 1', 'NS 2', 'MT 1', 'NP 1', 'NP 2', 'CB 1', 'AT 1']
            for col in key_columns:
                if col in row.index and pd.notna(row[col]):
                    country_chart_text += f"  - {col}: {row[col]}\n"
    
    prompt = f"""
You are an expert on US EAR re-export regulations. Analyze the following contract and determine US EAR regulatory requirements.

[Important Prerequisites]
This system analyzes only US EAR regulations for "re-exporting US-origin items from Japan to other countries".
Japanese Foreign Exchange and Foreign Trade Act is outside the scope.

[Contract Content]
{contract_text[:5000]}  # First 5000 chars due to token limit

{eccn_data_text[:3000]}

{country_chart_text[:3000]}

[Knowledge Base (Reference)]
{knowledge_base[:1000]}

Please analyze the following items in detail:

## 1. Contract Information Extraction
- Product Name・製品名（whether US-origin）
- Re-export destination (Japan → Other country)
- End User情報
- End Use
- Contract Value
- Delivery Date

## 2. US EAR Re-export Decision Flow Analysis

### A. Does it qualify as re-export of EAR-controlled items?
Evaluate possibilities of US-origin items, incorporated items, or foreign direct products

### B. ECCN Number Determination
Refer to the ECCN database above and determine the most appropriate ECCN number.
- Estimated ECCN number (5-digit code, e.g., 3A001, 5A002, or EAR99)
- Category (1st digit meaning)
- Group (2nd digit meaning)
- Reason for Control (3rd digit: NS=National Security, MT=Missile Tech, NP=Nuclear Non-Proliferation, etc.)
- Selection rationale (explain in detail why this ECCN was chosen)

### C. Country Chart Analysis
Refer to the Country Chart data above and determine regulations for the destination country.
- Destination country
- Applicable reasons for control (NS 1, NS 2, MT 1, NP 1, etc.)
- License requirement for each reason (\'X\' mark indicates license required)
- Overall determination (License Required or License Exception Available or No License Required)

### D. License Exception Review
Review applicable license exceptions (LVS, GBS, TSR, TMP, ENC, etc.)

### E. Embargo Countries & Restricted Lists
- DPL（Denied Persons List）該当チェック
- Entity List該当チェック
- Check for embargo countries (North Korea, Iran, Syria, Cuba, Crimea)

## 3. Overall Assessment & Risk Evaluation
- **US EAR Determination**: License Required / License Exception Available / No License Required
- **Risk Level**: High / Medium / Low
- **Recommended Actions**: Specific next steps

## 4. Required Procedures
Specific procedures and contact points for BIS license application if required

**Important**: Do not mention Japanese FEFTA. This system only handles US EAR regulations.

Please respond in a clear and structured format.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are an expert on US EAR re-export regulations. You analyze regulations for re-exporting US-origin items from Japan to other countries. Japanese FEFTA is out of scope."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=3000
        )
        
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"分析エラー: {str(e)}")
        return None


def analyze_contract_step_by_step(contract_text, knowledge_base, result_container):
    """Analyze contract step by step with GPT (US EAR Re-export Regulations only)"""
    
    # Prepare ECCN database
    eccn_json = st.session_state.sample_data.get('eccn_json')
    eccn_data_text = ""
    if eccn_json and 'ccl_categories' in eccn_json:
        eccn_data_text = "\n[ECCN Number Database (Complete)]\n"
        for category in eccn_json['ccl_categories']:
            eccn_data_text += f"\n## Category {category.get('category_number', '')}: {category.get('title', '')}\n"
            for group in category.get('product_groups', []):
                eccn_data_text += f"\n### {group.get('group_title', '')}\n"
                for item in group.get('items', [])[:10]:
                    eccn_data_text += f"- **{item.get('eccn', '')}**: {item.get('description', '')[:200]}...\n"
    
    # Prepare Country Chart data
    country_chart = st.session_state.sample_data.get('country_chart')
    country_chart_text = ""
    if country_chart is not None and not country_chart.empty:
        country_chart_text = "\n[Country Chart (Complete)]\n"
        country_chart_text += "Below is actual US EAR Country Chart data.\'X\'は許可が必要であることを示します。\n\n"
        for idx, row in country_chart.head(30).iterrows():
            country_name = row.iloc[0]
            country_chart_text += f"\n**{country_name}**:\n"
            key_columns = ['NS 1', 'NS 2', 'MT 1', 'NP 1', 'NP 2', 'CB 1', 'AT 1']
            for col in key_columns:
                if col in row.index and pd.notna(row[col]):
                    country_chart_text += f"  - {col}: {row[col]}\n"
    
    # Analysis Resultsを格納
    full_analysis = ""
    
    # ステップ1: 契約情報の抽出
    with st.spinner("📝 Step 1: Extracting contract information..."):
        step1_prompt = f"""
あなたは米国EAR再輸出規制の専門家です。Extract important information from the following contract.

[Contract Content]
{contract_text[:3000]}

Extract the following information:
## 1. Contract Information Extraction
- Product Name・製品名（whether US-origin）
- Re-export destination (Japan → Other country)
- End User情報
- End Use
- Contract Value
- Delivery Date

Please respond concisely in bullet points.
"""
        try:
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "あなたは米国EAR再輸出規制の専門家です。"},
                    {"role": "user", "content": step1_prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            step1_result = response.choices[0].message.content
            full_analysis += f"## 1. Contract Information Extraction\n{step1_result}\n\n"
            
            with result_container:
                st.markdown("### 📝 Step 1: Contract Information Extraction")
                st.markdown(step1_result)
                st.markdown("---")
        except Exception as e:
            st.error(f"Step 1 Error: {str(e)}")
            return None
    
    # ステップ2-A: EAR対象Product判定
    with st.spinner("🔍 Step 2-A: Determining EAR-controlled items..."):
        step2a_prompt = f"""
{contract_text[:2000]}

For the above contract, determine the following:

### A. Does it qualify as re-export of EAR-controlled items?
- Possibility of US-origin items
- Possibility of incorporated US items
- Applicability of Foreign Direct Product (FDP) rule

Please make a concise determination.
"""
        try:
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "あなたは米国EAR再輸出規制の専門家です。"},
                    {"role": "user", "content": step2a_prompt}
                ],
                temperature=0.3,
                max_tokens=400
            )
            step2a_result = response.choices[0].message.content
            full_analysis += f"### A. EAR対象Productの判定\n{step2a_result}\n\n"
            
            with result_container:
                st.markdown("### 🔍 Step 2-A: EAR-Controlled Items Determination")
                st.markdown(step2a_result)
                st.markdown("---")
        except Exception as e:
            st.error(f"Step 2-A Error: {str(e)}")
    
    # ステップ2-B: ECCN番号判定
    with st.spinner("🔢 Step 2-B: Determining ECCN number..."):
        step2b_prompt = f"""
Product: {contract_text[:1000]}

{eccn_data_text[:2500]}

Refer to the ECCN database above and determine the most appropriate ECCN number.

### B. ECCN Number Determination
- **推定ECCN番号**: [5桁の番号、e.g., 3A001、5A002、またはEAR99]
- **Category**: [1桁目の意味]
- **Group**: [2桁目の意味]
- **Reason for Control**: [3桁目：NS=National Security、MT=Missile Technology、等]
- **Selection Rationale**: [Why this ECCN was chosen]

Please respond in the format above.
"""
        try:
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "あなたは米国EAR再輸出規制の専門家です。ECCNデータベースを参照して正確に判定してください。"},
                    {"role": "user", "content": step2b_prompt}
                ],
                temperature=0.2,
                max_tokens=600
            )
            step2b_result = response.choices[0].message.content
            full_analysis += f"### B. ECCN Number Determination\n{step2b_result}\n\n"
            
            with result_container:
                st.markdown("### 🔢 Step 2-B: ECCN Number Determination")
                st.markdown(step2b_result)
                st.markdown("---")
        except Exception as e:
            st.error(f"Step 2-B Error: {str(e)}")
    
    # ステップ2-C: カントリーチャート分析
    with st.spinner("🗺️ Step 2-C: Analyzing Country Chart..."):
        step2c_prompt = f"""
Product: {contract_text[:1000]}

{country_chart_text[:2500]}

Refer to the Country Chart data above and determine regulations for the destination country.

### C. Country Chart Analysis
- Destination country
- Applicable reasons for control (NS 1, NS 2, MT 1, NP 1, etc.)
- License requirement for each reason (\'X\' mark indicates license required)
- Overall determination (License Required or License Exception Available or No License Required)

Please respond in the format above.
"""
        try:
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "あなたは米国EAR再輸出規制の専門家です。カントリーチャートを参照して正確に判定してください。"},
                    {"role": "user", "content": step2c_prompt}
                ],
                temperature=0.2,
                max_tokens=600
            )
            step2c_result = response.choices[0].message.content
            full_analysis += f"### C. Country Chart Analysis\n{step2c_result}\n\n"
            
            with result_container:
                st.markdown("### 🗺️ Step 2-C: Country Chart Analysis")
                st.markdown(step2c_result)
                st.markdown("---")
        except Exception as e:
            st.error(f"Step 2-C Error: {str(e)}")
    
    # ステップ2-D: 許可例外の検討
    with st.spinner("📋 Step 2-D: Reviewing License Exceptions..."):
        step2d_prompt = f"""
Product: {contract_text[:1000]}

### D. License Exception Review
Applicable license exceptions（LVS, GBS, TSR, TMP, ENC等）について検討してください。

- Applicable license exceptions
- Application conditions
- Determination rationale

簡潔に回答してください。
"""
        try:
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "あなたは米国EAR再輸出規制の専門家です。"},
                    {"role": "user", "content": step2d_prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            step2d_result = response.choices[0].message.content
            full_analysis += f"### D. License Exception Review\n{step2d_result}\n\n"
            
            with result_container:
                st.markdown("### 📋 Step 2-D: License Exception Review")
                st.markdown(step2d_result)
                st.markdown("---")
        except Exception as e:
            st.error(f"Step 2-D Error: {str(e)}")
    
    # ステップ2-E: 禁輸国・リスト規制
    with st.spinner("🚨 Step 2-E: Checking Embargo & Restricted Lists..."):
        step2e_prompt = f"""
Product: {contract_text[:1000]}

### E. Embargo Countries & Restricted Lists
Please check the following:

- DPL（Denied Persons List）該当チェック
- Entity List該当チェック
- Check for embargo countries (North Korea, Iran, Syria, Cuba, Crimea)
- Military End User List該当チェック

Please make a concise determination.
"""
        try:
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "あなたは米国EAR再輸出規制の専門家です。"},
                    {"role": "user", "content": step2e_prompt}
                ],
                temperature=0.3,
                max_tokens=400
            )
            step2e_result = response.choices[0].message.content
            full_analysis += f"### E. Embargo Countries & Restricted Lists\n{step2e_result}\n\n"
            
            with result_container:
                st.markdown("### 🚨 Step 2-E: Embargo & Restricted Lists")
                st.markdown(step2e_result)
                st.markdown("---")
        except Exception as e:
            st.error(f"Step 2-E Error: {str(e)}")
    
    # ステップ3: 総合判定とリスク評価
    with st.spinner("📊 Step 3: Overall Assessment & Risk Evaluation..."):
        step3_prompt = f"""
Analysis results so far:
{full_analysis}

Based on the analysis results above, make an overall assessment.

## 3. Overall Assessment & Risk Evaluation
- **US EAR Determination**: License Required / License Exception Available / No License Required
- **Risk Level**: High / Medium / Low
- **Recommended Actions**: Specific next steps

Please make a clear determination.
"""
        try:
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "あなたは米国EAR再輸出規制の専門家です。"},
                    {"role": "user", "content": step3_prompt}
                ],
                temperature=0.3,
                max_tokens=600
            )
            step3_result = response.choices[0].message.content
            full_analysis += f"## 3. Overall Assessment & Risk Evaluation\n{step3_result}\n\n"
            
            with result_container:
                st.markdown("### 📊 Step 3: Overall Assessment & Risk Evaluation")
                st.markdown(step3_result)
                st.markdown("---")
        except Exception as e:
            st.error(f"Step 3 Error: {str(e)}")
    
    # ステップ4: 必要な手続き
    with st.spinner("📝 Step 4: Determining Required Procedures..."):
        step4_prompt = f"""
Overall Assessment: {step3_result[:500]}

## 4. Required Procedures
Specific procedures and contact points for BIS license application if requiredを説明してください。

簡潔に回答してください。
"""
        try:
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "あなたは米国EAR再輸出規制の専門家です。"},
                    {"role": "user", "content": step4_prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            step4_result = response.choices[0].message.content
            full_analysis += f"## 4. Required Procedures\n{step4_result}\n\n"
            
            with result_container:
                st.markdown("### 📝 Step 4: Required Procedures")
                st.markdown(step4_result)
        except Exception as e:
            st.error(f"Step 4 Error: {str(e)}")
    
    return full_analysis



def analyze_chat_step_by_step(product_input, destination_input, additional_info, eccn_context, chart_context, knowledge_base, result_container):
    """Step-by-step analysis for chat consultation"""
    
    full_analysis = ""
    
    # ステップ1: ECCN番号判定
    with st.spinner("🔢 Step 1: Determining ECCN number..."):
        step1_prompt = f"""
あなたは米国輸出管理規則（EAR）の専門家です。

Product Name: {product_input}

{eccn_context[:2500]}

Refer to the ECCN database above and determine the most appropriate ECCN number.

必ず以下の形式で回答：
- **推定ECCN番号**: [5桁の番号] または EAR99
- **分類**: [カテゴリー名]
- **Group**: [グループ名]
- **Reason for Control**: [NS, AT, MT等]
- **選定理由**: [詳細な理由]
"""
        try:
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "あなたは米国EAR規制の専門家です。"},
                    {"role": "user", "content": step1_prompt}
                ],
                temperature=0.2,
                max_tokens=600
            )
            step1_result = response.choices[0].message.content
            full_analysis += f"## ステップ1: ECCN番号判定\n{step1_result}\n\n"
            
            with result_container:
                st.markdown("### 🔢 Step 1: ECCN Number Determination")
                st.markdown(step1_result)
                st.markdown("---")
        except Exception as e:
            st.error(f"Step 1 Error: {str(e)}")
            return None
    
    # ステップ2: カントリーチャート分析
    if destination_input:
        with st.spinner("🗺️ Step 2: Analyzing Country Chart..."):
            step2_prompt = f"""
Product: {product_input}
Destination: {destination_input}

{chart_context[:2500]}

上記のカントリーチャートを参照し、Destinationに対する規制を判定してください。

必ず以下を分析：
- Destination名
- 規制理由（NS, AT, MT等）ごとの許可要否
- 「×」マークがある場合は許可必要
- 総合判定
"""
            try:
                response = client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {"role": "system", "content": "あなたは米国EAR規制の専門家です。"},
                        {"role": "user", "content": step2_prompt}
                    ],
                    temperature=0.2,
                    max_tokens=600
                )
                step2_result = response.choices[0].message.content
                full_analysis += f"## ステップ2: カントリーチャート分析\n{step2_result}\n\n"
                
                with result_container:
                    st.markdown("### 🗺️ Step 2: Country Chart Analysis")
                    st.markdown(step2_result)
                    st.markdown("---")
            except Exception as e:
                st.error(f"ステップ2エラー: {str(e)}")
    
    # ステップ3: General Prohibitions確認
    with st.spinner("🚨 Step 3: Checking General Prohibitions..."):
        step3_prompt = f"""
Product: {product_input}
Destination: {destination_input if destination_input else 'Not specified'}

{knowledge_base[:1500]}

Please check the following:

**GP4: Denied Parties Lists（DPL）**
**GP5: End-Use/End-User Controls（Entity List）**
**GP6: Embargo Countries**
**GP7: Proliferation Activities Prohibition**
**GP8: Transit Controls**

Determine applicability for each item.
"""
        try:
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "あなたは米国EAR規制の専門家です。"},
                    {"role": "user", "content": step3_prompt}
                ],
                temperature=0.3,
                max_tokens=600
            )
            step3_result = response.choices[0].message.content
            full_analysis += f"## ステップ3: General Prohibitions\n{step3_result}\n\n"
            
            with result_container:
                st.markdown("### 🚨 Step 3: General Prohibitions Check")
                st.markdown(step3_result)
                st.markdown("---")
        except Exception as e:
            st.error(f"Step 3 Error: {str(e)}")
    
    # ステップ4: 総合判定
    with st.spinner("📊 Step 4: Overall Assessment & Risk Evaluation..."):
        step4_prompt = f"""
Analysis results so far:

{full_analysis}

Additional Info: {additional_info if additional_info else 'None'}

上記を踏まえて、総合判定を行ってください。

必ず以下の形式で回答：

### 📊 リスク評価
- **リスクレベル**: ⚠️ 高 / ⚠️ 中 / ✅ 低
- **License Application Requirement**: 必要 / 要確認 / 不要

### 🚨 警告事項（該当する場合）
[該当するGeneral Prohibitions]

### 📋 推奨アクション
1. [Specific next steps]
2. [Items to verify]
3. [Procedures if application required]
"""
        try:
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "あなたは米国EAR規制の専門家です。"},
                    {"role": "user", "content": step4_prompt}
                ],
                temperature=0.3,
                max_tokens=700
            )
            step4_result = response.choices[0].message.content
            full_analysis += f"## ステップ4: 総合判定\n{step4_result}\n\n"
            
            with result_container:
                st.markdown("### 📊 ステップ4: 総合判定とリスク評価")
                st.markdown(step4_result)
                st.markdown("---")
        except Exception as e:
            st.error(f"Step 4 Error: {str(e)}")
    
    return full_analysis

def main():
    # Enhanced Header with Icon
    st.markdown('''
    <div class="main-header">
        <span style="font-size: 3.5rem; margin-right: 1rem;">🌐</span>
        Export Control AI Assistant
    </div>
    ''', unsafe_allow_html=True)
    
    # Subtitle with description
    st.markdown('''
    <div style="text-align: center; margin-top: -1.5rem; margin-bottom: 2.5rem; color: #64748b; font-size: 1.1rem; font-weight: 500;">
        Smart AI-Powered Analysis for US EAR Re-export Regulations
    </div>
    ''', unsafe_allow_html=True)
    
    # Enhanced database status display with modern cards
    if 'eccn_json' in st.session_state.sample_data and st.session_state.sample_data['eccn_json']:
        eccn_count = sum(get_eccn_categories_summary(st.session_state.sample_data['eccn_json']).values())
        
        # Create a modern status bar
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f'''
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 12px; text-align: center; box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);">
                <div style="color: white; font-size: 2rem; font-weight: 800; margin-bottom: 0.5rem;">{eccn_count}</div>
                <div style="color: rgba(255,255,255,0.9); font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">ECCN Items</div>
            </div>
            ''', unsafe_allow_html=True)
        
        with col2:
            st.markdown('''
            <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 1.5rem; border-radius: 12px; text-align: center; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);">
                <div style="color: white; font-size: 2rem; font-weight: 800; margin-bottom: 0.5rem;">33+</div>
                <div style="color: rgba(255,255,255,0.9); font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Countries</div>
            </div>
            ''', unsafe_allow_html=True)
        
        with col3:
            st.markdown('''
            <div style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); padding: 1.5rem; border-radius: 12px; text-align: center; box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);">
                <div style="color: white; font-size: 2rem; font-weight: 800; margin-bottom: 0.5rem;">✓</div>
                <div style="color: rgba(255,255,255,0.9); font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">RAG Active</div>
            </div>
            ''', unsafe_allow_html=True)
        
        with col4:
            st.markdown('''
            <div style="background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%); padding: 1.5rem; border-radius: 12px; text-align: center; box-shadow: 0 4px 12px rgba(6, 182, 212, 0.3);">
                <div style="color: white; font-size: 2rem; font-weight: 800; margin-bottom: 0.5rem;">🚀</div>
                <div style="color: rgba(255,255,255,0.9); font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Online</div>
            </div>
            ''', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    # Sidebar with enhanced design
    with st.sidebar:
        st.markdown('''
        <div style="text-align: center; padding: 1rem 0; margin-bottom: 1.5rem;">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">🛡️</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: #667eea;">Export Control</div>
            <div style="font-size: 0.9rem; color: #64748b;">AI Assistant</div>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown("### 📚 System Information")
        st.info("""
        **Main Features**
        
        - ✅ AI Contract Analysis
        - ✅ US EAR Decision Flow
        - ✅ ECCN Search
        - ✅ Country Chart Analysis
        - ✅ Risk Assessment
        - ✅ RAG License Exception
        
        **Database**
        - ECCN Numbers: 141 items
        - Country List: 33 countries
        - License Exception Info: RAG-enabled
        """)
        
        st.markdown("### ⚠️ Disclaimer")
        st.warning("""
        This system provides reference information only.
        
        Consult with experts for legal decisions.
        """)
        
        # Version info
        st.markdown("---")
        st.caption("Version 2.0 - Enhanced UI")
        st.caption("© 2025 Export Control AI")
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["📄 Contract Analysis", "💬 Chat Consultation", "📊 Data Management"])
    
    with tab1:
        st.markdown('<div class="section-header">Contract Upload</div>', unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Upload export contract PDF or enter text information",
            type=['pdf', 'txt'],
            help="AI will automatically analyze when you upload a contract"
        )
        
        # Manual input option
        with st.expander("📝 Or Enter Contract Information Manually"):
            col1, col2 = st.columns(2)
            with col1:
                product_name = st.text_input("Product Name")
                destination = st.text_input("Destination Country")
                end_user = st.text_input("End User")
            with col2:
                purpose = st.text_area("End Use")
                amount = st.text_input("Contract Value")
                delivery_date = st.date_input("Delivery Date")
            
            manual_text = f"""
Product Name: {product_name}
Destination: {destination}
需要者: {end_user}
End Use: {purpose}
Contract Value: {amount}
Delivery Date: {delivery_date}
"""
        
        if st.button("🔍 Start Analysis", type="primary"):
            knowledge_base = load_knowledge_base()
            
            if uploaded_file is not None:
                if uploaded_file.type == "application/pdf":
                    uploaded_file.seek(0)  # ファイルポインタを先頭に戻す
                    contract_text = extract_text_from_pdf(uploaded_file)
                else:
                    contract_text = uploaded_file.read().decode('utf-8')
            else:
                contract_text = manual_text
            
            if contract_text.strip():
                # 契約情報を抽出
                st.session_state.extracted_info = extract_contract_info(contract_text)
                
                # 追加情報の収集
                additional_context = ""
                
                # Destinationチェック
                if st.session_state.extracted_info['Destination']:
                    destination = st.session_state.extracted_info['Destination']
                    is_group_a = check_group_a_country(destination, st.session_state.sample_data.get('countries'))
                    is_concern, concern_type = check_concern_country(destination, st.session_state.sample_data.get('countries'))
                    
                    additional_context += f"\n\n[Destination Information]\n"
                    additional_context += f"- Destination: {destination}\n"
                    additional_context += f"- Group A Country: {'Yes' if is_group_a else 'No'}\n"
                    if is_concern:
                        additional_context += f"- ⚠️ Country of Concern: {concern_type}\n"
                
                # 需要者チェック
                if st.session_state.extracted_info['需要者']:
                    end_user = st.session_state.extracted_info['需要者']
                    is_listed, entity_info = check_entity_list(end_user, st.session_state.sample_data.get('entities'))
                    
                    if is_listed:
                        additional_context += f"\n[End User Information]\n"
                        additional_context += f"- ⚠️ Possibly listed on Entity List\n"
                        additional_context += f"- Listing Reason: {entity_info['掲載理由']}\n"
                        additional_context += f"- Regulation: {entity_info['規制内容']}\n"
                
                # 段階的AI分析実行
                st.markdown('<div class="section-header">📋 Analysis Results (Progressive Display)</div>', unsafe_allow_html=True)
                result_container = st.container()
                
                analysis = analyze_contract_step_by_step(contract_text + additional_context, knowledge_base, result_container)
                st.session_state.analysis_result = analysis
            else:
                st.error("No contract information provided")
        
        # Display analysis results and download options
        if st.session_state.analysis_result:
            st.markdown("---")
            
            # Download buttons
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📥 Download Analysis (Text)",
                    data=st.session_state.analysis_result,
                    file_name=f"export_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
            with col2:
                # 詳細レポートの生成
                risk_level = assess_risk_level(st.session_state.analysis_result)
                full_report = f"""Export Control Analysis Report
Generated: {datetime.now().strftime('%Y/%m/%d %H:%M:%S')}

[Risk Level]
{risk_level}

[Extracted Contract Information]
"""
                if st.session_state.extracted_info:
                    for key, value in st.session_state.extracted_info.items():
                        full_report += f"{key}: {value}\n"
                
                full_report += f"\n[AI Analysis Results]\n{st.session_state.analysis_result}\n\n"
                full_report += "\n[Disclaimer]\nThis analysis is for reference only and not legal advice. Consult with experts or authorities for final decisions."
                
                st.download_button(
                    label="📥 Download Detailed Report",
                    data=full_report,
                    file_name=f"export_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
    
    with tab2:
        st.markdown('<div class="section-header">💬 米国EAR再輸出規制 チャット相談</div>', unsafe_allow_html=True)
        st.info("🇺🇸 米国から輸入したProductを日本から他国へ再輸出する際の米国EAR規制を分析します。Product NameとDestinationを入力してください。")
        
        # Enhanced Chat interface with structured input
        col1, col2 = st.columns(2)
        with col1:
            product_input = st.text_input("Product Name（e.g., semiconductor equipment、encryption software）", key="chat_product")
        with col2:
            destination_input = st.text_input("Destination (e.g., China, Russia)", key="chat_destination")
        
        additional_info = st.text_area("Additional Information/Questions (Optional)", key="chat_additional", height=100)
        
        if st.button("🔍 Start Analysis（RAG許可例外判定含む）", key="chat_submit", type="primary"):
            if product_input:
                # データ準備
                eccn_json = st.session_state.sample_data.get('eccn_json')
                country_chart = st.session_state.sample_data.get('country_chart')
                
                # ECCN番号データをテキスト化（完全版）
                eccn_context = ""
                if eccn_json:
                    eccn_context = "[ECCN Number Database (Complete)]\n"
                    for category in eccn_json.get('ccl_categories', []):
                        eccn_context += f"\n## Category {category.get('category_number', '')}: {category.get('title', '')}\n"
                        for group in category.get('product_groups', []):
                            eccn_context += f"\n### {group.get('group_title', '')}\n"
                            for item in group.get('items', [])[:10]:  # Max 10 items from each group
                                eccn_context += f"- **{item.get('eccn', '')}**: {item.get('description', '')[:200]}...\n"
                
                # カントリーチャートデータをテキスト化（完全版）
                chart_context = ""
                if country_chart is not None and not country_chart.empty:
                    chart_context = "\n[Country Chart (Complete)]\n"
                    chart_context += "Below is actual US EAR Country Chart data.\'X\'は許可が必要であることを示します。\n\n"
                    # 主要国を含める（トークン制限を考慮）
                    for idx, row in country_chart.head(50).iterrows():
                        country_name = row.iloc[0]
                        chart_context += f"\n**{country_name}**:\n"
                        # Show only key regulation reason columns
                        key_columns = ['NS 1', 'NS 2', 'MT 1', 'NP 1', 'NP 2', 'CB 1', 'CB 2', 'AT 1', 'AT 2']
                        for col in key_columns:
                            if col in row.index and pd.notna(row[col]):
                                chart_context += f"  - {col}: {row[col]}\n"
                
                # General Prohibitionsの情報を追加
                knowledge_base = load_knowledge_base()
                
                # 段階的分析を表示
                st.markdown('<div class="section-header">📋 Analysis Results (Progressive Display)</div>', unsafe_allow_html=True)
                result_container = st.container()
                
                # 段階的分析実行
                analysis = analyze_chat_step_by_step(
                    product_input, 
                    destination_input, 
                    additional_info, 
                    eccn_context, 
                    chart_context, 
                    knowledge_base,
                    result_container
                )
                
                # ステップ5: RAG許可例外判定
                with st.spinner("🎯 Step 5: Analyzing RAG License Exceptions..."):
                    with result_container:
                        st.markdown("### 🎯 Step 5: License Exceptions Determination [RAG Analysis]")
                        
                        try:
                            # RAG分析実行
                            success, rag_result = check_license_exception_with_rag(
                                eccn_number="推定ECCN（AIが判定したもの）",
                                destination=destination_input,
                                product_description=product_input,
                                end_user=None,
                                end_use=additional_info if additional_info else None
                            )
                            
                            if success:
                                # RAGAnalysis Resultsを表示
                                rag = LicenseExceptionRAG()
                                rag.display_license_exception_analysis(rag_result)
                            else:
                                st.warning(f"⚠️ Error occurred in RAG analysis: {rag_result.get('error', '不明')}")
                                st.info("💡 Check Pinecone connection. Verify PINECONE_API_KEY is set in .env file.")
                        
                        except Exception as e:
                            st.error(f"❌ RAG System Error: {str(e)}")
                            st.info("**RAG System Setup**: Add PINECONE_API_KEY to .env file.")
                        
                        st.markdown("---")
                
                # チャット履歴に保存
                st.session_state.chat_history.append({
                    "product": product_input,
                    "destination": destination_input,
                    "question": additional_info if additional_info else "ECCN Determination & Country Chart Analysis",
                    "answer": analysis if analysis else "Analysis Complete",
                    "timestamp": datetime.now()
                })
                
                # カントリーチャート詳細表示
                if destination_input and country_chart is not None and not country_chart.empty:
                    with result_container:
                        st.markdown("### 📊 Country Chart Details")
                        
                        # 国名で検索（部分一致）
                        matching_countries = country_chart[
                            country_chart.iloc[:, 0].str.contains(destination_input, case=False, na=False)
                        ]
                        
                        if not matching_countries.empty:
                            st.dataframe(matching_countries, use_container_width=True)
                        else:
                            st.warning(f"⚠️ '{destination_input}' not found in Country Chart.")
            else:
                st.warning("Please enter Product Name.")
        
        # Display chat history
        if st.session_state.chat_history:
            st.markdown("---")
            st.markdown("### 💬 Analysis History")
            for i, chat in enumerate(reversed(st.session_state.chat_history)):
                timestamp_str = chat['timestamp'].strftime('%Y-%m-%d %H:%M')
                product = chat.get('product', chat.get('question', ''))[:30]
                
                with st.expander(f"🔍 {product}... ({timestamp_str})"):
                    if 'product' in chat:
                        st.markdown(f"**Product**: {chat['product']}")
                        if chat.get('destination'):
                            st.markdown(f"**Destination**: {chat['destination']}")
                    st.markdown(f"**Question**: {chat['question']}")
                    st.markdown("---")
                    st.markdown(f"**Analysis Results**:\n\n{chat['answer']}")
    
    with tab3:
        st.markdown('<div class="section-header">📊 Regulation Data Visualization & Management</div>', unsafe_allow_html=True)
        
        st.info("🎨 Intuitive data visualization with interactive charts")
        
        # タブで可視化とデータ管理を分離
        viz_tab1, viz_tab2 = st.tabs([
            "🗺️ World Regulation Map",
            "🔢 ECCN Search"
        ])
        
        with viz_tab1:
            st.markdown("### 🗺️ ECCN番号別 世界規制マップ")
            st.markdown("Visualize which countries require export licenses for specific ECCN numbers")
            
            col1, col2 = st.columns([2, 1])
            with col1:
                eccn_for_map = st.text_input(
                    "Enter ECCN Number",
                    value="3B001",
                    key="map_eccn",
                    help="e.g., 3B001, 5A002, 4A003"
                )
            with col2:
                regulation_reason = st.selectbox(
                    "Select Regulation Reason",
                    ["NS 1", "NS 2", "MT 1", "NP 1", "NP 2", "CB 1", "CB 2", "AT 1", "AT 2"],
                    key="map_regulation"
                )
            
            if st.button("🗺️ Generate Map", type="primary", key="generate_map"):
                if st.session_state.sample_data.get('country_chart') is not None:
                    with st.spinner("Generating map..."):
                        world_map = create_world_map_restrictions(
                            st.session_state.sample_data['country_chart'],
                            eccn_for_map,
                            regulation_reason
                        )
                        if world_map:
                            st.plotly_chart(world_map, use_container_width=True)
                            
                            st.success(f"""
                            ✅ **ECCN {eccn_for_map} - {regulation_reason}** regulation map displayed
                            
                            - 🟢 **Green**: No License Required (Export Allowed)
                            - 🔴 **Red**: License Required (BIS Application Needed)
                            """)
                        else:
                            st.error("Failed to generate map")
                else:
                    st.warning("Country Chart data not loaded")
        
        with viz_tab2:
            st.markdown("### 🔢 ECCN Number Database Search")
            
            # インタラクティブテーブル
            if 'eccn_json' in st.session_state.sample_data:
                eccn_df = create_interactive_eccn_table(st.session_state.sample_data['eccn_json'])
                
                if eccn_df is not None and not eccn_df.empty:
                    st.info(f"📚 Total of **{len(eccn_df)}** ECCN items registered")
                    
                    # 検索機能
                    search_keyword = st.text_input(
                        "🔍 Search by Keyword",
                        placeholder="e.g., semiconductor, encryption, 5A002",
                        key="eccn_search"
                    )
                    
                    if search_keyword:
                        filtered_df = eccn_df[
                            eccn_df.apply(lambda row: row.astype(str).str.contains(search_keyword, case=False).any(), axis=1)
                        ]
                        st.success(f"✅ {len(filtered_df)} matches found")
                        st.dataframe(filtered_df, use_container_width=True, height=500)
                    else:
                        st.dataframe(eccn_df, use_container_width=True, height=500)
                    
                    # クリックで詳細表示（選択機能）
                    st.markdown("---")
                    st.markdown("#### 📋 ECCN Details")
                    selected_eccn = st.selectbox(
                        "Select ECCN number to view details",
                        options=eccn_df['ECCN番号'].unique(),
                        key="selected_eccn_detail"
                    )
                    
                    if selected_eccn:
                        selected_row = eccn_df[eccn_df['ECCN番号'] == selected_eccn].iloc[0]
                        
                        st.markdown(f"""
                        <div class="info-box">
                        <h4>🔢 {selected_eccn}</h4>
                        <p><strong>カテゴリー:</strong> {selected_row['カテゴリー']}</p>
                        <p><strong>グループ:</strong> {selected_row['グループ']}</p>
                        <p><strong>説明:</strong> {selected_row['説明']}</p>
                        <p><strong>規制理由:</strong> {selected_row['規制理由']}</p>
                        <p><strong>参照:</strong> Commerce Control List (CCL)</p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("ECCN data not loaded")

if __name__ == "__main__":
    main()


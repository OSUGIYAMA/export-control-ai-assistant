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
    page_title="米国EAR再輸出規制 判断支援システム",
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
    """GPTで契約書を分析（米国EAR再輸出規制のみ）"""
    
    # ECCN番号データベースを準備
    eccn_json = st.session_state.sample_data.get('eccn_json')
    eccn_data_text = ""
    if eccn_json and 'ccl_categories' in eccn_json:
        eccn_data_text = "\n【ECCN番号データベース（完全版）】\n"
        for category in eccn_json['ccl_categories']:
            eccn_data_text += f"\n## Category {category.get('category_number', '')}: {category.get('title', '')}\n"
            for group in category.get('product_groups', []):
                eccn_data_text += f"\n### {group.get('group_title', '')}\n"
                for item in group.get('items', [])[:10]:  # 各グループから最大10項目
                    eccn_data_text += f"- **{item.get('eccn', '')}**: {item.get('description', '')[:200]}...\n"
    
    # カントリーチャートデータを準備
    country_chart = st.session_state.sample_data.get('country_chart')
    country_chart_text = ""
    if country_chart is not None and not country_chart.empty:
        country_chart_text = "\n【カントリーチャート（完全版）】\n"
        country_chart_text += "以下は米国EARカントリーチャートの実データです。\'X\'は許可が必要であることを示します。\n\n"
        # 最初の30カ国程度を含める（トークン制限を考慮）
        for idx, row in country_chart.head(30).iterrows():
            country_name = row.iloc[0]
            country_chart_text += f"\n**{country_name}**:\n"
            # 主要な規制理由カラムのみ表示
            key_columns = ['NS 1', 'NS 2', 'MT 1', 'NP 1', 'NP 2', 'CB 1', 'AT 1']
            for col in key_columns:
                if col in row.index and pd.notna(row[col]):
                    country_chart_text += f"  - {col}: {row[col]}\n"
    
    prompt = f"""
あなたは米国EAR再輸出規制の専門家です。以下の契約書を分析し、米国EAR規制について判断してください。

【重要な前提】
このシステムは「米国から輸入した品目を日本から他国へ再輸出する場合」の米国EAR規制のみを分析します。
日本の外為法は分析対象外です。

【契約書内容】
{contract_text[:5000]}  # トークン制限のため最初の5000文字

{eccn_data_text[:3000]}

{country_chart_text[:3000]}

【ナレッジベース（参考）】
{knowledge_base[:1000]}

以下の項目について詳細に分析してください：

## 1. 契約情報の抽出
- 品目名・製品名（米国原産品かどうか）
- 再輸出先（日本→他国）
- 需要者（エンドユーザー）情報
- 最終用途（End Use）
- 契約金額
- 納期

## 2. 米国EAR再輸出判断フロー分析

### A. EAR対象品目の再輸出に該当するか
米国原産品・組込品・外国直接製品の可能性を評価

### B. ECCN番号の判定
上記のECCN番号データベースを参照し、最も適切なECCN番号を判定してください。
- 推定ECCN番号（5桁の番号、例：3A001、5A002、またはEAR99）
- カテゴリー（1桁目の意味）
- グループ（2桁目の意味）
- 規制理由（3桁目：NS=国家安全保障、MT=ミサイル技術、NP=核不拡散、等）
- 選定理由（なぜこのECCN番号を選んだか詳細に説明）

### C. カントリーチャート分析
上記のカントリーチャートデータを参照し、仕向国に対する規制を判定してください。
- 仕向国名
- 該当する規制理由（NS 1, NS 2, MT 1, NP 1, 等）
- 各規制理由での許可要否（\'X\'マークがあれば許可必要）
- 総合判定（許可必要 or 許可例外が適用可能 or 許可不要）

### D. 許可例外の検討
適用可能な許可例外（LVS, GBS, TSR, TMP, ENC等）を検討

### E. 禁輸国・リスト規制
- DPL（Denied Persons List）該当チェック
- Entity List該当チェック
- 禁輸国（北朝鮮、イラン、シリア、キューバ、クリミア）該当チェック

## 3. 総合判定とリスク評価
- **米国EAR判定**: 許可必要 / 許可例外適用可能 / 許可不要
- **リスクレベル**: 高 / 中 / 低
- **推奨アクション**: 具体的な次のステップ

## 4. 必要な手続き
BISへの許可申請が必要な場合の具体的な手順と窓口

**重要**: 外為法については言及しないでください。このシステムは米国EAR規制のみを扱います。

明確で構造化された形式で回答してください。
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "あなたは米国EAR再輸出規制の専門家です。米国から輸入した品目を日本から他国へ再輸出する際の規制を分析します。日本の外為法は対象外です。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=3000
        )
        
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"分析エラー: {str(e)}")
        return None

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
        米国EAR再輸出規制の判断を、AI技術でスマートにサポート
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
        
        st.markdown("### 📚 システム情報")
        st.info("""
        **主な機能**
        
        - ✅ 契約書AI分析
        - ✅ 米国EAR判断フロー
        - ✅ ECCN番号検索
        - ✅ カントリーチャート分析
        - ✅ リスク評価
        - ✅ RAG許可例外判定
        
        **データベース**
        - ECCN番号: 141項目
        - カントリーリスト: 33カ国
        - 許可例外情報: RAG対応
        """)
        
        st.markdown("### ⚠️ 免責事項")
        st.warning("""
        本システムは参考情報を提供するツールです。
        
        法的判断が必要な場合は専門家にご相談ください。
        """)
        
        # Version info
        st.markdown("---")
        st.caption("Version 2.0 - Enhanced UI")
        st.caption("© 2025 Export Control AI")
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["📄 契約書分析", "💬 チャット相談", "📊 データ管理"])
    
    with tab1:
        st.markdown('<div class="section-header">契約書アップロード</div>', unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "輸出契約書PDF、またはテキスト情報を入力してください",
            type=['pdf', 'txt'],
            help="契約書をアップロードすると、AIが自動的に分析します"
        )
        
        # Manual input option
        with st.expander("📝 または、契約情報を手動で入力"):
            col1, col2 = st.columns(2)
            with col1:
                product_name = st.text_input("品目名")
                destination = st.text_input("仕向地（輸出先国）")
                end_user = st.text_input("需要者（エンドユーザー）")
            with col2:
                purpose = st.text_area("用途")
                amount = st.text_input("契約金額")
                delivery_date = st.date_input("納期")
            
            manual_text = f"""
品目名: {product_name}
仕向地: {destination}
需要者: {end_user}
用途: {purpose}
契約金額: {amount}
納期: {delivery_date}
"""
        
        if st.button("🔍 分析開始", type="primary"):
            with st.spinner("契約書を分析中..."):
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
                    
                    # 仕向地チェック
                    if st.session_state.extracted_info['仕向地']:
                        destination = st.session_state.extracted_info['仕向地']
                        is_group_a = check_group_a_country(destination, st.session_state.sample_data.get('countries'))
                        is_concern, concern_type = check_concern_country(destination, st.session_state.sample_data.get('countries'))
                        
                        additional_context += f"\n\n【仕向地情報】\n"
                        additional_context += f"- 仕向地: {destination}\n"
                        additional_context += f"- グループA国: {'はい' if is_group_a else 'いいえ'}\n"
                        if is_concern:
                            additional_context += f"- ⚠️ 懸念国: {concern_type}\n"
                    
                    # 需要者チェック
                    if st.session_state.extracted_info['需要者']:
                        end_user = st.session_state.extracted_info['需要者']
                        is_listed, entity_info = check_entity_list(end_user, st.session_state.sample_data.get('entities'))
                        
                        if is_listed:
                            additional_context += f"\n【需要者情報】\n"
                            additional_context += f"- ⚠️ エンティティリスト掲載企業の可能性あり\n"
                            additional_context += f"- 掲載理由: {entity_info['掲載理由']}\n"
                            additional_context += f"- 規制内容: {entity_info['規制内容']}\n"
                    
                    # AI分析実行
                    analysis = analyze_contract_with_gpt(contract_text + additional_context, knowledge_base)
                    st.session_state.analysis_result = analysis
                else:
                    st.error("契約情報が入力されていません")
        
        # Display analysis results
        if st.session_state.analysis_result:
            st.markdown('<div class="section-header">📋 分析結果</div>', unsafe_allow_html=True)
            
            # リスクレベルの評価
            risk_level = assess_risk_level(st.session_state.analysis_result)
            
            # リスクレベルに応じた色分け
            if risk_level == "高":
                st.markdown('<div class="danger-box"><strong>⚠️ リスクレベル: 高</strong><br>詳細な審査と許可申請が必要な可能性が高いです</div>', unsafe_allow_html=True)
            elif risk_level == "中":
                st.markdown('<div class="warning-box"><strong>⚠️ リスクレベル: 中</strong><br>追加確認と慎重な判断が必要です</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="success-box"><strong>✅ リスクレベル: 低</strong><br>重大な懸念は検出されていません</div>', unsafe_allow_html=True)
            
            # 抽出された情報を表示
            if st.session_state.extracted_info:
                st.markdown("### 📝 抽出された契約情報")
                info_df = pd.DataFrame([st.session_state.extracted_info]).T
                info_df.columns = ['内容']
                st.dataframe(info_df, use_container_width=True)
            
            # AI分析結果を表示
            st.markdown("### 🤖 AI分析詳細")
            st.markdown(st.session_state.analysis_result)
            
            # 推奨アクションを表示
            st.markdown("### ✅ 推奨アクション")
            actions = generate_action_items(st.session_state.analysis_result)
            for action in actions:
                st.markdown(f"- {action}")
            
            # Download buttons
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📥 分析結果をダウンロード（テキスト）",
                    data=st.session_state.analysis_result,
                    file_name=f"export_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
            with col2:
                # 詳細レポートの生成
                full_report = f"""安全保障貿易管理 分析レポート
生成日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}

【リスクレベル】
{risk_level}

【抽出された契約情報】
"""
                if st.session_state.extracted_info:
                    for key, value in st.session_state.extracted_info.items():
                        full_report += f"{key}: {value}\n"
                
                full_report += f"\n【AI分析結果】\n{st.session_state.analysis_result}\n\n【推奨アクション】\n"
                for action in actions:
                    full_report += f"{action}\n"
                
                full_report += "\n【免責事項】\n本分析結果は参考情報であり、法的助言ではありません。最終判断は必ず専門家や関係当局にご相談ください。"
                
                st.download_button(
                    label="📥 詳細レポートをダウンロード",
                    data=full_report,
                    file_name=f"export_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
    
    with tab2:
        st.markdown('<div class="section-header">💬 米国EAR再輸出規制 チャット相談</div>', unsafe_allow_html=True)
        st.info("🇺🇸 米国から輸入した品目を日本から他国へ再輸出する際の米国EAR規制を分析します。品目名と仕向地を入力してください。")
        
        # Enhanced Chat interface with structured input
        col1, col2 = st.columns(2)
        with col1:
            product_input = st.text_input("品目名（例：半導体製造装置、暗号化ソフトウェア）", key="chat_product")
        with col2:
            destination_input = st.text_input("仕向地（例：中国、ロシア）", key="chat_destination")
        
        additional_info = st.text_area("追加情報・質問（オプション）", key="chat_additional", height=100)
        
        if st.button("🔍 分析開始（RAG許可例外判定含む）", key="chat_submit", type="primary"):
            if product_input:
                with st.spinner("ECCN番号を判定し、カントリーチャートを分析中..."):
                    # データ準備
                    eccn_json = st.session_state.sample_data.get('eccn_json')
                    country_chart = st.session_state.sample_data.get('country_chart')
                    
                    # ECCN番号データをテキスト化（完全版）
                    eccn_context = ""
                    if eccn_json:
                        eccn_context = "【ECCN番号データベース（完全版）】\n"
                        for category in eccn_json.get('ccl_categories', []):
                            eccn_context += f"\n## Category {category.get('category_number', '')}: {category.get('title', '')}\n"
                            for group in category.get('product_groups', []):
                                eccn_context += f"\n### {group.get('group_title', '')}\n"
                                for item in group.get('items', [])[:10]:  # 各グループから最大10項目
                                    eccn_context += f"- **{item.get('eccn', '')}**: {item.get('description', '')[:200]}...\n"
                    
                    # カントリーチャートデータをテキスト化（完全版）
                    chart_context = ""
                    if country_chart is not None and not country_chart.empty:
                        chart_context = "\n【カントリーチャート（完全版）】\n"
                        chart_context += "以下は米国EARカントリーチャートの実データです。\'X\'は許可が必要であることを示します。\n\n"
                        # 主要国を含める（トークン制限を考慮）
                        for idx, row in country_chart.head(50).iterrows():
                            country_name = row.iloc[0]
                            chart_context += f"\n**{country_name}**:\n"
                            # 主要な規制理由カラムのみ表示
                            key_columns = ['NS 1', 'NS 2', 'MT 1', 'NP 1', 'NP 2', 'CB 1', 'CB 2', 'AT 1', 'AT 2']
                            for col in key_columns:
                                if col in row.index and pd.notna(row[col]):
                                    chart_context += f"  - {col}: {row[col]}\n"
                    
                    # General Prohibitionsの情報を追加
                    knowledge_base = load_knowledge_base()
                    
                    # AIプロンプト構築
                    chat_prompt = f"""
あなたは米国輸出管理規則（EAR）の再輸出規制の専門家です。

【重要な前提】
このシステムは「米国から輸入した品目を日本から他国へ再輸出する場合」の米国EAR規制のみを分析します。
日本の外為法は対象外です。

【ユーザー入力】
- 品目名（米国原産品）: {product_input}
- 再輸出先（日本→他国）: {destination_input if destination_input else '未指定'}
- 追加情報: {additional_info if additional_info else 'なし'}

【分析手順】

## ステップ1: ECCN番号の判定

品目名から、最も適切と思われるECCN番号を以下のデータベースから選択してください。

{eccn_context}

必ず以下の形式でECCN番号を提示してください：
- **推定ECCN番号**: [5桁のECCN番号] または EAR99（規制対象外）
- **分類**: [1桁目] - [カテゴリー名]
- **グループ**: [2桁目] - [グループ名]
- **規制理由**: [3桁目の説明]（例: NS=国家安全保障, AT=反テロ, MT=ミサイル技術等）
- **選定理由**: [なぜこのECCN番号を選んだか]

## ステップ2: カントリーチャート分析

{chart_context}

仕向地が指定されている場合、以下を分析：
1. 規制理由（NS, AT, MT, NP, CB等）ごとの許可要否
2. 「×」マークがある場合は許可申請が必要
3. 許可例外（LVS, GBS, TSR, TMP等）が適用できる可能性

**カントリーチャート判定例**:
- 中国: NS 1: ×, NS 2: ×, MT 1: × → 許可必要
- オーストラリア: ほぼすべて空欄 → 許可不要（友好国）

## ステップ3: 許可例外（License Exceptions）の判定 ★RAG使用★

リスト規制に該当する場合でも、許可例外が適用できれば許可申請が不要になります。
以下の主要な許可例外について、RAGシステムから取得した情報に基づいて判定してください：

**主要な許可例外**:
- **LVS** (Limited Value Shipment): 少額特例
- **GBS** (Shipment to Country Group B): B国群向け貨物
- **TSR** (Technology and Software under Restriction): B国群向け技術・ソフトウェア
- **TMP** (Temporary): 一時的な輸出・展示用
- **ENC** (Encryption): 暗号製品
- その他の許可例外

**判定に必要な情報**:
- ECCN番号と規制理由
- 仕向地（国グループ）
- 品目の性質・価値
- 用途（一時的か恒久的か等）

※この情報はPinecone RAGシステムから自動的に取得されます

## ステップ4: 一般禁止事項（General Prohibitions）の確認 ★重要★

以下の10項目を必ずチェックしてください：

**GP4: 取引禁止リスト**
- DPL（Denied Persons List）に掲載されていないか確認必須
- 該当する場合: ⚠️ 取引全面禁止

**GP5: エンドユース・エンドユーザー規制**
- Entity List（大量破壊兵器拡散懸念企業）
- Unverified List（検証未完了企業）
- Military End User List（軍事エンドユーザー）
- 最終用途が軍事・核・ミサイル・化学生物兵器関連でないか
- 該当する場合: ⚠️ 許可申請必要または取引禁止

**GP6: 禁輸国規制**
- 仕向地が北朝鮮、イラン、シリア、キューバ、クリミアでないか
- 該当する場合: ⚠️ 原則輸出禁止

**GP7: 拡散活動支援禁止**
- 軍事インテリジェンス用途（中国、ロシア、ベラルーシ等）
- 該当する場合: ⚠️ 米国人の関与禁止

**GP8: 通過規制**
- ロシア、ベラルーシ、北朝鮮、中国等を経由しないか
- 該当する場合: ⚠️ 通過許可が必要

## ステップ5: 総合判定

以下の形式で明確に判定してください：

### 📊 リスク評価
- **リスクレベル**: ⚠️ 高 / ⚠️ 中 / ✅ 低
- **許可申請の要否**: 
  - ⚠️ **必要** - BISへの輸出許可申請が必要
  - ⚠️ **要確認** - 詳細確認後に判断
  - ✅ **不要** - 許可申請は不要

### 🚨 警告事項（該当する場合のみ）
- GP4: DPL該当 → 取引禁止
- GP5: Entity List該当 → 許可申請必要
- GP6: 禁輸国 → 輸出禁止
- その他のGP該当状況

### 📋 推奨アクション
1. [具体的な次のステップ]
2. [確認すべき事項]
3. [申請が必要な場合の手順]

**重要事項**:
- ECCN番号は必ず5桁（例: 5A002, 3B001）またはEAR99で表示
- General Prohibitions（GP4-10）は必ず確認
- リスクレベルは保守的に判定（疑わしい場合は「高」または「中」）

【参考: ナレッジベース】
{knowledge_base[:2000]}
"""
                    
                    try:
                        response = client.chat.completions.create(
                            model="gpt-4-turbo-preview",
                            messages=[
                                {"role": "system", "content": "あなたは米国EAR再輸出規制の専門家です。米国から輸入した品目を日本から他国へ再輸出する際の規制を分析します。日本の外為法は分析対象外です。ECCN番号判定、カントリーチャート分析、General Prohibitions（GP4-10）チェックを実施してください。"},
                                {"role": "user", "content": chat_prompt}
                            ],
                            temperature=0.2,
                            max_tokens=2000
                        )
                        
                        answer = response.choices[0].message.content
                        
                        # 結果を表示
                        st.markdown("### 📋 分析結果")
                        st.markdown(answer)
                        
                        # RAGで許可例外を判定（ステップD）
                        st.markdown("---")
                        st.markdown("### 🎯 ステップD: 許可例外（License Exceptions）判定【RAG分析】")
                        
                        with st.spinner("Pinecone RAGで許可例外を分析中..."):
                            try:
                                # RAG分析実行
                                success, rag_result = check_license_exception_with_rag(
                                    eccn_number="推定ECCN（AIが判定したもの）",  # 実際にはAIの回答から抽出
                                    destination=destination_input,
                                    product_description=product_input,
                                    end_user=None,
                                    end_use=additional_info if additional_info else None
                                )
                                
                                if success:
                                    # RAG分析結果を表示
                                    rag = LicenseExceptionRAG()
                                    rag.display_license_exception_analysis(rag_result)
                                else:
                                    st.warning(f"⚠️ RAG分析でエラーが発生しました: {rag_result.get('error', '不明')}")
                                    st.info("💡 Pinecone接続を確認してください。PINECONE_API_KEYが.envファイルに設定されているか確認してください。")
                            
                            except Exception as e:
                                st.error(f"❌ RAGシステムエラー: {str(e)}")
                                st.info("""
                                **RAGシステムの設定**
                                
                                `.env`ファイルに以下を追加してください：
                                ```
                                PINECONE_API_KEY=pcsk_3a2fsG_JL8VwCUz3REyx76mdPG6erdmwazPNM2dU3Ra7c7P11saQz6ovw2aTdPPRiYaKbp
                                ```
                                """)
                        
                        # チャット履歴に保存
                        st.session_state.chat_history.append({
                            "product": product_input,
                            "destination": destination_input,
                            "question": additional_info if additional_info else "ECCN番号判定・カントリーチャート分析",
                            "answer": answer,
                            "timestamp": datetime.now()
                        })
                        
                        # カントリーチャート詳細表示
                        if destination_input and country_chart is not None and not country_chart.empty:
                            st.markdown("---")
                            st.markdown("### 📊 カントリーチャート詳細")
                            
                            # 国名で検索（部分一致）
                            matching_countries = country_chart[
                                country_chart.iloc[:, 0].str.contains(destination_input, case=False, na=False)
                            ]
                            
                            if not matching_countries.empty:
                                st.dataframe(matching_countries, use_container_width=True)
                            else:
                                st.warning(f"⚠️ カントリーチャートに「{destination_input}」の情報が見つかりませんでした。")
                        
                    except Exception as e:
                        st.error(f"エラー: {str(e)}")
            else:
                st.warning("品目名を入力してください。")
        
        # Display chat history
        if st.session_state.chat_history:
            st.markdown("---")
            st.markdown("### 💬 分析履歴")
            for i, chat in enumerate(reversed(st.session_state.chat_history)):
                timestamp_str = chat['timestamp'].strftime('%Y-%m-%d %H:%M')
                product = chat.get('product', chat.get('question', ''))[:30]
                
                with st.expander(f"🔍 {product}... ({timestamp_str})"):
                    if 'product' in chat:
                        st.markdown(f"**品目**: {chat['product']}")
                        if chat.get('destination'):
                            st.markdown(f"**仕向地**: {chat['destination']}")
                    st.markdown(f"**質問**: {chat['question']}")
                    st.markdown("---")
                    st.markdown(f"**分析結果**:\n\n{chat['answer']}")
    
    with tab3:
        st.markdown('<div class="section-header">📊 規制データ可視化 & 管理</div>', unsafe_allow_html=True)
        
        st.info("🎨 インタラクティブな可視化でデータを直感的に理解できます")
        
        # タブで可視化とデータ管理を分離
        viz_tab1, viz_tab2, viz_tab3, viz_tab4 = st.tabs([
            "🗺️ 世界規制マップ",
            "📊 カントリーチャート",
            "🔢 ECCN検索",
            "🚨 制裁リスト"
        ])
        
        with viz_tab1:
            st.markdown("### 🗺️ ECCN番号別 世界規制マップ")
            st.markdown("特定のECCN番号に対して、どの国が規制対象かを地図上で可視化します")
            
            col1, col2 = st.columns([2, 1])
            with col1:
                eccn_for_map = st.text_input(
                    "ECCN番号を入力",
                    value="3B001",
                    key="map_eccn",
                    help="例: 3B001, 5A002, 4A003"
                )
            with col2:
                regulation_reason = st.selectbox(
                    "規制理由を選択",
                    ["NS 1", "NS 2", "MT 1", "NP 1", "NP 2", "CB 1", "CB 2", "AT 1", "AT 2"],
                    key="map_regulation"
                )
            
            if st.button("🗺️ 地図を生成", type="primary", key="generate_map"):
                if st.session_state.sample_data.get('country_chart') is not None:
                    with st.spinner("地図を生成中..."):
                        world_map = create_world_map_restrictions(
                            st.session_state.sample_data['country_chart'],
                            eccn_for_map,
                            regulation_reason
                        )
                        if world_map:
                            st.plotly_chart(world_map, use_container_width=True)
                            
                            st.success(f"""
                            ✅ **ECCN {eccn_for_map} - {regulation_reason}** の規制マップを表示しました
                            
                            - 🟢 **緑**: 許可不要（輸出可能）
                            - 🔴 **赤**: 許可必要（BISへの申請が必要）
                            """)
                        else:
                            st.error("地図の生成に失敗しました")
                else:
                    st.warning("カントリーチャートデータが読み込まれていません")
        
        with viz_tab2:
            st.markdown("### 📊 カントリーチャート - ヒートマップ")
            st.markdown("全世界の規制状況を一目で確認できます")
            
            if st.session_state.sample_data.get('country_chart') is not None:
                # 規制サマリーチャート
                st.markdown("#### 📈 規制理由別の統計")
                summary_chart = create_regulation_summary_chart(
                    st.session_state.sample_data['country_chart']
                )
                if summary_chart:
                    st.plotly_chart(summary_chart, use_container_width=True)
                
                st.markdown("---")
                
                # ヒートマップ
                st.markdown("#### 🔥 全世界規制ヒートマップ")
                st.info("💡 各セルをホバーすると、国名・規制理由・ステータスが表示されます")
                
                heatmap = create_country_chart_heatmap(
                    st.session_state.sample_data['country_chart']
                )
                if heatmap:
                    st.plotly_chart(heatmap, use_container_width=True)
                
                # 生データも表示
                with st.expander("📋 カントリーチャート生データを表示"):
                    st.dataframe(
                        st.session_state.sample_data['country_chart'],
                        use_container_width=True,
                        height=400
                    )
            else:
                st.warning("カントリーチャートデータが読み込まれていません")
        
        with viz_tab3:
            st.markdown("### 🔢 ECCN番号データベース検索")
            
            # インタラクティブテーブル
            if 'eccn_json' in st.session_state.sample_data:
                eccn_df = create_interactive_eccn_table(st.session_state.sample_data['eccn_json'])
                
                if eccn_df is not None and not eccn_df.empty:
                    st.info(f"📚 合計 **{len(eccn_df)}** 項目のECCN番号が登録されています")
                    
                    # 検索機能
                    search_keyword = st.text_input(
                        "🔍 キーワードで検索",
                        placeholder="例: semiconductor, encryption, 5A002",
                        key="eccn_search"
                    )
                    
                    if search_keyword:
                        filtered_df = eccn_df[
                            eccn_df.apply(lambda row: row.astype(str).str.contains(search_keyword, case=False).any(), axis=1)
                        ]
                        st.success(f"✅ {len(filtered_df)}件の一致が見つかりました")
                        st.dataframe(filtered_df, use_container_width=True, height=500)
                    else:
                        st.dataframe(eccn_df, use_container_width=True, height=500)
                    
                    # クリックで詳細表示（選択機能）
                    st.markdown("---")
                    st.markdown("#### 📋 ECCN詳細表示")
                    selected_eccn = st.selectbox(
                        "ECCN番号を選択して詳細を表示",
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
                st.warning("ECCNデータが読み込まれていません")
        
        with viz_tab4:
            create_entity_list_viewer(st.session_state.sample_data)
        
        st.markdown("---")
        
        # 従来のデータ管理セクション
        st.markdown("### 📁 データ管理")
        data_type = st.selectbox(
            "表示するデータを選択",
            ["ECCN番号リスト", "カントリーグループ", "エンティティリスト（サンプル）"]
        )
        
        if data_type == "ECCN番号リスト":
            st.markdown("### 📋 ECCN番号データベース")
            
            # 統計情報を表示
            if 'eccn_json' in st.session_state.sample_data:
                eccn_json = st.session_state.sample_data['eccn_json']
                summary = get_eccn_categories_summary(eccn_json)
                
                st.info(f"🔢 合計 **{sum(summary.values())}** 項目のECCN番号が登録されています")
                
                # カテゴリー別統計
                col1, col2, col3 = st.columns(3)
                categories_list = list(summary.items())
                
                with col1:
                    for cat, count in categories_list[:4]:
                        st.metric(cat, f"{count}項目")
                with col2:
                    for cat, count in categories_list[4:8]:
                        st.metric(cat, f"{count}項目")
                with col3:
                    for cat, count in categories_list[8:]:
                        st.metric(cat, f"{count}項目")
            
            st.markdown("---")
            
            # ECCN検索機能
            st.markdown("### 🔍 ECCN番号検索")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                search_keyword = st.text_input("キーワードで検索（品目名、ECCN番号、説明文）", placeholder="例: semiconductor, encryption, 5A002")
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                search_button = st.button("🔍 検索", type="primary")
            
            if search_keyword or search_button:
                if search_keyword:
                    # JSON検索
                    eccn_json = st.session_state.sample_data.get('eccn_json')
                    eccn_csv = st.session_state.sample_data.get('eccn_csv')
                    
                    results = search_eccn(search_keyword, df=eccn_csv, eccn_json=eccn_json)
                    
                    if results:
                        st.success(f"✅ {len(results)}件の該当品目が見つかりました")
                        
                        # 結果を表示（最大20件）
                        for i, result in enumerate(results[:20], 1):
                            with st.expander(f"{i}. {result.get('ECCN番号', 'N/A')}", expanded=(i <= 3)):
                                if 'カテゴリー' in result:
                                    st.markdown(f"**カテゴリー**: {result['カテゴリー']}")
                                if 'グループ' in result:
                                    st.markdown(f"**グループ**: {result['グループ']}")
                                if '分類' in result:
                                    st.markdown(f"**分類**: {result.get('分類', 'N/A')}")
                                if '品目名' in result:
                                    st.markdown(f"**品目名**: {result.get('品目名', 'N/A')}")
                                if '規制理由' in result:
                                    st.markdown(f"**規制理由**: {result.get('規制理由', 'N/A')}")
                                st.markdown(f"**説明**: {result.get('説明', 'N/A')}")
                                if 'ソース' in result:
                                    st.caption(f"データソース: {result['ソース']}")
                        
                        if len(results) > 20:
                            st.info(f"📊 さらに{len(results) - 20}件の結果があります。キーワードを絞り込んでください。")
                    else:
                        st.warning("⚠️ 該当する品目が見つかりませんでした。別のキーワードをお試しください。")
            
            # 直接ECCN番号を入力して検索
            st.markdown("---")
            st.markdown("### 🎯 ECCN番号で直接検索")
            eccn_direct = st.text_input("ECCN番号を入力", placeholder="例: 5A002, 3A001")
            
            if eccn_direct and 'eccn_json' in st.session_state.sample_data:
                eccn_info = get_eccn_by_number(eccn_direct, st.session_state.sample_data['eccn_json'])
                if eccn_info:
                    st.success(f"✅ ECCN番号 **{eccn_direct}** の情報が見つかりました")
                    st.markdown(f"**ECCN番号**: {eccn_info['ECCN番号']}")
                    st.markdown(f"**カテゴリー**: {eccn_info['カテゴリー']}")
                    st.markdown(f"**グループ**: {eccn_info['グループ']}")
                    st.markdown(f"**説明**: {eccn_info['説明']}")
                else:
                    st.warning(f"⚠️ ECCN番号 **{eccn_direct}** の情報が見つかりませんでした")
            
            # CSVデータも表示（参考用）
            if 'eccn_csv' in st.session_state.sample_data:
                st.markdown("---")
                st.markdown("### 📋 サンプルECCN番号リスト（CSV）")
                st.caption("参考：基本的なECCN番号のサンプルリスト")
                st.dataframe(st.session_state.sample_data['eccn_csv'], use_container_width=True)
        
        elif data_type == "カントリーグループ" and 'countries' in st.session_state.sample_data:
            st.markdown("### 🌏 カントリーグループ")
            st.dataframe(st.session_state.sample_data['countries'], use_container_width=True)
            
            # 国別統計
            group_a_count = st.session_state.sample_data['countries']['グループA'].sum()
            concern_count = st.session_state.sample_data['countries']['懸念国'].sum()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("グループA国", f"{group_a_count}カ国")
            with col2:
                st.metric("懸念国", f"{concern_count}カ国")
        
        elif data_type == "エンティティリスト（サンプル）" and 'entities' in st.session_state.sample_data:
            st.markdown("### 🚫 エンティティリスト（サンプル）")
            st.warning("⚠️ これはサンプルデータです。実際の取引では最新の公式リストを確認してください。")
            st.dataframe(st.session_state.sample_data['entities'], use_container_width=True)
        
        st.markdown("---")
        
        # カスタムCSVアップロード
        st.markdown("### 📤 カスタムデータのアップロード")
        csv_file = st.file_uploader("規制データCSVをアップロード", type=['csv'])
        
        if csv_file is not None:
            df = pd.read_csv(csv_file)
            st.dataframe(df, use_container_width=True)
            
            # Save to session state
            st.session_state.regulation_data = df
            st.success("データが読み込まれました")

if __name__ == "__main__":
    main()


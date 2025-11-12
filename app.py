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
from knowledge_base import get_full_knowledge_base, get_gaiame_knowledge, get_ear_knowledge
from utils import (
    extract_contract_info,
    check_group_a_country,
    check_concern_country,
    search_eccn,
    check_entity_list,
    assess_risk_level,
    generate_action_items,
    load_eccn_json,
    get_eccn_by_number,
    get_eccn_categories_summary
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

# Custom CSS - Clean White Flat Design (Light Mode)
st.markdown("""
<style>
    /* Force Light Mode - White Background, Black Text */
    .stApp {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* Override all text to black */
    body, p, span, div, h1, h2, h3, h4, h5, h6, label {
        color: #000000 !important;
    }
    
    /* Main Header - Simple and Clean */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #000000 !important;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1.5rem 0;
        border-bottom: 3px solid #3182ce;
    }
    
    /* Section Headers - Minimal Design */
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #000000 !important;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e2e8f0;
    }
    
    /* Force all Streamlit elements to black text */
    .stMarkdown, .stMarkdown p, .stMarkdown span {
        color: #000000 !important;
    }
    
    .stText {
        color: #000000 !important;
    }
    
    [data-testid="stMarkdownContainer"] {
        color: #000000 !important;
    }
    
    [data-testid="stMarkdownContainer"] p {
        color: #000000 !important;
    }
    
    /* Alert Boxes - Flat with Subtle Colors, BLACK TEXT */
    .warning-box {
        background-color: #fef5e7;
        border-left: 4px solid #f39c12;
        border-radius: 4px;
        padding: 1rem;
        margin: 1rem 0;
        color: #000000 !important;
    }
    
    .info-box {
        background-color: #ebf8ff;
        border-left: 4px solid #3182ce;
        border-radius: 4px;
        padding: 1rem;
        margin: 1rem 0;
        color: #000000 !important;
    }
    
    .success-box {
        background-color: #f0fdf4;
        border-left: 4px solid #10b981;
        border-radius: 4px;
        padding: 1rem;
        margin: 1rem 0;
        color: #000000 !important;
    }
    
    .danger-box {
        background-color: #fef2f2;
        border-left: 4px solid #ef4444;
        border-radius: 4px;
        padding: 1rem;
        margin: 1rem 0;
        color: #000000 !important;
    }
    
    /* Buttons - Clean Blue */
    .stButton>button {
        background-color: #3182ce;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.625rem 1.5rem;
        font-weight: 500;
        transition: background-color 0.2s;
    }
    
    .stButton>button:hover {
        background-color: #2c5282;
    }
    
    /* Input Fields - Clean Borders */
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea,
    .stSelectbox>div>div>div {
        border-radius: 6px;
        border: 1px solid #cbd5e0;
        padding: 0.5rem;
    }
    
    .stTextInput>div>div>input:focus,
    .stTextArea>div>div>textarea:focus {
        border-color: #3182ce;
        outline: none;
    }
    
    /* Expander - Subtle Background */
    .streamlit-expanderHeader {
        background-color: #f7fafc;
        border-radius: 6px;
        border: 1px solid #e2e8f0;
        font-weight: 500;
    }
    
    /* Dataframe - Clean Table */
    .stDataFrame {
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        overflow: hidden;
    }
    
    /* Tabs - Simple and Clean */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background-color: transparent;
        border-bottom: 2px solid #e2e8f0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 6px 6px 0 0;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        color: #4a5568;
        border: none;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #3182ce;
        color: white;
    }
    
    /* Sidebar - Clean White/Gray with BLACK TEXT */
    [data-testid="stSidebar"] {
        background-color: #f7fafc !important;
        border-right: 1px solid #e2e8f0;
    }
    
    [data-testid="stSidebar"] * {
        color: #000000 !important;
    }
    
    /* Metrics - Clean Cards with BLACK TEXT */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem;
        font-weight: 600;
        color: #000000 !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.875rem;
        font-weight: 500;
        color: #000000 !important;
    }
    
    [data-testid="stMetricDelta"] {
        color: #000000 !important;
    }
    
    /* File Uploader - Clean Design */
    [data-testid="stFileUploader"] {
        background-color: #f7fafc;
        border: 2px dashed #cbd5e0;
        border-radius: 6px;
        padding: 1rem;
    }
    
    /* Success/Info/Warning Messages - BLACK TEXT */
    .stSuccess {
        background-color: #f0fdf4;
        border-left: 4px solid #10b981;
        color: #000000 !important;
    }
    
    .stInfo {
        background-color: #ebf8ff;
        border-left: 4px solid #3182ce;
        color: #000000 !important;
    }
    
    .stWarning {
        background-color: #fef5e7;
        border-left: 4px solid #f39c12;
        color: #000000 !important;
    }
    
    /* Expander content - BLACK TEXT */
    [data-testid="stExpander"] {
        background-color: #ffffff !important;
    }
    
    [data-testid="stExpander"] * {
        color: #000000 !important;
    }
    
    /* Tab content - BLACK TEXT */
    .stTabs [data-baseweb="tab-panel"] {
        background-color: #ffffff !important;
    }
    
    .stTabs [data-baseweb="tab-panel"] * {
        color: #000000 !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Scrollbar - Clean Design */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #cbd5e0;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #a0aec0;
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
    """GPTで契約書を分析"""
    
    prompt = f"""
あなたは安全保障貿易管理の専門家です。以下の契約書を分析し、外為法と米国EARの両方について判断してください。

【契約書内容】
{contract_text[:5000]}  # トークン制限のため最初の5000文字

【ナレッジベース】
{knowledge_base}

以下の項目について詳細に分析してください：

## 1. 契約情報の抽出
- 品目名・製品名
- 仕向地（輸出先国）
- 需要者（エンドユーザー）情報
- 用途
- 契約金額
- 納期

## 2. 外為法判断フロー分析

### A. 貨物の輸出 or 技術の提供に該当するか
判定結果と理由を記載

### B. リスト規制に該当するか（該非判定）
該当する場合は項番号を記載

### C. 許可例外が適用できるか
適用可能な例外を記載

### D. 包括許可が適用できるか
適用可能性を評価

### E. キャッチオール規制の懸念
- 用途要件の評価
- 需要者要件の評価
- 明らかガイドラインのチェック

## 3. 米国EAR判断フロー分析

### A. EAR対象品目の再輸出に該当するか
米国原産品・組込品・外国直接製品の可能性

### B. ECCN番号
推定されるECCN番号

### C. カントリーチャート
仕向国に対する規制の有無

### D. 許可例外
適用可能な例外

### E. 禁輸国・リスト規制
該当する懸念の有無

## 4. 総合判定とリスク評価
- 外為法：許可必要/不要
- 米国EAR：許可必要/不要
- リスクレベル：高/中/低
- 推奨アクション

## 5. 必要な手続き
具体的な申請手順と窓口

明確で構造化された形式で回答してください。
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "あなたは安全保障貿易管理の専門家です。外為法と米国EARに精通しています。"},
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
    # Header
    st.markdown('<div class="main-header">🔒 Export Control AI Assistant</div>', unsafe_allow_html=True)
    
    # データベース読み込み状態を表示（コンパクトに）
    if 'eccn_json' in st.session_state.sample_data and st.session_state.sample_data['eccn_json']:
        eccn_count = sum(get_eccn_categories_summary(st.session_state.sample_data['eccn_json']).values())
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("ECCN Database", f"{eccn_count} items", delta="Active")
        with col2:
            st.metric("Countries", "33", delta="Monitored")
        with col3:
            st.metric("Status", "Online", delta="Ready")
    
    # Sidebar
    with st.sidebar:
        st.header("📚 システム情報")
        st.info("""
        **主な機能**
        
        - ✅ 契約書AI分析
        - ✅ 外為法判断フロー
        - ✅ 米国EAR判断フロー
        - ✅ ECCN番号検索
        - ✅ リスク評価
        
        **データベース**
        - ECCN番号: 141項目
        - カントリーリスト: 33カ国
        """)
        
        st.header("⚠️ 免責事項")
        st.warning("""
        本システムは参考情報を提供するツールです。
        
        法的判断が必要な場合は専門家にご相談ください。
        """)
    
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
        
        if st.button("🔍 分析開始", key="chat_submit", type="primary"):
            if product_input:
                with st.spinner("ECCN番号を判定し、カントリーチャートを分析中..."):
                    # データ準備
                    eccn_json = st.session_state.sample_data.get('eccn_json')
                    country_chart = st.session_state.sample_data.get('country_chart')
                    
                    # ECCN番号データをテキスト化
                    eccn_context = ""
                    if eccn_json:
                        eccn_context = "【利用可能なECCN番号データベース】\n"
                        for category in eccn_json.get('ccl_categories', [])[:5]:  # 最初の5カテゴリー
                            eccn_context += f"\nCategory {category.get('category_number', '')}: {category.get('title', '')}\n"
                            for group in category.get('product_groups', []):
                                for item in group.get('items', [])[:3]:  # 各グループの最初の3項目
                                    eccn_context += f"  - {item.get('eccn', '')}: {item.get('description', '')[:100]}...\n"
                    
                    # カントリーチャートデータをテキスト化
                    chart_context = ""
                    if country_chart is not None and not country_chart.empty:
                        chart_context = f"\n【カントリーチャート情報】\n利用可能な国数: {len(country_chart)}カ国\n"
                    
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

## ステップ3: 一般禁止事項（General Prohibitions）の確認 ★重要★

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

## ステップ4: 総合判定

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
        st.markdown('<div class="section-header">📊 規制データ管理</div>', unsafe_allow_html=True)
        
        st.info("CSVファイルで規制リスト（ECCN番号、カントリーリスト等）を管理できます。")
        
        # サンプルデータの表示
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


# Economic Security Compliance Advisor

An AI-powered system that analyzes export contracts and assists with compliance assessments under Japan's Foreign Exchange and Foreign Trade Act (FEFTA / 外為法) and the U.S. Export Administration Regulations (EAR).

## 🎯 Features

- **Automated Contract Analysis**: Extracts item descriptions, destination countries, and end-user information from PDF contracts
- **FEFTA Assessment Flow**: Automatically evaluates List Control and Catch-All regulations under Japanese law
- **U.S. EAR Assessment Flow**: Verifies ECCN classifications and Country Chart requirements
- **ECCN Database**: Detailed dataset of 1,500+ ECCN entries in JSON format
- **Advanced Search**: Lookup by keyword or ECCN number
- **Risk Evaluation**: Generates comprehensive risk ratings and recommended actions
- **Compliance Chat**: Interactive Q&A on export control matters
- **Data Management**: Manage regulatory lists in CSV / JSON formats

## 🚀 Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment variables

Set your OpenAI API key in the `.env` file:
OPENAI_API_KEY=your_api_key_here

### 3. Launch the application

```bash
streamlit run app.py
```

Your browser will automatically open `http://localhost:8501`.

## 📖 Usage

### Contract Analysis

1. Open the **Contract Analysis** tab
2. Upload an export contract PDF, or enter the relevant information manually
3. Click **Start Analysis**
4. Review the AI-generated assessment
5. Download the results as needed

### Compliance Chat

1. Open the **Chat Consultation** tab
2. Ask any question related to export controls
3. The system responds based on FEFTA and EAR provisions

### Data Management

1. Open the **Data Management** tab
2. Browse and search the ECCN database (1,500+ entries)
   - Category-level statistics
   - Keyword search (item name, description)
   - Direct ECCN number lookup
3. Review Country Groups and Entity Lists
4. Upload custom regulatory lists via CSV

## ⚠️ Important Disclaimers

- **This system provides reference information only and does not constitute legal advice.**
- All final compliance determinations must be made in consultation with qualified professionals and the relevant authorities.
- Japan METI Security Export Control Policy Division: +81-3-3501-2801
- CISTEC (Center for Information on Security Trade Control): https://www.cistec.or.jp

## 📋 Assessment Workflows

### Japan FEFTA (外為法) — Steps 1–5
1. Does the transaction constitute an export of goods or transfer of technology?
2. Does the item fall under List Control? (該非判定 / classification determination)
3. Is a license exception applicable?
4. Does a comprehensive (bulk) license apply?
5. Are there Catch-All concerns?

### U.S. EAR — Steps 1–5
1. Is the transaction a re-export of an EAR-controlled item?
2. Does the item have an ECCN classification?
3. What does the Country Chart require?
4. Are license exceptions available?
5. Are there embargoed-country, end-use, or end-user concerns?

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **LLM**: OpenAI GPT-4
- **PDF Processing**: PyPDF2, pdfplumber
- **Data Processing**: Pandas
- **Environment Management**: python-dotenv

## 📁 Project Structure
Economic Security Professor/
├── app.py                          # Main application
├── knowledge_base.py               # Knowledge base (FEFTA and U.S. EAR)
├── utils.py                        # Utility functions
├── requirements.txt                # Python dependencies
├── .env                            # Environment variables (API keys)
├── eccnnumber.json                 # ECCN database (1,500+ entries) ★NEW
├── README.md                       # This file
├── USAGE_GUIDE.md                  # Detailed usage guide
├── QUICK_START.md                  # Quick start guide
└── sample_data/                    # Sample data
├── eccn_list.csv               # ECCN list (basic)
├── country_groups.csv          # Country Groups
└── entity_list_sample.csv      # Entity List (sample)

## 🔮 Roadmap

- [ ] Integration with more granular regulatory databases
- [ ] Multi-language support
- [ ] Expanded export formats (PDF, Excel, etc.)
- [ ] Persistence and search of analysis history
- [ ] User authentication
- [ ] Coverage of China's export control regime

## 📞 Support

For questions or compliance issues, please consult qualified export control professionals.

## 📜 License

This system was developed for educational and research purposes.
Please verify appropriate licensing for any commercial use.

---

**Disclaimer**: All information provided by this system is for reference only. For actual export compliance work, always consult qualified professionals and the relevant regulatory authorities.



↓ in Japanese below!
---
# 安全保障貿易管理 判断支援システム

輸出契約書を自動分析し、外為法と米国EARの適用判断を支援するAIシステム

## 🎯 機能

- **契約書自動分析**: PDFから品目、仕向地、需要者情報を抽出
- **外為法判断フロー**: リスト規制、キャッチオール規制の自動判定
- **米国EAR判断フロー**: ECCN番号、カントリーチャートの確認
- **ECCN番号データベース**: 1500+項目の詳細なECCN番号データ（JSON形式）
- **高度な検索機能**: キーワード・ECCN番号での検索
- **リスク評価**: 総合的なリスクレベルと推奨アクションを提示
- **チャット相談**: 輸出管理に関する質問に回答
- **データ管理**: CSV/JSON形式で規制リストを管理

## 🚀 セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env`ファイルにOpenAI APIキーを設定してください：

```
OPENAI_API_KEY=your_api_key_here
```

### 3. アプリケーションの起動

```bash
streamlit run app.py
```

ブラウザで `http://localhost:8501` が自動的に開きます。

## 📖 使い方

### 契約書分析

1. 「契約書分析」タブを選択
2. 輸出契約書PDFをアップロード、または手動で情報を入力
3. 「分析開始」ボタンをクリック
4. AI分析結果を確認
5. 必要に応じて結果をダウンロード

### チャット相談

1. 「チャット相談」タブを選択
2. 輸出管理に関する質問を入力
3. AIが外為法やEARに基づいて回答

### データ管理

1. 「データ管理」タブを選択
2. ECCN番号データベース（1500+項目）を検索・閲覧
   - カテゴリー別統計表示
   - キーワード検索（品目名、説明文）
   - ECCN番号での直接検索
3. カントリーグループ、エンティティリストの確認
4. カスタム規制リストのCSVアップロード

## ⚠️ 重要な注意事項

- **本システムは参考情報を提供するものであり、法的助言ではありません**
- 最終的な判断は必ず専門家や関係当局にご相談ください
- 経済産業省安全保障貿易審査課：03-3501-2801
- CISTEC（安全保障貿易情報センター）：https://www.cistec.or.jp

## 📋 判断フロー

### 外為法（P.6-16）
1. 貨物の輸出 or 技術の提供に該当するか
2. リスト規制に該当するか（該非判定）
3. 許可例外が適用できるか
4. 包括許可が適用できるか
5. キャッチオール規制の懸念があるか

### 米国EAR（P.17-21）
1. EAR対象品目の再輸出に該当するか
2. ECCN番号の有無
3. カントリーチャートの確認
4. 許可例外の適用
5. 禁輸国・エンドユース・エンドユーザー規制

## 🛠️ 技術スタック

- **フロントエンド**: Streamlit
- **LLM**: OpenAI GPT-4
- **PDF処理**: PyPDF2, pdfplumber
- **データ処理**: Pandas
- **環境変数管理**: python-dotenv

## 📁 プロジェクト構成

```
Economic Security Professor/
├── app.py                          # メインアプリケーション
├── knowledge_base.py               # ナレッジベース（外為法・米国EAR）
├── utils.py                        # ユーティリティ関数
├── requirements.txt                # Python依存関係
├── .env                           # 環境変数（API keys）
├── eccnnumber.json                # ECCN番号データベース（1500+項目）★NEW
├── README.md                      # このファイル
├── USAGE_GUIDE.md                 # 詳細使用ガイド
├── QUICK_START.md                 # クイックスタート
└── sample_data/                   # サンプルデータ
    ├── eccn_list.csv             # ECCN番号リスト（基本）
    ├── country_groups.csv        # カントリーグループ
    └── entity_list_sample.csv    # エンティティリスト（サンプル）
```

## 🔮 今後の拡張予定

- [ ] より詳細な規制データベースの統合
- [ ] 多言語対応
- [ ] エクスポート形式の拡充（PDF、Excel等）
- [ ] 過去の分析履歴の保存・検索
- [ ] ユーザー認証機能
- [ ] 中国の輸出管理規制への対応

## 📞 サポート

質問や問題がある場合は、輸出管理の専門家にご相談ください。

## 📜 ライセンス

本システムは教育・研究目的で作成されています。
商用利用の際は適切なライセンス確認を行ってください。

---

**免責事項**: 本システムで提供される情報は参考情報です。実際の輸出管理業務においては、必ず専門家や関係当局に確認してください。


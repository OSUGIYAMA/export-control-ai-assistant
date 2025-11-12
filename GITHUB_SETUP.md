# GitHubへの接続手順

## ✅ 完了したステップ

1. ✅ Gitリポジトリの初期化
2. ✅ 全ファイルのステージング
3. ✅ 初回コミット作成
4. ✅ ブランチ名を`main`に変更

```
コミットID: 72c03f7
コミットメッセージ: Initial commit: Export Control AI Assistant with ECCN auto-detection and Country Chart analysis
ファイル数: 15ファイル
行数: 4,657行追加
```

---

## 🚀 次のステップ: GitHubリポジトリの作成と接続

### 方法1: GitHubウェブサイトで作成（推奨）

#### 1. GitHubで新規リポジトリを作成

1. https://github.com にアクセス
2. 右上の「+」→「New repository」をクリック
3. 以下の情報を入力：
   - **Repository name**: `export-control-ai-assistant` または任意の名前
   - **Description**: `AI-powered Export Control (US EAR & Japan) compliance assistant with ECCN auto-detection`
   - **Public/Private**: お好みで選択
   - ⚠️ **「Initialize this repository with a README」のチェックは外す**（既にREADMEがあるため）
4. 「Create repository」をクリック

#### 2. リモートリポジトリを追加してプッシュ

GitHubでリポジトリを作成したら、以下のコマンドを実行してください：

```bash
cd "/Users/tatsuyasugiyamahome/Economic Security Professor"

# リモートリポジトリを追加（URLは実際のリポジトリのURLに置き換えてください）
git remote add origin https://github.com/YOUR_USERNAME/REPOSITORY_NAME.git

# プッシュ
git push -u origin main
```

**例**:
```bash
git remote add origin https://github.com/tatsuyasugiyama/export-control-ai-assistant.git
git push -u origin main
```

---

### 方法2: GitHub CLIを使用（オプション）

GitHub CLIがインストールされていない場合、インストールして使用できます：

```bash
# Homebrewでインストール
brew install gh

# GitHubにログイン
gh auth login

# リポジトリを作成してプッシュ
cd "/Users/tatsuyasugiyamahome/Economic Security Professor"
gh repo create export-control-ai-assistant --public --source=. --remote=origin --push
```

---

## 📦 リポジトリに含まれるファイル

### アプリケーションコア
- `app.py` - Streamlitメインアプリケーション
- `knowledge_base.py` - 外為法・米国EARナレッジベース
- `utils.py` - ユーティリティ関数
- `requirements.txt` - Python依存関係

### データファイル
- `eccnnumber.json` - ECCN番号データベース（1,557項目）
- `11_12_2025_country_chart_export.csv` - カントリーチャート（212カ国）
- `sample_data/eccn_list.csv` - ECCNリストサンプル
- `sample_data/country_groups.csv` - カントリーグループ
- `sample_data/entity_list_sample.csv` - エンティティリスト

### ドキュメント
- `README.md` - プロジェクト概要
- `USAGE_GUIDE.md` - 詳細な使用ガイド
- `QUICK_START.md` - クイックスタートガイド
- `DESIGN_NOTES.md` - UI設計メモ

### 設定ファイル
- `.gitignore` - Git除外設定
- `.streamlit/config.toml` - Streamlit設定（ライトモード）

---

## 🔐 セキュリティ注意事項

### `.env`ファイルは含まれていません

OpenAI APIキーを含む`.env`ファイルは`.gitignore`で除外されています。
新しい環境でセットアップする際は、以下を実行してください：

```bash
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

---

## 📊 プロジェクト統計

```
ファイル数: 15
総行数: 4,657行
プログラミング言語: Python
フレームワーク: Streamlit
AIモデル: OpenAI GPT-4 Turbo
データベース: ECCN 1,557項目, 国 212カ国
```

---

## 🎯 主な機能

1. **PDF契約書AI分析**
   - 自動テキスト抽出
   - リスク判定（高/中/低）
   - アクションアイテム生成

2. **ECCN番号自動判定**
   - 品目名から最適なECCN番号を選択
   - 1,557項目のデータベース参照
   - 5桁形式で明確に表示

3. **カントリーチャート分析**
   - 212カ国のデータベース
   - 規制理由ごとに許可要否を判定
   - リアルタイムで「×」マーク確認

4. **チャット相談機能**
   - 外為法・米国EARに関する質問応答
   - 構造化された3ステップ分析
   - 履歴管理

5. **規制データ管理**
   - CSV/JSONデータの可視化
   - ECCN検索
   - 統計情報表示

---

## 🌐 デプロイ

### Streamlit Cloud（推奨）

1. GitHubにプッシュ後、https://streamlit.io/cloud にアクセス
2. 「New app」をクリック
3. リポジトリを選択
4. `app.py`を指定
5. **Secrets**にAPIキーを追加：
   ```
   OPENAI_API_KEY = "your-api-key-here"
   ```
6. 「Deploy」をクリック

---

## 📞 サポート

問題が発生した場合は、GitHubのIssuesで報告してください。

---

**作成日**: 2025年11月12日
**初回コミット**: 72c03f7
**プロジェクト**: Export Control AI Assistant


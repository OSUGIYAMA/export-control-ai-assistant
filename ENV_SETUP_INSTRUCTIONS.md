# 環境変数設定手順

## .envファイルの設定

プロジェクトルートに`.env`ファイルを作成し、以下の内容を追加してください：

```env
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Pinecone API Key (RAG用)
PINECONE_API_KEY=your_pinecone_api_key_here
```

## Pinecone設定情報

- **Index名**: `license-exceptions`
- **Host**: https://license-exceptions-3hxjxa0.svc.aped-4627-b74a.pinecone.io
- **用途**: 米国EAR許可例外（License Exceptions）の判定

## 確認方法

`.env`ファイルを作成後、以下のコマンドでアプリを再起動してください：

```bash
streamlit run app.py
```

RAG機能が有効になり、「ステップD: 許可例外判定」で自動的にPineconeから関連情報を取得して分析します。

## セキュリティ注意事項

- `.env`ファイルは`.gitignore`で除外されており、Gitにコミットされません
- APIキーは絶対に公開リポジトリにプッシュしないでください
- 本番環境では環境変数として設定することを推奨します


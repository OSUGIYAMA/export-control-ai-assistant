"""
RAG (Retrieval-Augmented Generation) ツール
Pineconeを使用した許可例外判断システム
"""

import os
from typing import Dict, List, Optional, Tuple
from pinecone import Pinecone
from openai import OpenAI
import streamlit as st

class LicenseExceptionRAG:
    """
    許可例外（License Exceptions）判断用RAGシステム
    """
    
    def __init__(self):
        """
        PineconeとOpenAIクライアントを初期化
        """
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.pinecone_api_key:
            raise ValueError("PINECONE_API_KEY が設定されていません")
        
        # Pinecone接続
        self.pc = Pinecone(api_key=self.pinecone_api_key)
        self.index = self.pc.Index("license-exceptions")
        
        # OpenAI接続
        self.openai_client = OpenAI(api_key=self.openai_api_key)
    
    def create_query_embedding(self, query_text: str) -> List[float]:
        """
        クエリテキストからembeddingを生成
        
        Args:
            query_text: クエリテキスト
            
        Returns:
            embedding vector
        """
        response = self.openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=query_text
        )
        return response.data[0].embedding
    
    def search_license_exceptions(
        self, 
        eccn_number: str, 
        destination: str, 
        product_description: str,
        top_k: int = 5
    ) -> List[Dict]:
        """
        許可例外を検索
        
        Args:
            eccn_number: ECCN番号
            destination: 仕向地
            product_description: 品目説明
            top_k: 取得する上位結果数
            
        Returns:
            検索結果のリスト
        """
        # クエリテキストを構築
        query_text = f"""
        ECCN Number: {eccn_number}
        Destination: {destination}
        Product: {product_description}
        
        What license exceptions are available for this export?
        """
        
        # Embedding生成
        query_embedding = self.create_query_embedding(query_text)
        
        # Pineconeで検索
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        return results.matches
    
    def analyze_license_exception_applicability(
        self,
        eccn_number: str,
        destination: str,
        product_description: str,
        end_user: Optional[str] = None,
        end_use: Optional[str] = None
    ) -> Dict:
        """
        許可例外の適用可否を分析
        
        Args:
            eccn_number: ECCN番号
            destination: 仕向地
            product_description: 品目説明
            end_user: エンドユーザー（オプション）
            end_use: 用途（オプション）
            
        Returns:
            分析結果（許可例外、適用可否、根拠）
        """
        # RAGで関連情報を取得
        search_results = self.search_license_exceptions(
            eccn_number=eccn_number,
            destination=destination,
            product_description=product_description
        )
        
        # 検索結果をテキスト化
        context_text = self._format_search_results(search_results)
        
        # GPTで判断
        analysis_prompt = f"""
あなたは米国EAR許可例外（License Exceptions）の専門家です。

以下の情報に基づいて、許可例外の適用可否を判断してください。

【輸出情報】
- ECCN番号: {eccn_number}
- 仕向地: {destination}
- 品目: {product_description}
- エンドユーザー: {end_user if end_user else '未指定'}
- 用途: {end_use if end_use else '未指定'}

【関連する許可例外情報（RAG検索結果）】
{context_text}

【分析指示】
以下の形式で回答してください：

## 📋 適用可能な許可例外

### 1. [許可例外名]（例: LVS, GBS, TSR, TMP等）
- **適用可否**: ✅ 適用可能 / ⚠️ 条件付き / ❌ 適用不可
- **条件**: [適用に必要な条件]
- **根拠**: [判断の根拠となる規定・条項]
- **参照**: [15 CFR §740.X]

### 2. [次の許可例外...]
...

## 🎯 推奨事項
- [最も適切な許可例外]
- [必要な手続き]
- [注意事項]

## 📚 判断根拠
[RAG検索結果から抽出した具体的な規定文を引用]

**重要**: 判断の根拠となる条文・規定を必ず明記してください。
"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system", 
                        "content": "あなたは米国EAR許可例外の専門家です。RAG検索結果に基づいて、正確で詳細な判断を提供します。"
                    },
                    {
                        "role": "user", 
                        "content": analysis_prompt
                    }
                ],
                temperature=0.2,
                max_tokens=2000
            )
            
            analysis_result = response.choices[0].message.content
            
            return {
                "success": True,
                "analysis": analysis_result,
                "search_results": search_results,
                "context_used": context_text,
                "eccn_number": eccn_number,
                "destination": destination
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "search_results": search_results,
                "context_used": context_text
            }
    
    def _format_search_results(self, results) -> str:
        """
        Pinecone検索結果をテキスト形式に整形
        
        Args:
            results: Pinecone検索結果
            
        Returns:
            整形されたテキスト
        """
        formatted_text = ""
        
        for i, match in enumerate(results, 1):
            score = match.score
            metadata = match.metadata
            
            formatted_text += f"\n【検索結果 {i}】（関連度: {score:.3f}）\n"
            formatted_text += f"ID: {match.id}\n"
            
            # メタデータを表示
            if metadata:
                for key, value in metadata.items():
                    formatted_text += f"{key}: {value}\n"
            
            formatted_text += "\n" + "-" * 80 + "\n"
        
        return formatted_text
    
    def display_license_exception_analysis(
        self,
        analysis_result: Dict
    ):
        """
        Streamlitで許可例外分析結果を表示
        
        Args:
            analysis_result: analyze_license_exception_applicability()の返り値
        """
        if not analysis_result.get("success"):
            st.error(f"❌ 分析エラー: {analysis_result.get('error', '不明なエラー')}")
            return
        
        st.markdown("### 📋 許可例外（License Exceptions）分析結果")
        
        # 分析結果を表示
        st.markdown(analysis_result["analysis"])
        
        st.markdown("---")
        
        # RAG検索の詳細を表示
        with st.expander("🔍 RAG検索詳細（判断根拠のデータソース）"):
            st.markdown("#### 📚 Pineconeから取得した関連情報")
            
            search_results = analysis_result.get("search_results", [])
            
            if search_results:
                for i, match in enumerate(search_results, 1):
                    st.markdown(f"""
                    **検索結果 {i}** - 関連度: {match.score:.3f}
                    
                    **ID**: {match.id}
                    """)
                    
                    # メタデータを表示
                    if match.metadata:
                        st.json(match.metadata)
                    
                    st.markdown("---")
            else:
                st.info("検索結果がありません")
            
            # 使用されたコンテキストを表示
            with st.expander("📄 GPTに提供されたコンテキスト全文"):
                st.text(analysis_result.get("context_used", ""))


def check_license_exception_with_rag(
    eccn_number: str,
    destination: str,
    product_description: str,
    end_user: Optional[str] = None,
    end_use: Optional[str] = None
) -> Tuple[bool, Dict]:
    """
    RAGを使用して許可例外をチェック（簡易インターフェース）
    
    Args:
        eccn_number: ECCN番号
        destination: 仕向地
        product_description: 品目説明
        end_user: エンドユーザー
        end_use: 用途
        
    Returns:
        (成功フラグ, 分析結果)
    """
    try:
        rag = LicenseExceptionRAG()
        result = rag.analyze_license_exception_applicability(
            eccn_number=eccn_number,
            destination=destination,
            product_description=product_description,
            end_user=end_user,
            end_use=end_use
        )
        return (result.get("success", False), result)
    except Exception as e:
        return (False, {"error": str(e)})


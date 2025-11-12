"""
ユーティリティ関数
PDF解析、テキスト処理、データ検索等
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import pandas as pd

def extract_contract_info(text: str) -> Dict[str, str]:
    """
    契約書テキストから主要情報を抽出
    
    Args:
        text: 契約書のテキスト
        
    Returns:
        抽出された情報の辞書
    """
    info = {
        "品目名": "",
        "仕向地": "",
        "需要者": "",
        "用途": "",
        "契約金額": "",
        "納期": ""
    }
    
    # 品目名の抽出（例：「品目」「製品」「商品」等のキーワード後の文字列）
    product_pattern = r'(?:品目|製品|商品|貨物)[\s：:]*([^\n]+)'
    product_match = re.search(product_pattern, text, re.IGNORECASE)
    if product_match:
        info["品目名"] = product_match.group(1).strip()
    
    # 仕向地の抽出
    destination_pattern = r'(?:仕向地|輸出先|輸出国|出荷先国)[\s：:]*([^\n]+)'
    dest_match = re.search(destination_pattern, text, re.IGNORECASE)
    if dest_match:
        info["仕向地"] = dest_match.group(1).strip()
    
    # 需要者の抽出
    end_user_pattern = r'(?:需要者|エンドユーザー|最終需要者|顧客)[\s：:]*([^\n]+)'
    user_match = re.search(end_user_pattern, text, re.IGNORECASE)
    if user_match:
        info["需要者"] = user_match.group(1).strip()
    
    # 用途の抽出
    purpose_pattern = r'(?:用途|使用目的|利用目的)[\s：:]*([^\n]+)'
    purpose_match = re.search(purpose_pattern, text, re.IGNORECASE)
    if purpose_match:
        info["用途"] = purpose_match.group(1).strip()
    
    # 契約金額の抽出
    amount_pattern = r'(?:契約金額|金額|価格|総額)[\s：:]*([^\n]+)'
    amount_match = re.search(amount_pattern, text, re.IGNORECASE)
    if amount_match:
        info["契約金額"] = amount_match.group(1).strip()
    
    return info

def check_group_a_country(country: str, df: Optional[pd.DataFrame] = None) -> bool:
    """
    国がグループA国（旧ホワイト国）かどうかを判定
    
    Args:
        country: 国名
        df: カントリーリストのDataFrame（オプション）
        
    Returns:
        グループA国の場合True
    """
    group_a_countries = [
        "アルゼンチン", "オーストラリア", "オーストリア", "ベルギー", "ブルガリア",
        "カナダ", "チェコ", "デンマーク", "フィンランド", "フランス", "ドイツ",
        "ギリシャ", "ハンガリー", "アイルランド", "イタリア", "ルクセンブルク",
        "オランダ", "ニュージーランド", "ノルウェー", "ポーランド", "ポルトガル",
        "スペイン", "スウェーデン", "スイス", "英国", "米国", "韓国",
        # 英語名も追加
        "Argentina", "Australia", "Austria", "Belgium", "Bulgaria",
        "Canada", "Czech", "Denmark", "Finland", "France", "Germany",
        "Greece", "Hungary", "Ireland", "Italy", "Luxembourg",
        "Netherlands", "New Zealand", "Norway", "Poland", "Portugal",
        "Spain", "Sweden", "Switzerland", "United Kingdom", "UK", "United States", "USA", "South Korea"
    ]
    
    if df is not None:
        # DataFrameから確認
        matching_rows = df[df['国名'].str.contains(country, case=False, na=False)]
        if not matching_rows.empty:
            return matching_rows.iloc[0].get('グループA', '') == '○'
    
    # デフォルトリストから確認
    for ga_country in group_a_countries:
        if ga_country.lower() in country.lower() or country.lower() in ga_country.lower():
            return True
    
    return False

def check_concern_country(country: str, df: Optional[pd.DataFrame] = None) -> Tuple[bool, str]:
    """
    懸念国かどうかを判定
    
    Args:
        country: 国名
        df: カントリーリストのDataFrame（オプション）
        
    Returns:
        (懸念国の場合True, 懸念の種類)
    """
    concern_countries = {
        "北朝鮮": "国連武器禁輸国・懸念国",
        "イラン": "国連武器禁輸国・懸念国",
        "イラク": "国連武器禁輸国・懸念国",
        "シリア": "国連武器禁輸国・懸念国",
        "キューバ": "懸念国",
        "North Korea": "国連武器禁輸国・懸念国",
        "Iran": "国連武器禁輸国・懸念国",
        "Iraq": "国連武器禁輸国・懸念国",
        "Syria": "国連武器禁輸国・懸念国",
        "Cuba": "懸念国"
    }
    
    if df is not None:
        matching_rows = df[df['国名'].str.contains(country, case=False, na=False)]
        if not matching_rows.empty:
            row = matching_rows.iloc[0]
            concerns = []
            if row.get('国連武器禁輸', '') == '○':
                concerns.append("国連武器禁輸国")
            if row.get('懸念国', '') == '○':
                concerns.append("懸念国")
            if concerns:
                return True, "・".join(concerns)
    
    for concern_country, concern_type in concern_countries.items():
        if concern_country.lower() in country.lower() or country.lower() in concern_country.lower():
            return True, concern_type
    
    return False, ""

def load_eccn_json(json_path: str = "eccnnumber.json") -> Optional[Dict]:
    """
    ECCN番号のJSONデータを読み込む
    
    Args:
        json_path: JSONファイルのパス
        
    Returns:
        ECCN データの辞書
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"ECCN JSONファイルの読み込みエラー: {str(e)}")
        return None

def search_eccn_json(keyword: str, eccn_data: Dict) -> List[Dict]:
    """
    JSONデータからECCN番号を検索
    
    Args:
        keyword: 検索キーワード
        eccn_data: ECCN JSONデータ
        
    Returns:
        マッチしたECCN情報のリスト
    """
    results = []
    keyword_lower = keyword.lower()
    
    if not eccn_data or 'ccl_categories' not in eccn_data:
        return results
    
    # 各カテゴリーを検索
    for category in eccn_data['ccl_categories']:
        category_number = category.get('category_number', '')
        category_title = category.get('title', '')
        
        # 各プロダクトグループを検索
        for group in category.get('product_groups', []):
            group_letter = group.get('group_letter', '')
            group_title = group.get('group_title', '')
            
            # 各アイテムを検索
            for item in group.get('items', []):
                eccn = item.get('eccn', '')
                description = item.get('description', '')
                
                # キーワードマッチング
                if (keyword_lower in eccn.lower() or 
                    keyword_lower in description.lower() or
                    keyword_lower in category_title.lower()):
                    
                    results.append({
                        "ECCN番号": eccn,
                        "カテゴリー": f"{category_number} - {category_title}",
                        "グループ": f"{group_letter} - {group_title}",
                        "説明": description
                    })
    
    return results

def search_eccn(keyword: str, df: pd.DataFrame = None, eccn_json: Dict = None) -> List[Dict]:
    """
    キーワードでECCN番号を検索（CSV/JSON両対応）
    
    Args:
        keyword: 検索キーワード
        df: ECCN リストのDataFrame（オプション）
        eccn_json: ECCN JSONデータ（オプション）
        
    Returns:
        マッチしたECCN情報のリスト
    """
    results = []
    
    # JSONデータから検索
    if eccn_json:
        json_results = search_eccn_json(keyword, eccn_json)
        results.extend(json_results)
    
    # CSVデータから検索
    if df is not None and not df.empty:
        # 品目名または説明にキーワードが含まれる行を検索
        matching_rows = df[
            df['品目名'].str.contains(keyword, case=False, na=False) |
            df['説明'].str.contains(keyword, case=False, na=False)
        ]
        
        for _, row in matching_rows.iterrows():
            results.append({
                "ECCN番号": row['ECCN番号'],
                "分類": row.get('分類', ''),
                "品目名": row.get('品目名', ''),
                "規制理由": row.get('規制理由', ''),
                "説明": row.get('説明', ''),
                "ソース": "CSV"
            })
    
    return results

def get_eccn_by_number(eccn_number: str, eccn_json: Dict) -> Optional[Dict]:
    """
    ECCN番号から詳細情報を取得
    
    Args:
        eccn_number: ECCN番号（例: "5A002"）
        eccn_json: ECCN JSONデータ
        
    Returns:
        ECCN情報の辞書
    """
    if not eccn_json or 'ccl_categories' not in eccn_json:
        return None
    
    eccn_number_clean = eccn_number.strip().upper()
    
    for category in eccn_json['ccl_categories']:
        for group in category.get('product_groups', []):
            for item in group.get('items', []):
                eccn = item.get('eccn', '')
                # ECCN番号は複数含まれる場合がある（例: "0A998, 0A999"）
                if eccn_number_clean in eccn.upper().replace(' ', ''):
                    return {
                        "ECCN番号": eccn,
                        "カテゴリー": f"{category.get('category_number', '')} - {category.get('title', '')}",
                        "グループ": f"{group.get('group_letter', '')} - {group.get('group_title', '')}",
                        "説明": item.get('description', '')
                    }
    
    return None

def get_eccn_categories_summary(eccn_json: Dict) -> Dict[str, int]:
    """
    ECCN番号のカテゴリー別統計を取得
    
    Args:
        eccn_json: ECCN JSONデータ
        
    Returns:
        カテゴリー別のアイテム数
    """
    summary = {}
    
    if not eccn_json or 'ccl_categories' not in eccn_json:
        return summary
    
    for category in eccn_json['ccl_categories']:
        category_name = category.get('category_number', 'Unknown')
        total_items = 0
        
        for group in category.get('product_groups', []):
            total_items += len(group.get('items', []))
        
        summary[category_name] = total_items
    
    return summary

def check_entity_list(company_name: str, df: Optional[pd.DataFrame] = None) -> Tuple[bool, Optional[Dict]]:
    """
    企業がエンティティリストに掲載されているか確認
    
    Args:
        company_name: 企業名
        df: エンティティリストのDataFrame（オプション）
        
    Returns:
        (掲載されている場合True, 掲載情報の辞書)
    """
    if df is None:
        return False, None
    
    matching_rows = df[df['企業・機関名'].str.contains(company_name, case=False, na=False)]
    
    if matching_rows.empty:
        return False, None
    
    row = matching_rows.iloc[0]
    info = {
        "企業・機関名": row['企業・機関名'],
        "国": row['国'],
        "掲載理由": row['掲載理由'],
        "規制内容": row['規制内容'],
        "掲載日": row['掲載日']
    }
    
    return True, info

def format_currency(amount_str: str) -> Optional[float]:
    """
    金額文字列を数値に変換
    
    Args:
        amount_str: 金額文字列（例：「¥1,000,000」「$10,000」）
        
    Returns:
        数値（円）
    """
    # 数字以外を削除
    numbers = re.findall(r'\d+', amount_str.replace(',', ''))
    if not numbers:
        return None
    
    amount = float(''.join(numbers))
    
    # ドル表記の場合は円に換算（仮に1ドル=150円）
    if '$' in amount_str or 'USD' in amount_str.upper():
        amount *= 150
    
    return amount

def assess_risk_level(analysis_result: str) -> str:
    """
    分析結果からリスクレベルを評価
    
    Args:
        analysis_result: AI分析結果のテキスト
        
    Returns:
        リスクレベル（「高」「中」「低」）
    """
    high_risk_keywords = [
        "許可が必要", "許可申請", "禁止", "規制対象", "懸念",
        "エンティティリスト", "DPL", "武器", "大量破壊兵器",
        "軍事", "北朝鮮", "イラン", "シリア"
    ]
    
    medium_risk_keywords = [
        "確認が必要", "注意", "審査", "キャッチオール",
        "要確認", "デューデリジェンス"
    ]
    
    low_risk_keywords = [
        "許可不要", "問題なし", "リスト該当なし",
        "グループA国", "少額特例"
    ]
    
    high_count = sum(1 for keyword in high_risk_keywords if keyword in analysis_result)
    medium_count = sum(1 for keyword in medium_risk_keywords if keyword in analysis_result)
    low_count = sum(1 for keyword in low_risk_keywords if keyword in analysis_result)
    
    if high_count > 0:
        return "高"
    elif medium_count > 0:
        return "中"
    elif low_count > 0:
        return "低"
    else:
        return "中"

def generate_action_items(analysis_result: str) -> List[str]:
    """
    分析結果から推奨アクションを生成
    
    Args:
        analysis_result: AI分析結果のテキスト
        
    Returns:
        推奨アクションのリスト
    """
    actions = []
    
    if "許可申請" in analysis_result or "許可が必要" in analysis_result:
        actions.append("✅ 輸出許可申請の準備を開始する")
    
    if "該非判定" in analysis_result or "リスト規制" in analysis_result:
        actions.append("✅ 正確な該非判定を実施する")
    
    if "エンドユーザー" in analysis_result or "需要者" in analysis_result:
        actions.append("✅ エンドユーザーの詳細情報を確認・記録する")
    
    if "用途" in analysis_result:
        actions.append("✅ 製品の最終用途を明確に確認・文書化する")
    
    if "エンティティリスト" in analysis_result or "DPL" in analysis_result:
        actions.append("✅ 制裁者リストとの照合を徹底する")
    
    if "包括許可" in analysis_result:
        actions.append("✅ 包括許可制度の適用可能性を検討する")
    
    if "社内体制" in analysis_result or "輸出管理" in analysis_result:
        actions.append("✅ 輸出管理内部規程（CP）を整備・更新する")
    
    # デフォルトアクション
    if not actions:
        actions.append("✅ 専門家に相談する")
    
    actions.append("✅ 分析結果を記録・保管する")
    
    return actions


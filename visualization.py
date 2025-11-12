"""
可視化機能モジュール
カントリーチャート、ECCN規制の視覚化
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from typing import Dict, List, Optional

def create_country_chart_heatmap(country_chart_df: pd.DataFrame, eccn_number: Optional[str] = None):
    """
    カントリーチャートをヒートマップで可視化
    
    Args:
        country_chart_df: カントリーチャートのDataFrame
        eccn_number: 特定のECCN番号（指定した場合、その規制理由のみ表示）
    """
    if country_chart_df is None or country_chart_df.empty:
        return None
    
    # 国名列を取得
    countries = country_chart_df.iloc[:, 0]
    
    # 規制理由の列（CB 1, NS 1等）を取得
    regulation_columns = country_chart_df.columns[1:17]  # CB 1からAT 2まで
    
    # データを数値化（Xを1、空白を0に）
    data_matrix = country_chart_df[regulation_columns].copy()
    data_matrix = data_matrix.replace('X', 1).fillna(0)
    
    # ヒートマップ作成
    fig = go.Figure(data=go.Heatmap(
        z=data_matrix.values,
        x=regulation_columns,
        y=countries,
        colorscale=[
            [0, '#f0f0f0'],  # 規制なし（グレー）
            [1, '#ef4444']   # 規制あり（赤）
        ],
        showscale=True,
        colorbar=dict(
            title="規制",
            tickvals=[0, 1],
            ticktext=["許可不要", "許可必要"]
        ),
        hovertemplate='国: %{y}<br>規制理由: %{x}<br>ステータス: %{z}<extra></extra>',
        text=country_chart_df[regulation_columns].values,
        texttemplate='%{text}',
        textfont={"size": 10}
    ))
    
    fig.update_layout(
        title={
            'text': f'カントリーチャート - 規制マップ{" (ECCN: " + eccn_number + ")" if eccn_number else ""}',
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title="規制理由",
        yaxis_title="国名",
        height=max(600, len(countries) * 15),
        font=dict(size=10),
        yaxis=dict(tickmode='linear'),
        xaxis=dict(tickangle=-45)
    )
    
    return fig


def create_world_map_restrictions(country_chart_df: pd.DataFrame, eccn_number: str, regulation_reason: str = "NS 1"):
    """
    世界地図上で規制国を色分け表示
    
    Args:
        country_chart_df: カントリーチャートのDataFrame
        eccn_number: ECCN番号
        regulation_reason: 規制理由（例: "NS 1", "AT 1"）
    """
    if country_chart_df is None or country_chart_df.empty:
        return None
    
    # 国名と規制状況を取得
    countries = country_chart_df.iloc[:, 0].tolist()
    
    # 規制理由の列が存在するか確認
    if regulation_reason not in country_chart_df.columns:
        return None
    
    restrictions = country_chart_df[regulation_reason].tolist()
    
    # データフレーム作成
    map_data = pd.DataFrame({
        'country': countries,
        'restriction': ['許可必要' if r == 'X' else '許可不要' for r in restrictions],
        'status': [1 if r == 'X' else 0 for r in restrictions]
    })
    
    # 国名を標準化（ISO3コードに変換）
    # 簡易的なマッピング（実際にはより詳細なマッピングが必要）
    country_mapping = {
        'China (P.R.C.)': 'CHN',
        'Russia': 'RUS',
        'Japan': 'JPN',
        'United States': 'USA',
        'United Kingdom': 'GBR',
        'Germany': 'DEU',
        'France': 'FRA',
        'South Korea': 'KOR',
        'North Korea': 'PRK',
        'Iran': 'IRN',
        'Syria': 'SYR',
        'Cuba': 'CUB',
        # 他の国も追加...
    }
    
    map_data['iso_alpha'] = map_data['country'].map(country_mapping)
    
    # 世界地図作成
    fig = px.choropleth(
        map_data,
        locations='iso_alpha',
        color='status',
        hover_name='country',
        hover_data={'restriction': True, 'status': False, 'iso_alpha': False},
        color_continuous_scale=[
            [0, '#10b981'],  # 緑（許可不要）
            [1, '#ef4444']   # 赤（許可必要）
        ],
        labels={'status': '規制ステータス'},
        title=f'ECCN {eccn_number} - {regulation_reason} 規制マップ'
    )
    
    fig.update_geos(
        showcoastlines=True,
        coastlinecolor="RebeccaPurple",
        showland=True,
        landcolor="lightgray",
        showocean=True,
        oceancolor="LightBlue"
    )
    
    fig.update_layout(
        height=600,
        coloraxis_colorbar=dict(
            title="規制",
            tickvals=[0, 1],
            ticktext=["許可不要", "許可必要"]
        )
    )
    
    return fig


def create_regulation_summary_chart(country_chart_df: pd.DataFrame):
    """
    規制理由別の規制国数を棒グラフで表示
    """
    if country_chart_df is None or country_chart_df.empty:
        return None
    
    # 規制理由の列
    regulation_columns = country_chart_df.columns[1:17]
    
    # 各規制理由での「X」の数をカウント
    restriction_counts = {}
    for col in regulation_columns:
        restriction_counts[col] = (country_chart_df[col] == 'X').sum()
    
    # データフレーム作成
    summary_df = pd.DataFrame({
        '規制理由': list(restriction_counts.keys()),
        '規制国数': list(restriction_counts.values())
    })
    
    # 棒グラフ作成
    fig = px.bar(
        summary_df,
        x='規制理由',
        y='規制国数',
        title='規制理由別の規制国数',
        color='規制国数',
        color_continuous_scale='Reds',
        labels={'規制国数': '規制が必要な国の数'}
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        height=400,
        showlegend=False
    )
    
    return fig


def create_interactive_eccn_table(eccn_json: Dict):
    """
    クリック可能なECCNテーブルを作成
    """
    if not eccn_json:
        return None
    
    # ECCNデータを平坦化
    eccn_list = []
    for category in eccn_json.get('ccl_categories', []):
        cat_num = category.get('category_number', '')
        cat_title = category.get('title', '')
        
        for group in category.get('product_groups', []):
            group_code = group.get('group_code', '')
            
            for item in group.get('items', []):
                eccn_list.append({
                    'ECCN番号': item.get('eccn', ''),
                    'カテゴリー': f"{cat_num} - {cat_title}",
                    'グループ': group_code,
                    '説明': item.get('description', '')[:100] + '...' if len(item.get('description', '')) > 100 else item.get('description', ''),
                    '規制理由': item.get('reason_for_control', '')
                })
    
    df = pd.DataFrame(eccn_list)
    return df


def display_reference_data(eccn_number: str, country: str, eccn_json: Dict, country_chart_df: pd.DataFrame):
    """
    参照データを表示（分析結果の根拠）
    
    Args:
        eccn_number: ECCN番号
        country: 対象国
        eccn_json: ECCNデータベース
        country_chart_df: カントリーチャート
    """
    st.markdown("---")
    st.markdown("### 📚 参照データ（分析の根拠）")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔢 ECCN番号詳細")
        
        # ECCN詳細を検索
        eccn_detail = None
        if eccn_json:
            for category in eccn_json.get('ccl_categories', []):
                for group in category.get('product_groups', []):
                    for item in group.get('items', []):
                        if item.get('eccn', '') == eccn_number:
                            eccn_detail = item
                            break
        
        if eccn_detail:
            st.info(f"""
            **ECCN番号**: {eccn_detail.get('eccn', 'N/A')}  
            **説明**: {eccn_detail.get('description', 'N/A')}  
            **規制理由**: {eccn_detail.get('reason_for_control', 'N/A')}  
            **参照**: Commerce Control List (CCL)
            """)
        else:
            st.warning(f"ECCN番号 {eccn_number} の詳細情報が見つかりません")
    
    with col2:
        st.markdown("#### 🌍 カントリーチャート")
        
        # 対象国の規制状況を検索
        if country_chart_df is not None and not country_chart_df.empty:
            country_row = country_chart_df[country_chart_df.iloc[:, 0].str.contains(country, case=False, na=False)]
            
            if not country_row.empty:
                st.info(f"""
                **対象国**: {country}  
                **参照**: BIS Country Chart  
                **データ日付**: 2025年11月12日
                """)
                
                # 規制状況を表示
                with st.expander("📋 詳細な規制状況"):
                    st.dataframe(country_row.T, use_container_width=True)
            else:
                st.warning(f"国名 {country} がカントリーチャートに見つかりません")


def create_entity_list_viewer(sample_data: Dict):
    """
    Entity List / DPL / UVL / MEU の検索可能なビューワー
    """
    st.markdown("### 🚨 制裁リスト検索")
    
    search_term = st.text_input("🔍 企業名・個人名・住所で検索", placeholder="例: Huawei, SMIC, Moscow")
    
    if search_term:
        st.info(f"""
        **検索ワード**: {search_term}  
        **参照リスト**: 
        - DPL (Denied Persons List)
        - Entity List
        - Unverified List (UVL)
        - Military End User List (MEU)
        
        **注意**: 実際の検索には米国商務省の統合スクリーニングリスト（CSL）を使用してください  
        🔗 https://www.trade.gov/consolidated-screening-list
        """)
        
        # サンプルエンティティリストがあれば表示
        if 'entities' in sample_data and sample_data['entities'] is not None:
            entities = sample_data['entities']
            filtered = entities[
                entities.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)
            ]
            
            if not filtered.empty:
                st.warning(f"⚠️ {len(filtered)}件の一致が見つかりました")
                st.dataframe(filtered, use_container_width=True)
            else:
                st.success("✅ 該当なし（サンプルデータ内）")


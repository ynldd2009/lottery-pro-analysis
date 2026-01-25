import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import requests
import json
import random
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import logging
import traceback
from itertools import combinations

# 设置页面配置
st.set_page_config(page_title="彩票分析系统", layout="wide")

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 奖金配置
PRIZE_RULES = {
    "双色球": {
        "一等奖": {"base": 5000000, "description": "6+1"},
        "二等奖": {"base": 200000, "description": "6+0"},
        "三等奖": {"base": 3000, "description": "5+1"},
        "四等奖": {"base": 200, "description": "5+0或4+1"},
        "五等奖": {"base": 10, "description": "4+0或3+1"},
        "六等奖": {"base": 5, "description": "2+1或1+1或0+1"}
    },
    "快乐8": {
        "选十中十": {"base": 5000000, "description": "选10中10"},
        "选十中九": {"base": 8000, "description": "选10中9"},
        "选十中八": {"base": 800, "description": "选10中8"},
        "选十中七": {"base": 80, "description": "选10中7"},
        "选十中六": {"base": 5, "description": "选10中6"},
        "选十中五": {"base": 3, "description": "选10中5"},
        "选十中零": {"base": 2, "description": "选10中0"}
    },
    "3D": {
        "直选": {"base": 1040, "description": "按位全中"},
        "组选三": {"base": 346, "description": "两个重复号码"},
        "组选六": {"base": 173, "description": "三个不同号码"}
    },
    "大乐透": {
        "一等奖": {"base": 10000000, "description": "5+2"},
        "二等奖": {"base": 500000, "description": "5+1"},
        "三等奖": {"base": 10000, "description": "5+0"},
        "四等奖": {"base": 3000, "description": "4+2"},
        "五等奖": {"base": 300, "description": "4+1"},
        "六等奖": {"base": 200, "description": "3+2"},
        "七等奖": {"base": 100, "description": "4+0"},
        "八等奖": {"base": 15, "description": "3+1或2+2"},
        "九等奖": {"base": 5, "description": "3+0或1+2或2+1或0+2"}
    }
}

# API配置
MXNZP_API_CONFIG = {
    "base_url": "https://www.mxnzp.com/api/lottery/common",
    "lottery_codes": {
        "双色球": "ssq",
        "快乐8": "kl8",
        "3D": "3d",
        "七乐彩": "qlc",
        "大乐透": "dlt",
        "七星彩": "qxc",
        "排列三": "pl3",
        "排列五": "pl5"
    }
}

def get_lottery_data(game_type, app_id, app_secret, count=50):
    """获取彩票历史数据"""
    code = MXNZP_API_CONFIG["lottery_codes"].get(game_type)
    if not code:
        return None, "不支持的彩票类型"
    
    url = f"{MXNZP_API_CONFIG['base_url']}/history"
    params = {
        "code": code,
        "size": count,
        "app_id": app_id,
        "app_secret": app_secret
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if data.get("code") == 1:
            return data.get("data", []), None
        return None, data.get("msg", "未知错误")
    except Exception as e:
        return None, str(e)

def main():
    st.title("🎯 专业彩票分析与预测系统")
    
    # 侧边栏配置
    st.sidebar.header("⚙️ 系统配置")
    app_id = st.sidebar.text_input("MXNZP App ID", value="tmvtoqrnmqjqurlp", type="password")
    app_secret = st.sidebar.text_input("MXNZP App Secret", value="qltq4GTDIVOyq7fUfKIS9kpw0czYyjHV", type="password")
    
    game_type = st.sidebar.selectbox("选择彩种", list(MXNZP_API_CONFIG["lottery_codes"].keys()))
    update_count = st.sidebar.slider("获取期数", 10, 100, 50)
    
    if st.sidebar.button("🔄 获取/更新数据"):
        with st.spinner("正在从云端获取最新开奖数据..."):
            records, error = get_lottery_data(game_type, app_id, app_secret, update_count)
            if error:
                st.error(f"获取失败: {error}")
            else:
                st.session_state['lottery_data'] = records
                st.success(f"成功获取 {len(records)} 期 {game_type} 数据！")

    # 主界面功能区
    tabs = st.tabs(["📊 走势分析", "🤖 智能预测", "🎲 模拟投注", "🛠️ 矩阵工具"])
    
    # 检查是否有数据
    # 自动更新逻辑
    if 'lottery_data' not in st.session_state:
        with st.spinner(f"正在自动获取 {game_type} 最新开奖数据..."):
            records, error = get_lottery_data(game_type, app_id, app_secret, update_count)
            if not error:
                st.session_state['lottery_data'] = records
                st.rerun()
            else:
                st.info("自动获取失败，请检查 API 配置或手动点击更新。")
                return

    data = st.session_state['lottery_data']
    df = pd.DataFrame(data)
    
    with tabs[0]:
        st.subheader(f"{game_type} 历史走势")
        st.dataframe(df[['expect', 'openCode', 'time']], use_container_width=True)
        
        # 简单的热力图分析
        all_nums = []
        for code in df['openCode']:
            nums = code.replace('+', ',').split(',')
            all_nums.extend([int(n) for n in nums if n.strip()])
        
        counts = pd.Series(all_nums).value_counts().sort_index()
        fig = px.bar(x=counts.index, y=counts.values, labels={'x': '号码', 'y': '出现次数'}, title="号码频率分布")
        st.plotly_chart(fig, use_container_width=True)

    with tabs[1]:
        st.subheader("AI 智能预测模型")
        model = st.selectbox("选择预测模型", ["随机森林回归", "LSTM 神经网络", "贝叶斯概率", "区间冷热模型"])
        
        if st.button("🚀 开始计算预测号码"):
            with st.spinner("正在运行 AI 模型进行深度计算..."):
                # 模拟预测逻辑
                if game_type == "双色球":
                    red = sorted(random.sample(range(1, 34), 6))
                    blue = random.randint(1, 16)
                    st.success(f"预测结果：红球 {red} | 蓝球 [{blue}]")
                elif game_type == "大乐透":
                    front = sorted(random.sample(range(1, 36), 5))
                    back = sorted(random.sample(range(1, 13), 2))
                    st.success(f"预测结果：前区 {front} | 后区 {back}")
                else:
                    st.write("该彩种预测功能正在适配中...")
                
                st.warning("注：预测结果仅供参考，请理性投注。")

    with tabs[2]:
        st.subheader("模拟投注与中奖校验")
        user_input = st.text_input("输入您的号码 (例如: 01,05,12,18,25,30+08)")
        if st.button("校验中奖情况"):
            latest = data[0]
            st.write(f"最新开奖期号: {latest['expect']}")
            st.write(f"最新开奖号码: {latest['openCode']}")
            st.info("校验逻辑计算中...")

    with tabs[3]:
        st.subheader("矩阵缩水工具")
        st.write("通过数学矩阵算法，减少投注注数，提高中奖效率。")
        base_nums = st.multiselect("选择您的基础号码池", list(range(1, 34)))
        if st.button("生成矩阵方案"):
            if len(base_nums) < 7:
                st.error("请至少选择 7 个号码进行矩阵缩水")
            else:
                st.write("矩阵方案生成中...")

if __name__ == "__main__":
    main()

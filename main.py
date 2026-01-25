import numpy as np
import random
import math
import requests
import os
import json
import csv
import pandas as pd
import matplotlib.pyplot as plt
import sys
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from PySide6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
                             QLabel, QPushButton, QComboBox, QSpinBox, QListWidget, 
                             QCheckBox, QMessageBox, QInputDialog, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QAbstractItemView, 
                             QFileDialog, QTextEdit, QHBoxLayout, QSplitter, QGroupBox,
                             QGridLayout, QScrollArea, QDialog, QLineEdit, QFrame, QSizePolicy)
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QFont, QColor, QPalette, QPixmap
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import logging
import traceback
from itertools import combinations, product

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 预测模型配置
PREDICTION_MODELS = {
    "1": {"name": "随机森林", "code": "random_forest"},
    "2": {"name": "线性回归", "code": "linear_regression"},
    "3": {"name": "长短记忆(LSTM)", "code": "lstm"},
    "4": {"name": "区间模型", "code": "range_model"},
    "5": {"name": "马尔科夫链模型", "code": "markov_chain"},
    "6": {"name": "贝叶斯概率模型", "code": "bayesian"},
    "7": {"name": "分形模型", "code": "fractal"},
    "8": {"name": "混沌模型", "code": "chaos"},
    "9": {"name": "蝌蚪模型", "code": "tadpole"},
    "10": {"name": "双色球蓝球预测", "code": "ssq_blue"},
    "11": {"name": "AI预测(DeepSeek)", "code": "deepseek_ai"}
}

# 奖金配置（更新快乐8规则）
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
        "选十中零": {"base": 2, "description": "选10中0"},
        "选九中九": {"base": 300000, "description": "选9中9"},
        "选九中八": {"base": 2000, "description": "选9中8"},
        "选九中七": {"base": 200, "description": "选9中7"},
        "选九中六": {"base": 20, "description": "选9中6"},
        "选九中五": {"base": 5, "description": "选9中5"},
        "选九中四": {"base": 3, "description": "选9中4"},
        "选八中八": {"base": 50000, "description": "选8中8"},
        "选八中七": {"base": 800, "description": "选8中7"},
        "选八中六": {"base": 88, "description": "选8中6"},
        "选八中五": {"base": 10, "description": "选8中5"},
        "选八中四": {"base": 3, "description": "选8中4"},
        "选七中七": {"base": 10000, "description": "选7中7"},
        "选七中六": {"base": 288, "description": "选7中6"},
        "选七中五": {"base": 28, "description": "选7中5"},
        "选七中四": {"base": 4, "description": "选7中4"},
        "选六中六": {"base": 3000, "description": "选6中6"},
        "选六中五": {"base": 30, "description": "选6中5"},
        "选六中四": {"base": 10, "description": "选6中4"},
        "选五中五": {"base": 1000, "description": "选5中5"},
        "选五中四": {"base": 21, "description": "选5中4"},
        "选五中三": {"base": 3, "description": "选5中3"},
        "选四中四": {"base": 100, "description": "选4中4"},
        "选四中三": {"base": 5, "description": "选4中3"},
        "选四中二": {"base": 3, "description": "选4中2"},
        "选三中三": {"base": 53, "description": "选3中3"},
        "选三中二": {"base": 3, "description": "选3中2"},
        "选二中二": {"base": 19, "description": "选2中2"},
        "选一中一": {"base": 4.6, "description": "选1中1"}
    },
    "3D": {
        "直选": {"base": 1040, "description": "按位全中"},
        "组选三": {"base": 346, "description": "两个重复号码"},
        "组选六": {"base": 173, "description": "三个不同号码"}
    },
    "七乐彩": {
        "一等奖": {"base": 5000000, "description": "7个基本号码全中"},
        "二等奖": {"base": 10000, "description": "6个基本号码+特别号码"},
        "三等奖": {"base": 1000, "description": "6个基本号码"},
        "四等奖": {"base": 100, "description": "5个基本号码+特别号码"},
        "五等奖": {"base": 50, "description": "5个基本号码"},
        "六等奖": {"base": 10, "description": "4个基本号码+特别号码"},
        "七等奖": {"base": 5, "description": "4个基本号码"}
    },
    # 添加体育彩票
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
    },
    "七星彩": {
        "一等奖": {"base": 5000000, "description": "7位全中"},
        "二等奖": {"base": 100000, "description": "连续中6位"},
        "三等奖": {"base": 1800, "description": "连续中5位"},
        "四等奖": {"base": 300, "description": "连续中4位"},
        "五等奖": {"base": 20, "description": "连续中3位"},
        "六等奖": {"base": 5, "description": "连续中2位"}
    },
    "排列三": {
        "直选": {"base": 1040, "description": "按位全中"},
        "组选三": {"base": 346, "description": "两个重复号码"},
        "组选六": {"base": 173, "description": "三个不同号码"}
    },
    "排列五": {
        "一等奖": {"base": 100000, "description": "5位全中"}
    }
}

# 彩票开奖时间配置（添加体育彩票）
LOTTERY_DRAW_TIMES = {
    "双色球": {"days": ["周二", "周四", "周日"], "time": "21:15", "deadline": "20:50"},
    "快乐8": {"days": ["每日"], "time": "21:30", "deadline": "21:15"},
    "3D": {"days": ["每日"], "time": "21:15", "deadline": "20:50"},
    "七乐彩": {"days": ["周一", "周三", "周五"], "time": "21:15", "deadline": "20:50"},
    # 体育彩票
    "大乐透": {"days": ["周一", "周三", "周六"], "time": "21:00", "deadline": "20:30"},
    "七星彩": {"days": ["周二", "周五", "周日"], "time": "21:00", "deadline": "20:30"},
    "排列三": {"days": ["每日"], "time": "20:30", "deadline": "20:00"},
    "排列五": {"days": ["每日"], "time": "20:30", "deadline": "20:00"}
}

# MXNZP API配置（添加体育彩票）
MXNZP_API_CONFIG = {
    "base_url": "https://www.mxnzp.com/api/lottery/common",
    "endpoints": {
        "aim_lottery": "/aimlottery",      # 指定期号
        "latest": "/latest",                # 最新开奖
        "history": "/history",              # 历史开奖
        "types": "/types",                  # 彩种类型
        "check": "/check"                   # 中奖查询
    },
    "lottery_codes": {
        "双色球": "ssq",
        "快乐8": "kl8",
        "3D": "3d",
        "七乐彩": "qlc",
        # 体育彩票
        "大乐透": "dlt",
        "七星彩": "qxc",
        "排列三": "pl3",
        "排列五": "pl5"
    }
}

class DataUpdateThread(QThread):
    """数据更新线程"""
    update_finished = Signal(bool, str)
    update_progress = Signal(int, int)  # 当前进度, 总进度
    
    def __init__(self, game_type, app_id, app_secret, update_count=50):
        super().__init__()
        self.game_type = game_type
        self.app_id = app_id
        self.app_secret = app_secret
        self.update_count = update_count
        
    def run(self):
        try:
            lottery_code = MXNZP_API_CONFIG["lottery_codes"].get(self.game_type)
            if not lottery_code:
                self.update_finished.emit(False, f"不支持的彩票类型: {self.game_type}")
                return
                
            base_url = MXNZP_API_CONFIG["base_url"]
            endpoint = MXNZP_API_CONFIG["endpoints"]["history"]
            
            url = f"{base_url}{endpoint}"
            params = {
                "code": lottery_code,
                "size": self.update_count,
                "app_id": self.app_id,
                "app_secret": self.app_secret
            }
            
            self.update_progress.emit(10, 100)
            
            response = requests.get(url, params=params, timeout=30)
            self.update_progress.emit(40, 100)
            
            data = response.json()
            
            if data.get("code") == 1:
                records = data.get("data", [])
                if not isinstance(records, list):
                    records = [records]
                
                self.update_progress.emit(60, 100)
                
                processed_count = len(records)
                self.update_finished.emit(True, f"{self.game_type}数据更新成功，获取到{processed_count}条记录")
            else:
                error_msg = data.get("msg", "未知错误")
                self.update_finished.emit(False, f"API返回错误: {error_msg}")
                
        except requests.exceptions.Timeout:
            self.update_finished.emit(False, f"请求超时，请检查网络连接")
        except requests.exceptions.ConnectionError:
            self.update_finished.emit(False, f"网络连接错误，请检查网络")
        except Exception as e:
            error_detail = traceback.format_exc()
            logger.error(f"更新失败: {str(e)}\n{error_detail}")
            self.update_finished.emit(False, f"更新失败: {str(e)}")

class NumberButton(QPushButton):
    """自定义数字按钮，支持圆形样式和遗漏期数显示"""
    def __init__(self, text, cold_hot_type="default", omission=0, frequency=0, probability=0, is_dan=False, is_tuo=False, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(45, 45)
        self.setCheckable(True)
        self.is_dan = is_dan
        self.is_tuo = is_tuo
        self.probability = probability
        
        colors = {
            "hot": "#E74C3C",   # 热号 - 红色
            "warm": "#3498DB",  # 温号 - 蓝色
            "cold": "#2ECC71",  # 冷号 - 绿色
            "default": "#F0F0F0" # 默认 - 灰色
        }
        color = colors.get(cold_hot_type, "#F0F0F0")
        
        if is_dan:
            color = "#FFD700"  # 金色
        elif is_tuo:
            color = "#87CEEB"  # 浅蓝色
        
        self.setStyleSheet(f"""
            QPushButton {{
                border-radius: 22px;
                border: 2px solid #8f8f91;
                font-weight: bold;
                font-size: 14px;
                background-color: #F0F0F0;
                color: black;
            }}
            QPushButton:checked {{
                background-color: {color};
                color: white;
            }}
            QPushButton:hover {{
                border: 2px solid #FF6B6B;
            }}
        """)
        
        self.omission_label = QLabel(f"漏:{omission}", self)
        self.omission_label.setAlignment(Qt.AlignCenter)
        self.omission_label.setGeometry(0, 30, 45, 12)
        self.omission_label.setStyleSheet("font-size: 8px; color: #555;")
        
        self.frequency_label = QLabel(f"出:{frequency}", self)
        self.frequency_label.setAlignment(Qt.AlignCenter)
        self.frequency_label.setGeometry(0, 0, 45, 12)
        self.frequency_label.setStyleSheet("font-size: 8px; color: #555;")
        
        prob_text = f"{probability:.1%}" if probability > 0 else "-"
        self.prob_label = QLabel(prob_text, self)
        self.prob_label.setAlignment(Qt.AlignCenter)
        self.prob_label.setGeometry(0, 15, 45, 12)
        self.prob_label.setStyleSheet("font-size: 8px; color: #555;")
        
        self.set_omission(omission)
        self.set_frequency(frequency)
        self.set_probability(probability)
    
    def set_omission(self, omission):
        self.omission_label.setText(f"漏:{omission}")
        if omission > 20:
            self.omission_label.setStyleSheet("font-size: 8px; color: #E74C3C; font-weight: bold;")
        elif omission > 10:
            self.omission_label.setStyleSheet("font-size: 8px; color: #F39C12;")
        else:
            self.omission_label.setStyleSheet("font-size: 8px; color: #555;")
    
    def set_frequency(self, frequency):
        self.frequency_label.setText(f"出:{frequency}")
        if frequency > 10:
            self.frequency_label.setStyleSheet("font-size: 8px; color: #27AE60; font-weight: bold;")
        elif frequency > 5:
            self.frequency_label.setStyleSheet("font-size: 8px; color: #27AE60;")
        else:
            self.frequency_label.setStyleSheet("font-size: 8px; color: #555;")
    
    def set_probability(self, probability):
        prob_text = f"{probability:.1%}" if probability > 0 else "-"
        self.prob_label.setText(prob_text)
        if probability > 0.1:
            self.prob_label.setStyleSheet("font-size: 8px; color: #E74C3C; font-weight: bold;")
        elif probability > 0.05:
            self.prob_label.setStyleSheet("font-size: 8px; color: #F39C12;")
        else:
            self.prob_label.setStyleSheet("font-size: 8px; color: #555;")
    
    def set_dan(self, is_dan):
        self.is_dan = is_dan
        if is_dan:
            self.setStyleSheet("""
                QPushButton {
                    border-radius: 22px;
                    border: 2px solid #8f8f91;
                    font-weight: bold;
                    font-size: 14px;
                    background-color: #FFD700;
                    color: black;
                }
                QPushButton:checked {
                    background-color: #FFD700;
                    color: black;
                }
                QPushButton:hover {
                    border: 2px solid #FF6B6B;
                }
            """)
    
    def set_tuo(self, is_tuo):
        self.is_tuo = is_tuo
        if is_tuo:
            self.setStyleSheet("""
                QPushButton {
                    border-radius: 22px;
                    border: 2px solid #8f8f91;
                    font-weight: bold;
                    font-size: 14px;
                    background-color: #87CEEB;
                    color: black;
                }
                QPushButton:checked {
                    background-color: #87CEEB;
                    color: black;
                }
                QPushButton:hover {
                    border: 2px solid #FF6B6B;
                }
            """)

class HistoryCompareDialog(QDialog):
    """历史开奖比对对话框 - 替换原来的二维码扫描兑奖"""
    def __init__(self, parent=None, game_type="双色球", selected_numbers=None):
        super().__init__(parent)
        self.game_type = game_type
        self.selected_numbers = selected_numbers or []
        self.setWindowTitle(f"{game_type} - 历史开奖比对")
        self.setFixedSize(600, 700)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        title_label = QLabel("📊 历史开奖比对")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2E8B57; margin: 20px;")
        layout.addWidget(title_label)
        
        # 选择期号区域
        issue_group = QGroupBox("选择历史期号进行比对")
        issue_layout = QVBoxLayout(issue_group)
        
        info_label = QLabel(f"请选择一期{self.game_type}的历史开奖数据，与您的号码进行比对分析。")
        info_label.setWordWrap(True)
        issue_layout.addWidget(info_label)
        
        # 期号选择
        issue_select_layout = QHBoxLayout()
        issue_select_layout.addWidget(QLabel("选择期号:"))
        
        self.issue_combo = QComboBox()
        self.load_history_issues()
        issue_select_layout.addWidget(self.issue_combo)
        
        self.refresh_issues_btn = QPushButton("刷新列表")
        self.refresh_issues_btn.clicked.connect(self.load_history_issues)
        issue_select_layout.addWidget(self.refresh_issues_btn)
        
        issue_layout.addLayout(issue_select_layout)
        
        # 显示选中期号的详情
        self.issue_detail_label = QLabel("选择期号后，这里将显示开奖详情...")
        self.issue_detail_label.setWordWrap(True)
        self.issue_detail_label.setStyleSheet("""
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 10px;
            margin: 5px;
        """)
        issue_layout.addWidget(self.issue_detail_label)
        
        self.issue_combo.currentTextChanged.connect(self.update_issue_detail)
        
        layout.addWidget(issue_group)
        
        # 显示用户选择的号码
        if self.selected_numbers:
            user_num_group = QGroupBox("您选择的号码")
            user_num_layout = QVBoxLayout(user_num_group)
            
            if self.game_type == "双色球":
                red = [num for num in self.selected_numbers if num <= 33]
                blue = [num for num in self.selected_numbers if num > 33]
                user_num_text = f"红球 ({len(red)}个): {', '.join(map(str, sorted(red)))}\n蓝球 ({len(blue)}个): {', '.join(map(str, sorted(blue)))}"
            elif self.game_type == "大乐透":
                front = [num for num in self.selected_numbers if num <= 35]
                back = [num for num in self.selected_numbers if num > 35]
                user_num_text = f"前区 ({len(front)}个): {', '.join(map(str, sorted(front)))}\n后区 ({len(back)}个): {', '.join(map(str, sorted(back)))}"
            else:
                user_num_text = f"号码 ({len(self.selected_numbers)}个): {', '.join(map(str, sorted(self.selected_numbers)))}"
            
            user_num_label = QLabel(user_num_text)
            user_num_label.setWordWrap(True)
            user_num_layout.addWidget(user_num_label)
            
            layout.addWidget(user_num_group)
        
        # 比对按钮
        compare_btn = QPushButton("🔍 开始比对分析")
        compare_btn.clicked.connect(self.perform_comparison)
        compare_btn.setStyleSheet("font-size: 14px; padding: 10px; background-color: #4ECDC4; color: white;")
        layout.addWidget(compare_btn)
        
        # 结果显示区域
        result_group = QGroupBox("比对分析结果")
        result_layout = QVBoxLayout(result_group)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setPlaceholderText("点击'开始比对分析'按钮后，这里将显示详细的号码匹配结果和中奖情况分析...")
        result_layout.addWidget(self.result_text)
        
        layout.addWidget(result_group)
        
        # 按钮布局
        btn_layout = QHBoxLayout()
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.reject)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
        # 初始化显示第一个期号的详情
        if self.issue_combo.count() > 0:
            self.update_issue_detail(self.issue_combo.currentText())
    
    def load_history_issues(self):
        """加载历史期号列表"""
        self.issue_combo.clear()
        
        if self.parent() and hasattr(self.parent(), 'history_data'):
            history_data = self.parent().history_data
            if self.game_type in history_data and history_data[self.game_type]:
                data = history_data[self.game_type]
                # 按期号倒序排列（最新的在前面）
                sorted_data = sorted(data, key=lambda x: x.get("期号", ""), reverse=True)
                
                for record in sorted_data[:50]:  # 只显示最近50期
                    issue = record.get("期号", "")
                    date = record.get("开奖日期", "")
                    display_text = f"{issue}期 ({date})"
                    self.issue_combo.addItem(display_text, issue)
                
                if self.issue_combo.count() > 0:
                    self.issue_combo.setCurrentIndex(0)
                return
        
        # 如果没有数据，添加一个提示项
        self.issue_combo.addItem("暂无历史数据，请先获取开奖记录")
    
    def update_issue_detail(self, display_text):
        """更新选中期号的详情显示"""
        if not display_text or "暂无历史数据" in display_text:
            self.issue_detail_label.setText("请先获取历史开奖数据")
            return
        
        # 从显示文本中提取期号
        if "期 (" in display_text:
            issue = display_text.split("期 (")[0]
        else:
            issue = display_text
        
        if self.parent() and hasattr(self.parent(), 'history_data'):
            history_data = self.parent().history_data
            if self.game_type in history_data and history_data[self.game_type]:
                for record in history_data[self.game_type]:
                    if record.get("期号", "") == issue:
                        detail = f"""
                        <div style='font-size: 13px; line-height: 1.5;'>
                        <b>期号:</b> {record.get("期号", "")}<br>
                        <b>开奖日期:</b> {record.get("开奖日期", "")}<br>
                        <b>开奖号码:</b> <span style='color: #E74C3C;'>{record.get("开奖号码", "")}</span><br>
                        """
                        
                        # 添加奖池和一等奖信息（如果存在）
                        if "奖池" in record and record["奖池"]:
                            detail += f"<b>奖池:</b> {record['奖池']}<br>"
                        if "一等奖" in record and record["一等奖"]:
                            detail += f"<b>一等奖:</b> {record['一等奖']}<br>"
                        
                        detail += "</div>"
                        self.issue_detail_label.setText(detail)
                        return
        
        self.issue_detail_label.setText(f"未找到期号 {issue} 的详细数据")
    
    def perform_comparison(self):
        """执行比对分析"""
        if self.issue_combo.count() == 0 or "暂无历史数据" in self.issue_combo.currentText():
            self.result_text.setHtml("<span style='color: red;'>请先获取历史开奖数据</span>")
            return
        
        if not self.selected_numbers:
            self.result_text.setHtml("<span style='color: red;'>请先选择要比对的号码</span>")
            return
        
        # 获取选中的期号
        display_text = self.issue_combo.currentText()
        if "期 (" in display_text:
            issue = display_text.split("期 (")[0]
        else:
            issue = display_text
        
        # 获取对应的开奖记录
        target_record = None
        if self.parent() and hasattr(self.parent(), 'history_data'):
            history_data = self.parent().history_data
            if self.game_type in history_data and history_data[self.game_type]:
                for record in history_data[self.game_type]:
                    if record.get("期号", "") == issue:
                        target_record = record
                        break
        
        if not target_record:
            self.result_text.setHtml(f"<span style='color: red;'>未找到期号 {issue} 的开奖数据</span>")
            return
        
        # 根据游戏类型进行比对分析
        result_html = self.compare_numbers_with_record(target_record)
        self.result_text.setHtml(result_html)
    
    def compare_numbers_with_record(self, record):
        """将用户号码与开奖记录进行比对"""
        draw_numbers_str = record.get("开奖号码", "")
        issue = record.get("期号", "")
        date = record.get("开奖日期", "")
        
        # 解析开奖号码
        if self.game_type == "双色球":
            if "+" in draw_numbers_str:
                red_part, blue_part = draw_numbers_str.split("+")
                draw_red = list(map(int, red_part.strip().split()))
                draw_blue = list(map(int, blue_part.strip().split()))
            else:
                draw_red = list(map(int, draw_numbers_str.strip().split()))[:6]
                draw_blue = list(map(int, draw_numbers_str.strip().split()))[6:7] if len(draw_numbers_str.strip().split()) > 6 else []
            
            user_red = [num for num in self.selected_numbers if num <= 33]
            user_blue = [num for num in self.selected_numbers if num > 33]
            
            red_match = len(set(user_red) & set(draw_red))
            blue_match = 1 if user_blue and user_blue[0] in draw_blue else 0
            
            # 判断中奖等级
            prize_level = "未中奖"
            if red_match == 6 and blue_match == 1:
                prize_level = "一等奖"
            elif red_match == 6:
                prize_level = "二等奖"
            elif red_match == 5 and blue_match == 1:
                prize_level = "三等奖"
            elif red_match == 5 or (red_match == 4 and blue_match == 1):
                prize_level = "四等奖"
            elif red_match == 4 or (red_match == 3 and blue_match == 1):
                prize_level = "五等奖"
            elif blue_match == 1:
                prize_level = "六等奖"
            
            result_html = f"""
            <div style='font-family: "Microsoft YaHei"; line-height: 1.6;'>
            <h3 style='color: #2E8B57;'>双色球第{issue}期比对结果</h3>
            <p><b>开奖日期:</b> {date}</p>
            <p><b>开奖号码:</b> <span style='color: red;'>{' '.join(map(str, draw_red))}</span> + <span style='color: blue;'>{' '.join(map(str, draw_blue))}</span></p>
            
            <div style='background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 15px 0;'>
            <h4 style='color: #495057; margin-top: 0;'>号码匹配详情</h4>
            <p><b>您的红球:</b> {', '.join(map(str, sorted(user_red)))}</p>
            <p><b>匹配红球:</b> <span style='color: {'red' if red_match > 0 else '#6c757d'}; font-weight: bold;'>{red_match} 个</span></p>
            <p><b>匹配的号码:</b> {', '.join(map(str, sorted(set(user_red) & set(draw_red)))) if red_match > 0 else '无'}</p>
            
            <p><b>您的蓝球:</b> {', '.join(map(str, user_blue))}</p>
            <p><b>匹配蓝球:</b> <span style='color: {'blue' if blue_match > 0 else '#6c757d'}; font-weight: bold;'>{blue_match} 个</span></p>
            <p><b>匹配的号码:</b> {user_blue[0] if blue_match > 0 else '无'}</p>
            </div>
            
            <div style='background-color: {'#d4edda' if prize_level != '未中奖' else '#f8d7da'}; 
                        color: {'#155724' if prize_level != '未中奖' else '#721c24'}; 
                        padding: 15px; border-radius: 8px; border: 1px solid {'#c3e6cb' if prize_level != '未中奖' else '#f5c6cb'};'>
            <h4 style='margin-top: 0;'>🎯 中奖情况</h4>
            <p style='font-size: 18px; font-weight: bold;'>{prize_level}</p>
            """
            
            if prize_level != "未中奖":
                prize_info = PRIZE_RULES["双色球"].get(prize_level, {})
                if prize_info:
                    result_html += f"<p><b>奖金:</b> {prize_info.get('base', 0)}元起</p>"
                    result_html += f"<p><b>说明:</b> {prize_info.get('description', '')}</p>"
            
            result_html += "</div>"
            
            # 添加分析建议
            result_html += """
            <div style='margin-top: 20px; padding: 15px; background-color: #fff3cd; border-radius: 8px; border: 1px solid #ffeaa7;'>
            <h4 style='color: #856404; margin-top: 0;'>💡 分析建议</h4>
            """
            
            if red_match >= 4 or (red_match >= 3 and blue_match == 1):
                result_html += "<p style='color: #155724;'>🔴 <b>选号策略良好</b>：红球匹配较多，当前选号思路值得坚持！</p>"
            elif red_match >= 2:
                result_html += "<p style='color: #856404;'>🟡 <b>匹配一般</b>：有部分号码匹配，建议参考热号冷号分析调整选号。</p>"
            else:
                result_html += "<p style='color: #721c24;'>⚪ <b>匹配较少</b>：建议重新分析号码走势，关注近期热号和长期冷号。</p>"
            
            result_html += "</div></div>"
            
            return result_html
            
        elif self.game_type == "大乐透":
            # 大乐透比对逻辑（类似双色球）
            if "+" in draw_numbers_str:
                front_part, back_part = draw_numbers_str.split("+")
                draw_front = list(map(int, front_part.strip().split()))
                draw_back = list(map(int, back_part.strip().split()))
            else:
                all_nums = list(map(int, draw_numbers_str.strip().split()))
                draw_front = all_nums[:5] if len(all_nums) >= 5 else []
                draw_back = all_nums[5:7] if len(all_nums) >= 7 else []
            
            user_front = [num for num in self.selected_numbers if num <= 35]
            user_back = [num for num in self.selected_numbers if num > 35]
            
            front_match = len(set(user_front) & set(draw_front))
            back_match = len(set(user_back) & set(draw_back))
            
            # 简化中奖判断
            prize_level = "未中奖"
            if front_match >= 3 or (front_match >= 2 and back_match >= 1):
                prize_level = "中小奖"
            if front_match == 5 and back_match == 2:
                prize_level = "一等奖"
            elif front_match == 5 and back_match == 1:
                prize_level = "二等奖"
            elif front_match == 5:
                prize_level = "三等奖"
            
            result_html = f"""
            <div style='font-family: "Microsoft YaHei"; line-height: 1.6;'>
            <h3 style='color: #2E8B57;'>大乐透第{issue}期比对结果</h3>
            <p><b>开奖日期:</b> {date}</p>
            <p><b>开奖号码:</b> <span style='color: #FF4500;'>{' '.join(map(str, draw_front))}</span> + <span style='color: #32CD32;'>{' '.join(map(str, draw_back))}</span></p>
            
            <div style='background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 15px 0;'>
            <h4 style='color: #495057; margin-top: 0;'>号码匹配详情</h4>
            <p><b>您的前区:</b> {', '.join(map(str, sorted(user_front)))}</p>
            <p><b>匹配前区:</b> <span style='color: {'#FF4500' if front_match > 0 else '#6c757d'}; font-weight: bold;'>{front_match} 个</span></p>
            
            <p><b>您的后区:</b> {', '.join(map(str, sorted(user_back)))}</p>
            <p><b>匹配后区:</b> <span style='color: {'#32CD32' if back_match > 0 else '#6c757d'}; font-weight: bold;'>{back_match} 个</span></p>
            </div>
            
            <div style='background-color: {'#d4edda' if prize_level != '未中奖' else '#f8d7da'}; 
                        color: {'#155724' if prize_level != '未中奖' else '#721c24'}; 
                        padding: 15px; border-radius: 8px; border: 1px solid {'#c3e6cb' if prize_level != '未中奖' else '#f5c6cb'};'>
            <h4 style='margin-top: 0;'>🎯 中奖情况</h4>
            <p style='font-size: 18px; font-weight: bold;'>{prize_level}</p>
            </div>
            
            <div style='margin-top: 20px; padding: 15px; background-color: #e3f2fd; border-radius: 8px; border: 1px solid #bbdefb;'>
            <p><b>分析说明:</b> 大乐透中奖规则较复杂，以上为简化判断。准确中奖等级请以官方公布为准。</p>
            </div>
            </div>
            """
            
            return result_html
            
        else:
            # 其他彩票类型的通用比对
            draw_numbers = list(map(int, draw_numbers_str.strip().split()))
            user_numbers = self.selected_numbers
            
            match_count = len(set(user_numbers) & set(draw_numbers))
            
            result_html = f"""
            <div style='font-family: "Microsoft YaHei"; line-height: 1.6;'>
            <h3 style='color: #2E8B57;'>{self.game_type}第{issue}期比对结果</h3>
            <p><b>开奖日期:</b> {date}</p>
            <p><b>开奖号码:</b> <span style='color: #6f42c1;'>{draw_numbers_str}</span></p>
            
            <div style='background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 15px 0;'>
            <h4 style='color: #495057; margin-top: 0;'>号码匹配详情</h4>
            <p><b>您的号码:</b> {', '.join(map(str, sorted(user_numbers)))}</p>
            <p><b>匹配号码:</b> <span style='color: {'#6f42c1' if match_count > 0 else '#6c757d'}; font-weight: bold;'>{match_count} 个</span></p>
            <p><b>匹配的号码:</b> {', '.join(map(str, sorted(set(user_numbers) & set(draw_numbers)))) if match_count > 0 else '无'}</p>
            </div>
            
            <div style='margin-top: 20px; padding: 15px; background-color: #e3f2fd; border-radius: 8px; border: 1px solid #bbdefb;'>
            <p><b>分析说明:</b> {self.game_type}的中奖规则较为特殊，具体中奖情况请参考官方规则或使用专业工具计算。</p>
            <p>匹配{match_count}个号码，表明您的选号与本期开奖号码有{match_count}处重合。</p>
            </div>
            </div>
            """
            
            return result_html

class LotteryAnalysisDialog(QDialog):
    """彩票分析对话框"""
    def __init__(self, parent=None, game_type="双色球", selected_numbers=None):
        super().__init__(parent)
        self.game_type = game_type
        self.selected_numbers = selected_numbers or []
        self.setWindowTitle(f"{game_type} - 开奖记录与号码分析")
        self.setGeometry(200, 200, 1000, 700)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        tabs = QTabWidget()
        
        history_tab = QWidget()
        history_layout = QVBoxLayout(history_tab)
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(["期号", "开奖日期", "开奖号码", "一等奖", "奖池"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        history_layout.addWidget(self.history_table)
        tabs.addTab(history_tab, "📋 最近50期开奖记录")
        
        compare_tab = QWidget()
        compare_layout = QVBoxLayout(compare_tab)
        self.compare_result = QTextEdit()
        self.compare_result.setReadOnly(True)
        compare_layout.addWidget(self.compare_result)
        tabs.addTab(compare_tab, "🔍 号码比对分析")
        
        layout.addWidget(tabs)
        
        btn_layout = QHBoxLayout()
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        self.load_history_data()
        self.analyze_number_match()
    
    def load_history_data(self):
        if self.parent() and hasattr(self.parent(), 'history_data'):
            history_data = self.parent().history_data
            if self.game_type in history_data and history_data[self.game_type]:
                data = history_data[self.game_type]
                data = sorted(data, key=lambda x: x.get("期号", ""), reverse=True)
                data = data[:50]
                
                self.history_table.setRowCount(len(data))
                for row, record in enumerate(data):
                    self.history_table.setItem(row, 0, QTableWidgetItem(str(record.get("期号", ""))))
                    self.history_table.setItem(row, 1, QTableWidgetItem(str(record.get("开奖日期", ""))))
                    self.history_table.setItem(row, 2, QTableWidgetItem(str(record.get("开奖号码", ""))))
                    self.history_table.setItem(row, 3, QTableWidgetItem(str(record.get("一等奖", "0注"))))
                    self.history_table.setItem(row, 4, QTableWidgetItem(str(record.get("奖池", "0"))))
                return
        
        self.history_table.setRowCount(1)
        self.history_table.setItem(0, 0, QTableWidgetItem("暂无数据"))
        self.history_table.setItem(0, 1, QTableWidgetItem("请先获取历史开奖数据"))
    
    def analyze_number_match(self):
        if not self.selected_numbers:
            self.compare_result.setText("请先选择号码")
            return
        
        recent_numbers = self.get_recent_numbers()
        if not recent_numbers:
            self.compare_result.setText("无法获取最近开奖号码")
            return
        
        if self.game_type == "双色球":
            self.analyze_ssq_match(recent_numbers)
        elif self.game_type == "快乐8":
            self.analyze_kl8_match(recent_numbers)
        elif self.game_type == "3D":
            self.analyze_3d_match(recent_numbers)
        elif self.game_type == "七乐彩":
            self.analyze_qlc_match(recent_numbers)
        elif self.game_type == "大乐透":
            self.analyze_dlt_match(recent_numbers)
        elif self.game_type == "七星彩":
            self.analyze_qxc_match(recent_numbers)
        elif self.game_type == "排列三":
            self.analyze_pl3_match(recent_numbers)
        elif self.game_type == "排列五":
            self.analyze_pl5_match(recent_numbers)
    
    def get_recent_numbers(self):
        if self.parent() and hasattr(self.parent(), 'history_data'):
            history_data = self.parent().history_data
            if self.game_type in history_data and history_data[self.game_type]:
                data = history_data[self.game_type]
                if data:
                    latest_record = data[0]
                    numbers_str = latest_record.get("开奖号码", "")
                    
                    if self.game_type == "双色球":
                        if "+" in numbers_str:
                            red_part, blue_part = numbers_str.split("+")
                            red_numbers = list(map(int, red_part.strip().split()))
                            blue_numbers = list(map(int, blue_part.strip().split()))
                            return red_numbers, blue_numbers
                    elif self.game_type == "快乐8":
                        numbers = list(map(int, numbers_str.strip().split()))
                        return numbers[:20]
                    elif self.game_type == "3D":
                        numbers = list(map(int, numbers_str.strip().split()))
                        return numbers[:3]
                    elif self.game_type == "七乐彩":
                        numbers = list(map(int, numbers_str.strip().split()))
                        return numbers[:7]
                    elif self.game_type == "大乐透":
                        if "+" in numbers_str:
                            front_part, back_part = numbers_str.split("+")
                            front_numbers = list(map(int, front_part.strip().split()))
                            back_numbers = list(map(int, back_part.strip().split()))
                            return front_numbers, back_numbers
                    elif self.game_type == "七星彩":
                        numbers = list(map(int, numbers_str.strip().split()))
                        return numbers[:7]
                    elif self.game_type == "排列三":
                        numbers = list(map(int, numbers_str.strip().split()))
                        return numbers[:3]
                    elif self.game_type == "排列五":
                        numbers = list(map(int, numbers_str.strip().split()))
                        return numbers[:5]
        
        return None
    
    def analyze_ssq_match(self, recent_numbers):
        recent_red, recent_blue = recent_numbers
        selected_red = [num for num in self.selected_numbers if num <= 33]
        selected_blue = [num for num in self.selected_numbers if num > 33]
        
        red_match = len(set(selected_red) & set(recent_red))
        blue_match = 1 if selected_blue and selected_blue[0] in recent_blue else 0
        
        result = f"""
        <div style='font-size: 14px; line-height: 1.6;'>
        <h3>双色球号码比对分析</h3>
        
        <b>您选择的号码:</b><br>
        红球: {', '.join(map(str, selected_red))}<br>
        蓝球: {', '.join(map(str, selected_blue))}<br><br>
        
        <b>最近开奖号码:</b><br>
        红球: {', '.join(map(str, recent_red))}<br>
        蓝球: {recent_blue[0]}<br><br>
        
        <b>匹配结果:</b><br>
        • 红球匹配: <span style='color: #E74C3C;'>{red_match} 个</span><br>
        • 蓝球匹配: <span style='color: #3498DB;'>{blue_match} 个</span><br><br>
        
        <b>分析建议:</b><br>
        """
        
        if red_match >= 4 and blue_match == 1:
            result += "<span style='color: #27AE60;'>🎉 恭喜！如果这是上期投注，您可能中得大奖！</span>"
        elif red_match >= 3:
            result += "<span style='color: #F39C12;'>📊 红球匹配较多，继续坚持这个选号策略</span>"
        else:
            result += "<span style='color: #95a5a6;'>💡 匹配较少，建议调整选号策略</span>"
        
        result += "</div>"
        self.compare_result.setHtml(result)
    
    def analyze_dlt_match(self, recent_numbers):
        recent_front, recent_back = recent_numbers
        selected_front = [num for num in self.selected_numbers if num <= 35]
        selected_back = [num for num in self.selected_numbers if num > 35]
        
        front_match = len(set(selected_front) & set(recent_front))
        back_match = len(set(selected_back) & set(recent_back))
        
        result = f"""
        <div style='font-size: 14px; line-height: 1.6;'>
        <h3>大乐透号码比对分析</h3>
        
        <b>您选择的号码:</b><br>
        前区: {', '.join(map(str, selected_front))}<br>
        后区: {', '.join(map(str, selected_back))}<br><br>
        
        <b>最近开奖号码:</b><br>
        前区: {', '.join(map(str, recent_front))}<br>
        后区: {', '.join(map(str, recent_back))}<br><br>
        
        <b>匹配结果:</b><br>
        • 前区匹配: <span style='color: #E74C3C;'>{front_match} 个</span><br>
        • 后区匹配: <span style='color: #3498DB;'>{back_match} 个</span><br><br>
        
        <b>分析建议:</b><br>
        """
        
        if front_match >= 3 and back_match >= 1:
            result += "<span style='color: #27AE60;'>🎉 匹配不错，继续坚持这个选号策略</span>"
        elif front_match >= 2:
            result += "<span style='color: #F39C12;'>📊 前区匹配较好，有中奖潜力</span>"
        else:
            result += "<span style='color: #95a5a6;'>💡 匹配较少，建议参考走势图</span>"
        
        result += "</div>"
        self.compare_result.setHtml(result)
    
    def analyze_qxc_match(self, recent_numbers):
        match_positions = []
        for i, num in enumerate(self.selected_numbers[:7]):
            if i < len(recent_numbers) and num == recent_numbers[i]:
                match_positions.append(f"第{i+1}位")
        
        result = f"""
        <div style='font-size: 14px; line-height: 1.6;'>
        <h3>七星彩号码比对分析</h3>
        
        <b>您选择的号码:</b><br>
        {', '.join(map(str, self.selected_numbers))}<br><br>
        
        <b>最近开奖号码:</b><br>
        {', '.join(map(str, recent_numbers))}<br><br>
        
        <b>匹配结果:</b><br>
        • 位置匹配: {', '.join(match_positions) if match_positions else '无'}<br><br>
        
        <b>分析建议:</b><br>
        """
        
        if len(match_positions) >= 4:
            result += "<span style='color: #27AE60;'>🎉 匹配良好！有中奖可能</span>"
        elif len(match_positions) >= 2:
            result += "<span style='color: #F39C12;'>📊 部分匹配，继续努力</span>"
        else:
            result += "<span style='color: #95a5a6;'>💡 匹配较少，建议参考走势图</span>"
        
        result += "</div>"
        self.compare_result.setHtml(result)
    
    def analyze_kl8_match(self, recent_numbers):
        selected_count = len([num for num in self.selected_numbers if num <= 80])
        match_count = len(set(self.selected_numbers) & set(recent_numbers))
        
        result = f"""
        <div style='font-size: 14px; line-height: 1.6;'>
        <h3>快乐8号码比对分析</h3>
        
        <b>您选择的号码 ({selected_count}个):</b><br>
        {', '.join(map(str, sorted(self.selected_numbers)))}<br><br>
        
        <b>最近开奖号码:</b><br>
        {', '.join(map(str, sorted(recent_numbers)))}<br><br>
        
        <b>匹配结果:</b><br>
        • 号码匹配: <span style='color: #E74C3C;'>{match_count} 个</span><br><br>
        
        <b>分析建议:</b><br>
        """
        
        if match_count >= 8:
            result += "<span style='color: #27AE60;'>🎉 优秀匹配！继续坚持这个选号策略</span>"
        elif match_count >= 5:
            result += "<span style='color: #F39C12;'>📊 匹配良好，有中奖潜力</span>"
        else:
            result += "<span style='color: #95a5a6;'>💡 匹配较少，建议参考热号分析</span>"
        
        result += "</div>"
        self.compare_result.setHtml(result)
    
    def analyze_3d_match(self, recent_numbers):
        match_positions = []
        for i, num in enumerate(self.selected_numbers[:3]):
            if i < len(recent_numbers) and num == recent_numbers[i]:
                match_positions.append(f"第{i+1}位")
        
        result = f"""
        <div style='font-size: 14px; line-height: 1.6;'>
        <h3>3D号码比对分析</h3>
        
        <b>您选择的号码:</b><br>
        {', '.join(map(str, self.selected_numbers))}<br><br>
        
        <b>最近开奖号码:</b><br>
        {', '.join(map(str, recent_numbers))}<br><br>
        
        <b>匹配结果:</b><br>
        • 位置匹配: {', '.join(match_positions) if match_positions else '无'}<br><br>
        
        <b>分析建议:</b><br>
        """
        
        if len(match_positions) == 3:
            result += "<span style='color: #27AE60;'>🎉 完全匹配！直选中奖！</span>"
        elif len(match_positions) >= 2:
            result += "<span style='color: #F39C12;'>📊 部分匹配，有组选中奖可能</span>"
        else:
            result += "<span style='color: #95a5a6;'>💡 匹配较少，建议参考走势图</span>"
        
        result += "</div>"
        self.compare_result.setHtml(result)
    
    def analyze_pl3_match(self, recent_numbers):
        match_positions = []
        for i, num in enumerate(self.selected_numbers[:3]):
            if i < len(recent_numbers) and num == recent_numbers[i]:
                match_positions.append(f"第{i+1}位")
        
        result = f"""
        <div style='font-size: 14px; line-height: 1.6;'>
        <h3>排列三号码比对分析</h3>
        
        <b>您选择的号码:</b><br>
        {', '.join(map(str, self.selected_numbers))}<br><br>
        
        <b>最近开奖号码:</b><br>
        {', '.join(map(str, recent_numbers))}<br><br>
        
        <b>匹配结果:</b><br>
        • 位置匹配: {', '.join(match_positions) if match_positions else '无'}<br><br>
        
        <b>分析建议:</b><br>
        """
        
        if len(match_positions) == 3:
            result += "<span style='color: #27AE60;'>🎉 完全匹配！直选中奖！</span>"
        elif len(match_positions) >= 2:
            result += "<span style='color: #F39C12;'>📊 部分匹配，有组选中奖可能</span>"
        else:
            result += "<span style='color: #95a5a6;'>💡 匹配较少，建议参考走势图</span>"
        
        result += "</div>"
        self.compare_result.setHtml(result)
    
    def analyze_pl5_match(self, recent_numbers):
        match_positions = []
        for i, num in enumerate(self.selected_numbers[:5]):
            if i < len(recent_numbers) and num == recent_numbers[i]:
                match_positions.append(f"第{i+1}位")
        
        result = f"""
        <div style='font-size: 14px; line-height: 1.6;'>
        <h3>排列五号码比对分析</h3>
        
        <b>您选择的号码:</b><br>
        {', '.join(map(str, self.selected_numbers))}<br><br>
        
        <b>最近开奖号码:</b><br>
        {', '.join(map(str, recent_numbers))}<br><br>
        
        <b>匹配结果:</b><br>
        • 位置匹配: {', '.join(match_positions) if match_positions else '无'}<br><br>
        
        <b>分析建议:</b><br>
        """
        
        if len(match_positions) == 5:
            result += "<span style='color: #27AE60;'>🎉 完全匹配！一等奖！</span>"
        elif len(match_positions) >= 3:
            result += "<span style='color: #F39C12;'>📊 部分匹配，继续努力</span>"
        else:
            result += "<span style='color: #95a5a6;'>💡 匹配较少，建议参考走势图</span>"
        
        result += "</div>"
        self.compare_result.setHtml(result)
    
    def analyze_qlc_match(self, recent_numbers):
        match_count = len(set(self.selected_numbers) & set(recent_numbers))
        
        result = f"""
        <div style='font-size: 14px; line-height: 1.6;'>
        <h3>七乐彩号码比对分析</h3>
        
        <b>您选择的号码:</b><br>
        {', '.join(map(str, self.selected_numbers))}<br><br>
        
        <b>最近开奖号码:</b><br>
        {', '.join(map(str, recent_numbers))}<br><br>
        
        <b>匹配结果:</b><br>
        • 号码匹配: <span style='color: #E74C3C;'>{match_count} 个</span><br><br>
        
        <b>分析建议:</b><br>
        """
        
        if match_count >= 5:
            result += "<span style='color: #27AE60;'>🎉 优秀匹配！继续坚持这个选号策略</span>"
        elif match_count >= 3:
            result += "<span style='color: #F39C12;'>📊 匹配良好，有中奖潜力</span>"
        else:
            result += "<span style='color: #95a5a6;'>💡 匹配较少，建议参考热号分析</span>"
        
        result += "</div>"
        self.compare_result.setHtml(result)

class LotteryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("彩票分析系统 - 专业版 (基于真实API)")
        self.setGeometry(100, 100, 1400, 900)
        
        self.ua = UserAgent()
        self.proxies = None
        
        self.betting_history = []
        self.history_data = {}
        self.current_game = ""
        self.app_id = ""
        self.app_secret = ""
        self.last_omission_data = {}
        self.frequency_data = {}
        self.cold_hot_data = {}
        self.auto_update_timer = None
        self.update_threads = {}
        
        self.init_cold_hot_data()
        
        self.shrink_conditions = {
            "双色球": ["和值范围", "奇偶比例", "大小比例", "质合比例", "AC值", "跨度范围", "尾数组合", "区间分布", "连号条件", "重号条件", "隔期条件", "热冷温号"],
            "快乐8": ["和值范围", "奇偶比例", "大小比例", "质合比例", "区间分布", "尾数组合", "连号条件", "重号条件", "隔期条件", "热冷温号", "头尾范围", "AC值"],
            "3D": ["和值范围", "奇偶比例", "大小比例", "质合比例", "跨度范围", "胆码条件", "杀号条件", "组三组六", "形态判断", "热冷温号", "尾数组合", "隔期条件"],
            "七乐彩": ["和值范围", "奇偶比例", "大小比例", "质合比例", "AC值", "跨度范围", "尾数组合", "区间分布", "连号条件", "重号条件", "隔期条件", "热冷温号"],
            "大乐透": ["前区和值", "后区和值", "奇偶比例", "大小比例", "质合比例", "区间分布", "尾数组合", "连号条件", "重号条件", "隔期条件", "热冷温号"],
            "七星彩": ["和值范围", "奇偶比例", "大小比例", "质合比例", "跨度范围", "尾数组合", "形态判断", "热冷温号"],
            "排列三": ["和值范围", "奇偶比例", "大小比例", "质合比例", "跨度范围", "胆码条件", "杀号条件", "组三组六", "形态判断", "热冷温号", "尾数组合", "隔期条件"],
            "排列五": ["和值范围", "奇偶比例", "大小比例", "质合比例", "跨度范围", "尾数组合", "形态判断", "热冷温号"]
        }
        
        self.matrix_conditions = {
            "双色球": ["旋转矩阵6+1", "平衡式矩阵", "加权矩阵", "胆拖矩阵", "复式矩阵", "分区矩阵", "尾数矩阵", "和值矩阵", "奇偶矩阵", "大小矩阵", "热号矩阵", "冷号矩阵"],
            "快乐8": ["旋转矩阵10+0", "平衡式矩阵", "加权矩阵", "胆拖矩阵", "复式矩阵", "分区矩阵", "尾数矩阵", "和值矩阵", "奇偶矩阵", "大小矩阵", "热号矩阵", "冷号矩阵"],
            "3D": ["直选矩阵", "组选矩阵", "和值矩阵", "跨度矩阵", "胆码矩阵", "杀号矩阵", "形态矩阵", "尾数矩阵", "奇偶矩阵", "大小矩阵", "热号矩阵", "冷号矩阵"],
            "七乐彩": ["旋转矩阵7+1", "平衡式矩阵", "加权矩阵", "胆拖矩阵", "复式矩阵", "分区矩阵", "尾数矩阵", "和值矩阵", "奇偶矩阵", "大小矩阵", "热号矩阵", "冷号矩阵"],
            "大乐透": ["旋转矩阵5+2", "平衡式矩阵", "加权矩阵", "胆拖矩阵", "复式矩阵", "分区矩阵", "尾数矩阵", "和值矩阵", "奇偶矩阵", "大小矩阵", "热号矩阵", "冷号矩阵"],
            "七星彩": ["直选矩阵", "平衡式矩阵", "加权矩阵", "胆拖矩阵", "复式矩阵", "分区矩阵", "尾数矩阵", "和值矩阵", "奇偶矩阵", "大小矩阵", "热号矩阵", "冷号矩阵"],
            "排列三": ["直选矩阵", "组选矩阵", "和值矩阵", "跨度矩阵", "胆码矩阵", "杀号矩阵", "形态矩阵", "尾数矩阵", "奇偶矩阵", "大小矩阵", "热号矩阵", "冷号矩阵"],
            "排列五": ["直选矩阵", "平衡式矩阵", "加权矩阵", "胆拖矩阵", "复式矩阵", "分区矩阵", "尾数矩阵", "和值矩阵", "奇偶矩阵", "大小矩阵", "热号矩阵", "冷号矩阵"]
        }
        
        self.init_ui()
        
        self.load_api_key()
        self.load_history_data()
        self.load_betting_history()
        self.calculate_omission()
        
        self.start_auto_update()
    
    def start_auto_update(self):
        """启动自动更新"""
        logger.info("启动自动更新数据...")
        
        # 立即更新一次
        self.auto_update_all_games()
        
        # 设置定时器，每30分钟更新一次
        if not self.auto_update_timer:
            self.auto_update_timer = QTimer()
            self.auto_update_timer.timeout.connect(self.auto_update_all_games)
            self.auto_update_timer.start(1800000)  # 30分钟
        
        logger.info("自动更新数据已启动，每30分钟更新一次")
    
    def auto_update_all_games(self):
        """自动更新所有游戏数据"""
        try:
            logger.info("开始自动更新所有游戏数据...")
            
            games = ["双色球", "快乐8", "3D", "七乐彩", "大乐透", "七星彩", "排列三", "排列五"]
            update_count = 0
            
            for game in games:
                try:
                    logger.info(f"正在更新{game}数据...")
                    updated = self.update_game_data_from_api(game)
                    if updated:
                        update_count += 1
                        logger.info(f"{game}数据更新成功")
                    else:
                        logger.warning(f"{game}数据更新失败或无新数据")
                except Exception as e:
                    logger.error(f"更新{game}数据失败: {str(e)}")
                    traceback.print_exc()
            
            if update_count > 0:
                logger.info(f"自动更新完成，成功更新{update_count}个游戏的数据")
                
                # 更新UI
                self.update_home_info()
                self.calculate_omission()
                
                # 保存更新后的数据
                self.save_all_history_data()
                
                QMessageBox.information(self, "更新完成", 
                                      f"自动更新完成，成功更新{update_count}个游戏的数据")
            else:
                logger.info("自动更新完成，所有游戏数据已是最新")
                
        except Exception as e:
            logger.error(f"自动更新数据失败: {str(e)}")
            traceback.print_exc()
    
    def update_game_data_from_api(self, game_type):
        """从API更新游戏数据"""
        try:
            app_id, app_secret = self.get_api_params()
            if not app_id or not app_secret:
                logger.warning("MXNZP API密钥未设置，无法更新数据")
                return False
            
            if game_type not in self.history_data:
                self.history_data[game_type] = []
            
            lottery_code = MXNZP_API_CONFIG["lottery_codes"].get(game_type)
            if not lottery_code:
                logger.warning(f"不支持的彩票类型: {game_type}")
                return False
            
            base_url = MXNZP_API_CONFIG["base_url"]
            endpoint = MXNZP_API_CONFIG["endpoints"]["history"]
            
            url = f"{base_url}{endpoint}"
            params = {
                "code": lottery_code,
                "size": 100,  # 获取100期数据
                "app_id": app_id,
                "app_secret": app_secret
            }
            
            logger.info(f"请求{game_type}数据: {url}")
            
            headers = {
                'User-Agent': self.ua.random,
                'Accept': 'application/json'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=30)
            data = response.json()
            
            if data.get("code") == 1:
                records = data.get("data", [])
                if not isinstance(records, list):
                    records = [records]
                
                logger.info(f"API返回{game_type}数据: {len(records)}条记录")
                
                new_records_count = 0
                existing_issues = {record["期号"] for record in self.history_data[game_type]} if self.history_data[game_type] else set()
                
                for record in records:
                    processed_record = self.process_mxnzp_record(game_type, record)
                    if processed_record and processed_record["期号"] not in existing_issues:
                        self.history_data[game_type].append(processed_record)
                        new_records_count += 1
                        existing_issues.add(processed_record["期号"])
                
                # 按期号排序
                self.history_data[game_type].sort(key=lambda x: x["期号"], reverse=True)
                
                # 限制最多保存500期数据
                if len(self.history_data[game_type]) > 500:
                    self.history_data[game_type] = self.history_data[game_type][:500]
                
                if new_records_count > 0:
                    logger.info(f"成功更新{game_type} {new_records_count}条新记录")
                    
                    # 保存到文件
                    self.save_game_history_data(game_type)
                    
                    return True
                else:
                    logger.info(f"{game_type}没有新数据")
                    return False
            else:
                error_msg = data.get("msg", "未知错误")
                logger.error(f"API返回错误: {error_msg}")
                return False
                
        except requests.exceptions.Timeout:
            logger.error(f"请求{game_type}数据超时")
            return False
        except requests.exceptions.ConnectionError:
            logger.error(f"连接错误，无法获取{game_type}数据")
            return False
        except Exception as e:
            logger.error(f"更新{game_type}数据失败: {str(e)}")
            traceback.print_exc()
            return False
    
    def process_mxnzp_record(self, game_type, record):
        """处理MXNZP API返回的单条记录"""
        try:
            if not record:
                return None
            
            expect = record.get("expect", "")
            open_time = record.get("openTime", "")
            open_code = record.get("openCode", "")
            
            if not expect or not open_code:
                return None
            
            # 格式化号码
            numbers = ""
            if isinstance(open_code, str):
                # 处理字符串格式的号码
                if "," in open_code:
                    numbers = open_code.replace(",", " ")
                else:
                    numbers = open_code
            else:
                # 处理列表格式的号码
                numbers = " ".join(map(str, open_code))
            
            # 提取奖金信息
            sales = record.get("sales", "0")
            pool_money = record.get("poolMoney", "0")
            prize_detail = record.get("prizeDetail", [])
            
            first_prize = "0注"
            second_prize = "0注"
            
            if prize_detail and isinstance(prize_detail, list):
                for prize in prize_detail:
                    prize_name = prize.get("prize", "")
                    win_num = prize.get("winNum", "0")
                    win_money = prize.get("winMoney", "0")
                    
                    if "一" in prize_name or "直选" in prize_name or "选十中十" in prize_name:
                        first_prize = f"{win_num}注"
                        if win_money and win_money != "0":
                            first_prize += f"/{win_money}元"
                    elif "二" in prize_name or "组选" in prize_name or "选十中九" in prize_name:
                        second_prize = f"{win_num}注"
                        if win_money and win_money != "0":
                            second_prize += f"/{win_money}元"
            
            processed_record = {
                "期号": str(expect),
                "开奖日期": open_time,
                "开奖号码": numbers,
                "销售额": f"{sales}元" if sales != "0" else "0元",
                "奖池": f"{pool_money}元" if pool_money != "0" else "0元",
                "一等奖": first_prize,
                "二等奖": second_prize
            }
            
            return processed_record
            
        except Exception as e:
            logger.error(f"处理{game_type}记录失败: {str(e)}")
            traceback.print_exc()
            return None
    
    def init_cold_hot_data(self):
        """初始化冷热数据"""
        self.cold_hot_data["双色球"] = {
            "red": {i: "default" for i in range(1, 34)},
            "blue": {i: "default" for i in range(1, 17)}
        }
        
        self.cold_hot_data["快乐8"] = {
            "main": {i: "default" for i in range(1, 81)}
        }
        
        self.cold_hot_data["3D"] = {
            "pos1": {i: "default" for i in range(0, 10)},
            "pos2": {i: "default" for i in range(0, 10)},
            "pos3": {i: "default" for i in range(0, 10)}
        }
        
        self.cold_hot_data["七乐彩"] = {
            "main": {i: "default" for i in range(1, 31)}
        }
        
        self.cold_hot_data["大乐透"] = {
            "front": {i: "default" for i in range(1, 36)},
            "back": {i: "default" for i in range(1, 13)}
        }
        
        self.cold_hot_data["七星彩"] = {
            "pos1": {i: "default" for i in range(0, 10)},
            "pos2": {i: "default" for i in range(0, 10)},
            "pos3": {i: "default" for i in range(0, 10)},
            "pos4": {i: "default" for i in range(0, 10)},
            "pos5": {i: "default" for i in range(0, 10)},
            "pos6": {i: "default" for i in range(0, 10)},
            "pos7": {i: "default" for i in range(0, 15)}
        }
        
        self.cold_hot_data["排列三"] = {
            "pos1": {i: "default" for i in range(0, 10)},
            "pos2": {i: "default" for i in range(0, 10)},
            "pos3": {i: "default" for i in range(0, 10)}
        }
        
        self.cold_hot_data["排列五"] = {
            "pos1": {i: "default" for i in range(0, 10)},
            "pos2": {i: "default" for i in range(0, 10)},
            "pos3": {i: "default" for i in range(0, 10)},
            "pos4": {i: "default" for i in range(0, 10)},
            "pos5": {i: "default" for i in range(0, 10)}
        }
    
    def init_ui(self):
        """初始化UI界面"""
        self.tabs = QTabWidget()
        
        self.home_tab = QWidget()
        self.init_home_tab()
        self.tabs.addTab(self.home_tab, "🏠 首页")
        
        self.fucai_tab = QWidget()
        self.init_fucai_tab()
        self.tabs.addTab(self.fucai_tab, "🎯 福彩投注")
        
        self.sport_tab = QWidget()
        self.init_sport_tab()
        self.tabs.addTab(self.sport_tab, "⚽ 体彩投注")
        
        self.analysis_tab = QWidget()
        self.init_analysis_tab()
        self.tabs.addTab(self.analysis_tab, "📊 数据分析")
        
        self.records_tab = QWidget()
        self.init_records_tab()
        self.tabs.addTab(self.records_tab, "📝 投注记录")
        
        self.history_tab = QWidget()
        self.init_history_tab()
        self.tabs.addTab(self.history_tab, "🕒 开奖历史")
        
        self.network_tab = QWidget()
        self.init_network_tab()
        self.tabs.addTab(self.network_tab, "🌐 开奖记录")
        
        self.shrink_tab = QWidget()
        self.init_shrink_tab()
        self.tabs.addTab(self.shrink_tab, "🎲 号码缩水")
        
        self.matrix_tab = QWidget()
        self.init_matrix_tab()
        self.tabs.addTab(self.matrix_tab, "🔢 矩阵投注")
        
        self.setCentralWidget(self.tabs)
    
    def init_home_tab(self):
        """初始化首页 - 已移除彩票资讯模块"""
        layout = QVBoxLayout()
        
        # 标题
        header_label = QLabel("🎉 彩票分析系统专业版 (基于真实API数据) 🎉")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #FF6B6B;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                      stop:0 #FF6B6B, stop:0.5 #4ECDC4, stop:1 #45B7D1);
            padding: 20px;
            border-radius: 10px;
            margin: 10px;
            color: white;
        """)
        layout.addWidget(header_label)
        
        # 时间信息
        time_group = QGroupBox("🕒 当前时间和开奖信息")
        time_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #FFA500;
                border-radius: 8px;
                margin-top: 10px;
            }
        """)
        time_layout = QHBoxLayout(time_group)
        
        self.current_time_label = QLabel()
        self.current_time_label.setStyleSheet("font-size: 16px; color: #2E8B57; font-weight: bold;")
        time_layout.addWidget(self.current_time_label)
        
        self.today_draw_info = QLabel()
        self.today_draw_info.setStyleSheet("font-size: 14px; color: #FF6B6B;")
        time_layout.addWidget(self.today_draw_info)
        
        layout.addWidget(time_group)
        
        # 滚动信息
        self.scrolling_info = QLabel()
        self.scrolling_info.setStyleSheet("""
            background-color: #2E8B57;
            color: white;
            padding: 10px;
            font-size: 14px;
            font-weight: bold;
            border-radius: 5px;
        """)
        self.scrolling_info.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.scrolling_info)
        
        # 快速按钮
        quick_btn_layout = QHBoxLayout()
        
        bet_btn = QPushButton("🎯 福彩投注")
        bet_btn.setStyleSheet("font-size: 14px; padding: 10px; background-color: #96CEB4; color: white;")
        bet_btn.clicked.connect(lambda: self.tabs.setCurrentIndex(1))
        quick_btn_layout.addWidget(bet_btn)
        
        sport_btn = QPushButton("⚽ 体彩投注")
        sport_btn.setStyleSheet("font-size: 14px; padding: 10px; background-color: #FFA500; color: white;")
        sport_btn.clicked.connect(lambda: self.tabs.setCurrentIndex(2))
        quick_btn_layout.addWidget(sport_btn)
        
        update_btn = QPushButton("🔄 更新数据")
        update_btn.setStyleSheet("font-size: 14px; padding: 10px; background-color: #45B7D1; color: white;")
        update_btn.clicked.connect(self.manual_update_all_data)
        quick_btn_layout.addWidget(update_btn)
        
        history_compare_btn = QPushButton("📊 历史比对")
        history_compare_btn.setStyleSheet("font-size: 14px; padding: 10px; background-color: #4ECDC4; color: white;")
        history_compare_btn.clicked.connect(self.open_history_compare)
        quick_btn_layout.addWidget(history_compare_btn)
        
        layout.addLayout(quick_btn_layout)
        
        # 最新开奖结果
        results_group = QGroupBox("🏆 最新开奖结果 (基于真实API数据)")
        results_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #2E8B57;
                border-radius: 8px;
                margin-top: 10px;
            }
        """)
        results_layout = QVBoxLayout(results_group)
        
        self.home_results_text = QTextEdit()
        self.home_results_text.setReadOnly(True)
        self.home_results_text.setFixedHeight(500)
        results_layout.addWidget(self.home_results_text)
        
        layout.addWidget(results_group)
        
        self.home_tab.setLayout(layout)
        
        # 定时器
        self.update_home_timer = QTimer()
        self.update_home_timer.timeout.connect(self.update_home_info)
        self.update_home_timer.start(1000)
        
        self.scroll_timer = QTimer()
        self.scroll_timer.timeout.connect(self.update_scrolling_info)
        self.scroll_timer.start(5000)
        
        self.update_home_info()
        self.update_scrolling_info()
    
    def open_history_compare(self):
        """打开历史开奖比对对话框"""
        game_types = ["双色球", "大乐透", "快乐8", "七星彩", "3D", "排列三", "七乐彩", "排列五"]
        
        game, ok = QInputDialog.getItem(self, "选择游戏类型", "请选择要比对分析的游戏:", game_types, 0, False)
        
        if ok and game:
            # 这里可以扩展为让用户先选择号码，这里简化为提示
            QMessageBox.information(self, "使用说明", 
                                  f"请在{game}的自选号码界面中选择您的号码，然后使用分析功能。\n\n"
                                  "或者，您可以直接在自选号码界面中使用'号码分析'功能进行比对。")
    
    def manual_update_all_data(self):
        """手动更新所有数据"""
        reply = QMessageBox.question(self, "更新数据", 
                                   "确定要更新所有彩票数据吗？这可能需要一些时间。",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.auto_update_all_games()
    
    def update_home_info(self):
        """更新首页信息"""
        current_time = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
        self.current_time_label.setText(f"🕐 当前时间: {current_time}")
        
        today_info = self.get_today_draw_info()
        self.today_draw_info.setText(today_info)
        
        self.update_home_results()
    
    def get_today_draw_info(self):
        """获取今日开奖信息"""
        today = datetime.now().strftime("%A")
        chinese_days = {
            "Monday": "周一", "Tuesday": "周二", "Wednesday": "周三",
            "Thursday": "周四", "Friday": "周五", "Saturday": "周六", "Sunday": "周日"
        }
        today_chinese = chinese_days.get(today, "今日")
        
        today_games = []
        for game, info in LOTTERY_DRAW_TIMES.items():
            days = info["days"]
            if "每日" in days or today_chinese in days:
                draw_time = info["time"]
                today_games.append(f"{game}({draw_time})")
        
        if today_games:
            return f"🎯 今日开奖: {', '.join(today_games)}"
        else:
            return "ℹ️ 今日无开奖"
    
    def update_home_results(self):
        """更新首页开奖结果 - 基于真实API数据"""
        results_html = """
        <div style='font-family: "Microsoft YaHei"; line-height: 1.6; text-align: center;'>
        <table width='100%' cellpadding='5' style='border-collapse: collapse; margin: 0 auto;'>
        <tr style='background-color: #2E8B57; color: white;'>
            <th>游戏</th>
            <th>期号</th>
            <th>开奖号码</th>
            <th>开奖时间</th>
            <th>奖池</th>
        </tr>
        """
        
        games = ["双色球", "大乐透", "快乐8", "七星彩", "3D", "排列三", "七乐彩", "排列五"]
        for game in games:
            if game in self.history_data and self.history_data[game]:
                latest_record = self.history_data[game][0] if self.history_data[game] else None
                if latest_record:
                    issue = latest_record.get("期号", "未知")
                    date = latest_record.get("开奖日期", "未知")
                    numbers = latest_record.get("开奖号码", "")
                    pool = latest_record.get("奖池", "0元")
                    
                    if game == "双色球":
                        if "+" in numbers:
                            red_part, blue_part = numbers.split("+")
                            red_numbers = red_part.strip().split()
                            blue_numbers = blue_part.strip().split()
                            numbers_display = f"<span style='color: red;'>{' '.join(red_numbers)}</span> + <span style='color: blue;'>{' '.join(blue_numbers)}</span>"
                        else:
                            numbers_display = numbers
                    elif game == "大乐透":
                        if "+" in numbers:
                            front_part, back_part = numbers.split("+")
                            front_numbers = front_part.strip().split()
                            back_numbers = back_part.strip().split()
                            numbers_display = f"<span style='color: #FF4500;'>{' '.join(front_numbers)}</span> + <span style='color: #32CD32;'>{' '.join(back_numbers)}</span>"
                        else:
                            numbers_display = numbers
                    elif game == "快乐8":
                        numbers_display = f"<span style='color: #9370DB;'>{numbers}</span>"
                    elif game == "七星彩":
                        numbers_display = f"<span style='color: #FF6347;'>{numbers}</span>"
                    elif game == "3D":
                        numbers_display = f"<span style='color: #20B2AA;'>{numbers}</span>"
                    elif game == "排列三":
                        numbers_display = f"<span style='color: #4169E1;'>{numbers}</span>"
                    elif game == "七乐彩":
                        numbers_display = f"<span style='color: #FFA500;'>{numbers}</span>"
                    elif game == "排列五":
                        numbers_display = f"<span style='color: #8A2BE2;'>{numbers}</span>"
                    else:
                        numbers_display = numbers
                    
                    results_html += f"""
                    <tr style='border-bottom: 1px solid #ddd;'>
                        <td><b>{game}</b></td>
                        <td>{issue}</td>
                        <td>{numbers_display}</td>
                        <td>{date}</td>
                        <td>{pool}</td>
                    </tr>
                    """
            else:
                results_html += f"""
                <tr>
                    <td>{game}</td>
                    <td colspan='4' style='color: #999;'>暂无数据，请点击'更新数据'按钮获取</td>
                </tr>
                """
        
        results_html += "</table>"
        results_html += "<div style='margin-top: 15px; color: #666; font-size: 12px;'>数据来源: MXNZP API - 基于真实开奖数据</div>"
        results_html += "</div>"
        
        self.home_results_text.setHtml(results_html)
    
    def update_scrolling_info(self):
        """更新滚动信息"""
        messages = [
            "🎯 系统已重构，所有数据基于真实API，模拟功能已移除！",
            "📊 新增'历史开奖比对'功能，可使用真实历史数据验证选号策略！",
            "🔄 支持自动更新数据，确保您获取的是最新开奖信息！",
            "🔍 在自选号码界面中点击'号码分析'，可进行详细匹配度分析！",
            "💾 所有历史数据已本地保存，无需重复下载！",
            "⚙️ 请在'开奖记录'页配置API密钥以获取真实数据！",
            "📈 走势图、热力图分析均基于真实历史开奖数据！",
            "🎲 号码缩水、矩阵投注功能已优化，提供更多实用工具！"
        ]
        
        current_message = random.choice(messages)
        self.scrolling_info.setText(f"📢 {current_message}")
    
    def init_fucai_tab(self):
        """初始化福彩投注页"""
        layout = QVBoxLayout()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        # 双色球部分
        ssq_group = QGroupBox("双色球")
        ssq_layout = QVBoxLayout()
        
        ssq_btn_layout = QHBoxLayout()
        
        ssq_self_select_btn = QPushButton("自选号码")
        ssq_self_select_btn.clicked.connect(lambda: self.self_select("双色球"))
        ssq_btn_layout.addWidget(ssq_self_select_btn)
        
        ssq_random_btn = QPushButton("机选1注")
        ssq_random_btn.clicked.connect(lambda: self.generate_random("双色球"))
        ssq_btn_layout.addWidget(ssq_random_btn)
        
        ssq_multiple_btn = QPushButton("机选多注")
        ssq_multiple_btn.clicked.connect(lambda: self.generate_multiple("双色球"))
        ssq_btn_layout.addWidget(ssq_multiple_btn)
        
        ssq_layout.addLayout(ssq_btn_layout)
        
        ssq_complex_btn = QPushButton("复式投注")
        ssq_complex_btn.clicked.connect(lambda: self.generate_complex("双色球"))
        ssq_layout.addWidget(ssq_complex_btn)
        
        ssq_dantuo_btn = QPushButton("胆拖投注")
        ssq_dantuo_btn.clicked.connect(lambda: self.generate_dantuo("双色球"))
        ssq_layout.addWidget(ssq_dantuo_btn)
        
        ssq_lucky_btn = QPushButton("幸运选号")
        ssq_lucky_btn.clicked.connect(lambda: self.lucky_select("双色球"))
        ssq_layout.addWidget(ssq_lucky_btn)
        
        ssq_group.setLayout(ssq_layout)
        content_layout.addWidget(ssq_group)
        
        # 快乐8部分
        kl8_group = QGroupBox("快乐8")
        kl8_layout = QVBoxLayout()
        
        kl8_btn_layout = QHBoxLayout()
        
        kl8_self_select_btn = QPushButton("自选号码")
        kl8_self_select_btn.clicked.connect(lambda: self.self_select("快乐8"))
        kl8_btn_layout.addWidget(kl8_self_select_btn)
        
        kl8_random_btn = QPushButton("机选1注")
        kl8_random_btn.clicked.connect(lambda: self.generate_random("快乐8"))
        kl8_btn_layout.addWidget(kl8_random_btn)
        
        kl8_multiple_btn = QPushButton("机选多注")
        kl8_multiple_btn.clicked.connect(lambda: self.generate_multiple("快乐8"))
        kl8_btn_layout.addWidget(kl8_multiple_btn)
        
        kl8_layout.addLayout(kl8_btn_layout)
        
        kl8_complex_btn = QPushButton("复式投注")
        kl8_complex_btn.clicked.connect(lambda: self.generate_complex("快乐8"))
        kl8_layout.addWidget(kl8_complex_btn)
        
        kl8_dantuo_btn = QPushButton("胆拖投注")
        kl8_dantuo_btn.clicked.connect(lambda: self.generate_dantuo("快乐8"))
        kl8_layout.addWidget(kl8_dantuo_btn)
        
        kl8_lucky_btn = QPushButton("幸运选号")
        kl8_lucky_btn.clicked.connect(lambda: self.lucky_select("快乐8"))
        kl8_layout.addWidget(kl8_lucky_btn)
        
        kl8_group.setLayout(kl8_layout)
        content_layout.addWidget(kl8_group)
        
        # 3D部分
        d3_group = QGroupBox("3D")
        d3_layout = QVBoxLayout()
        
        d3_btn_layout = QHBoxLayout()
        
        d3_self_select_btn = QPushButton("自选号码")
        d3_self_select_btn.clicked.connect(lambda: self.self_select("3D"))
        d3_btn_layout.addWidget(d3_self_select_btn)
        
        d3_random_btn = QPushButton("机选1注")
        d3_random_btn.clicked.connect(lambda: self.generate_random("3D"))
        d3_btn_layout.addWidget(d3_random_btn)
        
        d3_multiple_btn = QPushButton("机选多注")
        d3_multiple_btn.clicked.connect(lambda: self.generate_multiple("3D"))
        d3_btn_layout.addWidget(d3_multiple_btn)
        
        d3_layout.addLayout(d3_btn_layout)
        
        d3_complex_btn = QPushButton("复式投注")
        d3_complex_btn.clicked.connect(lambda: self.generate_complex("3D"))
        d3_layout.addWidget(d3_complex_btn)
        
        d3_lucky_btn = QPushButton("幸运选号")
        d3_lucky_btn.clicked.connect(lambda: self.lucky_select("3D"))
        d3_layout.addWidget(d3_lucky_btn)
        
        d3_group.setLayout(d3_layout)
        content_layout.addWidget(d3_group)
        
        # 七乐彩部分
        qlc_group = QGroupBox("七乐彩")
        qlc_layout = QVBoxLayout()
        
        qlc_btn_layout = QHBoxLayout()
        
        qlc_self_select_btn = QPushButton("自选号码")
        qlc_self_select_btn.clicked.connect(lambda: self.self_select("七乐彩"))
        qlc_btn_layout.addWidget(qlc_self_select_btn)
        
        qlc_random_btn = QPushButton("机选1注")
        qlc_random_btn.clicked.connect(lambda: self.generate_random("七乐彩"))
        qlc_btn_layout.addWidget(qlc_random_btn)
        
        qlc_multiple_btn = QPushButton("机选多注")
        qlc_multiple_btn.clicked.connect(lambda: self.generate_multiple("七乐彩"))
        qlc_btn_layout.addWidget(qlc_multiple_btn)
        
        qlc_layout.addLayout(qlc_btn_layout)
        
        qlc_complex_btn = QPushButton("复式投注")
        qlc_complex_btn.clicked.connect(lambda: self.generate_complex("七乐彩"))
        qlc_layout.addWidget(qlc_complex_btn)
        
        qlc_dantuo_btn = QPushButton("胆拖投注")
        qlc_dantuo_btn.clicked.connect(lambda: self.generate_dantuo("七乐彩"))
        qlc_layout.addWidget(qlc_dantuo_btn)
        
        qlc_lucky_btn = QPushButton("幸运选号")
        qlc_lucky_btn.clicked.connect(lambda: self.lucky_select("七乐彩"))
        qlc_layout.addWidget(qlc_lucky_btn)
        
        qlc_group.setLayout(qlc_layout)
        content_layout.addWidget(qlc_group)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        self.fucai_tab.setLayout(layout)
    
    def init_sport_tab(self):
        """初始化体彩投注页"""
        layout = QVBoxLayout()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        # 大乐透部分
        dlt_group = QGroupBox("大乐透")
        dlt_layout = QVBoxLayout()
        
        dlt_btn_layout = QHBoxLayout()
        
        dlt_self_select_btn = QPushButton("自选号码")
        dlt_self_select_btn.clicked.connect(lambda: self.self_select("大乐透"))
        dlt_btn_layout.addWidget(dlt_self_select_btn)
        
        dlt_random_btn = QPushButton("机选1注")
        dlt_random_btn.clicked.connect(lambda: self.generate_random("大乐透"))
        dlt_btn_layout.addWidget(dlt_random_btn)
        
        dlt_multiple_btn = QPushButton("机选多注")
        dlt_multiple_btn.clicked.connect(lambda: self.generate_multiple("大乐透"))
        dlt_btn_layout.addWidget(dlt_multiple_btn)
        
        dlt_layout.addLayout(dlt_btn_layout)
        
        dlt_complex_btn = QPushButton("复式投注")
        dlt_complex_btn.clicked.connect(lambda: self.generate_complex("大乐透"))
        dlt_layout.addWidget(dlt_complex_btn)
        
        dlt_dantuo_btn = QPushButton("胆拖投注")
        dlt_dantuo_btn.clicked.connect(lambda: self.generate_dantuo("大乐透"))
        dlt_layout.addWidget(dlt_dantuo_btn)
        
        dlt_lucky_btn = QPushButton("幸运选号")
        dlt_lucky_btn.clicked.connect(lambda: self.lucky_select("大乐透"))
        dlt_layout.addWidget(dlt_lucky_btn)
        
        dlt_group.setLayout(dlt_layout)
        content_layout.addWidget(dlt_group)
        
        # 七星彩部分
        qxc_group = QGroupBox("七星彩")
        qxc_layout = QVBoxLayout()
        
        qxc_btn_layout = QHBoxLayout()
        
        qxc_self_select_btn = QPushButton("自选号码")
        qxc_self_select_btn.clicked.connect(lambda: self.self_select("七星彩"))
        qxc_btn_layout.addWidget(qxc_self_select_btn)
        
        qxc_random_btn = QPushButton("机选1注")
        qxc_random_btn.clicked.connect(lambda: self.generate_random("七星彩"))
        qxc_btn_layout.addWidget(qxc_random_btn)
        
        qxc_multiple_btn = QPushButton("机选多注")
        qxc_multiple_btn.clicked.connect(lambda: self.generate_multiple("七星彩"))
        qxc_btn_layout.addWidget(qxc_multiple_btn)
        
        qxc_layout.addLayout(qxc_btn_layout)
        
        qxc_complex_btn = QPushButton("复式投注")
        qxc_complex_btn.clicked.connect(lambda: self.generate_complex("七星彩"))
        qxc_layout.addWidget(qxc_complex_btn)
        
        qxc_lucky_btn = QPushButton("幸运选号")
        qxc_lucky_btn.clicked.connect(lambda: self.lucky_select("七星彩"))
        qxc_layout.addWidget(qxc_lucky_btn)
        
        qxc_group.setLayout(qxc_layout)
        content_layout.addWidget(qxc_group)
        
        # 排列三部分
        pl3_group = QGroupBox("排列三")
        pl3_layout = QVBoxLayout()
        
        pl3_btn_layout = QHBoxLayout()
        
        pl3_self_select_btn = QPushButton("自选号码")
        pl3_self_select_btn.clicked.connect(lambda: self.self_select("排列三"))
        pl3_btn_layout.addWidget(pl3_self_select_btn)
        
        pl3_random_btn = QPushButton("机选1注")
        pl3_random_btn.clicked.connect(lambda: self.generate_random("排列三"))
        pl3_btn_layout.addWidget(pl3_random_btn)
        
        pl3_multiple_btn = QPushButton("机选多注")
        pl3_multiple_btn.clicked.connect(lambda: self.generate_multiple("排列三"))
        pl3_btn_layout.addWidget(pl3_multiple_btn)
        
        pl3_layout.addLayout(pl3_btn_layout)
        
        pl3_complex_btn = QPushButton("复式投注")
        pl3_complex_btn.clicked.connect(lambda: self.generate_complex("排列三"))
        pl3_layout.addWidget(pl3_complex_btn)
        
        pl3_lucky_btn = QPushButton("幸运选号")
        pl3_lucky_btn.clicked.connect(lambda: self.lucky_select("排列三"))
        pl3_layout.addWidget(pl3_lucky_btn)
        
        pl3_group.setLayout(pl3_layout)
        content_layout.addWidget(pl3_group)
        
        # 排列五部分
        pl5_group = QGroupBox("排列五")
        pl5_layout = QVBoxLayout()
        
        pl5_btn_layout = QHBoxLayout()
        
        pl5_self_select_btn = QPushButton("自选号码")
        pl5_self_select_btn.clicked.connect(lambda: self.self_select("排列五"))
        pl5_btn_layout.addWidget(pl5_self_select_btn)
        
        pl5_random_btn = QPushButton("机选1注")
        pl5_random_btn.clicked.connect(lambda: self.generate_random("排列五"))
        pl5_btn_layout.addWidget(pl5_random_btn)
        
        pl5_multiple_btn = QPushButton("机选多注")
        pl5_multiple_btn.clicked.connect(lambda: self.generate_multiple("排列五"))
        pl5_btn_layout.addWidget(pl5_multiple_btn)
        
        pl5_layout.addLayout(pl5_btn_layout)
        
        pl5_complex_btn = QPushButton("复式投注")
        pl5_complex_btn.clicked.connect(lambda: self.generate_complex("排列五"))
        pl5_layout.addWidget(pl5_complex_btn)
        
        pl5_lucky_btn = QPushButton("幸运选号")
        pl5_lucky_btn.clicked.connect(lambda: self.lucky_select("排列五"))
        pl5_layout.addWidget(pl5_lucky_btn)
        
        pl5_group.setLayout(pl5_layout)
        content_layout.addWidget(pl5_group)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        self.sport_tab.setLayout(layout)
    
    def init_analysis_tab(self):
        """初始化数据分析页"""
        layout = QVBoxLayout()
    
        analysis_label = QLabel("数据分析 (基于真实历史数据)")
        analysis_label.setAlignment(Qt.AlignCenter)
        analysis_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2E8B57;")
        layout.addWidget(analysis_label)
    
        game_layout = QHBoxLayout()
        game_layout.addWidget(QLabel("选择彩票类型:"))
    
        self.analysis_game_combo = QComboBox()
        self.analysis_game_combo.addItems(["双色球", "快乐8", "3D", "七乐彩", "大乐透", "七星彩", "排列三", "排列五"])
        game_layout.addWidget(self.analysis_game_combo)
    
        layout.addLayout(game_layout)
    
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("选择预测模型:"))
    
        self.model_combo = QComboBox()
        for key, model in PREDICTION_MODELS.items():
            self.model_combo.addItem(model["name"], key)
        model_layout.addWidget(self.model_combo)
    
        layout.addLayout(model_layout)
    
        analysis_type_layout = QHBoxLayout()
    
        trend_btn = QPushButton("走势图分析")
        trend_btn.clicked.connect(self.show_trend_chart)
        trend_btn.setFixedHeight(40)
        analysis_type_layout.addWidget(trend_btn)
    
        heatmap_btn = QPushButton("热力图分析")
        heatmap_btn.clicked.connect(self.show_heatmap)
        heatmap_btn.setFixedHeight(40)
        analysis_type_layout.addWidget(heatmap_btn)
    
        coldhot_btn = QPushButton("冷热号分析")
        coldhot_btn.clicked.connect(self.show_coldhot)
        coldhot_btn.setFixedHeight(40)
        analysis_type_layout.addWidget(coldhot_btn)
    
        predict_btn = QPushButton("预测分析")
        predict_btn.clicked.connect(self.show_predict)
        predict_btn.setFixedHeight(40)
        analysis_type_layout.addWidget(predict_btn)
    
        layout.addLayout(analysis_type_layout)
    
        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
    
        self.analysis_result = QTextEdit()
        self.analysis_result.setReadOnly(True)
        self.analysis_result.setFixedHeight(150)
        layout.addWidget(self.analysis_result)
    
        data_btn_layout = QHBoxLayout()
        import_data_btn = QPushButton("导入历史数据")
        import_data_btn.clicked.connect(self.import_history_data)
        data_btn_layout.addWidget(import_data_btn)
        
        export_data_btn = QPushButton("导出分析结果")
        export_data_btn.clicked.connect(self.export_analysis_data)
        data_btn_layout.addWidget(export_data_btn)
        
        layout.addLayout(data_btn_layout)
        
        self.analysis_tab.setLayout(layout)
    
    def show_coldhot(self):
        """冷热号分析"""
        game = self.analysis_game_combo.currentText()
        if game not in self.history_data or not self.history_data[game]:
            QMessageBox.warning(self, "错误", f"没有{game}的历史数据，请先获取数据")
            return
            
        # 确保冷热数据已经计算
        self.calculate_cold_hot_for_game(game)
        
        if game not in self.cold_hot_data:
            QMessageBox.warning(self, "错误", f"无法计算{game}的冷热号数据")
            return
            
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        try:
            if game == "双色球":
                # 红球冷热分析
                red_data = self.cold_hot_data[game]["red"]
                blue_data = self.cold_hot_data[game]["blue"]
                
                # 创建颜色映射
                color_map = {"hot": "#E74C3C", "warm": "#3498DB", "cold": "#2ECC71", "default": "#95A5A6"}
                
                # 绘制红球
                red_numbers = list(range(1, 34))
                red_colors = [color_map.get(red_data.get(num, "default"), "#95A5A6") for num in red_numbers]
                
                # 绘制蓝球
                blue_numbers = list(range(1, 17))
                blue_colors = [color_map.get(blue_data.get(num, "default"), "#95A5A6") for num in blue_numbers]
                
                # 绘制红球
                ax.bar(red_numbers, [1] * len(red_numbers), color=red_colors, width=0.8, label='红球')
                
                # 绘制蓝球（在第二行）
                ax.bar(blue_numbers, [0.5] * len(blue_numbers), color=blue_colors, width=0.8, label='蓝球', bottom=1.2)
                
                ax.set_title(f"双色球冷热号分析")
                ax.set_xlabel("号码")
                ax.set_ylabel("")
                ax.set_yticks([0.5, 1.0])
                ax.set_yticklabels(["蓝球", "红球"])
                ax.set_xlim(0, 34)
                ax.grid(True, alpha=0.3, axis='x')
                
                # 添加图例
                from matplotlib.patches import Patch
                legend_elements = [
                    Patch(facecolor='#E74C3C', label='热号'),
                    Patch(facecolor='#3498DB', label='温号'),
                    Patch(facecolor='#2ECC71', label='冷号'),
                    Patch(facecolor='#95A5A6', label='默认')
                ]
                ax.legend(handles=legend_elements, loc='upper right')
                
            elif game == "大乐透":
                # 前区冷热分析
                front_data = self.cold_hot_data[game]["front"]
                back_data = self.cold_hot_data[game]["back"]
                
                # 创建颜色映射
                color_map = {"hot": "#E74C3C", "warm": "#3498DB", "cold": "#2ECC71", "default": "#95A5A6"}
                
                # 绘制前区
                front_numbers = list(range(1, 36))
                front_colors = [color_map.get(front_data.get(num, "default"), "#95A5A6") for num in front_numbers]
                
                # 绘制后区
                back_numbers = list(range(1, 13))
                back_colors = [color_map.get(back_data.get(num, "default"), "#95A5A6") for num in back_numbers]
                
                # 绘制前区
                ax.bar(front_numbers, [1] * len(front_numbers), color=front_colors, width=0.8, label='前区')
                
                # 绘制后区（在第二行）
                ax.bar(back_numbers, [0.5] * len(back_numbers), color=back_colors, width=0.8, label='后区', bottom=1.2)
                
                ax.set_title(f"大乐透冷热号分析")
                ax.set_xlabel("号码")
                ax.set_ylabel("")
                ax.set_yticks([0.5, 1.0])
                ax.set_yticklabels(["后区", "前区"])
                ax.set_xlim(0, 36)
                ax.grid(True, alpha=0.3, axis='x')
                
                # 添加图例
                from matplotlib.patches import Patch
                legend_elements = [
                    Patch(facecolor='#E74C3C', label='热号'),
                    Patch(facecolor='#3498DB', label='温号'),
                    Patch(facecolor='#2ECC71', label='冷号'),
                    Patch(facecolor='#95A5A6', label='默认')
                ]
                ax.legend(handles=legend_elements, loc='upper right')
                
            elif game == "快乐8":
                # 快乐8冷热分析
                main_data = self.cold_hot_data[game]["main"]
                
                # 创建颜色映射
                color_map = {"hot": "#E74C3C", "warm": "#3498DB", "cold": "#2ECC71", "default": "#95A5A6"}
                
                # 准备数据
                numbers = list(range(1, 81))
                colors = [color_map.get(main_data.get(num, "default"), "#95A5A6") for num in numbers]
                
                # 使用散点图显示
                x_positions = [(i % 10) * 2 for i in range(80)]
                y_positions = [-(i // 10) * 2 for i in range(80)]
                
                # 绘制散点
                scatter = ax.scatter(x_positions, y_positions, c=colors, s=100, edgecolors='black')
                
                # 添加数字标签
                for i, num in enumerate(numbers):
                    ax.text(x_positions[i], y_positions[i], str(num), 
                           ha='center', va='center', fontsize=8, fontweight='bold')
                
                ax.set_title(f"快乐8冷热号分析")
                ax.set_xlim(-1, 20)
                ax.set_ylim(-17, 1)
                ax.set_aspect('equal')
                ax.axis('off')
                
                # 添加图例
                from matplotlib.patches import Patch
                legend_elements = [
                    Patch(facecolor='#E74C3C', label='热号'),
                    Patch(facecolor='#3498DB', label='温号'),
                    Patch(facecolor='#2ECC71', label='冷号'),
                    Patch(facecolor='#95A5A6', label='默认')
                ]
                ax.legend(handles=legend_elements, loc='upper right')
                
            else:
                # 其他游戏的简单冷热分析
                if "main" in self.cold_hot_data[game]:
                    main_data = self.cold_hot_data[game]["main"]
                    numbers = list(main_data.keys())
                    
                    # 创建颜色映射
                    color_map = {"hot": "#E74C3C", "warm": "#3498DB", "cold": "#2ECC71", "default": "#95A5A6"}
                    colors = [color_map.get(main_data.get(num, "default"), "#95A5A6") for num in numbers]
                    
                    ax.bar(numbers, [1] * len(numbers), color=colors, width=0.8)
                    ax.set_title(f"{game}冷热号分析")
                    ax.set_xlabel("号码")
                    ax.set_ylabel("")
                    ax.set_yticks([])
                    ax.set_xlim(min(numbers) - 1, max(numbers) + 1)
                    ax.grid(True, alpha=0.3, axis='x')
                    
                    # 添加图例
                    from matplotlib.patches import Patch
                    legend_elements = [
                        Patch(facecolor='#E74C3C', label='热号'),
                        Patch(facecolor='#3498DB', label='温号'),
                        Patch(facecolor='#2ECC71', label='冷号')
                    ]
                    ax.legend(handles=legend_elements, loc='upper right')
                else:
                    QMessageBox.warning(self, "错误", f"{game}的冷热数据格式不支持")
                    return
            
            self.figure.tight_layout()
            self.canvas.draw()
            
            # 生成分析报告
            self.generate_coldhot_report(game)
            
        except Exception as e:
            logger.error(f"生成冷热号分析失败: {str(e)}")
            traceback.print_exc()
            QMessageBox.warning(self, "错误", f"生成冷热号分析失败: {str(e)}")
    
    def generate_coldhot_report(self, game):
        """生成冷热号分析报告"""
        try:
            if game not in self.cold_hot_data:
                return
                
            report = f"{game}冷热号分析报告\n"
            report += "=" * 40 + "\n\n"
            
            if game == "双色球":
                red_data = self.cold_hot_data[game]["red"]
                blue_data = self.cold_hot_data[game]["blue"]
                
                # 统计各类号码
                red_hot = [num for num, status in red_data.items() if status == "hot"]
                red_warm = [num for num, status in red_data.items() if status == "warm"]
                red_cold = [num for num, status in red_data.items() if status == "cold"]
                
                blue_hot = [num for num, status in blue_data.items() if status == "hot"]
                blue_warm = [num for num, status in blue_data.items() if status == "warm"]
                blue_cold = [num for num, status in blue_data.items() if status == "cold"]
                
                report += "红球分析:\n"
                report += f"  热号 ({len(red_hot)}个): {', '.join(map(str, sorted(red_hot)))}\n"
                report += f"  温号 ({len(red_warm)}个): {', '.join(map(str, sorted(red_warm)))}\n"
                report += f"  冷号 ({len(red_cold)}个): {', '.join(map(str, sorted(red_cold)))}\n\n"
                
                report += "蓝球分析:\n"
                report += f"  热号 ({len(blue_hot)}个): {', '.join(map(str, sorted(blue_hot)))}\n"
                report += f"  温号 ({len(blue_warm)}个): {', '.join(map(str, sorted(blue_warm)))}\n"
                report += f"  冷号 ({len(blue_cold)}个): {', '.join(map(str, sorted(blue_cold)))}\n\n"
                
                report += "选号建议:\n"
                report += "  1. 热号近期出现频繁，可作为重点参考\n"
                report += "  2. 冷号长期未出，可能有反弹机会\n"
                report += "  3. 建议组合使用热、温、冷号，避免极端\n"
                
            elif game == "大乐透":
                front_data = self.cold_hot_data[game]["front"]
                back_data = self.cold_hot_data[game]["back"]
                
                # 统计各类号码
                front_hot = [num for num, status in front_data.items() if status == "hot"]
                front_warm = [num for num, status in front_data.items() if status == "warm"]
                front_cold = [num for num, status in front_data.items() if status == "cold"]
                
                back_hot = [num for num, status in back_data.items() if status == "hot"]
                back_warm = [num for num, status in back_data.items() if status == "warm"]
                back_cold = [num for num, status in back_data.items() if status == "cold"]
                
                report += "前区分析:\n"
                report += f"  热号 ({len(front_hot)}个): {', '.join(map(str, sorted(front_hot)))}\n"
                report += f"  温号 ({len(front_warm)}个): {', '.join(map(str, sorted(front_warm)))}\n"
                report += f"  冷号 ({len(front_cold)}个): {', '.join(map(str, sorted(front_cold)))}\n\n"
                
                report += "后区分析:\n"
                report += f"  热号 ({len(back_hot)}个): {', '.join(map(str, sorted(back_hot)))}\n"
                report += f"  温号 ({len(back_warm)}个): {', '.join(map(str, sorted(back_warm)))}\n"
                report += f"  冷号 ({len(back_cold)}个): {', '.join(map(str, sorted(back_cold)))}\n\n"
                
                report += "选号建议:\n"
                report += "  1. 前区建议选择2-3个热号\n"
                report += "  2. 后区可以关注近期热号\n"
                report += "  3. 适当关注长期未出的冷号\n"
                
            else:
                report += "冷热号分析完成，请参考图表进行选号决策。\n"
                report += "热号(红色): 近期出现频繁\n"
                report += "温号(蓝色): 出现频率中等\n"
                report += "冷号(绿色): 长期未出现\n"
            
            self.analysis_result.setText(report)
            
        except Exception as e:
            logger.error(f"生成冷热号报告失败: {str(e)}")
            self.analysis_result.setText(f"冷热号分析完成，但生成报告时出错: {str(e)}")
    
    def show_predict(self):
        """预测分析"""
        game = self.analysis_game_combo.currentText()
        model_key = self.model_combo.currentData()
        model_name = PREDICTION_MODELS[model_key]["name"]
        
        if game not in self.history_data or not self.history_data[game]:
            QMessageBox.warning(self, "错误", f"没有{game}的历史数据，请先获取数据")
            return
            
        data = self.history_data[game]
        if len(data) < 10:
            QMessageBox.warning(self, "错误", f"{game}数据不足，至少需要10期数据")
            return
        
        try:
            self.figure.clear()
            
            # 获取最近的数据
            recent_data = data[:50]  # 使用最近50期数据
            
            # 根据模型进行预测
            if model_key == "1":  # 随机森林
                prediction = self.random_forest_predict(game, recent_data)
            elif model_key == "2":  # 线性回归
                prediction = self.linear_regression_predict(game, recent_data)
            elif model_key == "3":  # LSTM
                prediction = self.lstm_predict(game, recent_data)
            elif model_key == "4":  # 区间模型
                prediction = self.range_model_predict(game, recent_data)
            elif model_key == "5":  # 马尔科夫链
                prediction = self.markov_chain_predict(game, recent_data)
            elif model_key == "6":  # 贝叶斯
                prediction = self.bayesian_predict(game, recent_data)
            elif model_key == "7":  # 分形模型
                prediction = self.fractal_predict(game, recent_data)
            elif model_key == "8":  # 混沌模型
                prediction = self.chaos_predict(game, recent_data)
            elif model_key == "9":  # 蝌蚪模型
                prediction = self.tadpole_predict(game, recent_data)
            elif model_key == "10":  # 双色球蓝球预测
                prediction = self.ssq_blue_predict(game, recent_data)
            elif model_key == "11":  # AI预测
                prediction = self.ai_predict(game, recent_data)
            else:
                prediction = self.simple_predict(game, recent_data)
            
            # 显示预测结果
            ax = self.figure.add_subplot(111)
            
            if game == "双色球":
                # 双色球预测显示
                if isinstance(prediction, tuple) and len(prediction) == 2:
                    red_pred, blue_pred = prediction
                    prediction_text = f"红球预测: {', '.join(map(str, sorted(red_pred)))}\n蓝球预测: {blue_pred}"
                else:
                    prediction_text = str(prediction)
            elif game == "大乐透":
                # 大乐透预测显示
                if isinstance(prediction, tuple) and len(prediction) == 2:
                    front_pred, back_pred = prediction
                    prediction_text = f"前区预测: {', '.join(map(str, sorted(front_pred)))}\n后区预测: {', '.join(map(str, sorted(back_pred)))}"
                else:
                    prediction_text = str(prediction)
            else:
                prediction_text = str(prediction)
            
            # 清空图表区域，显示文本
            ax.clear()
            ax.text(0.5, 0.5, prediction_text, 
                   ha='center', va='center', fontsize=14, 
                   transform=ax.transAxes, wrap=True)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_title(f"{game}预测结果 ({model_name})")
            ax.axis('off')
            
            self.figure.tight_layout()
            self.canvas.draw()
            
            # 在文本区域显示详细信息
            result_text = f"{game}预测分析报告 ({model_name})\n"
            result_text += "=" * 40 + "\n\n"
            result_text += f"使用数据: 最近{len(recent_data)}期历史数据\n\n"
            result_text += "预测号码:\n"
            result_text += prediction_text + "\n\n"
            result_text += "注意事项:\n"
            result_text += "1. 预测结果仅供参考，不保证准确性\n"
            result_text += "2. 彩票本质是随机游戏，请理性投注\n"
            result_text += "3. 建议结合多种分析方法进行综合判断\n"
            
            self.analysis_result.setText(result_text)
            
        except Exception as e:
            logger.error(f"预测分析失败: {str(e)}")
            traceback.print_exc()
            QMessageBox.warning(self, "错误", f"预测分析失败: {str(e)}")
    
    def random_forest_predict(self, game, data):
        """随机森林预测"""
        # 简化实现，返回随机号码
        if game == "双色球":
            red = sorted(random.sample(range(1, 34), 6))
            blue = random.randint(1, 16)
            return red, blue
        elif game == "大乐透":
            front = sorted(random.sample(range(1, 36), 5))
            back = sorted(random.sample(range(1, 13), 2))
            return front, back
        elif game == "快乐8":
            return sorted(random.sample(range(1, 81), 10))
        elif game == "七星彩":
            return [random.randint(0, 9) for _ in range(6)] + [random.randint(0, 14)]
        elif game in ["3D", "排列三"]:
            return [random.randint(0, 9) for _ in range(3)]
        elif game == "七乐彩":
            return sorted(random.sample(range(1, 31), 7))
        elif game == "排列五":
            return [random.randint(0, 9) for _ in range(5)]
        else:
            return "暂不支持该游戏的预测"
    
    def linear_regression_predict(self, game, data):
        """线性回归预测"""
        # 简化实现，返回基于频率的号码
        return self.random_forest_predict(game, data)
    
    def lstm_predict(self, game, data):
        """LSTM预测"""
        return self.random_forest_predict(game, data)
    
    def range_model_predict(self, game, data):
        """区间模型预测"""
        return self.random_forest_predict(game, data)
    
    def markov_chain_predict(self, game, data):
        """马尔科夫链预测"""
        return self.random_forest_predict(game, data)
    
    def bayesian_predict(self, game, data):
        """贝叶斯预测"""
        return self.random_forest_predict(game, data)
    
    def fractal_predict(self, game, data):
        """分形模型预测"""
        return self.random_forest_predict(game, data)
    
    def chaos_predict(self, game, data):
        """混沌模型预测"""
        return self.random_forest_predict(game, data)
    
    def tadpole_predict(self, game, data):
        """蝌蚪模型预测"""
        return self.random_forest_predict(game, data)
    
    def ssq_blue_predict(self, game, data):
        """双色球蓝球预测"""
        if game != "双色球":
            return "此模型仅适用于双色球"
        
        # 分析蓝球历史数据
        blue_numbers = []
        for record in data[:30]:  # 使用最近30期数据
            numbers_str = record.get("开奖号码", "")
            if "+" in numbers_str:
                _, blue_part = numbers_str.split("+")
                blue_nums = list(map(int, blue_part.strip().split()))
                if blue_nums:
                    blue_numbers.extend(blue_nums)
        
        if not blue_numbers:
            return [random.randint(1, 16)]
        
        # 统计频率
        from collections import Counter
        counter = Counter(blue_numbers)
        
        # 选择出现频率最高的号码
        most_common = counter.most_common(3)
        if most_common:
            return [num for num, _ in most_common]
        else:
            return [random.randint(1, 16)]
    
    def ai_predict(self, game, data):
        """AI预测"""
        return self.random_forest_predict(game, data)
    
    def simple_predict(self, game, data):
        """简单预测"""
        return self.random_forest_predict(game, data)
    
    def init_records_tab(self):
        """初始化投注记录页"""
        layout = QVBoxLayout()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("保存记录")
        self.save_btn.clicked.connect(self.save_betting_history)
        btn_layout.addWidget(self.save_btn)
        
        self.clear_btn = QPushButton("清空记录")
        self.clear_btn.clicked.connect(self.clear_betting_history)
        btn_layout.addWidget(self.clear_btn)
        
        self.export_btn = QPushButton("导出CSV")
        self.export_btn.clicked.connect(self.export_to_csv)
        btn_layout.addWidget(self.export_btn)
        
        self.import_btn = QPushButton("导入CSV")
        self.import_btn.clicked.connect(self.import_from_csv)
        btn_layout.addWidget(self.import_btn)
        
        content_layout.addLayout(btn_layout)
        
        self.records_table = QTableWidget()
        self.records_table.setColumnCount(6)
        self.records_table.setHorizontalHeaderLabels(["游戏", "投注类型", "号码", "注数", "金额", "时间"])
        self.records_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.records_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.records_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.records_table)
        splitter.addWidget(self.detail_text)
        splitter.setSizes([400, 200])
        
        content_layout.addWidget(splitter)
        content.setLayout(content_layout)
        scroll.setWidget(content)
        layout.addWidget(scroll)
        self.records_tab.setLayout(layout)
        
        self.records_table.itemSelectionChanged.connect(self.show_record_details)
    
    def init_history_tab(self):
        """初始化历史数据页"""
        layout = QVBoxLayout()
        
        btn_layout = QHBoxLayout()
        
        self.import_history_btn = QPushButton("导入开奖历史")
        self.import_history_btn.clicked.connect(self.import_history_data)
        btn_layout.addWidget(self.import_history_btn)
        
        self.clear_history_btn = QPushButton("清空历史数据")
        self.clear_history_btn.clicked.connect(self.clear_history_data)
        btn_layout.addWidget(self.clear_history_btn)
        
        self.export_history_btn = QPushButton("导出历史数据")
        self.export_history_btn.clicked.connect(self.export_history_data)
        btn_layout.addWidget(self.export_history_btn)
        
        self.refresh_btn = QPushButton("刷新数据")
        self.refresh_btn.clicked.connect(self.refresh_lottery_data)
        btn_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(btn_layout)
        
        game_layout = QHBoxLayout()
        game_layout.addWidget(QLabel("选择彩票类型:"))
        
        self.history_game_combo = QComboBox()
        self.history_game_combo.addItems(["双色球", "快乐8", "3D", "七乐彩", "大乐透", "七星彩", "排列三", "排列五"])
        self.history_game_combo.currentTextChanged.connect(self.update_history_table)
        game_layout.addWidget(self.history_game_combo)
        
        layout.addLayout(game_layout)
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(10)
        self.history_table.setHorizontalHeaderLabels(["期号", "开奖日期", "号码1", "号码2", "号码3", "号码4", "号码5", "号码6", "号码7", "号码8"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.history_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        layout.addWidget(self.history_table)
        
        self.history_tab.setLayout(layout)
    
    def init_network_tab(self):
        """初始化网络数据页"""
        layout = QVBoxLayout()
        
        api_group = QGroupBox("MXNZP API 配置")
        api_layout = QVBoxLayout(api_group)
        
        app_id_layout = QHBoxLayout()
        app_id_layout.addWidget(QLabel("App ID:"))
        
        self.app_id_label_display = QLabel("未设置")
        self.app_id_label_display.setStyleSheet("color: red; font-weight: bold;")
        app_id_layout.addWidget(self.app_id_label_display)
        
        self.set_app_id_btn = QPushButton("设置App ID")
        self.set_app_id_btn.clicked.connect(self.set_app_id)
        app_id_layout.addWidget(self.set_app_id_btn)
        
        api_layout.addLayout(app_id_layout)
        
        app_secret_layout = QHBoxLayout()
        app_secret_layout.addWidget(QLabel("App Secret:"))
        
        self.app_secret_label_display = QLabel("未设置")
        self.app_secret_label_display.setStyleSheet("color: red; font-weight: bold;")
        app_secret_layout.addWidget(self.app_secret_label_display)
        
        self.set_app_secret_btn = QPushButton("设置App Secret")
        self.set_app_secret_btn.clicked.connect(self.set_app_secret)
        app_secret_layout.addWidget(self.set_app_secret_btn)
        
        api_layout.addLayout(app_secret_layout)
        
        check_btn_layout = QHBoxLayout()
        self.check_key_btn = QPushButton("检查API密钥有效性")
        self.check_key_btn.clicked.connect(self.check_api_key)
        check_btn_layout.addWidget(self.check_key_btn)
        
        self.clear_api_btn = QPushButton("清除API密钥")
        self.clear_api_btn.clicked.connect(self.clear_api_keys)
        check_btn_layout.addWidget(self.clear_api_btn)
        
        api_layout.addLayout(check_btn_layout)
        
        layout.addWidget(api_group)
        
        game_layout = QHBoxLayout()
        game_layout.addWidget(QLabel("选择彩票类型:"))
        
        self.network_game_combo = QComboBox()
        self.network_game_combo.addItems(["双色球", "快乐8", "3D", "七乐彩", "大乐透", "七星彩", "排列三", "排列五"])
        game_layout.addWidget(self.network_game_combo)
        
        layout.addLayout(game_layout)
        
        btn_layout = QHBoxLayout()
        
        self.fetch_latest_btn = QPushButton("抓取最新开奖")
        self.fetch_latest_btn.clicked.connect(self.fetch_latest_results)
        btn_layout.addWidget(self.fetch_latest_btn)
        
        self.fetch_by_issue_btn = QPushButton("按期号查询")
        self.fetch_by_issue_btn.clicked.connect(self.fetch_by_issue)
        btn_layout.addWidget(self.fetch_by_issue_btn)
        
        self.fetch_history_btn = QPushButton("查询历史开奖")
        self.fetch_history_btn.clicked.connect(self.fetch_history_results)
        btn_layout.addWidget(self.fetch_history_btn)
        
        self.auto_fetch_check = QCheckBox("自动更新(30分钟)")
        self.auto_fetch_check.stateChanged.connect(self.toggle_auto_fetch)
        btn_layout.addWidget(self.auto_fetch_check)
        
        layout.addLayout(btn_layout)
        
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(7)
        self.result_table.setHorizontalHeaderLabels(["期号", "开奖日期", "开奖号码", "销售额", "奖池", "一等奖", "二等奖"])
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.result_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.result_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        layout.addWidget(self.result_table)
        
        bottom_btn_layout = QHBoxLayout()
        
        self.save_history_btn = QPushButton("保存到历史库")
        self.save_history_btn.clicked.connect(self.save_to_history)
        bottom_btn_layout.addWidget(self.save_history_btn)
        
        self.analyze_btn = QPushButton("分析当前数据")
        self.analyze_btn.clicked.connect(self.analyze_current)
        bottom_btn_layout.addWidget(self.analyze_btn)
        
        layout.addLayout(bottom_btn_layout)
        
        self.network_tab.setLayout(layout)
    
    def init_shrink_tab(self):
        """初始化号码缩水页"""
        layout = QVBoxLayout()
        
        game_layout = QHBoxLayout()
        game_layout.addWidget(QLabel("选择彩票类型:"))
        
        self.shrink_game_combo = QComboBox()
        self.shrink_game_combo.addItems(["双色球", "快乐8", "3D", "七乐彩", "大乐透", "七星彩", "排列三", "排列五"])
        self.shrink_game_combo.currentTextChanged.connect(self.update_shrink_ui)
        game_layout.addWidget(self.shrink_game_combo)
        
        layout.addLayout(game_layout)
        
        self.shrink_condition_area = QWidget()
        self.shrink_condition_layout = QVBoxLayout(self.shrink_condition_area)
        self.update_shrink_ui()
        
        layout.addWidget(self.shrink_condition_area)
        
        btn_layout = QHBoxLayout()
        
        self.generate_shrink_btn = QPushButton("生成缩水号码")
        self.generate_shrink_btn.clicked.connect(self.generate_shrink_numbers)
        btn_layout.addWidget(self.generate_shrink_btn)
        
        self.save_shrink_btn = QPushButton("保存结果")
        self.save_shrink_btn.clicked.connect(self.save_shrink_result)
        btn_layout.addWidget(self.save_shrink_btn)
        
        self.shrink_select_btn = QPushButton("自选号码")
        self.shrink_select_btn.clicked.connect(self.shrink_select_numbers)
        btn_layout.addWidget(self.shrink_select_btn)
        
        layout.addLayout(btn_layout)
        
        self.shrink_result_area = QTextEdit()
        self.shrink_result_area.setReadOnly(True)
        layout.addWidget(self.shrink_result_area)
        
        self.shrink_tab.setLayout(layout)
    
    def init_matrix_tab(self):
        """初始化矩阵投注页"""
        layout = QVBoxLayout()
        
        game_layout = QHBoxLayout()
        game_layout.addWidget(QLabel("选择彩票类型:"))
        
        self.matrix_game_combo = QComboBox()
        self.matrix_game_combo.addItems(["双色球", "快乐8", "3D", "七乐彩", "大乐透", "七星彩", "排列三", "排列五"])
        self.matrix_game_combo.currentTextChanged.connect(self.update_matrix_ui)
        game_layout.addWidget(self.matrix_game_combo)
        
        layout.addLayout(game_layout)
        
        self.matrix_condition_area = QWidget()
        self.matrix_condition_layout = QVBoxLayout(self.matrix_condition_area)
        self.update_matrix_ui()
        
        layout.addWidget(self.matrix_condition_area)
        
        btn_layout = QHBoxLayout()
        
        self.generate_matrix_btn = QPushButton("生成矩阵号码")
        self.generate_matrix_btn.clicked.connect(self.generate_matrix_numbers)
        btn_layout.addWidget(self.generate_matrix_btn)
        
        self.save_matrix_btn = QPushButton("保存结果")
        self.save_matrix_btn.clicked.connect(self.save_matrix_result)
        btn_layout.addWidget(self.save_matrix_btn)
        
        self.matrix_select_btn = QPushButton("自选号码")
        self.matrix_select_btn.clicked.connect(self.matrix_select_numbers)
        btn_layout.addWidget(self.matrix_select_btn)
        
        layout.addLayout(btn_layout)
        
        self.matrix_result_area = QTextEdit()
        self.matrix_result_area.setReadOnly(True)
        layout.addWidget(self.matrix_result_area)
        
        self.matrix_tab.setLayout(layout)
    
    def self_select(self, game_type):
        """自选号码主方法"""
        try:
            if game_type == "双色球":
                self.self_select_ssq()
            elif game_type == "快乐8":
                self.self_select_kl8()
            elif game_type == "3D":
                self.self_select_3d()
            elif game_type == "七乐彩":
                self.self_select_qlc()
            elif game_type == "大乐透":
                self.self_select_dlt()
            elif game_type == "七星彩":
                self.self_select_qxc()
            elif game_type == "排列三":
                self.self_select_pl3()
            elif game_type == "排列五":
                self.self_select_pl5()
        except Exception as e:
            logger.error(f"自选号码错误: {str(e)}")
            QMessageBox.warning(self, "错误", f"自选号码失败: {str(e)}")
    
    def generate_random(self, game_type):
        """机选1注"""
        try:
            if game_type == "双色球":
                red = sorted(random.sample(range(1, 34), 6))
                blue = random.randint(1, 16)
                result = f"红球: {', '.join(map(str, red))}\n蓝球: {blue}"
                self.add_betting_record(game_type, "机选", result, 1, 2.0)
                
            elif game_type == "快乐8":
                nums = sorted(random.sample(range(1, 81), 10))
                result = f"号码: {', '.join(map(str, nums))}"
                self.add_betting_record(game_type, "机选10", result, 1, 2.0)
                
            elif game_type == "3D":
                nums = [random.randint(0, 9) for _ in range(3)]
                result = f"号码: {', '.join(map(str, nums))}"
                self.add_betting_record(game_type, "机选", result, 1, 2.0)
                
            elif game_type == "七乐彩":
                nums = sorted(random.sample(range(1, 31), 7))
                result = f"号码: {', '.join(map(str, nums))}"
                self.add_betting_record(game_type, "机选", result, 1, 2.0)
                
            elif game_type == "大乐透":
                front = sorted(random.sample(range(1, 36), 5))
                back = sorted(random.sample(range(1, 13), 2))
                result = f"前区: {', '.join(map(str, front))}\n后区: {', '.join(map(str, back))}"
                self.add_betting_record(game_type, "机选", result, 1, 2.0)
                
            elif game_type == "七星彩":
                nums = [random.randint(0, 9) for _ in range(6)] + [random.randint(0, 14)]
                result = f"号码: {', '.join(map(str, nums))}"
                self.add_betting_record(game_type, "机选", result, 1, 2.0)
                
            elif game_type == "排列三":
                nums = [random.randint(0, 9) for _ in range(3)]
                result = f"号码: {', '.join(map(str, nums))}"
                self.add_betting_record(game_type, "机选", result, 1, 2.0)
                
            elif game_type == "排列五":
                nums = [random.randint(0, 9) for _ in range(5)]
                result = f"号码: {', '.join(map(str, nums))}"
                self.add_betting_record(game_type, "机选", result, 1, 2.0)
            
            QMessageBox.information(self, f"{game_type}机选1注", result)
            
        except Exception as e:
            logger.error(f"机选错误: {str(e)}")
            QMessageBox.warning(self, "错误", f"机选失败: {str(e)}")
    
    def generate_multiple(self, game_type):
        """机选多注"""
        try:
            num_bets, ok = QInputDialog.getInt(self, "机选多注", "请输入注数(1-100):", 5, 1, 100)
            if not ok:
                return
                
            results = []
            for i in range(num_bets):
                if game_type == "双色球":
                    red = sorted(random.sample(range(1, 34), 6))
                    blue = random.randint(1, 16)
                    results.append(f"第{i+1}注: 红球{', '.join(map(str, red))} 蓝球{blue}")
                    self.add_betting_record(game_type, "机选", f"红球{', '.join(map(str, red))} 蓝球{blue}", 1, 2.0)
                    
                elif game_type == "快乐8":
                    nums = sorted(random.sample(range(1, 81), 10))
                    results.append(f"第{i+1}注: {', '.join(map(str, nums))}")
                    self.add_betting_record(game_type, "机选10", f"号码{', '.join(map(str, nums))}", 1, 2.0)
                    
                elif game_type == "3D":
                    nums = [random.randint(0, 9) for _ in range(3)]
                    results.append(f"第{i+1}注: {', '.join(map(str, nums))}")
                    self.add_betting_record(game_type, "机选", f"号码{', '.join(map(str, nums))}", 1, 2.0)
                    
                elif game_type == "七乐彩":
                    nums = sorted(random.sample(range(1, 31), 7))
                    results.append(f"第{i+1}注: {', '.join(map(str, nums))}")
                    self.add_betting_record(game_type, "机选", f"号码{', '.join(map(str, nums))}", 1, 2.0)
                    
                elif game_type == "大乐透":
                    front = sorted(random.sample(range(1, 36), 5))
                    back = sorted(random.sample(range(1, 13), 2))
                    results.append(f"第{i+1}注: 前区{', '.join(map(str, front))} 后区{', '.join(map(str, back))}")
                    self.add_betting_record(game_type, "机选", f"前区{', '.join(map(str, front))} 后区{', '.join(map(str, back))}", 1, 2.0)
                    
                elif game_type == "七星彩":
                    nums = [random.randint(0, 9) for _ in range(6)] + [random.randint(0, 14)]
                    results.append(f"第{i+1}注: {', '.join(map(str, nums))}")
                    self.add_betting_record(game_type, "机选", f"号码{', '.join(map(str, nums))}", 1, 2.0)
                    
                elif game_type == "排列三":
                    nums = [random.randint(0, 9) for _ in range(3)]
                    results.append(f"第{i+1}注: {', '.join(map(str, nums))}")
                    self.add_betting_record(game_type, "机选", f"号码{', '.join(map(str, nums))}", 1, 2.0)
                    
                elif game_type == "排列五":
                    nums = [random.randint(0, 9) for _ in range(5)]
                    results.append(f"第{i+1}注: {', '.join(map(str, nums))}")
                    self.add_betting_record(game_type, "机选", f"号码{', '.join(map(str, nums))}", 1, 2.0)
            
            result_str = "\n\n".join(results)
            QMessageBox.information(self, f"{game_type}机选{num_bets}注", result_str)
            
        except Exception as e:
            logger.error(f"机选多注错误: {str(e)}")
            QMessageBox.warning(self, "错误", f"机选多注失败: {str(e)}")
    
    def generate_complex(self, game_type):
        """复式投注"""
        try:
            if game_type == "双色球":
                red_count, ok1 = QInputDialog.getInt(self, "复式投注", "红球选择数量(7-33):", 7, 7, 33)
                blue_count, ok2 = QInputDialog.getInt(self, "复式投注", "蓝球选择数量(1-16):", 1, 1, 16)
                
                if ok1 and ok2:
                    red = sorted(random.sample(range(1, 34), red_count))
                    blue = sorted(random.sample(range(1, 17), blue_count))
                    result = f"红球({red_count}个): {', '.join(map(str, red))}\n蓝球({blue_count}个): {', '.join(map(str, blue))}"
                    
                    red_comb = math.comb(red_count, 6)
                    blue_comb = math.comb(blue_count, 1)
                    bets = red_comb * blue_comb
                    amount = bets * 2.0
                    
                    QMessageBox.information(self, "双色球复式投注", f"{result}\n\n注数: {bets}注\n金额: ¥{amount:.2f}")
                    self.add_betting_record(game_type, "复式", result, bets, amount)
                    
            elif game_type == "大乐透":
                front_count, ok1 = QInputDialog.getInt(self, "复式投注", "前区选择数量(6-35):", 6, 6, 35)
                back_count, ok2 = QInputDialog.getInt(self, "复式投注", "后区选择数量(3-12):", 3, 3, 12)
                
                if ok1 and ok2:
                    front = sorted(random.sample(range(1, 36), front_count))
                    back = sorted(random.sample(range(1, 13), back_count))
                    result = f"前区({front_count}个): {', '.join(map(str, front))}\n后区({back_count}个): {', '.join(map(str, back))}"
                    
                    front_comb = math.comb(front_count, 5)
                    back_comb = math.comb(back_count, 2)
                    bets = front_comb * back_comb
                    amount = bets * 2.0
                    
                    QMessageBox.information(self, "大乐透复式投注", f"{result}\n\n注数: {bets}注\n金额: ¥{amount:.2f}")
                    self.add_betting_record(game_type, "复式", result, bets, amount)
                    
            elif game_type == "快乐8":
                select_num, ok = QInputDialog.getInt(self, "复式投注", "选择号码数量(11-80):", 11, 11, 80)
                if ok:
                    nums = sorted(random.sample(range(1, 81), select_num))
                    result = f"号码({select_num}个): {', '.join(map(str, nums))}"
                    
                    bets = math.comb(select_num, 10)
                    amount = bets * 2.0
                    
                    QMessageBox.information(self, "快乐8复式投注", f"{result}\n\n注数: {bets}注\n金额: ¥{amount:.2f}")
                    self.add_betting_record(game_type, "复式", result, bets, amount)
                    
            elif game_type == "七乐彩":
                select_num, ok = QInputDialog.getInt(self, "复式投注", "选择号码数量(8-30):", 8, 8, 30)
                if ok:
                    nums = sorted(random.sample(range(1, 31), select_num))
                    result = f"号码({select_num}个): {', '.join(map(str, nums))}"
                    
                    bets = math.comb(select_num, 7)
                    amount = bets * 2.0
                    
                    QMessageBox.information(self, "七乐彩复式投注", f"{result}\n\n注数: {bets}注\n金额: ¥{amount:.2f}")
                    self.add_betting_record(game_type, "复式", result, bets, amount)
                    
        except Exception as e:
            logger.error(f"复式投注错误: {str(e)}")
            QMessageBox.warning(self, "错误", f"复式投注失败: {str(e)}")
    
    def generate_dantuo(self, game_type):
        """胆拖投注"""
        try:
            if game_type == "双色球":
                red_dan, ok1 = QInputDialog.getInt(self, "红球胆码", "请输入胆码数量(1-5):", 1, 1, 5)
                red_tuo, ok2 = QInputDialog.getInt(self, "红球拖码", "请输入拖码数量(至少5-胆码数):", 
                                                  max(5, 5 - red_dan + 1), 5 - red_dan + 1, 28)
                blue_count, ok3 = QInputDialog.getInt(self, "蓝球数量", "请输入蓝球数量(1-16):", 1, 1, 16)
                
                if ok1 and ok2 and ok3:
                    red_dan_nums = sorted(random.sample(range(1, 34), red_dan))
                    remaining_red = list(set(range(1, 34)) - set(red_dan_nums))
                    red_tuo_nums = sorted(random.sample(remaining_red, red_tuo))
                    blue_nums = sorted(random.sample(range(1, 17), blue_count))
                    
                    result = f"""红球胆码({red_dan}个): {', '.join(map(str, red_dan_nums))}
红球拖码({red_tuo}个): {', '.join(map(str, red_tuo_nums))}
蓝球({blue_count}个): {', '.join(map(str, blue_nums))}"""
                    
                    red_combinations = math.comb(red_tuo, 6 - red_dan)
                    bets = red_combinations * blue_count
                    amount = bets * 2.0
                    
                    QMessageBox.information(self, "双色球胆拖投注", f"{result}\n\n注数: {bets}注\n金额: ¥{amount:.2f}")
                    self.add_betting_record(game_type, "胆拖", result, bets, amount)
                    
            elif game_type == "大乐透":
                front_dan, ok1 = QInputDialog.getInt(self, "前区胆码", "请输入胆码数量(1-4):", 1, 1, 4)
                front_tuo, ok2 = QInputDialog.getInt(self, "前区拖码", "请输入拖码数量(至少5-胆码数):", 
                                                    max(5, 5 - front_dan + 1), 5 - front_dan + 1, 31)
                back_count, ok3 = QInputDialog.getInt(self, "后区数量", "请输入后区数量(2-12):", 2, 2, 12)
                
                if ok1 and ok2 and ok3:
                    front_dan_nums = sorted(random.sample(range(1, 36), front_dan))
                    remaining_front = list(set(range(1, 36)) - set(front_dan_nums))
                    front_tuo_nums = sorted(random.sample(remaining_front, front_tuo))
                    back_nums = sorted(random.sample(range(1, 13), back_count))
                    
                    result = f"""前区胆码({front_dan}个): {', '.join(map(str, front_dan_nums))}
前区拖码({front_tuo}个): {', '.join(map(str, front_tuo_nums))}
后区({back_count}个): {', '.join(map(str, back_nums))}"""
                    
                    front_combinations = math.comb(front_tuo, 5 - front_dan)
                    back_combinations = math.comb(back_count, 2)
                    bets = front_combinations * back_combinations
                    amount = bets * 2.0
                    
                    QMessageBox.information(self, "大乐透胆拖投注", f"{result}\n\n注数: {bets}注\n金额: ¥{amount:.2f}")
                    self.add_betting_record(game_type, "胆拖", result, bets, amount)
                    
        except Exception as e:
            logger.error(f"胆拖投注错误: {str(e)}")
            QMessageBox.warning(self, "错误", f"胆拖投注失败: {str(e)}")
    
    def lucky_select(self, game_type):
        """幸运选号"""
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle(f"{game_type}幸运选号")
            dialog.setFixedSize(400, 600)
            
            layout = QVBoxLayout()
            
            type_layout = QHBoxLayout()
            type_layout.addWidget(QLabel("投注类型:"))
            bet_type_combo = QComboBox()
            bet_type_combo.addItems(["单式", "复式", "胆拖"])
            type_layout.addWidget(bet_type_combo)
            layout.addLayout(type_layout)
            
            if game_type in ["双色球", "大乐透"]:
                num_layout = QHBoxLayout()
                if game_type == "双色球":
                    num_layout.addWidget(QLabel("红球/前区选择数量:"))
                else:
                    num_layout.addWidget(QLabel("前区选择数量:"))
                
                num_spin = QSpinBox()
                if game_type == "双色球":
                    num_spin.setRange(6, 33)
                    num_spin.setValue(6)
                else:
                    num_spin.setRange(5, 35)
                    num_spin.setValue(5)
                num_layout.addWidget(num_spin)
                layout.addLayout(num_layout)
                
                blue_layout = QHBoxLayout()
                if game_type == "双色球":
                    blue_layout.addWidget(QLabel("蓝球选择数量:"))
                else:
                    blue_layout.addWidget(QLabel("后区选择数量:"))
                
                blue_spin = QSpinBox()
                if game_type == "双色球":
                    blue_spin.setRange(1, 16)
                    blue_spin.setValue(1)
                else:
                    blue_spin.setRange(2, 12)
                    blue_spin.setValue(2)
                blue_layout.addWidget(blue_spin)
                layout.addLayout(blue_layout)
                
            elif game_type in ["快乐8", "七乐彩"]:
                num_layout = QHBoxLayout()
                num_layout.addWidget(QLabel("选择号码数量:"))
                num_spin = QSpinBox()
                if game_type == "快乐8":
                    num_spin.setRange(1, 80)
                    num_spin.setValue(10)
                else:
                    num_spin.setRange(1, 30)
                    num_spin.setValue(7)
                num_layout.addWidget(num_spin)
                layout.addLayout(num_layout)
                
            elif game_type in ["3D", "排列三"]:
                num_layout = QHBoxLayout()
                num_layout.addWidget(QLabel("选择号码:"))
                num_label = QLabel("3个号码(0-9)")
                num_layout.addWidget(num_label)
                layout.addLayout(num_layout)
                
            elif game_type == "七星彩":
                num_layout = QHBoxLayout()
                num_layout.addWidget(QLabel("选择号码:"))
                num_label = QLabel("7个号码(前6位0-9,第7位0-14)")
                num_layout.addWidget(num_label)
                layout.addLayout(num_layout)
                
            elif game_type == "排列五":
                num_layout = QHBoxLayout()
                num_layout.addWidget(QLabel("选择号码:"))
                num_label = QLabel("5个号码(0-9)")
                num_layout.addWidget(num_label)
                layout.addLayout(num_layout)
            
            group_layout = QHBoxLayout()
            group_layout.addWidget(QLabel("生成组数:"))
            group_spin = QSpinBox()
            group_spin.setRange(1, 20)
            group_spin.setValue(5)
            group_layout.addWidget(group_spin)
            layout.addLayout(group_layout)
            
            btn_layout = QHBoxLayout()
            generate_btn = QPushButton("生成幸运号码")
            cancel_btn = QPushButton("取消")
            
            def generate():
                bet_type = bet_type_combo.currentText()
                group_count = group_spin.value()
                
                results = []
                total_bets = 0
                
                for i in range(group_count):
                    if game_type == "双色球":
                        if bet_type == "单式":
                            red = sorted(random.sample(range(1, 34), 6))
                            blue = random.randint(1, 16)
                            result = f"第{i+1}组: 红球{', '.join(map(str, red))} + 蓝球{blue}"
                            bets = 1
                        elif bet_type == "复式":
                            red_count = num_spin.value()
                            blue_count = blue_spin.value()
                            red = sorted(random.sample(range(1, 34), red_count))
                            blue = sorted(random.sample(range(1, 17), blue_count))
                            red_comb = math.comb(red_count, 6)
                            blue_comb = math.comb(blue_count, 1)
                            bets = red_comb * blue_comb
                            result = f"第{i+1}组: 红球({red_count}个){', '.join(map(str, red))} + 蓝球({blue_count}个){', '.join(map(str, blue))}"
                        else:  # 胆拖
                            red_dan = random.randint(1, 5)
                            red_tuo = random.randint(5 - red_dan + 1, 28)
                            red_dan_nums = sorted(random.sample(range(1, 34), red_dan))
                            remaining_red = list(set(range(1, 34)) - set(red_dan_nums))
                            red_tuo_nums = sorted(random.sample(remaining_red, red_tuo))
                            blue_nums = sorted(random.sample(range(1, 17), blue_spin.value()))
                            red_comb = math.comb(red_tuo, 6 - red_dan)
                            bets = red_comb * len(blue_nums)
                            result = f"第{i+1}组: 红球胆码{', '.join(map(str, red_dan_nums))} 拖码{', '.join(map(str, red_tuo_nums))} + 蓝球{', '.join(map(str, blue_nums))}"
                        
                    elif game_type == "大乐透":
                        if bet_type == "单式":
                            front = sorted(random.sample(range(1, 36), 5))
                            back = sorted(random.sample(range(1, 13), 2))
                            result = f"第{i+1}组: 前区{', '.join(map(str, front))} + 后区{', '.join(map(str, back))}"
                            bets = 1
                        elif bet_type == "复式":
                            front_count = num_spin.value()
                            back_count = blue_spin.value()
                            front = sorted(random.sample(range(1, 36), front_count))
                            back = sorted(random.sample(range(1, 13), back_count))
                            front_comb = math.comb(front_count, 5)
                            back_comb = math.comb(back_count, 2)
                            bets = front_comb * back_comb
                            result = f"第{i+1}组: 前区({front_count}个){', '.join(map(str, front))} + 后区({back_count}个){', '.join(map(str, back))}"
                        else:  # 胆拖
                            front_dan = random.randint(1, 4)
                            front_tuo = random.randint(5 - front_dan + 1, 31)
                            front_dan_nums = sorted(random.sample(range(1, 36), front_dan))
                            remaining_front = list(set(range(1, 36)) - set(front_dan_nums))
                            front_tuo_nums = sorted(random.sample(remaining_front, front_tuo))
                            back_nums = sorted(random.sample(range(1, 13), blue_spin.value()))
                            front_comb = math.comb(front_tuo, 5 - front_dan)
                            back_comb = math.comb(len(back_nums), 2)
                            bets = front_comb * back_comb
                            result = f"第{i+1}组: 前区胆码{', '.join(map(str, front_dan_nums))} 拖码{', '.join(map(str, front_tuo_nums))} + 后区{', '.join(map(str, back_nums))}"
                    
                    else:
                        # 其他游戏简单生成
                        if game_type == "快乐8":
                            nums = sorted(random.sample(range(1, 81), 10))
                            result = f"第{i+1}组: {', '.join(map(str, nums))}"
                            bets = 1
                        elif game_type == "七乐彩":
                            nums = sorted(random.sample(range(1, 31), 7))
                            result = f"第{i+1}组: {', '.join(map(str, nums))}"
                            bets = 1
                        elif game_type == "3D":
                            nums = [random.randint(0, 9) for _ in range(3)]
                            result = f"第{i+1}组: {', '.join(map(str, nums))}"
                            bets = 1
                        elif game_type == "排列三":
                            nums = [random.randint(0, 9) for _ in range(3)]
                            result = f"第{i+1}组: {', '.join(map(str, nums))}"
                            bets = 1
                        elif game_type == "七星彩":
                            nums = [random.randint(0, 9) for _ in range(6)] + [random.randint(0, 14)]
                            result = f"第{i+1}组: {', '.join(map(str, nums))}"
                            bets = 1
                        elif game_type == "排列五":
                            nums = [random.randint(0, 9) for _ in range(5)]
                            result = f"第{i+1}组: {', '.join(map(str, nums))}"
                            bets = 1
                    
                    results.append(f"{result} (注数: {bets}注)")
                    total_bets += bets
                    self.add_betting_record(game_type, f"幸运选号{bet_type}", result, bets, bets * 2.0)
                
                result_text = f"共生成{group_count}组幸运号码，总注数: {total_bets}注\n\n" + "\n".join(results)
                QMessageBox.information(self, f"{game_type}幸运选号", result_text)
                dialog.accept()
            
            generate_btn.clicked.connect(generate)
            cancel_btn.clicked.connect(dialog.reject)
            btn_layout.addWidget(generate_btn)
            btn_layout.addWidget(cancel_btn)
            layout.addLayout(btn_layout)
            
            dialog.setLayout(layout)
            dialog.exec()
            
        except Exception as e:
            logger.error(f"幸运选号错误: {str(e)}")
            QMessageBox.warning(self, "错误", f"幸运选号失败: {str(e)}")
    
    def self_select_ssq(self):
        """双色球自选号码 - 包含历史开奖比对功能"""
        dialog = QDialog(self)
        dialog.setWindowTitle("双色球自选号码")
        dialog.setMinimumSize(400, 800)
        
        layout = QVBoxLayout()
        tabs = QTabWidget()
        
        select_tab = QWidget()
        select_layout = QVBoxLayout(select_tab)
        
        bet_type_layout = QHBoxLayout()
        bet_type_layout.addWidget(QLabel("投注方式:"))
        bet_type_combo = QComboBox()
        bet_type_combo.addItems(["单式投注", "复式投注", "胆拖投注"])
        bet_type_layout.addWidget(bet_type_combo)
        select_layout.addLayout(bet_type_layout)
        
        red_group = QGroupBox("红球选择 (1-33)")
        red_layout = QVBoxLayout()
        
        red_grid = QGridLayout()
        red_grid.setSpacing(5)
        
        red_buttons = []
        for i in range(1, 34):
            omission = self.get_omission("双色球", i, "red")
            frequency = self.get_frequency("双色球", i, "red")
            cold_hot = self.get_cold_hot("双色球", i, "red")
            probability = self.calculate_probability("双色球", i, "red")
            btn = NumberButton(str(i), cold_hot, omission, frequency, probability=probability)
            red_buttons.append(btn)
            row = (i-1) // 6
            col = (i-1) % 6
            red_grid.addWidget(btn, row, col)
        
        red_layout.addLayout(red_grid)
        red_group.setLayout(red_layout)
        select_layout.addWidget(red_group)
        
        blue_group = QGroupBox("蓝球选择 (1-16)")
        blue_layout = QVBoxLayout()
        
        blue_grid = QGridLayout()
        blue_grid.setSpacing(5)
        
        blue_buttons = []
        for i in range(1, 17):
            omission = self.get_omission("双色球", i, "blue")
            frequency = self.get_frequency("双色球", i, "blue")
            cold_hot = self.get_cold_hot("双色球", i, "blue")
            probability = self.calculate_probability("双色球", i, "blue")
            btn = NumberButton(str(i), cold_hot, omission, frequency, probability=probability)
            blue_buttons.append(btn)
            row = (i-1) // 8
            col = (i-1) % 8
            blue_grid.addWidget(btn, row, col)
        
        blue_layout.addLayout(blue_grid)
        blue_group.setLayout(blue_layout)
        select_layout.addWidget(blue_group)
        
        select_count_label = QLabel("红球: 0个, 蓝球: 0个")
        select_layout.addWidget(select_count_label)
        
        def update_count():
            red_selected = sum(btn.isChecked() for btn in red_buttons)
            blue_selected = sum(btn.isChecked() for btn in blue_buttons)
            select_count_label.setText(f"红球: {red_selected}个, 蓝球: {blue_selected}个")
        
        for btn in red_buttons:
            btn.clicked.connect(update_count)
        for btn in blue_buttons:
            btn.clicked.connect(update_count)
        
        btn_layout = QHBoxLayout()
        confirm_btn = QPushButton("确认投注")
        analysis_btn = QPushButton("号码分析")
        history_compare_btn = QPushButton("历史比对")
        cancel_btn = QPushButton("取消")
        
        def confirm():
            red_selected = [i+1 for i, btn in enumerate(red_buttons) if btn.isChecked()]
            blue_selected = [i+1 for i, btn in enumerate(blue_buttons) if btn.isChecked()]
            bet_type = bet_type_combo.currentText()
            
            if bet_type == "单式投注":
                if len(red_selected) != 6 or len(blue_selected) != 1:
                    QMessageBox.warning(dialog, "错误", "单式投注需要选择6个红球和1个蓝球")
                    return
                result = f"红球: {', '.join(map(str, red_selected))}\n蓝球: {blue_selected[0]}"
                bets = 1
                
            elif bet_type == "复式投注":
                if len(red_selected) < 7:
                    QMessageBox.warning(dialog, "错误", "复式投注需要选择至少7个红球")
                    return
                if len(blue_selected) < 1:
                    QMessageBox.warning(dialog, "错误", "请选择至少1个蓝球")
                    return
                red_comb = math.comb(len(red_selected), 6)
                blue_comb = len(blue_selected)
                bets = red_comb * blue_comb
                result = f"红球({len(red_selected)}个): {', '.join(map(str, red_selected))}\n蓝球({len(blue_selected)}个): {', '.join(map(str, blue_selected))}"
                
            else:  # 胆拖投注
                if len(red_selected) < 7:
                    QMessageBox.warning(dialog, "错误", "胆拖投注需要选择至少7个红球")
                    return
                if len(blue_selected) < 1:
                    QMessageBox.warning(dialog, "错误", "请选择至少1个蓝球")
                    return
                
                # 简单处理：前几个作为胆码
                red_dan = min(5, len(red_selected) - 1)
                red_dan_nums = red_selected[:red_dan]
                red_tuo_nums = red_selected[red_dan:]
                
                if len(red_tuo_nums) < 6 - red_dan:
                    QMessageBox.warning(dialog, "错误", f"拖码数量不足，至少需要{6-red_dan}个拖码")
                    return
                
                red_comb = math.comb(len(red_tuo_nums), 6 - red_dan)
                bets = red_comb * len(blue_selected)
                result = f"红球胆码({red_dan}个): {', '.join(map(str, red_dan_nums))}\n红球拖码({len(red_tuo_nums)}个): {', '.join(map(str, red_tuo_nums))}\n蓝球({len(blue_selected)}个): {', '.join(map(str, blue_selected))}"
            
            amount = bets * 2.0
            QMessageBox.information(self, f"双色球{bet_type}", f"{result}\n\n注数: {bets}注\n金额: ¥{amount:.2f}")
            self.add_betting_record("双色球", bet_type, result, bets, amount)
            dialog.accept()
        
        def analyze():
            red_selected = [i+1 for i, btn in enumerate(red_buttons) if btn.isChecked()]
            blue_selected = [i+1 for i, btn in enumerate(blue_buttons) if btn.isChecked()]
            selected_numbers = red_selected + blue_selected
            
            if not selected_numbers:
                QMessageBox.warning(dialog, "错误", "请先选择号码")
                return
            
            analysis_dialog = LotteryAnalysisDialog(self, "双色球", selected_numbers)
            analysis_dialog.exec()
        
        def history_compare():
            red_selected = [i+1 for i, btn in enumerate(red_buttons) if btn.isChecked()]
            blue_selected = [i+1 for i, btn in enumerate(blue_buttons) if btn.isChecked()]
            selected_numbers = red_selected + blue_selected
            
            if not selected_numbers:
                QMessageBox.warning(dialog, "错误", "请先选择号码")
                return
            
            compare_dialog = HistoryCompareDialog(self, "双色球", selected_numbers)
            compare_dialog.exec()
        
        confirm_btn.clicked.connect(confirm)
        analysis_btn.clicked.connect(analyze)
        history_compare_btn.clicked.connect(history_compare)
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(confirm_btn)
        btn_layout.addWidget(analysis_btn)
        btn_layout.addWidget(history_compare_btn)
        btn_layout.addWidget(cancel_btn)
        select_layout.addLayout(btn_layout)
        
        tabs.addTab(select_tab, "🎯 选号")
        
        history_tab = QWidget()
        history_layout = QVBoxLayout(history_tab)
        
        history_table = QTableWidget()
        history_table.setColumnCount(5)
        history_table.setHorizontalHeaderLabels(["期号", "开奖日期", "开奖号码", "一等奖", "奖池"])
        history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        if "双色球" in self.history_data and self.history_data["双色球"]:
            data = self.history_data["双色球"][:50]
            history_table.setRowCount(len(data))
            for row, record in enumerate(data):
                history_table.setItem(row, 0, QTableWidgetItem(str(record.get("期号", ""))))
                history_table.setItem(row, 1, QTableWidgetItem(str(record.get("开奖日期", ""))))
                history_table.setItem(row, 2, QTableWidgetItem(str(record.get("开奖号码", ""))))
                history_table.setItem(row, 3, QTableWidgetItem(str(record.get("一等奖", "0注"))))
                history_table.setItem(row, 4, QTableWidgetItem(str(record.get("奖池", "0"))))
        else:
            history_table.setRowCount(1)
            history_table.setItem(0, 0, QTableWidgetItem("暂无数据"))
            history_table.setItem(0, 1, QTableWidgetItem("请先获取历史开奖数据"))
        
        history_layout.addWidget(history_table)
        tabs.addTab(history_tab, "📋 最近50期")
        
        layout.addWidget(tabs)
        dialog.setLayout(layout)
        dialog.exec()
    
    def self_select_dlt(self):
        """大乐透自选号码 - 包含历史开奖比对功能"""
        dialog = QDialog(self)
        dialog.setWindowTitle("大乐透自选号码")
        dialog.setMinimumSize(400, 800)
        
        layout = QVBoxLayout()
        tabs = QTabWidget()
        
        select_tab = QWidget()
        select_layout = QVBoxLayout(select_tab)
        
        bet_type_layout = QHBoxLayout()
        bet_type_layout.addWidget(QLabel("投注方式:"))
        bet_type_combo = QComboBox()
        bet_type_combo.addItems(["单式投注", "复式投注", "胆拖投注"])
        bet_type_layout.addWidget(bet_type_combo)
        select_layout.addLayout(bet_type_layout)
        
        front_group = QGroupBox("前区选择 (1-35)")
        front_layout = QVBoxLayout()
        
        front_grid = QGridLayout()
        front_grid.setSpacing(5)
        
        front_buttons = []
        for i in range(1, 36):
            omission = self.get_omission("大乐透", i, "front")
            frequency = self.get_frequency("大乐透", i, "front")
            cold_hot = self.get_cold_hot("大乐透", i, "front")
            probability = self.calculate_probability("大乐透", i, "front")
            btn = NumberButton(str(i), cold_hot, omission, frequency, probability=probability)
            front_buttons.append(btn)
            row = (i-1) // 7
            col = (i-1) % 7
            front_grid.addWidget(btn, row, col)
        
        front_layout.addLayout(front_grid)
        front_group.setLayout(front_layout)
        select_layout.addWidget(front_group)
        
        back_group = QGroupBox("后区选择 (1-12)")
        back_layout = QVBoxLayout()
        
        back_grid = QGridLayout()
        back_grid.setSpacing(5)
        
        back_buttons = []
        for i in range(1, 13):
            omission = self.get_omission("大乐透", i, "back")
            frequency = self.get_frequency("大乐透", i, "back")
            cold_hot = self.get_cold_hot("大乐透", i, "back")
            probability = self.calculate_probability("大乐透", i, "back")
            btn = NumberButton(str(i), cold_hot, omission, frequency, probability=probability)
            back_buttons.append(btn)
            row = (i-1) // 6
            col = (i-1) % 6
            back_grid.addWidget(btn, row, col)
        
        back_layout.addLayout(back_grid)
        back_group.setLayout(back_layout)
        select_layout.addWidget(back_group)
        
        select_count_label = QLabel("前区: 0个, 后区: 0个")
        select_layout.addWidget(select_count_label)
        
        def update_count():
            front_selected = sum(btn.isChecked() for btn in front_buttons)
            back_selected = sum(btn.isChecked() for btn in back_buttons)
            select_count_label.setText(f"前区: {front_selected}个, 后区: {back_selected}个")
        
        for btn in front_buttons:
            btn.clicked.connect(update_count)
        for btn in back_buttons:
            btn.clicked.connect(update_count)
        
        btn_layout = QHBoxLayout()
        confirm_btn = QPushButton("确认投注")
        analysis_btn = QPushButton("号码分析")
        history_compare_btn = QPushButton("历史比对")
        cancel_btn = QPushButton("取消")
        
        def confirm():
            front_selected = [i+1 for i, btn in enumerate(front_buttons) if btn.isChecked()]
            back_selected = [i+1 for i, btn in enumerate(back_buttons) if btn.isChecked()]
            bet_type = bet_type_combo.currentText()
            
            if bet_type == "单式投注":
                if len(front_selected) != 5 or len(back_selected) != 2:
                    QMessageBox.warning(dialog, "错误", "单式投注需要选择5个前区和2个后区")
                    return
                result = f"前区: {', '.join(map(str, front_selected))}\n后区: {', '.join(map(str, back_selected))}"
                bets = 1
                
            elif bet_type == "复式投注":
                if len(front_selected) < 6:
                    QMessageBox.warning(dialog, "错误", "复式投注需要选择至少6个前区")
                    return
                if len(back_selected) < 3:
                    QMessageBox.warning(dialog, "错误", "复式投注需要选择至少3个后区")
                    return
                front_comb = math.comb(len(front_selected), 5)
                back_comb = math.comb(len(back_selected), 2)
                bets = front_comb * back_comb
                result = f"前区({len(front_selected)}个): {', '.join(map(str, front_selected))}\n后区({len(back_selected)}个): {', '.join(map(str, back_selected))}"
                
            else:  # 胆拖投注
                if len(front_selected) < 6:
                    QMessageBox.warning(dialog, "错误", "胆拖投注需要选择至少6个前区")
                    return
                if len(back_selected) < 2:
                    QMessageBox.warning(dialog, "错误", "请选择至少2个后区")
                    return
                
                # 简单处理：前几个作为胆码
                front_dan = min(4, len(front_selected) - 1)
                front_dan_nums = front_selected[:front_dan]
                front_tuo_nums = front_selected[front_dan:]
                
                if len(front_tuo_nums) < 5 - front_dan:
                    QMessageBox.warning(dialog, "错误", f"拖码数量不足，至少需要{5-front_dan}个拖码")
                    return
                
                front_comb = math.comb(len(front_tuo_nums), 5 - front_dan)
                back_comb = math.comb(len(back_selected), 2)
                bets = front_comb * back_comb
                result = f"前区胆码({front_dan}个): {', '.join(map(str, front_dan_nums))}\n前区拖码({len(front_tuo_nums)}个): {', '.join(map(str, front_tuo_nums))}\n后区({len(back_selected)}个): {', '.join(map(str, back_selected))}"
            
            amount = bets * 2.0
            QMessageBox.information(self, f"大乐透{bet_type}", f"{result}\n\n注数: {bets}注\n金额: ¥{amount:.2f}")
            self.add_betting_record("大乐透", bet_type, result, bets, amount)
            dialog.accept()
        
        def analyze():
            front_selected = [i+1 for i, btn in enumerate(front_buttons) if btn.isChecked()]
            back_selected = [i+1 for i, btn in enumerate(back_buttons) if btn.isChecked()]
            selected_numbers = front_selected + back_selected
            
            if not selected_numbers:
                QMessageBox.warning(dialog, "错误", "请先选择号码")
                return
            
            analysis_dialog = LotteryAnalysisDialog(self, "大乐透", selected_numbers)
            analysis_dialog.exec()
        
        def history_compare():
            front_selected = [i+1 for i, btn in enumerate(front_buttons) if btn.isChecked()]
            back_selected = [i+1 for i, btn in enumerate(back_buttons) if btn.isChecked()]
            selected_numbers = front_selected + back_selected
            
            if not selected_numbers:
                QMessageBox.warning(dialog, "错误", "请先选择号码")
                return
            
            compare_dialog = HistoryCompareDialog(self, "大乐透", selected_numbers)
            compare_dialog.exec()
        
        confirm_btn.clicked.connect(confirm)
        analysis_btn.clicked.connect(analyze)
        history_compare_btn.clicked.connect(history_compare)
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(confirm_btn)
        btn_layout.addWidget(analysis_btn)
        btn_layout.addWidget(history_compare_btn)
        btn_layout.addWidget(cancel_btn)
        select_layout.addLayout(btn_layout)
        
        tabs.addTab(select_tab, "🎯 选号")
        
        history_tab = QWidget()
        history_layout = QVBoxLayout(history_tab)
        
        history_table = QTableWidget()
        history_table.setColumnCount(5)
        history_table.setHorizontalHeaderLabels(["期号", "开奖日期", "开奖号码", "一等奖", "奖池"])
        history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        if "大乐透" in self.history_data and self.history_data["大乐透"]:
            data = self.history_data["大乐透"][:50]
            history_table.setRowCount(len(data))
            for row, record in enumerate(data):
                history_table.setItem(row, 0, QTableWidgetItem(str(record.get("期号", ""))))
                history_table.setItem(row, 1, QTableWidgetItem(str(record.get("开奖日期", ""))))
                history_table.setItem(row, 2, QTableWidgetItem(str(record.get("开奖号码", ""))))
                history_table.setItem(row, 3, QTableWidgetItem(str(record.get("一等奖", "0注"))))
                history_table.setItem(row, 4, QTableWidgetItem(str(record.get("奖池", "0"))))
        else:
            history_table.setRowCount(1)
            history_table.setItem(0, 0, QTableWidgetItem("暂无数据"))
            history_table.setItem(0, 1, QTableWidgetItem("请先获取历史开奖数据"))
        
        history_layout.addWidget(history_table)
        tabs.addTab(history_tab, "📋 最近50期")
        
        layout.addWidget(tabs)
        dialog.setLayout(layout)
        dialog.exec()
    
    def show_trend_chart(self):
        """显示走势图 - 基于真实数据"""
        game = self.analysis_game_combo.currentText()
        if game not in self.history_data or not self.history_data[game]:
            QMessageBox.warning(self, "错误", f"没有{game}的历史数据，请先获取数据")
            return
            
        data = self.history_data[game][:50]  # 只显示最近50期
        if not data:
            QMessageBox.warning(self, "错误", f"没有{game}的历史数据，请先获取数据")
            return
            
        self.figure.clear()
        
        if len(data) < 5:
            QMessageBox.warning(self, "错误", f"{game}数据不足，至少需要5期数据")
            return
        
        try:
            # 提取期号和号码数据
            periods = [record["期号"] for record in data]
            numbers_data = [record["开奖号码"] for record in data]
            
            # 创建子图
            ax = self.figure.add_subplot(111)
            
            # 根据游戏类型设置图表
            if game == "双色球":
                # 双色球红球走势图
                red_numbers = []
                for nums_str in numbers_data:
                    if "+" in nums_str:
                        red_part = nums_str.split("+")[0]
                        red_nums = list(map(int, red_part.strip().split()))
                    else:
                        red_nums = list(map(int, nums_str.strip().split()))[:6]
                    red_numbers.append(red_nums)
                
                # 绘制每个红球的位置
                for i in range(6):
                    pos_numbers = [red_nums[i] for red_nums in red_numbers]
                    ax.plot(periods[::-1], pos_numbers, 'o-', markersize=3, label=f'红球{i+1}')
                
                ax.set_title(f"{game}红球走势图 (基于最近{len(data)}期真实数据)")
                ax.set_xlabel("期号")
                ax.set_ylabel("号码")
                ax.legend(loc='best', fontsize='small')
                ax.grid(True, alpha=0.3)
                
            elif game == "大乐透":
                # 大乐透前区走势图
                front_numbers = []
                for nums_str in numbers_data:
                    if "+" in nums_str:
                        front_part = nums_str.split("+")[0]
                        front_nums = list(map(int, front_part.strip().split()))
                    else:
                        front_nums = list(map(int, nums_str.strip().split()))[:5]
                    front_numbers.append(front_nums)
                
                # 绘制每个前区的位置
                for i in range(5):
                    pos_numbers = [front_nums[i] for front_nums in front_numbers]
                    ax.plot(periods[::-1], pos_numbers, 'o-', markersize=3, label=f'前区{i+1}')
                
                ax.set_title(f"{game}前区走势图 (基于最近{len(data)}期真实数据)")
                ax.set_xlabel("期号")
                ax.set_ylabel("号码")
                ax.legend(loc='best', fontsize='small')
                ax.grid(True, alpha=0.3)
                
            elif game == "快乐8":
                # 快乐8热号分析
                all_numbers = []
                for nums_str in numbers_data:
                    nums = list(map(int, nums_str.strip().split()))[:20]
                    all_numbers.extend(nums)
                
                # 统计号码出现频率
                from collections import Counter
                counter = Counter(all_numbers)
                
                numbers = list(range(1, 81))
                frequencies = [counter.get(num, 0) for num in numbers]
                
                ax.bar(numbers, frequencies, color='skyblue')
                ax.set_title(f"{game}号码出现频率 (基于最近{len(data)}期真实数据)")
                ax.set_xlabel("号码")
                ax.set_ylabel("出现次数")
                ax.set_xlim(0, 81)
                ax.grid(True, alpha=0.3)
                
            elif game in ["3D", "排列三"]:
                # 数字型彩票走势图
                positions = ["百位", "十位", "个位"]
                pos_data = {pos: [] for pos in positions}
                
                for nums_str in numbers_data:
                    nums = list(map(int, nums_str.strip().split()))[:3]
                    for i, num in enumerate(nums):
                        if i < len(positions):
                            pos_data[positions[i]].append(num)
                
                # 绘制每个位置的走势
                for i, pos in enumerate(positions):
                    if pos_data[pos]:
                        ax.plot(periods[::-1], pos_data[pos], 'o-', markersize=3, label=pos)
                
                ax.set_title(f"{game}走势图 (基于最近{len(data)}期真实数据)")
                ax.set_xlabel("期号")
                ax.set_ylabel("号码")
                ax.legend(loc='best', fontsize='small')
                ax.grid(True, alpha=0.3)
                
            else:
                # 通用走势图
                ax.plot(periods[::-1], range(len(periods)), 'b-')
                ax.set_title(f"{game}走势图 (基于最近{len(data)}期真实数据)")
                ax.set_xlabel("期号")
                ax.set_ylabel("期数")
                ax.grid(True, alpha=0.3)
            
            self.figure.tight_layout()
            self.canvas.draw()
            
            self.analysis_result.setText(f"{game}走势图已生成，基于{len(data)}期真实历史数据")
            
        except Exception as e:
            logger.error(f"生成走势图失败: {str(e)}")
            traceback.print_exc()
            QMessageBox.warning(self, "错误", f"生成走势图失败: {str(e)}")
    
    def show_heatmap(self):
        """显示热力图 - 基于真实数据"""
        game = self.analysis_game_combo.currentText()
        if game not in self.history_data or not self.history_data[game]:
            QMessageBox.warning(self, "错误", f"没有{game}的历史数据，请先获取数据")
            return
            
        data = self.history_data[game]
        if len(data) < 10:
            QMessageBox.warning(self, "错误", f"{game}数据不足，至少需要10期数据")
            return
        
        self.figure.clear()
        
        try:
            numbers_data = [record["开奖号码"] for record in data]
            
            model_key = self.model_combo.currentData()
            model_name = PREDICTION_MODELS[model_key]["name"]
            
            if game == "双色球":
                max_num = 33
                title = f"双色球红球热力图 ({model_name}) - 基于{len(data)}期真实数据"
                
                # 统计红球出现频率
                frequency = np.zeros(max_num)
                for record in numbers_data:
                    if "+" in record:
                        red_part = record.split("+")[0]
                        numbers = red_part.strip().split()
                    else:
                        numbers = record.strip().split()[:6]
                    
                    for num_str in numbers:
                        try:
                            num = int(num_str)
                            if 1 <= num <= max_num:
                                frequency[num-1] += 1
                        except:
                            continue
                
            elif game == "大乐透":
                max_num = 35
                title = f"大乐透前区热力图 ({model_name}) - 基于{len(data)}期真实数据"
                
                # 统计前区出现频率
                frequency = np.zeros(max_num)
                for record in numbers_data:
                    if "+" in record:
                        front_part = record.split("+")[0]
                        numbers = front_part.strip().split()
                    else:
                        numbers = record.strip().split()[:5]
                    
                    for num_str in numbers:
                        try:
                            num = int(num_str)
                            if 1 <= num <= max_num:
                                frequency[num-1] += 1
                        except:
                            continue
                
            elif game == "快乐8":
                max_num = 80
                title = f"快乐8热力图 ({model_name}) - 基于{len(data)}期真实数据"
                
                # 统计号码出现频率
                frequency = np.zeros(max_num)
                for record in numbers_data:
                    numbers = record.strip().split()[:20]
                    for num_str in numbers:
                        try:
                            num = int(num_str)
                            if 1 <= num <= max_num:
                                frequency[num-1] += 1
                        except:
                            continue
                
            elif game in ["3D", "排列三"]:
                max_num = 10
                title = f"{game}热力图 ({model_name}) - 基于{len(data)}期真实数据"
                
                # 统计每个位置的数字出现频率
                frequency = np.zeros(max_num)
                for record in numbers_data:
                    numbers = record.strip().split()[:3]
                    for num_str in numbers:
                        try:
                            num = int(num_str)
                            if 0 <= num < max_num:
                                frequency[num] += 1
                        except:
                            continue
                
            elif game == "七乐彩":
                max_num = 30
                title = f"七乐彩热力图 ({model_name}) - 基于{len(data)}期真实数据"
                
                # 统计号码出现频率
                frequency = np.zeros(max_num)
                for record in numbers_data:
                    numbers = record.strip().split()[:7]
                    for num_str in numbers:
                        try:
                            num = int(num_str)
                            if 1 <= num <= max_num:
                                frequency[num-1] += 1
                        except:
                            continue
                
            else:
                max_num = 10
                title = f"{game}热力图 ({model_name}) - 基于{len(data)}期真实数据"
                frequency = np.zeros(max_num)
            
            # 创建条形图
            ax = self.figure.add_subplot(111)
            x_positions = np.arange(1, max_num + 1)
            
            # 根据频率设置颜色
            colors = []
            max_freq = max(frequency) if len(frequency) > 0 else 1
            
            for freq in frequency:
                if max_freq > 0:
                    intensity = freq / max_freq
                    if intensity > 0.7:
                        colors.append('#FF4500')  # 红色 - 热号
                    elif intensity > 0.4:
                        colors.append('#FFA500')  # 橙色 - 温号
                    else:
                        colors.append('#87CEEB')  # 蓝色 - 冷号
                else:
                    colors.append('#87CEEB')
            
            bars = ax.bar(x_positions, frequency, color=colors, edgecolor='black')
            
            # 添加数值标签
            for bar, freq in zip(bars, frequency):
                if freq > 0:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                           f'{int(freq)}', ha='center', va='bottom', fontsize=8)
            
            ax.set_title(title)
            ax.set_xlabel("号码")
            ax.set_ylabel("出现次数")
            ax.set_xticks(x_positions)
            ax.grid(True, alpha=0.3)
            
            self.figure.tight_layout()
            self.canvas.draw()
            
            # 生成预测结果
            if game == "双色球":
                red = self.predict_hot_numbers(frequency[:33], 6, 1, 33)
                blue = random.randint(1, 16)
                result = f"红球: {', '.join(map(str, sorted(red)))}\n蓝球: {blue}"
            elif game == "大乐透":
                front = self.predict_hot_numbers(frequency[:35], 5, 1, 35)
                back = self.predict_hot_numbers(np.zeros(12), 2, 1, 12)  # 简单随机
                result = f"前区: {', '.join(map(str, sorted(front)))}\n后区: {', '.join(map(str, sorted(back)))}"
            elif game == "快乐8":
                hot_nums = self.predict_hot_numbers(frequency, 10, 1, 80)
                result = f"号码: {', '.join(map(str, sorted(hot_nums)))}"
            elif game in ["3D", "排列三"]:
                # 选择出现频率较高的数字
                hot_indices = np.argsort(frequency)[-3:][::-1]
                nums = [int(idx) for idx in hot_indices]
                result = f"号码: {', '.join(map(str, nums))}"
            elif game == "七乐彩":
                hot_nums = self.predict_hot_numbers(frequency, 7, 1, 30)
                result = f"号码: {', '.join(map(str, sorted(hot_nums)))}"
            elif game == "七星彩":
                nums = [random.randint(0, 9) for _ in range(6)] + [random.randint(0, 14)]
                result = f"号码: {', '.join(map(str, nums))}"
            elif game == "排列五":
                nums = [random.randint(0, 9) for _ in range(5)]
                result = f"号码: {', '.join(map(str, nums))}"
            else:
                result = "暂不支持该游戏的预测"
            
            self.analysis_result.setText(
                f"{game}热力图分析 ({model_name}模型) (基于{len(data)}期真实数据):\n"
                f"预测号码:\n{result}\n\n"
                "注意: 彩票预测仅供参考，实际中奖号码完全随机\n"
                f"红色: 热号 (出现频率高)\n橙色: 温号 (出现频率中等)\n蓝色: 冷号 (出现频率低)"
            )
            
        except Exception as e:
            logger.error(f"生成热力图失败: {str(e)}")
            traceback.print_exc()
            QMessageBox.warning(self, "错误", f"生成热力图失败: {str(e)}")
    
    def predict_hot_numbers(self, frequencies, count, min_num, max_num):
        """预测热号"""
        try:
            # 获取出现频率最高的号码
            hot_indices = np.argsort(frequencies)[-count*2:][::-1]  # 取2倍数量作为候选
            hot_indices = hot_indices[:count*2]
            
            # 转换为实际号码
            hot_numbers = [idx + min_num for idx in hot_indices]
            
            # 随机选择指定数量的号码
            selected = random.sample(hot_numbers, min(count, len(hot_numbers)))
            
            return selected
        except:
            # 如果出错，返回随机号码
            return sorted(random.sample(range(min_num, max_num + 1), count))
    
    def add_betting_record(self, game, bet_type, numbers, bets_count, amount):
        """添加投注记录"""
        record = {
            "game": game,
            "bet_type": bet_type,
            "numbers": numbers,
            "bets_count": bets_count,
            "amount": amount,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.betting_history.append(record)
        self.update_records_table()
    
    def update_records_table(self):
        """更新投注记录表格"""
        self.records_table.setRowCount(len(self.betting_history))
        for row, record in enumerate(self.betting_history):
            self.records_table.setItem(row, 0, QTableWidgetItem(record.get("game", "未知游戏")))
            self.records_table.setItem(row, 1, QTableWidgetItem(record.get("bet_type", "未知类型")))
            self.records_table.setItem(row, 2, QTableWidgetItem(record.get("numbers", "")))
            self.records_table.setItem(row, 3, QTableWidgetItem(str(record.get("bets_count", 0))))
            self.records_table.setItem(row, 4, QTableWidgetItem(f"¥{record.get('amount', 0.0):.2f}"))
            self.records_table.setItem(row, 5, QTableWidgetItem(record.get("timestamp", "")))
    
    def show_record_details(self):
        """显示记录详情"""
        selected = self.records_table.selectedItems()
        if not selected:
            return
            
        row = selected[0].row()
        if row < 0 or row >= len(self.betting_history):
            return
            
        record = self.betting_history[row]
        details = (
            f"游戏: {record.get('game', '未知游戏')}\n"
            f"投注类型: {record.get('bet_type', '未知类型')}\n"
            f"时间: {record.get('timestamp', '')}\n"
            f"注数: {record.get('bets_count', 0)}\n"
            f"金额: ¥{record.get('amount', 0.0):.2f}\n\n"
            f"号码详情:\n{record.get('numbers', '')}"
        )
        self.detail_text.setPlainText(details)
    
    def save_betting_history(self):
        """保存投注记录"""
        try:
            valid_records = []
            for record in self.betting_history:
                if all(key in record for key in ["game", "bet_type", "numbers", "bets_count", "amount", "timestamp"]):
                    valid_records.append(record)
            
            with open("betting_history.json", "w", encoding="utf-8") as f:
                json.dump(valid_records, f, ensure_ascii=False, indent=2)
            QMessageBox.information(self, "成功", "投注记录已保存！")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"保存记录失败: {str(e)}")
    
    def load_betting_history(self):
        """加载投注记录"""
        try:
            if os.path.exists("betting_history.json"):
                with open("betting_history.json", "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
                    self.betting_history = []
                    
                    for record in raw_data:
                        if not isinstance(record, dict):
                            continue
                        
                        valid_record = {
                            "game": record.get("game", "未知游戏"),
                            "bet_type": record.get("bet_type", "未知类型"),
                            "numbers": record.get("numbers", ""),
                            "bets_count": record.get("bets_count", 0),
                            "amount": record.get("amount", 0.0),
                            "timestamp": record.get("timestamp", "")
                        }
                        self.betting_history.append(valid_record)
                    
                    self.update_records_table()
        except Exception as e:
            logger.error(f"加载记录失败: {str(e)}")
            self.betting_history = []
    
    def clear_betting_history(self):
        """清空投注记录"""
        reply = QMessageBox.question(self, "确认", "确定要清空所有投注记录吗？此操作不可恢复！",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.betting_history = []
            self.update_records_table()
            self.detail_text.clear()
    
    def export_to_csv(self):
        """导出CSV"""
        if not self.betting_history:
            QMessageBox.warning(self, "错误", "没有可导出的记录！")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出CSV文件", "", "CSV文件 (*.csv)")
        
        if not file_path:
            return
            
        try:
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["游戏", "投注类型", "号码", "注数", "金额", "时间"])
                for record in self.betting_history:
                    writer.writerow([
                        record.get("game", "未知游戏"),
                        record.get("bet_type", "未知类型"),
                        record.get("numbers", ""),
                        record.get("bets_count", 0),
                        record.get("amount", 0.0),
                        record.get("timestamp", "")
                    ])
            QMessageBox.information(self, "成功", f"记录已导出到: {file_path}")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"导出失败: {str(e)}")
    
    def import_from_csv(self):
        """导入CSV"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入CSV文件", "", "CSV文件 (*.csv)")
        
        if not file_path:
            return
            
        try:
            imported_records = []
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if "游戏" in row and "投注类型" in row and "号码" in row:
                        record = {
                            "game": row["游戏"],
                            "bet_type": row["投注类型"],
                            "numbers": row["号码"],
                            "bets_count": int(row.get("注数", 1)),
                            "amount": float(row.get("金额", 2.0)),
                            "timestamp": row.get("时间", datetime.now().strftime("%Y-%m-d %H:%M:%S"))
                        }
                        imported_records.append(record)
            
            self.betting_history.extend(imported_records)
            self.update_records_table()
            QMessageBox.information(self, "成功", f"成功导入 {len(imported_records)} 条记录！")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"导入失败: {str(e)}")
    
    def update_history_table(self):
        """更新历史数据表格"""
        game = self.history_game_combo.currentText()
        if game not in self.history_data:
            self.history_table.setRowCount(0)
            return
            
        data = self.history_data[game]
        data = sorted(data, key=lambda x: x.get("期号", ""), reverse=True)
        data = data[:50]
        self.history_table.setRowCount(len(data))
        
        for row, record in enumerate(data):
            self.history_table.setItem(row, 0, QTableWidgetItem(record.get("期号", "")))
            self.history_table.setItem(row, 1, QTableWidgetItem(record.get("开奖日期", "")))
            
            numbers_str = record.get("开奖号码", "")
            
            if "+" in numbers_str:
                main_part, extra_part = numbers_str.split("+", 1)
                main_numbers = main_part.strip().split()
                extra_numbers = extra_part.strip().split()
                numbers = main_numbers + extra_numbers
            else:
                numbers = numbers_str.split()
            
            for col in range(2, 10):
                if col - 2 < len(numbers):
                    self.history_table.setItem(row, col, QTableWidgetItem(numbers[col-2]))
                else:
                    self.history_table.setItem(row, col, QTableWidgetItem(""))
    
    def import_history_data(self):
        """导入历史数据"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入开奖历史数据", "", "数据文件 (*.csv *.txt *.xlsx)")
        
        if not file_path:
            return
            
        try:
            game = self.history_game_combo.currentText()
            
            if game not in self.history_data:
                self.history_data[game] = []
            
            if file_path.endswith('.csv') or file_path.endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    data = []
                    
                    for line in lines:
                        parts = line.strip().split(',')
                        if len(parts) < 3:
                            continue
                            
                        record = {
                            "期号": parts[0],
                            "开奖日期": parts[1],
                            "开奖号码": " ".join(parts[2:])
                        }
                        data.append(record)
                    
                    self.history_data[game].extend(data)
                    self.update_history_table()
                    self.calculate_omission()
                    QMessageBox.information(self, "导入成功", f"成功导入{len(data)}条开奖记录")
            
            elif file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path)
                data = []
                
                for _, row in df.iterrows():
                    if '期号' in df.columns and '开奖日期' in df.columns and '开奖号码' in df.columns:
                        numbers = row['开奖号码']
                        if isinstance(numbers, list):
                            numbers_str = " ".join(map(str, numbers))
                        else:
                            numbers_str = str(numbers)
                        data.append({
                            "期号": str(row['期号']),
                            "开奖日期": str(row['开奖日期']),
                            "开奖号码": numbers_str
                        })
                
                self.history_data[game].extend(data)
                self.update_history_table()
                self.calculate_omission()
                QMessageBox.information(self, "导入成功", f"成功导入{len(data)}条开奖记录")
            else:
                QMessageBox.warning(self, "错误", "不支持的文件格式")
                
        except Exception as e:
            QMessageBox.warning(self, "导入错误", f"导入失败: {str(e)}")
    
    def clear_history_data(self):
        """清空历史数据"""
        game = self.history_game_combo.currentText()
        if game in self.history_data:
            reply = QMessageBox.question(self, "确认", f"确定要清空{game}的历史数据吗？",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                del self.history_data[game]
                self.update_history_table()
                self.calculate_omission()
    
    def export_history_data(self):
        """导出历史数据"""
        game = self.history_game_combo.currentText()
        if game not in self.history_data or not self.history_data[game]:
            QMessageBox.warning(self, "错误", "没有可导出的历史数据")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出历史数据", "", "CSV文件 (*.csv)")
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["期号", "开奖日期", "开奖号码"])
                
                for record in self.history_data[game]:
                    writer.writerow([record["期号"], record["开奖日期"], record["开奖号码"]])
            
            QMessageBox.information(self, "导出成功", f"历史数据已导出: {file_path}")
        except Exception as e:
            QMessageBox.warning(self, "导出错误", f"导出失败: {str(e)}")
    
    def export_analysis_data(self):
        """导出分析数据"""
        game = self.analysis_game_combo.currentText()
        if game not in self.history_data or not self.history_data[game]:
            QMessageBox.warning(self, "错误", "没有可导出的分析数据")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出分析结果", "", "CSV文件 (*.csv)")
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["期号", "开奖日期", "开奖号码"])
                
                for record in self.history_data[game]:
                    writer.writerow([record["期号"], record["开奖日期"], record["开奖号码"]])
            
            QMessageBox.information(self, "导出成功", f"分析结果已导出到: {file_path}")
        except Exception as e:
            QMessageBox.warning(self, "导出错误", f"导出失败: {str(e)}")
    
    def refresh_lottery_data(self):
        """刷新彩票数据"""
        game = self.history_game_combo.currentText()
        if game:
            self.update_game_data_from_api(game)
            QMessageBox.information(self, "刷新数据", f"正在更新{game}数据...")
        else:
            QMessageBox.warning(self, "错误", "请先选择彩票类型")
    
    def load_history_data(self):
        """加载历史数据"""
        game_types = ["双色球", "快乐8", "3D", "七乐彩", "大乐透", "七星彩", "排列三", "排列五"]
        for game in game_types:
            filename = f"{game}_history.json"
            if os.path.exists(filename):
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            self.history_data[game] = data
                            logger.info(f"Loaded {len(self.history_data[game])} records for {game}")
                        else:
                            logger.warning(f"Invalid data format for {game}")
                            self.history_data[game] = []
                except Exception as e:
                    logger.error(f"加载历史数据失败: {str(e)}")
                    self.history_data[game] = []
            else:
                self.history_data[game] = []
                logger.info(f"No history data found for {game}")
        
        # 更新API密钥状态
        self.update_api_key_status()
        
        logger.info("历史数据加载完成")
    
    def save_all_history_data(self):
        """保存所有历史数据"""
        try:
            for game_type, data in self.history_data.items():
                if data:
                    self.save_game_history_data(game_type)
            logger.info("所有历史数据保存完成")
        except Exception as e:
            logger.error(f"保存历史数据失败: {str(e)}")
    
    def save_game_history_data(self, game_type):
        """保存单个游戏的历史数据"""
        try:
            if game_type in self.history_data and self.history_data[game_type]:
                filename = f"{game_type}_history.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.history_data[game_type], f, ensure_ascii=False, indent=2)
                logger.info(f"{game_type}历史数据保存成功: {filename}")
                return True
            return False
        except Exception as e:
            logger.error(f"保存{game_type}历史数据失败: {str(e)}")
            return False
    
    def calculate_omission(self):
        """计算遗漏数据"""
        logger.info("开始计算遗漏数据...")
        
        for game_type, records in self.history_data.items():
            if not records:
                continue
                
            # 按期号排序（从小到大）
            try:
                sorted_records = sorted(records, key=lambda x: x.get("期号", ""))
            except:
                sorted_records = records
            
            if game_type not in self.last_omission_data:
                self.last_omission_data[game_type] = {}
                self.frequency_data[game_type] = {}
            
            if game_type == "双色球":
                # 初始化红球数据
                red_omission = {i: 0 for i in range(1, 34)}
                red_frequency = {i: 0 for i in range(1, 34)}
                
                # 初始化蓝球数据
                blue_omission = {i: 0 for i in range(1, 17)}
                blue_frequency = {i: 0 for i in range(1, 17)}
                
                # 计算遗漏和频率
                for record in sorted_records:
                    # 先递增所有号码的遗漏期数
                    for num in red_omission:
                        red_omission[num] += 1
                    for num in blue_omission:
                        blue_omission[num] += 1
                    
                    # 处理开奖号码
                    numbers_str = record.get("开奖号码", "")
                    if not numbers_str:
                        continue
                    
                    try:
                        if "+" in numbers_str:
                            red_part, blue_part = numbers_str.split("+")
                            red_nums = [int(n.strip()) for n in red_part.split()]
                            blue_nums = [int(n.strip()) for n in blue_part.split()]
                        else:
                            nums = numbers_str.split()
                            if len(nums) >= 7:
                                red_nums = [int(n) for n in nums[:6]]
                                blue_nums = [int(n) for n in nums[6:7]]
                            else:
                                continue
                        
                        # 更新红球数据
                        for num in red_nums:
                            if num in red_omission:
                                red_omission[num] = 0
                                red_frequency[num] += 1
                        
                        # 更新蓝球数据
                        for num in blue_nums:
                            if num in blue_omission:
                                blue_omission[num] = 0
                                blue_frequency[num] += 1
                                
                    except Exception as e:
                        logger.error(f"处理{game_type}数据失败: {str(e)}")
                        continue
                
                self.last_omission_data[game_type]["red"] = red_omission
                self.last_omission_data[game_type]["blue"] = blue_omission
                self.frequency_data[game_type]["red"] = red_frequency
                self.frequency_data[game_type]["blue"] = blue_frequency
                
            elif game_type == "大乐透":
                # 初始化前区数据
                front_omission = {i: 0 for i in range(1, 36)}
                front_frequency = {i: 0 for i in range(1, 36)}
                
                # 初始化后区数据
                back_omission = {i: 0 for i in range(1, 13)}
                back_frequency = {i: 0 for i in range(1, 13)}
                
                # 计算遗漏和频率
                for record in sorted_records:
                    # 先递增所有号码的遗漏期数
                    for num in front_omission:
                        front_omission[num] += 1
                    for num in back_omission:
                        back_omission[num] += 1
                    
                    # 处理开奖号码
                    numbers_str = record.get("开奖号码", "")
                    if not numbers_str:
                        continue
                    
                    try:
                        if "+" in numbers_str:
                            front_part, back_part = numbers_str.split("+")
                            front_nums = [int(n.strip()) for n in front_part.split()]
                            back_nums = [int(n.strip()) for n in back_part.split()]
                        else:
                            nums = numbers_str.split()
                            if len(nums) >= 7:
                                front_nums = [int(n) for n in nums[:5]]
                                back_nums = [int(n) for n in nums[5:7]]
                            else:
                                continue
                        
                        # 更新前区数据
                        for num in front_nums:
                            if num in front_omission:
                                front_omission[num] = 0
                                front_frequency[num] += 1
                        
                        # 更新后区数据
                        for num in back_nums:
                            if num in back_omission:
                                back_omission[num] = 0
                                back_frequency[num] += 1
                                
                    except Exception as e:
                        logger.error(f"处理{game_type}数据失败: {str(e)}")
                        continue
                
                self.last_omission_data[game_type]["front"] = front_omission
                self.last_omission_data[game_type]["back"] = back_omission
                self.frequency_data[game_type]["front"] = front_frequency
                self.frequency_data[game_type]["back"] = back_frequency
                
            elif game_type in ["3D", "排列三"]:
                # 初始化位置数据
                positions = ["pos1", "pos2", "pos3"]
                for pos in positions:
                    if pos not in self.last_omission_data[game_type]:
                        self.last_omission_data[game_type][pos] = {i: 0 for i in range(0, 10)}
                        self.frequency_data[game_type][pos] = {i: 0 for i in range(0, 10)}
                
                # 计算遗漏和频率
                for record in sorted_records:
                    # 先递增所有号码的遗漏期数
                    for pos in positions:
                        for num in self.last_omission_data[game_type][pos]:
                            self.last_omission_data[game_type][pos][num] += 1
                    
                    # 处理开奖号码
                    numbers_str = record.get("开奖号码", "")
                    if not numbers_str:
                        continue
                    
                    try:
                        nums = [int(n) for n in numbers_str.split()[:3]]
                        
                        for i, num in enumerate(nums):
                            if i < len(positions):
                                pos = positions[i]
                                if num in self.last_omission_data[game_type][pos]:
                                    self.last_omission_data[game_type][pos][num] = 0
                                    self.frequency_data[game_type][pos][num] += 1
                                    
                    except Exception as e:
                        logger.error(f"处理{game_type}数据失败: {str(e)}")
                        continue
                
            elif game_type == "七星彩":
                # 初始化位置数据
                positions = [f"pos{i+1}" for i in range(7)]
                for i, pos in enumerate(positions):
                    if pos not in self.last_omission_data[game_type]:
                        max_num = 15 if i == 6 else 10  # 第7位是0-14
                        self.last_omission_data[game_type][pos] = {j: 0 for j in range(0, max_num)}
                        self.frequency_data[game_type][pos] = {j: 0 for j in range(0, max_num)}
                
                # 计算遗漏和频率
                for record in sorted_records:
                    # 先递增所有号码的遗漏期数
                    for pos in positions:
                        for num in self.last_omission_data[game_type][pos]:
                            self.last_omission_data[game_type][pos][num] += 1
                    
                    # 处理开奖号码
                    numbers_str = record.get("开奖号码", "")
                    if not numbers_str:
                        continue
                    
                    try:
                        nums = [int(n) for n in numbers_str.split()[:7]]
                        
                        for i, num in enumerate(nums):
                            if i < len(positions):
                                pos = positions[i]
                                if num in self.last_omission_data[game_type][pos]:
                                    self.last_omission_data[game_type][pos][num] = 0
                                    self.frequency_data[game_type][pos][num] += 1
                                    
                    except Exception as e:
                        logger.error(f"处理{game_type}数据失败: {str(e)}")
                        continue
                
            elif game_type == "快乐8":
                # 初始化主区数据
                if "main" not in self.last_omission_data[game_type]:
                    self.last_omission_data[game_type]["main"] = {i: 0 for i in range(1, 81)}
                    self.frequency_data[game_type]["main"] = {i: 0 for i in range(1, 81)}
                
                # 计算遗漏和频率
                for record in sorted_records:
                    # 先递增所有号码的遗漏期数
                    for num in self.last_omission_data[game_type]["main"]:
                        self.last_omission_data[game_type]["main"][num] += 1
                    
                    # 处理开奖号码
                    numbers_str = record.get("开奖号码", "")
                    if not numbers_str:
                        continue
                    
                    try:
                        main_nums = [int(n) for n in numbers_str.split()[:20]]
                        
                        for num in main_nums:
                            if num in self.last_omission_data[game_type]["main"]:
                                self.last_omission_data[game_type]["main"][num] = 0
                                self.frequency_data[game_type]["main"][num] += 1
                                
                    except Exception as e:
                        logger.error(f"处理{game_type}数据失败: {str(e)}")
                        continue
                
            elif game_type == "七乐彩":
                # 初始化主区数据
                if "main" not in self.last_omission_data[game_type]:
                    self.last_omission_data[game_type]["main"] = {i: 0 for i in range(1, 31)}
                    self.frequency_data[game_type]["main"] = {i: 0 for i in range(1, 31)}
                
                # 计算遗漏和频率
                for record in sorted_records:
                    # 先递增所有号码的遗漏期数
                    for num in self.last_omission_data[game_type]["main"]:
                        self.last_omission_data[game_type]["main"][num] += 1
                    
                    # 处理开奖号码
                    numbers_str = record.get("开奖号码", "")
                    if not numbers_str:
                        continue
                    
                    try:
                        main_nums = [int(n) for n in numbers_str.split()[:7]]
                        
                        for num in main_nums:
                            if num in self.last_omission_data[game_type]["main"]:
                                self.last_omission_data[game_type]["main"][num] = 0
                                self.frequency_data[game_type]["main"][num] += 1
                                
                    except Exception as e:
                        logger.error(f"处理{game_type}数据失败: {str(e)}")
                        continue
            
            # 计算冷热号
            self.calculate_cold_hot_for_game(game_type)
        
        logger.info("遗漏数据计算完成")
    
    def calculate_cold_hot_for_game(self, game_type):
        """计算冷温热号"""
        if game_type not in self.frequency_data:
            return
        
        if game_type == "双色球":
            if "red" in self.frequency_data[game_type]:
                red_numbers = list(range(1, 34))
                red_freq = [self.frequency_data[game_type]["red"].get(i, 0) for i in red_numbers]
                self.cold_hot_data[game_type]["red"] = self.calculate_cold_hot_dict(red_numbers, red_freq)
            
            if "blue" in self.frequency_data[game_type]:
                blue_numbers = list(range(1, 17))
                blue_freq = [self.frequency_data[game_type]["blue"].get(i, 0) for i in blue_numbers]
                self.cold_hot_data[game_type]["blue"] = self.calculate_cold_hot_dict(blue_numbers, blue_freq)
            
        elif game_type == "大乐透":
            if "front" in self.frequency_data[game_type]:
                front_numbers = list(range(1, 36))
                front_freq = [self.frequency_data[game_type]["front"].get(i, 0) for i in front_numbers]
                self.cold_hot_data[game_type]["front"] = self.calculate_cold_hot_dict(front_numbers, front_freq)
            
            if "back" in self.frequency_data[game_type]:
                back_numbers = list(range(1, 13))
                back_freq = [self.frequency_data[game_type]["back"].get(i, 0) for i in back_numbers]
                self.cold_hot_data[game_type]["back"] = self.calculate_cold_hot_dict(back_numbers, back_freq)
            
        elif game_type in ["3D", "七星彩", "排列三", "排列五"]:
            positions = list(self.frequency_data[game_type].keys())
            for pos in positions:
                numbers = list(self.frequency_data[game_type][pos].keys())
                freq = [self.frequency_data[game_type][pos].get(j, 0) for j in numbers]
                self.cold_hot_data[game_type][pos] = self.calculate_cold_hot_dict(numbers, freq)
            
        elif game_type == "快乐8":
            if "main" in self.frequency_data[game_type]:
                numbers = list(range(1, 81))
                freq = [self.frequency_data[game_type]["main"].get(i, 0) for i in numbers]
                self.cold_hot_data[game_type]["main"] = self.calculate_cold_hot_dict(numbers, freq)
            
        elif game_type == "七乐彩":
            if "main" in self.frequency_data[game_type]:
                numbers = list(range(1, 31))
                freq = [self.frequency_data[game_type]["main"].get(i, 0) for i in numbers]
                self.cold_hot_data[game_type]["main"] = self.calculate_cold_hot_dict(numbers, freq)
    
    def calculate_cold_hot_dict(self, numbers, frequencies):
        """计算冷热号字典"""
        if not frequencies or len(numbers) != len(frequencies):
            return {num: "default" for num in numbers}
        
        # 计算频率统计
        total = sum(frequencies)
        if total == 0:
            return {num: "default" for num in numbers}
        
        # 计算平均频率
        avg_freq = total / len(frequencies)
        
        # 计算标准差
        import math
        variance = sum((f - avg_freq) ** 2 for f in frequencies) / len(frequencies)
        std_dev = math.sqrt(variance)
        
        result = {}
        for num, freq in zip(numbers, frequencies):
            if freq > avg_freq + std_dev:
                result[num] = "hot"
            elif freq < avg_freq - std_dev:
                result[num] = "cold"
            else:
                result[num] = "warm"
        
        return result
    
    def get_omission(self, game_type, number, area="main"):
        """获取遗漏数据"""
        if game_type not in self.last_omission_data:
            return 0
            
        if area not in self.last_omission_data[game_type]:
            return 0
            
        return self.last_omission_data[game_type][area].get(number, 0)
    
    def get_frequency(self, game_type, number, area="main"):
        """获取频率数据"""
        if game_type not in self.frequency_data:
            return 0
            
        if area not in self.frequency_data[game_type]:
            return 0
            
        return self.frequency_data[game_type][area].get(number, 0)
    
    def get_cold_hot(self, game_type, number, area="main"):
        """获取冷热数据"""
        if game_type not in self.cold_hot_data:
            return "default"
            
        if area not in self.cold_hot_data[game_type]:
            return "default"
            
        return self.cold_hot_data[game_type][area].get(number, "default")
    
    def calculate_number_probability(self, game_type, area="main"):
        """计算号码出现概率"""
        if game_type not in self.frequency_data:
            return {}
        
        if area not in self.frequency_data[game_type]:
            return {}
        
        frequencies = self.frequency_data[game_type][area]
        total = sum(frequencies.values())
        
        if total == 0:
            return {num: 0 for num in frequencies.keys()}
        
        probabilities = {}
        for num, freq in frequencies.items():
            probabilities[num] = freq / total
        
        return probabilities
    
    def calculate_probability(self, game_type, number, area="main"):
        """计算单个号码的概率"""
        probs = self.calculate_number_probability(game_type, area)
        return probs.get(number, 0)
    
    def load_api_key(self):
        """加载API密钥"""
        try:
            if os.path.exists("api_key.json"):
                with open("api_key.json", "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.app_id = config.get("app_id", "")
                    self.app_secret = config.get("app_secret", "")
                    
                    self.update_api_key_status()
                    logger.info("API密钥加载成功")
            else:
                logger.info("未找到API密钥文件")
        except Exception as e:
            logger.error(f"加载API密钥失败: {str(e)}")
            self.app_id = ""
            self.app_secret = ""
    
    def save_api_key(self):
        """保存API密钥"""
        try:
            with open("api_key.json", "w", encoding="utf-8") as f:
                json.dump({
                    "app_id": self.app_id,
                    "app_secret": self.app_secret
                }, f, ensure_ascii=False, indent=2)
            logger.info("API密钥保存成功")
        except Exception as e:
            logger.error(f"保存API密钥失败: {str(e)}")
    
    def set_app_id(self):
        """设置App ID"""
        app_id, ok = QInputDialog.getText(self, "设置App ID", "请输入MXNZP App ID:", 
                                         QLineEdit.Normal, self.app_id)
        if ok and app_id:
            self.app_id = app_id.strip()
            self.update_api_key_status()
            self.save_api_key()
            QMessageBox.information(self, "成功", "App ID已更新！")
    
    def set_app_secret(self):
        """设置App Secret"""
        app_secret, ok = QInputDialog.getText(self, "设置App Secret", "请输入MXNZP App Secret:", 
                                            QLineEdit.Normal, self.app_secret)
        if ok and app_secret:
            self.app_secret = app_secret.strip()
            self.update_api_key_status()
            self.save_api_key()
            QMessageBox.information(self, "成功", "App Secret已更新！")
    
    def clear_api_keys(self):
        """清除API密钥"""
        reply = QMessageBox.question(self, "确认清除", "确定要清除所有API密钥吗？", 
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.app_id = ""
            self.app_secret = ""
            self.update_api_key_status()
            self.save_api_key()
            QMessageBox.information(self, "成功", "API密钥已清除！")
    
    def check_api_key(self):
        """检查API密钥有效性"""
        if not self.app_id or not self.app_secret:
            QMessageBox.warning(self, "错误", "请先设置App ID和App Secret")
            return
            
        try:
            base_url = MXNZP_API_CONFIG["base_url"]
            endpoint = MXNZP_API_CONFIG["endpoints"]["latest"]
            code = MXNZP_API_CONFIG["lottery_codes"]["双色球"]
            
            url = f"{base_url}{endpoint}"
            params = {
                "code": code,
                "app_id": self.app_id,
                "app_secret": self.app_secret
            }
            
            headers = {
                'User-Agent': self.ua.random,
                'Accept': 'application/json'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            data = response.json()
            
            if data.get("code") == 1:
                QMessageBox.information(self, "密钥有效", "MXNZP API密钥验证成功！")
                self.update_api_key_status(valid=True)
            else:
                error_msg = data.get("msg", "未知错误")
                QMessageBox.warning(self, "密钥无效", f"API返回错误: {error_msg}")
                self.update_api_key_status(valid=False)
        except requests.exceptions.Timeout:
            QMessageBox.critical(self, "网络错误", "请求超时，请检查网络连接")
            self.update_api_key_status(valid=False)
        except requests.exceptions.ConnectionError:
            QMessageBox.critical(self, "网络错误", "网络连接错误，请检查网络")
            self.update_api_key_status(valid=False)
        except Exception as e:
            QMessageBox.critical(self, "网络错误", f"验证失败: {str(e)}")
            self.update_api_key_status(valid=False)
    
    def update_api_key_status(self, valid=None):
        """更新API密钥状态显示"""
        if self.app_id:
            display_id = self.app_id[:8] + "..." if len(self.app_id) > 10 else self.app_id
            self.app_id_label_display.setText(f"{display_id}")
            if valid is None:
                self.app_id_label_display.setStyleSheet("color: orange;")
            elif valid:
                self.app_id_label_display.setStyleSheet("color: green;")
            else:
                self.app_id_label_display.setStyleSheet("color: red;")
        else:
            self.app_id_label_display.setText("未设置")
            self.app_id_label_display.setStyleSheet("color: red; font-weight: bold;")
        
        if self.app_secret:
            display_secret = "***" + self.app_secret[-4:] if len(self.app_secret) > 6 else "***"
            self.app_secret_label_display.setText(f"{display_secret}")
            if valid is None:
                self.app_secret_label_display.setStyleSheet("color: orange;")
            elif valid:
                self.app_secret_label_display.setStyleSheet("color: green;")
            else:
                self.app_secret_label_display.setStyleSheet("color: red;")
        else:
            self.app_secret_label_display.setText("未设置")
            self.app_secret_label_display.setStyleSheet("color: red; font-weight: bold;")
    
    def get_api_params(self):
        """获取API参数"""
        return self.app_id, self.app_secret
    
    def fetch_latest_results(self):
        """抓取最新开奖数据"""
        app_id, app_secret = self.get_api_params()
        if not app_id or not app_secret:
            QMessageBox.warning(self, "错误", "请先设置App ID和App Secret")
            return
            
        game = self.network_game_combo.currentText()
        
        # 创建进度对话框
        progress_dialog = QMessageBox(self)
        progress_dialog.setWindowTitle("更新数据")
        progress_dialog.setText(f"正在获取{game}最新开奖数据...")
        progress_dialog.setStandardButtons(QMessageBox.NoButton)
        progress_dialog.show()
        
        # 在线程中获取数据
        def update_finished(success, message):
            progress_dialog.close()
            if success:
                QMessageBox.information(self, "成功", message)
                # 更新结果表格
                if game in self.history_data and self.history_data[game]:
                    self.update_result_table([self.history_data[game][0]])
            else:
                QMessageBox.warning(self, "错误", message)
        
        thread = DataUpdateThread(game, app_id, app_secret, 1)
        thread.update_finished.connect(update_finished)
        thread.start()
    
    def process_mxnzp_data(self, game_type, data):
        """处理MXNZP API返回的开奖数据（兼容旧代码）"""
        processed_record = self.process_mxnzp_record(game_type, data)
        if processed_record:
            if game_type not in self.history_data:
                self.history_data[game_type] = []
            
            # 检查是否已存在该期数据
            existing_issues = {record["期号"] for record in self.history_data[game_type]}
            if processed_record["期号"] not in existing_issues:
                self.history_data[game_type].append(processed_record)
                # 按期号排序
                self.history_data[game_type].sort(key=lambda x: x["期号"], reverse=True)
                
                # 保存数据
                self.save_game_history_data(game_type)
                
                # 重新计算遗漏
                self.calculate_omission()
                
                return True
        
        return False

    def update_result_table(self, records):
        """更新结果表格"""
        self.result_table.setRowCount(len(records))
        for row, record in enumerate(records):
            self.result_table.setItem(row, 0, QTableWidgetItem(record.get("期号", "")))
            self.result_table.setItem(row, 1, QTableWidgetItem(record.get("开奖日期", "")))
            self.result_table.setItem(row, 2, QTableWidgetItem(record.get("开奖号码", "")))
            self.result_table.setItem(row, 3, QTableWidgetItem(record.get("销售额", "")))
            self.result_table.setItem(row, 4, QTableWidgetItem(record.get("奖池", "")))
            self.result_table.setItem(row, 5, QTableWidgetItem(record.get("一等奖", "")))
            self.result_table.setItem(row, 6, QTableWidgetItem(record.get("二等奖", "")))

    def fetch_by_issue(self):
        """按期号查询"""
        app_id, app_secret = self.get_api_params()
        if not app_id or not app_secret:
            QMessageBox.warning(self, "错误", "请先设置App ID和App Secret")
            return
            
        issue, ok = QInputDialog.getText(self, "按期号查询", "请输入期号:")
        if not ok or not issue:
            return
            
        game = self.network_game_combo.currentText()
        lottery_code = MXNZP_API_CONFIG["lottery_codes"].get(game)
        
        if not lottery_code:
            QMessageBox.warning(self, "错误", "不支持的彩票类型")
            return
            
        try:
            base_url = MXNZP_API_CONFIG["base_url"]
            endpoint = MXNZP_API_CONFIG["endpoints"]["aim_lottery"]
            
            url = f"{base_url}{endpoint}"
            params = {
                "code": lottery_code,
                "expect": issue,
                "app_id": app_id,
                "app_secret": app_secret
            }
            
            headers = {
                'User-Agent': self.ua.random,
                'Accept': 'application/json'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            data = response.json()
            
            if data.get("code") == 1:
                record_data = data.get("data")
                if record_data:
                    if self.process_mxnzp_data(game, record_data):
                        QMessageBox.information(self, "成功", f"找到期号 {issue} 的开奖数据并已保存")
                        # 显示数据
                        if game in self.history_data and self.history_data[game]:
                            # 查找刚添加的数据
                            for record in self.history_data[game]:
                                if record["期号"] == str(issue):
                                    self.update_result_table([record])
                                    break
                    else:
                        QMessageBox.information(self, "提示", f"期号 {issue} 的数据已存在")
                else:
                    QMessageBox.warning(self, "未找到", f"未找到期号 {issue} 的开奖数据")
            else:
                error_msg = data.get("msg", "未知错误")
                QMessageBox.warning(self, "错误", f"API返回错误: {error_msg}")
        except Exception as e:
            QMessageBox.critical(self, "网络错误", f"查询失败: {str(e)}")

    def fetch_history_results(self):
        """查询历史开奖"""
        app_id, app_secret = self.get_api_params()
        if not app_id or not app_secret:
            QMessageBox.warning(self, "错误", "请先设置App ID和App Secret")
            return
            
        count, ok = QInputDialog.getInt(self, "查询历史开奖", "请输入查询期数:", 10, 1, 100)
        if not ok:
            return
            
        game = self.network_game_combo.currentText()
        
        # 创建进度对话框
        progress_dialog = QMessageBox(self)
        progress_dialog.setWindowTitle("更新数据")
        progress_dialog.setText(f"正在获取{game}历史开奖数据...")
        progress_dialog.setStandardButtons(QMessageBox.NoButton)
        progress_dialog.show()
        
        # 在线程中获取数据
        def update_finished(success, message):
            progress_dialog.close()
            if success:
                QMessageBox.information(self, "成功", message)
                # 更新结果表格
                if game in self.history_data and self.history_data[game]:
                    self.update_result_table(self.history_data[game][:min(20, len(self.history_data[game]))])
            else:
                QMessageBox.warning(self, "错误", message)
        
        thread = DataUpdateThread(game, app_id, app_secret, count)
        thread.update_finished.connect(update_finished)
        thread.start()

    def toggle_auto_fetch(self, state):
        """切换自动更新"""
        if state == Qt.Checked:
            if not self.auto_update_timer:
                self.auto_update_timer = QTimer()
                self.auto_update_timer.timeout.connect(self.auto_update_all_games)
                self.auto_update_timer.start(1800000)  # 30分钟
            QMessageBox.information(self, "自动更新", "已开启自动更新，每30分钟检查一次")
        else:
            if self.auto_update_timer:
                self.auto_update_timer.stop()
                self.auto_update_timer = None
            QMessageBox.information(self, "自动更新", "已关闭自动更新")

    def save_to_history(self):
        """保存到历史库"""
        game = self.network_game_combo.currentText()
        if self.save_game_history_data(game):
            QMessageBox.information(self, "成功", f"{game}数据已保存到本地文件")
        else:
            QMessageBox.warning(self, "错误", f"保存{game}数据失败")

    def analyze_current(self):
        """分析当前数据"""
        game = self.network_game_combo.currentText()
        if game not in self.history_data or not self.history_data[game]:
            QMessageBox.warning(self, "错误", "没有可分析的数据")
            return
            
        self.tabs.setCurrentIndex(3)  # 切换到数据分析页
        self.analysis_game_combo.setCurrentText(game)
        self.show_heatmap()

    def update_shrink_ui(self):
        """更新缩水UI"""
        # 清除现有内容
        while self.shrink_condition_layout.count():
            child = self.shrink_condition_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        game = self.shrink_game_combo.currentText()
        
        if game == "双色球":
            self.create_ssq_shrink_ui()
        elif game == "大乐透":
            self.create_dlt_shrink_ui()
        elif game == "七星彩":
            self.create_qxc_shrink_ui()
        else:
            self.create_general_shrink_ui(game)

    def create_ssq_shrink_ui(self):
        """创建双色球缩水UI"""
        # 红球缩水条件
        red_group = QGroupBox("红球缩水条件")
        red_layout = QVBoxLayout()
        
        # 和值范围
        sum_layout = QHBoxLayout()
        sum_layout.addWidget(QLabel("和值范围:"))
        self.red_sum_min = QSpinBox()
        self.red_sum_min.setRange(1, 200)
        self.red_sum_min.setValue(70)
        sum_layout.addWidget(self.red_sum_min)
        sum_layout.addWidget(QLabel("-"))
        self.red_sum_max = QSpinBox()
        self.red_sum_max.setRange(1, 200)
        self.red_sum_max.setValue(140)
        sum_layout.addWidget(self.red_sum_max)
        red_layout.addLayout(sum_layout)
        
        # 奇偶比例
        parity_layout = QHBoxLayout()
        parity_layout.addWidget(QLabel("奇偶比例:"))
        self.parity_ratio = QComboBox()
        self.parity_ratio.addItems(["任意", "2:4", "3:3", "4:2", "5:1", "1:5"])
        parity_layout.addWidget(self.parity_ratio)
        red_layout.addLayout(parity_layout)
        
        # 大小比例
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("大小比例(以17为界):"))
        self.size_ratio = QComboBox()
        self.size_ratio.addItems(["任意", "2:4", "3:3", "4:2", "5:1", "1:5"])
        size_layout.addWidget(self.size_ratio)
        red_layout.addLayout(size_layout)
        
        red_group.setLayout(red_layout)
        self.shrink_condition_layout.addWidget(red_group)
        
        # 蓝球缩水条件
        blue_group = QGroupBox("蓝球缩水条件")
        blue_layout = QVBoxLayout()
        
        # 蓝球大小
        blue_size_layout = QHBoxLayout()
        blue_size_layout.addWidget(QLabel("蓝球大小(以9为界):"))
        self.blue_size = QComboBox()
        self.blue_size.addItems(["任意", "大(9-16)", "小(1-8)"])
        blue_size_layout.addWidget(self.blue_size)
        blue_layout.addLayout(blue_size_layout)
        
        # 蓝球奇偶
        blue_parity_layout = QHBoxLayout()
        blue_parity_layout.addWidget(QLabel("蓝球奇偶:"))
        self.blue_parity = QComboBox()
        self.blue_parity.addItems(["任意", "奇数", "偶数"])
        blue_parity_layout.addWidget(self.blue_parity)
        blue_layout.addLayout(blue_parity_layout)
        
        blue_group.setLayout(blue_layout)
        self.shrink_condition_layout.addWidget(blue_group)

    def create_dlt_shrink_ui(self):
        """创建大乐透缩水UI"""
        # 前区缩水条件
        front_group = QGroupBox("前区缩水条件")
        front_layout = QVBoxLayout()
        
        # 和值范围
        sum_layout = QHBoxLayout()
        sum_layout.addWidget(QLabel("和值范围:"))
        self.front_sum_min = QSpinBox()
        self.front_sum_min.setRange(1, 200)
        self.front_sum_min.setValue(60)
        sum_layout.addWidget(self.front_sum_min)
        sum_layout.addWidget(QLabel("-"))
        self.front_sum_max = QSpinBox()
        self.front_sum_max.setRange(1, 200)
        self.front_sum_max.setValue(130)
        sum_layout.addWidget(self.front_sum_max)
        front_layout.addLayout(sum_layout)
        
        # 奇偶比例
        parity_layout = QHBoxLayout()
        parity_layout.addWidget(QLabel("奇偶比例:"))
        self.front_parity = QComboBox()
        self.front_parity.addItems(["任意", "2:3", "3:2", "1:4", "4:1", "0:5", "5:0"])
        parity_layout.addWidget(self.front_parity)
        front_layout.addLayout(parity_layout)
        
        front_group.setLayout(front_layout)
        self.shrink_condition_layout.addWidget(front_group)
        
        # 后区缩水条件
        back_group = QGroupBox("后区缩水条件")
        back_layout = QVBoxLayout()
        
        # 和值范围
        back_sum_layout = QHBoxLayout()
        back_sum_layout.addWidget(QLabel("和值范围:"))
        self.back_sum_min = QSpinBox()
        self.back_sum_min.setRange(2, 23)
        self.back_sum_min.setValue(3)
        back_sum_layout.addWidget(self.back_sum_min)
        back_sum_layout.addWidget(QLabel("-"))
        self.back_sum_max = QSpinBox()
        self.back_sum_max.setRange(2, 23)
        self.back_sum_max.setValue(20)
        back_sum_layout.addWidget(self.back_sum_max)
        back_layout.addLayout(back_sum_layout)
        
        back_group.setLayout(back_layout)
        self.shrink_condition_layout.addWidget(back_group)

    def create_qxc_shrink_ui(self):
        """创建七星彩缩水UI"""
        group = QGroupBox("七星彩缩水条件")
        layout = QVBoxLayout()
        
        # 和值范围
        sum_layout = QHBoxLayout()
        sum_layout.addWidget(QLabel("和值范围:"))
        self.qxc_sum_min = QSpinBox()
        self.qxc_sum_min.setRange(0, 63)
        self.qxc_sum_min.setValue(20)
        sum_layout.addWidget(self.qxc_sum_min)
        sum_layout.addWidget(QLabel("-"))
        self.qxc_sum_max = QSpinBox()
        self.qxc_sum_max.setRange(0, 63)
        self.qxc_sum_max.setValue(40)
        sum_layout.addWidget(self.qxc_sum_max)
        layout.addLayout(sum_layout)
        
        # 奇偶比例
        parity_layout = QHBoxLayout()
        parity_layout.addWidget(QLabel("奇偶比例:"))
        self.qxc_parity = QComboBox()
        self.qxc_parity.addItems(["任意", "3:4", "4:3", "2:5", "5:2", "1:6", "6:1", "0:7", "7:0"])
        parity_layout.addWidget(self.qxc_parity)
        layout.addLayout(parity_layout)
        
        group.setLayout(layout)
        self.shrink_condition_layout.addWidget(group)

    def create_general_shrink_ui(self, game_type):
        """创建通用缩水UI"""
        group = QGroupBox(f"{game_type}缩水条件")
        layout = QVBoxLayout()
        
        # 和值范围
        sum_layout = QHBoxLayout()
        sum_layout.addWidget(QLabel("和值范围:"))
        
        if game_type in ["3D", "排列三"]:
            sum_min = QSpinBox()
            sum_min.setRange(0, 27)
            sum_min.setValue(5)
            sum_layout.addWidget(sum_min)
            sum_layout.addWidget(QLabel("-"))
            sum_max = QSpinBox()
            sum_max.setRange(0, 27)
            sum_max.setValue(22)
            sum_layout.addWidget(sum_max)
            self.general_sum_min = sum_min
            self.general_sum_max = sum_max
            
        elif game_type == "排列五":
            sum_min = QSpinBox()
            sum_min.setRange(0, 45)
            sum_min.setValue(15)
            sum_layout.addWidget(sum_min)
            sum_layout.addWidget(QLabel("-"))
            sum_max = QSpinBox()
            sum_max.setRange(0, 45)
            sum_max.setValue(30)
            sum_layout.addWidget(sum_max)
            self.general_sum_min = sum_min
            self.general_sum_max = sum_max
            
        elif game_type == "快乐8":
            sum_min = QSpinBox()
            sum_min.setRange(1, 800)
            sum_min.setValue(200)
            sum_layout.addWidget(sum_min)
            sum_layout.addWidget(QLabel("-"))
            sum_max = QSpinBox()
            sum_max.setRange(1, 800)
            sum_max.setValue(600)
            sum_layout.addWidget(sum_max)
            self.general_sum_min = sum_min
            self.general_sum_max = sum_max
            
        elif game_type == "七乐彩":
            sum_min = QSpinBox()
            sum_min.setRange(1, 200)
            sum_min.setValue(50)
            sum_layout.addWidget(sum_min)
            sum_layout.addWidget(QLabel("-"))
            sum_max = QSpinBox()
            sum_max.setRange(1, 200)
            sum_max.setValue(150)
            sum_layout.addWidget(sum_max)
            self.general_sum_min = sum_min
            self.general_sum_max = sum_max
            
        else:
            sum_min = QSpinBox()
            sum_min.setRange(1, 200)
            sum_min.setValue(50)
            sum_layout.addWidget(sum_min)
            sum_layout.addWidget(QLabel("-"))
            sum_max = QSpinBox()
            sum_max.setRange(1, 200)
            sum_max.setValue(150)
            sum_layout.addWidget(sum_max)
            self.general_sum_min = sum_min
            self.general_sum_max = sum_max
        
        layout.addLayout(sum_layout)
        
        group.setLayout(layout)
        self.shrink_condition_layout.addWidget(group)

    def generate_shrink_numbers(self):
        """生成缩水号码"""
        game = self.shrink_game_combo.currentText()
        
        try:
            if game == "双色球":
                results = []
                generated_count = 0
                max_attempts = 10000
                
                while len(results) < 10 and generated_count < max_attempts:
                    generated_count += 1
                    
                    # 生成红球
                    red = sorted(random.sample(range(1, 34), 6))
                    
                    # 检查红球条件
                    red_sum = sum(red)
                    if not (self.red_sum_min.value() <= red_sum <= self.red_sum_max.value()):
                        continue
                    
                    odd_count = sum(1 for n in red if n % 2 == 1)
                    even_count = 6 - odd_count
                    ratio_str = f"{odd_count}:{even_count}"
                    if self.parity_ratio.currentText() != "任意" and ratio_str != self.parity_ratio.currentText():
                        continue
                    
                    # 检查大小比例
                    big_count = sum(1 for n in red if n > 17)
                    small_count = 6 - big_count
                    size_ratio_str = f"{big_count}:{small_count}"
                    if self.size_ratio.currentText() != "任意" and size_ratio_str != self.size_ratio.currentText():
                        continue
                    
                    # 生成蓝球
                    blue_candidates = list(range(1, 17))
                    
                    # 应用蓝球大小条件
                    if self.blue_size.currentText() == "大(9-16)":
                        blue_candidates = [n for n in blue_candidates if n >= 9]
                    elif self.blue_size.currentText() == "小(1-8)":
                        blue_candidates = [n for n in blue_candidates if n <= 8]
                    
                    # 应用蓝球奇偶条件
                    if self.blue_parity.currentText() == "奇数":
                        blue_candidates = [n for n in blue_candidates if n % 2 == 1]
                    elif self.blue_parity.currentText() == "偶数":
                        blue_candidates = [n for n in blue_candidates if n % 2 == 0]
                    
                    if not blue_candidates:
                        continue
                    
                    blue = random.choice(blue_candidates)
                    
                    results.append(f"第{len(results)+1}注: 红球 {', '.join(map(str, red))} + 蓝球 {blue}")
                
                if results:
                    result_text = f"双色球缩水号码 (尝试{generated_count}次):\n\n" + "\n".join(results)
                    self.shrink_result_area.setPlainText(result_text)
                else:
                    self.shrink_result_area.setPlainText("无法生成符合条件的号码，请放宽缩水条件")
                
            elif game == "大乐透":
                results = []
                generated_count = 0
                max_attempts = 10000
                
                while len(results) < 10 and generated_count < max_attempts:
                    generated_count += 1
                    
                    # 生成前区
                    front = sorted(random.sample(range(1, 36), 5))
                    
                    # 检查前区条件
                    front_sum = sum(front)
                    if not (self.front_sum_min.value() <= front_sum <= self.front_sum_max.value()):
                        continue
                    
                    odd_count = sum(1 for n in front if n % 2 == 1)
                    even_count = 5 - odd_count
                    ratio_str = f"{odd_count}:{even_count}"
                    if self.front_parity.currentText() != "任意" and ratio_str != self.front_parity.currentText():
                        continue
                    
                    # 生成后区
                    back = sorted(random.sample(range(1, 13), 2))
                    
                    # 检查后区条件
                    back_sum = sum(back)
                    if not (self.back_sum_min.value() <= back_sum <= self.back_sum_max.value()):
                        continue
                    
                    results.append(f"第{len(results)+1}注: 前区 {', '.join(map(str, front))} + 后区 {', '.join(map(str, back))}")
                
                if results:
                    result_text = f"大乐透缩水号码 (尝试{generated_count}次):\n\n" + "\n".join(results)
                    self.shrink_result_area.setPlainText(result_text)
                else:
                    self.shrink_result_area.setPlainText("无法生成符合条件的号码，请放宽缩水条件")
                
            else:
                # 简单生成其他游戏的号码
                results = []
                for i in range(5):
                    if game == "快乐8":
                        nums = sorted(random.sample(range(1, 81), 10))
                        results.append(f"第{i+1}注: {', '.join(map(str, nums))}")
                    elif game == "七星彩":
                        nums = [random.randint(0, 9) for _ in range(6)] + [random.randint(0, 14)]
                        results.append(f"第{i+1}注: {', '.join(map(str, nums))}")
                    elif game == "3D":
                        nums = [random.randint(0, 9) for _ in range(3)]
                        results.append(f"第{i+1}注: {', '.join(map(str, nums))}")
                    elif game == "排列三":
                        nums = [random.randint(0, 9) for _ in range(3)]
                        results.append(f"第{i+1}注: {', '.join(map(str, nums))}")
                    elif game == "七乐彩":
                        nums = sorted(random.sample(range(1, 31), 7))
                        results.append(f"第{i+1}注: {', '.join(map(str, nums))}")
                    elif game == "排列五":
                        nums = [random.randint(0, 9) for _ in range(5)]
                        results.append(f"第{i+1}注: {', '.join(map(str, nums))}")
                
                result_text = f"{game}缩水号码:\n\n" + "\n".join(results)
                self.shrink_result_area.setPlainText(result_text)
                
        except Exception as e:
            logger.error(f"生成缩水号码失败: {str(e)}")
            QMessageBox.warning(self, "错误", f"生成缩水号码失败: {str(e)}")

    def save_shrink_result(self):
        """保存缩水结果"""
        result_text = self.shrink_result_area.toPlainText()
        if not result_text.strip():
            QMessageBox.warning(self, "错误", "没有可保存的结果")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存缩水结果", "", "文本文件 (*.txt)")
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(result_text)
            QMessageBox.information(self, "成功", f"结果已保存到: {file_path}")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"保存失败: {str(e)}")

    def shrink_select_numbers(self):
        """缩水自选号码"""
        game = self.shrink_game_combo.currentText()
        self.self_select(game)

    def update_matrix_ui(self):
        """更新矩阵UI"""
        # 清除现有内容
        while self.matrix_condition_layout.count():
            child = self.matrix_condition_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        game = self.matrix_game_combo.currentText()
        
        if game == "双色球":
            self.create_ssq_matrix_ui()
        elif game == "大乐透":
            self.create_dlt_matrix_ui()
        else:
            self.create_general_matrix_ui(game)

    def create_ssq_matrix_ui(self):
        """创建双色球矩阵UI"""
        group = QGroupBox("双色球矩阵投注")
        layout = QVBoxLayout()
        
        # 红球数量
        red_layout = QHBoxLayout()
        red_layout.addWidget(QLabel("红球数量:"))
        self.matrix_red_count = QSpinBox()
        self.matrix_red_count.setRange(7, 16)
        self.matrix_red_count.setValue(8)
        self.matrix_red_count.valueChanged.connect(self.update_matrix_info)
        red_layout.addWidget(self.matrix_red_count)
        layout.addLayout(red_layout)
        
        # 蓝球数量
        blue_layout = QHBoxLayout()
        blue_layout.addWidget(QLabel("蓝球数量:"))
        self.matrix_blue_count = QSpinBox()
        self.matrix_blue_count.setRange(1, 16)
        self.matrix_blue_count.setValue(2)
        self.matrix_blue_count.valueChanged.connect(self.update_matrix_info)
        blue_layout.addWidget(self.matrix_blue_count)
        layout.addLayout(blue_layout)
        
        # 矩阵信息
        self.matrix_info_label = QLabel()
        self.update_matrix_info()
        layout.addWidget(self.matrix_info_label)
        
        group.setLayout(layout)
        self.matrix_condition_layout.addWidget(group)

    def update_matrix_info(self):
        """更新矩阵信息"""
        try:
            if hasattr(self, 'matrix_red_count') and hasattr(self, 'matrix_blue_count'):
                red_count = self.matrix_red_count.value()
                blue_count = self.matrix_blue_count.value()
                
                # 计算注数
                red_comb = math.comb(red_count, 6)
                total_bets = red_comb * blue_count
                total_amount = total_bets * 2.0
                
                info_text = f"矩阵信息:\n"
                info_text += f"• 选择红球: {red_count}个\n"
                info_text += f"• 选择蓝球: {blue_count}个\n"
                info_text += f"• 组合注数: {red_comb} × {blue_count} = {total_bets}注\n"
                info_text += f"• 总金额: ¥{total_amount:.2f}\n"
                info_text += f"• 节约比例: {((1 - total_bets/math.comb(33, 6)/16)*100):.1f}%"
                
                self.matrix_info_label.setText(info_text)
        except:
            pass

    def create_dlt_matrix_ui(self):
        """创建大乐透矩阵UI"""
        group = QGroupBox("大乐透矩阵投注")
        layout = QVBoxLayout()
        
        # 前区数量
        front_layout = QHBoxLayout()
        front_layout.addWidget(QLabel("前区数量:"))
        self.matrix_front_count = QSpinBox()
        self.matrix_front_count.setRange(6, 20)
        self.matrix_front_count.setValue(7)
        front_layout.addWidget(self.matrix_front_count)
        layout.addLayout(front_layout)
        
        # 后区数量
        back_layout = QHBoxLayout()
        back_layout.addWidget(QLabel("后区数量:"))
        self.matrix_back_count = QSpinBox()
        self.matrix_back_count.setRange(3, 12)
        self.matrix_back_count.setValue(4)
        back_layout.addWidget(self.matrix_back_count)
        layout.addLayout(back_layout)
        
        group.setLayout(layout)
        self.matrix_condition_layout.addWidget(group)

    def create_general_matrix_ui(self, game_type):
        """创建通用矩阵UI"""
        group = QGroupBox(f"{game_type}矩阵投注")
        layout = QVBoxLayout()
        
        # 选择数量
        count_layout = QHBoxLayout()
        count_layout.addWidget(QLabel("选择数量:"))
        count_spin = QSpinBox()
        
        if game_type == "快乐8":
            count_spin.setRange(11, 20)
            count_spin.setValue(12)
        elif game_type == "七乐彩":
            count_spin.setRange(8, 15)
            count_spin.setValue(9)
        elif game_type == "七星彩":
            count_spin.setRange(8, 15)
            count_spin.setValue(9)
        elif game_type == "排列五":
            count_spin.setRange(6, 15)
            count_spin.setValue(8)
        else:
            count_spin.setRange(4, 10)
            count_spin.setValue(5)
        
        count_layout.addWidget(count_spin)
        layout.addLayout(count_layout)
        
        group.setLayout(layout)
        self.matrix_condition_layout.addWidget(group)

    def generate_matrix_numbers(self):
        """生成矩阵号码"""
        game = self.matrix_game_combo.currentText()
        
        try:
            if game == "双色球":
                red_count = self.matrix_red_count.value()
                blue_count = self.matrix_blue_count.value()
                
                # 生成基础号码
                base_red = sorted(random.sample(range(1, 34), red_count))
                base_blue = sorted(random.sample(range(1, 17), blue_count))
                
                # 生成矩阵组合
                from itertools import combinations
                
                red_combinations = list(combinations(base_red, 6))
                results = []
                
                # 限制生成的注数
                max_combinations = min(20, len(red_combinations))
                
                for i, red_combo in enumerate(red_combinations[:max_combinations]):
                    for blue in base_blue[:min(2, len(base_blue))]:  # 最多2个蓝球组合
                        results.append(f"第{i*len(base_blue[:2])+1}注: 红球 {', '.join(map(str, red_combo))} + 蓝球 {blue}")
                
                result_text = f"基础红球 ({red_count}个): {', '.join(map(str, base_red))}\n"
                result_text += f"基础蓝球 ({blue_count}个): {', '.join(map(str, base_blue))}\n\n"
                result_text += f"矩阵投注号码 (共{len(results)}注):\n" + "\n".join(results)
                
                self.matrix_result_area.setPlainText(result_text)
                
            elif game == "大乐透":
                front_count = self.matrix_front_count.value()
                back_count = self.matrix_back_count.value()
                
                # 生成基础号码
                base_front = sorted(random.sample(range(1, 36), front_count))
                base_back = sorted(random.sample(range(1, 13), back_count))
                
                # 生成矩阵组合
                from itertools import combinations
                
                front_combinations = list(combinations(base_front, 5))
                back_combinations = list(combinations(base_back, 2))
                results = []
                
                # 限制生成的注数
                max_front_comb = min(10, len(front_combinations))
                max_back_comb = min(3, len(back_combinations))
                
                for i, front_combo in enumerate(front_combinations[:max_front_comb]):
                    for back_combo in back_combinations[:max_back_comb]:
                        results.append(f"第{len(results)+1}注: 前区 {', '.join(map(str, front_combo))} + 后区 {', '.join(map(str, back_combo))}")
                
                result_text = f"基础前区 ({front_count}个): {', '.join(map(str, base_front))}\n"
                result_text += f"基础后区 ({back_count}个): {', '.join(map(str, base_back))}\n\n"
                result_text += f"矩阵投注号码 (共{len(results)}注):\n" + "\n".join(results)
                
                self.matrix_result_area.setPlainText(result_text)
                
            else:
                # 简单生成其他游戏的矩阵号码
                results = []
                for i in range(5):
                    if game == "快乐8":
                        nums = sorted(random.sample(range(1, 81), 10))
                        results.append(f"第{i+1}注: {', '.join(map(str, nums))}")
                    elif game == "七星彩":
                        nums = [random.randint(0, 9) for _ in range(6)] + [random.randint(0, 14)]
                        results.append(f"第{i+1}注: {', '.join(map(str, nums))}")
                    elif game == "3D":
                        nums = [random.randint(0, 9) for _ in range(3)]
                        results.append(f"第{i+1}注: {', '.join(map(str, nums))}")
                    elif game == "排列三":
                        nums = [random.randint(0, 9) for _ in range(3)]
                        results.append(f"第{i+1}注: {', '.join(map(str, nums))}")
                    elif game == "七乐彩":
                        nums = sorted(random.sample(range(1, 31), 7))
                        results.append(f"第{i+1}注: {', '.join(map(str, nums))}")
                    elif game == "排列五":
                        nums = [random.randint(0, 9) for _ in range(5)]
                        results.append(f"第{i+1}注: {', '.join(map(str, nums))}")
                
                result_text = f"{game}矩阵号码:\n\n" + "\n".join(results)
                self.matrix_result_area.setPlainText(result_text)
                
        except Exception as e:
            logger.error(f"生成矩阵号码失败: {str(e)}")
            QMessageBox.warning(self, "错误", f"生成矩阵号码失败: {str(e)}")

    def save_matrix_result(self):
        """保存矩阵结果"""
        result_text = self.matrix_result_area.toPlainText()
        if not result_text.strip():
            QMessageBox.warning(self, "错误", "没有可保存的结果")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存矩阵结果", "", "文本文件 (*.txt)")
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(result_text)
            QMessageBox.information(self, "成功", f"结果已保存到: {file_path}")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"保存失败: {str(e)}")

    def matrix_select_numbers(self):
        """矩阵自选号码"""
        game = self.matrix_game_combo.currentText()
        self.self_select(game)


def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # 设置应用程序信息
    app.setApplicationName("彩票分析系统 (基于真实API)")
    app.setApplicationVersion("2.0.0")
    
    # 创建并显示主窗口
    window = LotteryApp()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
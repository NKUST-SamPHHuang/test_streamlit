# D:
# cd Others
# cd "[20221106] Streamlit Demo"
# streamlit run Main.py
# https://docs.streamlit.io/

import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf
import prophet
from datetime import date
from plotly import graph_objects as go
from plotly.subplots import make_subplots
from prophet.plot import plot_plotly, plot_components_plotly
import matplotlib.pyplot as plt


# @st.cache
def load_data(ticker):
    data = yf.download(ticker, START_str, TODAY_str)
    data.reset_index(inplace=True)
    data["Date"] = pd.to_datetime(data["Date"], format="%Y-%m-%d").astype(str)
    data.rename({
        "Date": "日期",
        "Open": "開盤價",
        "High": "最高價",
        "Low": "最低價",
        "Close": "收盤價",
        "Adj Close": "收盤價(修正後)",
        "Volume": "成交股數"
    }, axis=1, inplace=True)

    return data

def plot_raw_data(stock_data):
    stock_candle = go.Candlestick(
        x=stock_data["日期"],
        open=stock_data["開盤價"],
        high=stock_data["最高價"],
        low=stock_data["最低價"],
        close=stock_data["收盤價"],
        increasing_line_color="red",
        decreasing_line_color="green",
        name="K線"
    )
    volume_bar = go.Bar(x=data["日期"], y=data["成交股數"], name="成交股數")

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
    fig.add_trace(
        stock_candle,
        row=1, col=1
    )
    fig.add_trace(
        volume_bar,
        row=2, col=1
    )
    fig.layout.update(
        xaxis_rangeslider_visible = False,
    )
    fig.update_xaxes(title_text="日期")
    fig.update_yaxes(title_text="股價", row=1, col=1)
    fig.update_yaxes(title_text="成交股數", row=2, col=1)
    return fig

def rename_describe(stock_data):
    return stock_data.rename({
        "count": "總筆數",
        "mean": "平均值",
        "std": "標準差",
        "mean": "平均值",
        "min": "最小值",
        "25%": "第1四分位數",
        "50%": "中位數",
        "75%": "第3四分位數",
        "max": "最大值",
    }, axis=0)

def reform_number_format(stock_data):
    for x in stock_data.columns:
        stock_data[x] = stock_data[x].map(lambda x: f"{x:,.0f}")
    return stock_data

def forecasting(stock_data):
    df = stock_data[["日期", "收盤價(修正後)"]].copy()
    df.columns = ['ds', 'y']  # Prophet model 需特定的欄位名稱 
    # 訓練集
    train = df.drop(stock_data.index[-250:])
    # 測試集
    future = df.iloc[stock_data.index[-250:]][["ds"]]
    future.reset_index(drop=True, inplace=True)
    # 模型建立
    model = prophet.Prophet()
    model.fit(train)
    # 模型預測
    forecast = model.predict(future)
    
    return model, forecast, df

def validation(df, forecast):
    # plot results
    fig = model.plot(forecast)
    plt.scatter(x=df.ds, y=df.y)
    plt.legend(['Actual', 'Predict'])

    return fig

# 參數設定
TODAY_val = date.today()
TODAY_str = TODAY_val.strftime("%Y-%m-%d")
START_str = "2021-1-1"

# Page Config
st.set_page_config(page_title='金融大數據',  layout='wide')

# 版面設定
st.title("金融大數據")


# 資料取得
st.subheader("讀取股價資料")
c1, c2, c3 = st.columns((1,1,1))
labeled_stock = c1.text_input("輸入股票代號", value="0050")
START_str = c2.date_input("設定開始日", date(2021, 1, 1))
TODAY_str = c3.date_input("設定結束日", TODAY_val)
with st.spinner(f"{labeled_stock} 資料讀取中..."):
    try:
        data = load_data(f"{labeled_stock}.tw")
    except:
        st.text("查詢失敗")
    
if not data.empty:
    data_load_state = st.text(f"{labeled_stock} 資料讀取完成!")

    st.subheader("資料分析")
    with st.expander("資料摘要"):
        temp_data = data[["日期", "開盤價", "最高價", "最低價", "收盤價"]].copy()
        
        # 資料呈現
        st.subheader("資料摘要")
        st.write(reform_number_format(rename_describe(temp_data.describe())))
        
        m1, m2 = st.columns((1,1))
        m1.subheader("最前5筆資料")
        m1.write(temp_data.head())
        m2.subheader("最後5筆資料")
        m2.write(temp_data.tail())
                
    with st.expander("資料視覺化"):
        # 資料繪圖
        st.title("股價K線")
        fig = plot_raw_data(data)
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("預測模型"):
        # 預測模型
        if data.shape[0] < 250:
            st.write("資料不足，無法預測")
        else:
            model, forecast, df = forecasting(data)
            fig = plot_plotly(model, forecast)
            st.plotly_chart(fig, use_container_width=True)

    with st.expander("模型驗證"):
        # 模型驗證
        if data.shape[0] < 250:
            st.write("資料不足，無法驗證")
        else:
            fig = validation(df, forecast)
            st.pyplot(fig, use_container_width=True)

    with st.expander("完整資料"):
        # 完整資料呈現
        st.subheader(f"完整資料: {START_str} 至 {TODAY_str}")
        st.write(data)

else:
    st.text("查無此代碼")


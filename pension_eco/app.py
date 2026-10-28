import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="养老生态全链条评估沙盘", layout="wide")

st.title("养老生态全链条评估沙盘")
st.caption("金融 · 健康 · 情感 三维联动 | 仅用于学术演示，不构成投资建议")

# ---------- 侧边栏：老人档案 ----------
with st.sidebar:
    st.header("老人档案")
    age = st.slider("年龄", 55, 85, 65)
    gender = st.selectbox("性别", ["男", "女"])
    savings = st.number_input("养老储备（万元）", 10, 500, 80)
    monthly = st.number_input("每月可追加（元）", 0, 10000, 2000)
    health = st.select_slider("健康自评", ["较差", "一般", "良好"], value="一般")
    lonely = st.selectbox("日常陪伴情况", ["独居，很少与人交流", "偶尔有人探望", "家人日常陪伴"])
    run = st.button("生成生态评估", type="primary")

# ---------- 预设的“AI分析结果”（演示用，后续可替换为真实调用） ----------
def mock_finance(gender, savings):
    base_eq = 35 if gender == "男" else 28
    return {
        "权益类建议比例": f"{base_eq}%",
        "固收类建议比例": f"{100 - base_eq}%",
        "偏差警示": "女性建议权益比例系统性偏低约7个百分点。若长期维持，按复利测算退休时可支配资产差距约12万元。",
        "审计结论": "该建议在“性别中性”维度存在可测量偏差，建议人工复核。",
    }

def mock_health(age, health):
    score = {"较差": 30, "一般": 60, "良好": 85}[health] - max(0, (age - 65)) * 1.5
    score = max(0, min(100, score))
    level = "高" if score < 40 else ("中" if score < 70 else "低")
    return {"健康风险分": f"{score:.0f}/100", "跌倒/慢病综合风险等级": level,
            "建议": "建议接入智能监护设备（如跌倒检测），并每季度进行一次慢病筛查。" if level != "低" else "维持现有健康管理节奏。"}

def mock_emotion(lonely):
    mapping = {"独居，很少与人交流": ("强", "建议接入AI语音陪伴或社区探访，每周至少3次主动交互。"),
               "偶尔有人探望": ("中", "可在日常提醒用药基础上增加娱乐互动功能。"),
               "家人日常陪伴": ("弱", "情感需求已基本满足，AI可侧重生活辅助而非陪伴。")}
    level, advice = mapping[lonely]
    return {"陪伴需求强度": level, "建议": advice}

# ---------- 主体：三链联动 ----------
if run:
    fin = mock_finance(gender, savings)
    hea = mock_health(age, health)
    emo = mock_emotion(lonely)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("金融链：AI配置审计")
        st.metric("权益类建议", fin["权益类建议比例"])
        st.metric("固收类建议", fin["固收类建议比例"])
        st.warning(fin["偏差警示"])
        st.caption(fin["审计结论"])

    with col2:
        st.subheader("健康链：风险前置预警")
        st.metric("健康风险分", hea["健康风险分"])
        st.metric("综合风险等级", hea["跌倒/慢病综合风险等级"])
        st.info(hea["建议"])

    with col3:
        st.subheader("情感链：陪伴需求匹配")
        st.metric("陪伴需求强度", emo["陪伴需求强度"])
        st.success(emo["建议"])

    st.divider()

    # ---------- 量化仪表盘 ----------
    st.subheader("生态健康度总览")

    fin_score = 100 - abs(35 - int(fin["权益类建议比例"].strip("%"))) * 2
    fin_score = max(0, min(100, fin_score))
    hea_score = int(hea["健康风险分"].split("/")[0])
    emo_score = {"强": 30, "中": 65, "弱": 90}[emo["陪伴需求强度"]]

    radar = go.Figure(data=go.Scatterpolar(
        r=[fin_score, hea_score, emo_score, fin_score],
        theta=["金融稳健度", "健康安全度", "情感满足度", "金融稳健度"],
        fill="toself",
    ))
    radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                        showlegend=False, height=380)
    st.plotly_chart(radar, use_container_width=True)

    # ---------- 蒙特卡洛：养老金耗尽年龄模拟 ----------
    st.subheader("养老金耗尽年龄模拟（蒙特卡洛）")
    np.random.seed(42)
    n_sim = 500
    annual_spend = 60000
    returns = np.random.normal(0.045, 0.10, (n_sim, 40))
    balances = np.zeros((n_sim, 41))
    balances[:, 0] = savings * 10000
    for t in range(1, 41):
        withdraw = annual_spend * (1.02 ** (t - 1))
        balances[:, t] = balances[:, t-1] * (1 + returns[:, t-1]) - withdraw
        balances[:, t] = np.maximum(balances[:, t], 0)
    depletion = []
    for i in range(n_sim):
        zero = np.where(balances[i] <= 0)[0]
        depletion.append(age + (zero[0] if len(zero) > 0 else 40))
    fig = px.histogram(x=depletion, nbins=20, labels={"x": "资金耗尽年龄", "y": "模拟频次"})
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"基于 {n_sim} 次模拟：中位耗尽年龄约 {int(np.median(depletion))} 岁。该曲线用于展示长寿风险，不构成预测。")

else:
    st.info("请在左侧填写档案后，点击「生成生态评估」。")
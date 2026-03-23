import os, streamlit as st, pandas as pd, numpy as np
import plotly.express as px, plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="RSF 기자 피해 현황 2015–2025",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800;900&family=Noto+Sans+KR:wght@300;400;500;700&family=JetBrains+Mono:wght@400;600&display=swap');

html,body,[class*="css"]{
  font-family:'Noto Sans KR',sans-serif;
  background:#09090f;
  color:#dde3ee;
}

/* ── 히어로 헤더 ── */
.hero {
  background:linear-gradient(135deg,#0d0d1a 0%,#1a1a2e 50%,#0a0a14 100%);
  border-left:6px solid #f5c518;
  border-bottom:1px solid #1e293b;
  padding:34px 40px 26px;
  margin-bottom:28px;
  border-radius:0 12px 12px 0;
  position:relative;
  overflow:hidden;
}
.hero::before {
  content:'PRESS FREEDOM';
  position:absolute;
  right:40px; top:50%;
  transform:translateY(-50%);
  font-family:'Playfair Display',serif;
  font-size:5rem;
  font-weight:900;
  color:rgba(245,197,24,0.04);
  letter-spacing:4px;
  pointer-events:none;
  white-space:nowrap;
}
.hero-label {
  font-family:'JetBrains Mono',monospace;
  font-size:0.66rem;
  color:#f5c518;
  letter-spacing:3px;
  text-transform:uppercase;
  margin-bottom:8px;
}
.hero h1 {
  font-family:'Playfair Display',serif;
  font-size:1.95rem;
  font-weight:800;
  color:#fff;
  margin:0 0 8px;
  line-height:1.2;
}
.hero p {
  color:#8a9ab8;
  font-size:0.8rem;
  font-family:'JetBrains Mono',monospace;
  margin:0;
}

/* ── KPI 카드 ── */
.kpi-card {
  background:linear-gradient(135deg,#13131f,#0d0d17);
  border:1px solid #1e293b;
  border-top:3px solid #f5c518;
  border-radius:10px;
  padding:18px 20px;
  text-align:center;
}
.kpi-lbl {
  font-family:'JetBrains Mono',monospace;
  font-size:0.6rem;
  color:#64748b;
  letter-spacing:1.5px;
  text-transform:uppercase;
  margin-bottom:6px;
}
.kpi-val {
  font-family:'Playfair Display',serif;
  font-size:2rem;
  font-weight:900;
  color:#f5c518;
  line-height:1;
  margin-bottom:4px;
}
.kpi-sub { font-size:0.68rem; color:#475569; }
.kpi-note { font-family:'JetBrains Mono',monospace; font-size:0.62rem; color:#f59e0b; margin-top:4px; }

/* ── 섹션 타이틀 ── */
.sec-title {
  font-family:'Playfair Display',serif;
  font-size:1.05rem;
  font-weight:700;
  color:#e2e8f0;
  border-left:4px solid #f5c518;
  padding-left:12px;
  margin:24px 0 14px;
}

/* ── 사건 카드 ── */
.inc-card {
  background:#13131f;
  border:1px solid #1e293b;
  border-left:4px solid #f5c518;
  border-radius:0 10px 10px 0;
  padding:16px 20px;
  margin-bottom:10px;
  transition:transform 0.2s, border-color 0.2s;
}
.inc-card:hover { transform:translateX(4px); border-left-color:#fbbf24; }
.inc-date { font-family:'JetBrains Mono',monospace; font-size:0.66rem; color:#64748b; margin-bottom:4px; }
.inc-name { font-size:0.95rem; font-weight:700; color:#e2e8f0; margin-bottom:2px; }
.inc-outlet { font-size:0.72rem; color:#94a3b8; margin-bottom:6px; }
.inc-detail { font-size:0.79rem; color:#8a9ab8; line-height:1.65; }
.inc-type {
  display:inline-block; background:#1a1a2e; border:1px solid #334155;
  border-radius:4px; padding:2px 8px; font-size:0.63rem;
  font-family:'JetBrains Mono',monospace; color:#fbbf24; margin-bottom:8px;
}
.inc-country {
  display:inline-block; background:#0f1a2e; border:1px solid #1e3a5f;
  border-radius:4px; padding:2px 8px; font-size:0.63rem;
  color:#93c5fd; margin-left:6px; margin-bottom:8px;
}

/* ── 언론자유지수 티어 뱃지 ── */
.tier-free     { color:#22c55e; font-weight:700; }
.tier-good     { color:#84cc16; font-weight:700; }
.tier-ok       { color:#f59e0b; font-weight:700; }
.tier-bad      { color:#f97316; font-weight:700; }
.tier-critical { color:#ef4444; font-weight:700; }

/* ── 출처 바 ── */
.src-bar {
  font-size:0.63rem; color:#334155;
  font-family:'JetBrains Mono',monospace;
  line-height:1.9; padding-top:16px;
  border-top:1px solid #1e293b; margin-top:8px;
}

#MainMenu,footer,header{visibility:hidden;}
.block-container{padding-top:1rem;}
</style>
""", unsafe_allow_html=True)

# ── 상수 ─────────────────────────────────────────────────────────────────────
BASE   = os.path.dirname(os.path.abspath(__file__))
BG     = "#09090f"
PBG    = "#13131f"
GOLD   = "#f5c518"
COLORS = [GOLD, "#e63946", "#457b9d", "#f59e0b", "#7c3aed", "#22c55e"]

TIER_COLOR = {
    "자유":     "#22c55e",
    "양호":     "#84cc16",
    "보통":     "#f59e0b",
    "어려움":   "#f97316",
    "매우 심각":"#ef4444",
}

# ── 데이터 로드 ───────────────────────────────────────────────────────────────
@st.cache_data
def load():
    y = pd.read_csv(os.path.join(BASE, "rsf_yearly_stats.csv"))
    c = pd.read_csv(os.path.join(BASE, "rsf_by_country.csv"))
    p = pd.read_csv(os.path.join(BASE, "rsf_press_freedom_index.csv"))
    d = pd.read_csv(os.path.join(BASE, "rsf_detained_by_country.csv"))
    i = pd.read_csv(os.path.join(BASE, "rsf_incidents.csv"))
    for col in ["killed","imprisoned","hostage","missing"]:
        y[col] = pd.to_numeric(y[col], errors="coerce")
    c["killed"]   = pd.to_numeric(c["killed"],   errors="coerce")
    d["detained"] = pd.to_numeric(d["detained"], errors="coerce")
    p["score"]    = pd.to_numeric(p["score"],    errors="coerce")
    p["rank"]     = pd.to_numeric(p["rank"],     errors="coerce")
    i["date"]     = pd.to_datetime(i["date"],    errors="coerce")
    return y, c, p, d, i

yearly, by_country, press_freedom, detained, incidents = load()

# ── 헤더 ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-label">Reporters Without Borders · RSF Press Freedom Data</div>
  <h1>📰 RSF 기자 피해 현황 2015–2025</h1>
  <p>사망 · 구금 · 납치 · 언론자유지수 | 출처: RSF Round-up · RSF Press Freedom Index</p>
</div>
""", unsafe_allow_html=True)

# ── KPI ───────────────────────────────────────────────────────────────────────
y_valid = yearly.dropna(subset=["killed"])
total_killed    = int(y_valid["killed"].sum())
total_imp       = int(yearly["imprisoned"].sum(skipna=True))
total_hostage   = int(yearly["hostage"].sum(skipna=True))
total_missing   = int(yearly["missing"].sum(skipna=True))
worst_yr        = int(yearly.loc[yearly["imprisoned"].idxmax(), "year"])
korea_rank      = int(press_freedom[press_freedom["country_kr"]=="대한민국"]["rank"].values[0])

k1,k2,k3,k4,k5,k6 = st.columns(6)
for col, lbl, val, sub, note in [
    (k1, "10년 총 사망",    f"{total_killed:,}",  "명 (2015~2025)",    "↑ 분쟁 지역 집중"),
    (k2, "10년 총 구금",    f"{total_imp:,}",     "명",                f"최고: {worst_yr}년 550명"),
    (k3, "10년 총 납치",    f"{total_hostage:,}", "명",                ""),
    (k4, "10년 총 실종",    f"{total_missing:,}", "명",                "2024년 급증"),
    (k5, "대한민국 순위",   f"{korea_rank}위",    "/ 180개국 (2024)",  "점수: 72.96"),
    (k6, "최다 구금국",     "중국",               "2024 124명 구금",   "홍콩 포함"),
]:
    col.markdown(
        f'<div class="kpi-card"><div class="kpi-lbl">{lbl}</div>'
        f'<div class="kpi-val">{val}</div><div class="kpi-sub">{sub}</div>'
        f'<div class="kpi-note">{note}</div></div>',
        unsafe_allow_html=True)

st.markdown("")

# ── 탭 ───────────────────────────────────────────────────────────────────────
t1, t2, t3, t4, t5, t6 = st.tabs([
    "📈 연도별 추이", "🗺️ 국가별 사망",
    "🏛️ 언론자유지수", "🔒 기자 구금", "🕯️ 사건 기록", "📄 원시 데이터"])

LO = dict(
    template="plotly_dark",
    paper_bgcolor=BG,
    plot_bgcolor=PBG,
    margin=dict(l=10, r=10, t=36, b=10),
    font=dict(family="Noto Sans KR, sans-serif", size=11, color="#94a3b8"),
    xaxis=dict(gridcolor="#1e293b", zeroline=False),
    yaxis=dict(gridcolor="#1e293b", zeroline=False),
)

# ════════ TAB 1: 연도별 추이 ══════════════════════════════════════════════════
with t1:
    st.markdown('<div class="sec-title">연도별 기자 피해 추이 (2015–2025)</div>', unsafe_allow_html=True)

    # 스택 영역 차트 — 사망·구금·납치
    y_melt = yearly.melt(
        id_vars="year",
        value_vars=["killed","imprisoned","hostage","missing"],
        var_name="유형", value_name="인원")
    y_melt["유형"] = y_melt["유형"].map({
        "killed":"사망", "imprisoned":"구금", "hostage":"납치", "missing":"실종"})
    y_melt = y_melt.dropna()

    fig1 = px.area(
        y_melt, x="year", y="인원", color="유형",
        color_discrete_map={"사망":GOLD,"구금":"#e63946","납치":"#457b9d","실종":"#7c3aed"},
        labels={"year":"연도","인원":"피해자 수","유형":"유형"})
    fig1.update_layout(
        **LO, height=380,
        legend=dict(orientation="h", y=1.05, x=0),
        title=dict(text="연도별 사망·구금·납치·실종 추이", font=dict(size=13, color="#e2e8f0"), x=0))
    fig1.update_traces(hovertemplate="%{x}년 %{fullData.name}: %{y:,}명<extra></extra>")
    st.plotly_chart(fig1, use_container_width=True)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="sec-title">연도별 사망자 수</div>', unsafe_allow_html=True)
        y_k = yearly.dropna(subset=["killed"])
        bar_clr = [GOLD if yr == int(y_k.loc[y_k["killed"].idxmax(),"year"]) else "#7a6010" for yr in y_k["year"]]
        fig2 = go.Figure(go.Bar(
            x=y_k["year"], y=y_k["killed"],
            marker_color=bar_clr,
            text=y_k["killed"], textposition="outside",
            hovertemplate="%{x}년<br>사망: %{y}명<extra></extra>"))
        fig2.update_layout(
            **LO, height=320,
            title=dict(text="연도별 기자 사망자 수", font=dict(size=12,color="#e2e8f0"), x=0),
            xaxis=dict(tickvals=list(y_k["year"]), gridcolor="#1e293b"),
            yaxis=dict(title="명", gridcolor="#1e293b"))
        st.plotly_chart(fig2, use_container_width=True)

    with c2:
        st.markdown('<div class="sec-title">연도별 구금자 추이</div>', unsafe_allow_html=True)
        y_i = yearly.dropna(subset=["imprisoned"])
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=y_i["year"], y=y_i["imprisoned"],
            mode="lines+markers",
            line=dict(color="#e63946", width=3),
            marker=dict(size=7, color="#e63946"),
            fill="tozeroy", fillcolor="rgba(230,57,70,0.08)",
            hovertemplate="%{x}년<br>구금: %{y}명<extra></extra>",
            name="구금"))
        fig3.add_annotation(
            x=2024, y=550,
            text="역대 최고<br>550명",
            showarrow=True, arrowhead=2,
            arrowcolor="#e63946",
            font=dict(color="#e63946", size=10),
            ax=50, ay=-40)
        fig3.update_layout(
            **LO, height=320, showlegend=False,
            title=dict(text="연도별 구금 기자 수 (지속 증가 추세)", font=dict(size=12,color="#e2e8f0"), x=0),
            xaxis=dict(tickvals=list(y_i["year"]), gridcolor="#1e293b"),
            yaxis=dict(title="명", gridcolor="#1e293b"))
        st.plotly_chart(fig3, use_container_width=True)

    # 4분할 서브플롯
    st.markdown('<div class="sec-title">유형별 10년 추이 비교</div>', unsafe_allow_html=True)
    fig4 = make_subplots(rows=1, cols=4,
        subplot_titles=["사망","구금","납치","실종"],
        shared_yaxes=False)
    FILL_MAP = {
        "killed":     (GOLD,     "rgba(245,197,24,0.08)"),
        "imprisoned": ("#e63946","rgba(230,57,70,0.08)"),
        "hostage":    ("#457b9d","rgba(69,123,157,0.08)"),
        "missing":    ("#7c3aed","rgba(124,58,237,0.08)"),
    }
    for ci, (col_name, (color, fill)) in enumerate(FILL_MAP.items(), 1):
        df_s = yearly.dropna(subset=[col_name])
        fig4.add_trace(go.Scatter(
            x=df_s["year"], y=df_s[col_name],
            mode="lines+markers",
            line=dict(color=color, width=2.5),
            marker=dict(size=5, color=color),
            fill="tozeroy", fillcolor=fill,
            hovertemplate="%{x}년: %{y:,}명<extra></extra>",
            showlegend=False), row=1, col=ci)
    fig4.update_layout(
        template="plotly_dark", paper_bgcolor=BG, plot_bgcolor=PBG,
        height=260, margin=dict(l=10,r=10,t=42,b=10),
        font=dict(family="Noto Sans KR", size=10, color="#94a3b8"))
    for ann in fig4['layout']['annotations']:
        ann['font'] = dict(size=11, color="#94a3b8")
    st.plotly_chart(fig4, use_container_width=True)

# ════════ TAB 2: 국가별 사망 ══════════════════════════════════════════════════
with t2:
    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="sec-title">2025년 국가별 사망자</div>', unsafe_allow_html=True)
        df25 = by_country[by_country["year"]==2025].dropna(subset=["killed"]).sort_values("killed")
        fig5 = px.bar(df25, x="killed", y="country_kr", orientation="h",
            color="killed",
            color_continuous_scale=[[0,"#3b2f00"],[1,GOLD]],
            labels={"killed":"사망자 수","country_kr":"국가"},
            text="killed")
        fig5.update_layout(
            **LO, height=300, coloraxis_showscale=False,
            title=dict(text="2025년 사망자 상위국", font=dict(size=12,color="#e2e8f0"), x=0))
        fig5.update_traces(textposition="outside",
            hovertemplate="%{y}<br>사망: %{x}명<extra></extra>")
        st.plotly_chart(fig5, use_container_width=True)

    with c2:
        st.markdown('<div class="sec-title">2024년 국가별 사망자</div>', unsafe_allow_html=True)
        df24 = by_country[by_country["year"]==2024].dropna(subset=["killed"]).sort_values("killed")
        fig6 = px.bar(df24, x="killed", y="country_kr", orientation="h",
            color="killed",
            color_continuous_scale=[[0,"#1a1a3e"],[1,"#7c3aed"]],
            labels={"killed":"사망자 수","country_kr":"국가"},
            text="killed")
        fig6.update_layout(
            **LO, height=300, coloraxis_showscale=False,
            title=dict(text="2024년 사망자 상위국", font=dict(size=12,color="#e2e8f0"), x=0))
        fig6.update_traces(textposition="outside",
            hovertemplate="%{y}<br>사망: %{x}명<extra></extra>")
        st.plotly_chart(fig6, use_container_width=True)

    # 연도별 국가 비교 버블
    st.markdown('<div class="sec-title">연도 × 국가 사망자 버블 차트</div>', unsafe_allow_html=True)
    df_all = by_country.dropna(subset=["killed"]).copy()
    fig7 = px.scatter(df_all,
        x="year", y="country_kr", size="killed", color="context",
        color_discrete_map={"분쟁":GOLD,"조직범죄":"#e63946","시위 탄압":"#7c3aed","치안붕괴":"#f59e0b"},
        hover_name="country_kr",
        hover_data={"killed":True,"context":True,"note":True,"year":False},
        labels={"year":"연도","country_kr":"국가","killed":"사망자","context":"분쟁 유형"})
    fig7.update_layout(
        **LO, height=380,
        legend=dict(orientation="h", y=1.06),
        title=dict(text="연도별·국가별 사망자 분포", font=dict(size=12,color="#e2e8f0"), x=0),
        xaxis=dict(tickvals=[2023,2024,2025], gridcolor="#1e293b"))
    fig7.update_traces(hovertemplate="%{hovertext}<br>사망: %{marker.size}명<br>%{customdata[0]}<extra></extra>")
    st.plotly_chart(fig7, use_container_width=True)

    # 분쟁 유형별 파이
    st.markdown('<div class="sec-title">분쟁 유형별 사망 비중</div>', unsafe_allow_html=True)
    ctx = by_country.groupby("context")["killed"].sum().reset_index()
    ctx.columns = ["유형","사망자"]
    fig8 = px.pie(ctx, names="유형", values="사망자", hole=0.52,
        color_discrete_map={"분쟁":GOLD,"조직범죄":"#e63946","시위 탄압":"#7c3aed","치안붕괴":"#f59e0b"})
    fig8.update_layout(
        template="plotly_dark", paper_bgcolor=BG,
        height=300, margin=dict(l=10,r=10,t=10,b=10),
        legend=dict(orientation="h", y=-0.12))
    fig8.update_traces(textinfo="percent+label",
        hovertemplate="%{label}<br>%{value}명<extra></extra>")
    st.plotly_chart(fig8, use_container_width=True)

# ════════ TAB 3: 언론자유지수 ═════════════════════════════════════════════════
with t3:
    st.markdown('<div class="sec-title">2024 RSF 언론자유지수 주요국 현황 (180개국)</div>', unsafe_allow_html=True)

    # 점수 막대 — 색상 티어별
    pf_sorted = press_freedom.sort_values("score", ascending=True)
    bar_colors_pf = [TIER_COLOR.get(t, "#64748b") for t in pf_sorted["tier"]]

    fig9 = go.Figure(go.Bar(
        x=pf_sorted["score"],
        y=pf_sorted["country_kr"],
        orientation="h",
        marker_color=bar_colors_pf,
        text=pf_sorted["score"].round(1),
        textposition="outside",
        customdata=pf_sorted[["rank","tier"]].values,
        hovertemplate="%{y}<br>순위: %{customdata[0]}위<br>점수: %{x}<br>등급: %{customdata[1]}<extra></extra>"))
    fig9.add_vline(x=75, line_dash="dot", line_color="#334155",
        annotation_text="75점 (양호 기준)", annotation_font_color="#64748b")
    fig9.update_layout(
        **LO, height=480, coloraxis_showscale=False,
        title=dict(text="국가별 언론자유지수 점수 (색상 = 등급)", font=dict(size=12,color="#e2e8f0"), x=0),
        xaxis=dict(range=[0,105], gridcolor="#1e293b", title="점수"),
        yaxis=dict(gridcolor="#1e293b"))
    st.plotly_chart(fig9, use_container_width=True)

    # 티어별 도넛
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="sec-title">등급 분포 (표시 국가 기준)</div>', unsafe_allow_html=True)
        tier_cnt = press_freedom["tier"].value_counts().reset_index()
        tier_cnt.columns = ["등급","건수"]
        fig10 = px.pie(tier_cnt, names="등급", values="건수", hole=0.5,
            color="등급",
            color_discrete_map=TIER_COLOR)
        fig10.update_layout(
            template="plotly_dark", paper_bgcolor=BG,
            height=280, margin=dict(l=10,r=10,t=10,b=10),
            legend=dict(orientation="h", y=-0.15))
        fig10.update_traces(textinfo="percent+label",
            hovertemplate="%{label}<br>%{value}개국<extra></extra>")
        st.plotly_chart(fig10, use_container_width=True)

    with c2:
        st.markdown('<div class="sec-title">지역별 평균 점수</div>', unsafe_allow_html=True)
        region_avg = press_freedom.groupby("region")["score"].mean().reset_index().sort_values("score")
        fig11 = px.bar(region_avg, x="score", y="region", orientation="h",
            color="score",
            color_continuous_scale=[[0,"#3b0a0a"],[0.5,"#f59e0b"],[1,"#22c55e"]],
            labels={"score":"평균 점수","region":"지역"})
        fig11.update_layout(
            **LO, height=280, coloraxis_showscale=False,
            title=dict(text="지역별 평균 언론자유 점수", font=dict(size=11,color="#e2e8f0"), x=0))
        fig11.update_traces(hovertemplate="%{y}<br>평균: %{x:.1f}점<extra></extra>")
        st.plotly_chart(fig11, use_container_width=True)

    # 한국 강조 카드
    kor = press_freedom[press_freedom["country_kr"]=="대한민국"].iloc[0]
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0d1a0d,#13131f);
      border:1px solid #1e293b;border-left:4px solid #22c55e;
      border-radius:0 10px 10px 0;padding:18px 24px;margin-top:8px;">
      <div style="font-family:'JetBrains Mono',monospace;font-size:0.66rem;
        color:#22c55e;letter-spacing:2px;margin-bottom:6px;">대한민국 현황</div>
      <div style="display:flex;gap:40px;flex-wrap:wrap;align-items:center;">
        <div><span style="font-family:'Playfair Display',serif;font-size:2.2rem;
          font-weight:900;color:{GOLD};">{int(kor['rank'])}위</span>
          <span style="font-size:0.75rem;color:#64748b;margin-left:8px;">/ 180개국</span></div>
        <div><span style="font-family:'Playfair Display',serif;font-size:2.2rem;
          font-weight:900;color:#22c55e;">{kor['score']}</span>
          <span style="font-size:0.75rem;color:#64748b;margin-left:8px;">점</span></div>
        <div><span style="font-size:0.75rem;color:#64748b;">등급: </span>
          <span style="font-weight:700;color:#84cc16;">{kor['tier']}</span></div>
        <div style="font-size:0.75rem;color:#64748b;">아시아 최상위권 · 2024 RSF Index</div>
      </div>
    </div>""", unsafe_allow_html=True)

# ════════ TAB 4: 기자 구금 ════════════════════════════════════════════════════
with t4:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="sec-title">2024년 기자 구금 상위국</div>', unsafe_allow_html=True)
        d24 = detained[detained["year"]==2024].sort_values("detained")
        fig12 = px.bar(d24, x="detained", y="country_kr", orientation="h",
            color="detained",
            color_continuous_scale=[[0,"#1a0a0a"],[1,"#e63946"]],
            labels={"detained":"구금자 수","country_kr":"국가"},
            text="detained")
        fig12.update_layout(
            **LO, height=340, coloraxis_showscale=False,
            title=dict(text="2024년 구금 기자 상위국", font=dict(size=12,color="#e2e8f0"), x=0))
        fig12.update_traces(textposition="outside",
            hovertemplate="%{y}<br>구금: %{x}명<extra></extra>")
        st.plotly_chart(fig12, use_container_width=True)

    with c2:
        st.markdown('<div class="sec-title">2025년 기자 구금 상위국</div>', unsafe_allow_html=True)
        d25 = detained[detained["year"]==2025].sort_values("detained")
        fig13 = px.bar(d25, x="detained", y="country_kr", orientation="h",
            color="detained",
            color_continuous_scale=[[0,"#0a0a1a"],[1,"#7c3aed"]],
            labels={"detained":"구금자 수","country_kr":"국가"},
            text="detained")
        fig13.update_layout(
            **LO, height=340, coloraxis_showscale=False,
            title=dict(text="2025년 구금 기자 상위국", font=dict(size=12,color="#e2e8f0"), x=0))
        fig13.update_traces(textposition="outside",
            hovertemplate="%{y}<br>구금: %{x}명<extra></extra>")
        st.plotly_chart(fig13, use_container_width=True)

    # 2024 vs 2025 비교
    st.markdown('<div class="sec-title">2024 vs 2025 구금자 수 비교</div>', unsafe_allow_html=True)
    common = set(detained[detained["year"]==2024]["country_kr"]) & \
             set(detained[detained["year"]==2025]["country_kr"])
    rows_cmp = []
    for ctry in common:
        for yr in [2024, 2025]:
            row = detained[(detained["country_kr"]==ctry)&(detained["year"]==yr)]
            rows_cmp.append({"국가":ctry,"연도":str(yr),"구금자":int(row["detained"].values[0])})
    df_cmp = pd.DataFrame(rows_cmp)
    fig14 = px.bar(df_cmp, x="국가", y="구금자", color="연도", barmode="group",
        color_discrete_map={"2024":"#e63946","2025":"#7c3aed"},
        text="구금자")
    fig14.update_layout(
        **LO, height=320,
        legend=dict(orientation="h", y=1.08),
        title=dict(text="주요국 2024→2025 구금자 변화", font=dict(size=12,color="#e2e8f0"), x=0))
    fig14.update_traces(textposition="outside",
        hovertemplate="%{x} %{fullData.name}년<br>구금: %{y}명<extra></extra>")
    st.plotly_chart(fig14, use_container_width=True)

    # 중국 설명 박스
    st.markdown("""
    <div style="background:#13131f;border:1px solid #1e293b;border-left:4px solid #e63946;
      border-radius:0 10px 10px 0;padding:16px 20px;margin-top:4px;">
      <div style="font-family:'JetBrains Mono',monospace;font-size:0.66rem;
        color:#e63946;letter-spacing:2px;margin-bottom:8px;">⚠ 구금 1위국 — 중국</div>
      <div style="font-size:0.8rem;color:#94a3b8;line-height:1.8;">
        중국은 2024년 <b style="color:#e2e8f0;">124명</b>을 구금해 7년 연속 세계 1위 기자 감금국입니다.
        홍콩의 언론 자유 탄압(국가보안법 적용)으로 11명 포함. 시진핑 집권 이후 독립 언론·탐사보도에 대한
        체계적 탄압이 지속되고 있으며, 외국 특파원 비자 거부·추방도 병행되고 있습니다.
      </div>
    </div>""", unsafe_allow_html=True)

# ════════ TAB 5: 사건 기록 ════════════════════════════════════════════════════
with t5:
    st.markdown('<div class="sec-title">🕯️ 주요 사건 기록 (RSF 공식 확인)</div>', unsafe_allow_html=True)

    fc1, fc2 = st.columns(2)
    with fc1:
        sel_c = st.multiselect("국가 필터",
            options=sorted(incidents["country_kr"].unique()),
            default=sorted(incidents["country_kr"].unique()))
    with fc2:
        sel_t = st.multiselect("사건 유형 필터",
            options=sorted(incidents["incident_type"].unique()),
            default=sorted(incidents["incident_type"].unique()))

    filtered = incidents[
        incidents["country_kr"].isin(sel_c) &
        incidents["incident_type"].isin(sel_t)
    ].sort_values("date", ascending=False)

    st.markdown(
        f"<p style='font-size:0.75rem;color:#64748b;margin-bottom:14px;'>"
        f"총 {len(filtered)}건 표시 중</p>",
        unsafe_allow_html=True)

    for _, row in filtered.iterrows():
        date_str = row["date"].strftime("%Y년 %m월 %d일") if pd.notna(row["date"]) else "날짜 미상"
        src_link = (f'<a href="{row["source_url"]}" target="_blank" '
                    f'style="color:#475569;text-decoration:none;">📎 {row["source"]}</a>')
        st.markdown(f"""
        <div class="inc-card">
          <div class="inc-date">{date_str}</div>
          <span class="inc-type">{row['incident_type']}</span>
          <span class="inc-country">{row['country_kr']}</span>
          <div class="inc-name">{row['name']}</div>
          <div class="inc-outlet">🗞 {row['outlet']}</div>
          <div class="inc-detail">{row['details']}</div>
          <div style="margin-top:8px;font-size:0.63rem;">{src_link}</div>
        </div>""", unsafe_allow_html=True)

    # 사건 유형 도넛
    st.markdown('<div class="sec-title">사건 유형 분포</div>', unsafe_allow_html=True)
    tc = incidents["incident_type"].value_counts().reset_index()
    tc.columns = ["유형","건수"]
    fig15 = px.pie(tc, names="유형", values="건수", hole=0.5,
        color_discrete_sequence=[GOLD,"#e63946","#457b9d","#7c3aed","#22c55e","#f59e0b"])
    fig15.update_layout(
        template="plotly_dark", paper_bgcolor=BG,
        height=300, margin=dict(l=10,r=10,t=10,b=10),
        legend=dict(orientation="h", y=-0.15, font=dict(size=10)))
    fig15.update_traces(textinfo="percent+label",
        hovertemplate="%{label}<br>%{value}건<extra></extra>")
    st.plotly_chart(fig15, use_container_width=True)

# ════════ TAB 6: 원시 데이터 ══════════════════════════════════════════════════
with t6:
    st.markdown('<div class="sec-title">📄 연도별 피해 통계</div>', unsafe_allow_html=True)
    st.dataframe(yearly.style.format(
        {"killed":"{:,.0f}","imprisoned":"{:,.0f}",
         "hostage":"{:,.0f}","missing":"{:,.0f}"}, na_rep="—"),
        use_container_width=True, height=320)

    st.markdown('<div class="sec-title">📄 국가별 사망 현황</div>', unsafe_allow_html=True)
    st.dataframe(by_country.style.format({"killed":"{:,.0f}"}, na_rep="—"),
        use_container_width=True, height=280)

    st.markdown('<div class="sec-title">📄 언론자유지수 (2024)</div>', unsafe_allow_html=True)
    st.dataframe(press_freedom.style.format({"score":"{:.2f}","rank":"{:.0f}"}, na_rep="—"),
        use_container_width=True, height=280)

    st.markdown('<div class="sec-title">📄 기자 구금 현황</div>', unsafe_allow_html=True)
    st.dataframe(detained.style.format({"detained":"{:,.0f}"}, na_rep="—"),
        use_container_width=True, height=260)

    st.markdown('<div class="sec-title">📄 주요 사건 기록</div>', unsafe_allow_html=True)
    st.dataframe(
        incidents[["date","country_kr","name","outlet","incident_type","details","source"]],
        use_container_width=True, height=280)

# ── 하단 출처 ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div class="src-bar">
📎 RSF Annual Round-up 2015–2025 (rsf.org) &nbsp;|&nbsp;
RSF Press Freedom Index 2024 &nbsp;|&nbsp;
RSF Barometer (rsf.org/en/barometer) &nbsp;|&nbsp;
Reporters Without Borders — Press Freedom Reports &nbsp;|&nbsp;
RSF Round-up 2025: A Deadly Year for Journalists (rsf.org)
</div>""", unsafe_allow_html=True)

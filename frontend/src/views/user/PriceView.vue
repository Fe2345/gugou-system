<script setup lang="ts">
import TopBar from '@/layouts/TopBar.vue'
</script>

<template>
  <TopBar />
  <main class="page">
    <section class="query-panel">
      <div>
        <p class="eyebrow">价格分析</p>
        <h1>查询谷子参考价与价格走势</h1>
        <p>输入谷子名称、IP 或角色查看当前参考价、最高最低成交价和趋势数据。</p>
      </div>
      <form class="query-form" @submit.prevent>
        <input type="search" value="玛奇朵 亚克力砖" aria-label="搜索谷子" placeholder="输入谷子名称 / IP / 角色">
        <div class="range-tabs" aria-label="时间范围">
          <button type="button">近7天</button>
          <button type="button">近30天</button>
          <button type="button" class="active">近90天</button>
        </div>
        <button class="primary" type="button">查询</button>
      </form>
    </section>

    <section class="summary-panel">
      <div class="product-info">
        <p class="eyebrow">当前谷子</p>
        <h2>玛奇朵 亚克力砖</h2>
        <div class="meta-tags">
          <span>女神异闻录3</span><span>玛奇朵</span><span>亚克力砖</span>
        </div>
      </div>
      <div class="metric-grid" aria-label="价格指标">
        <article><span>当前参考价</span><strong>¥286</strong></article>
        <article><span>近90日均价</span><strong>¥274</strong></article>
        <article><span>最高成交价</span><strong>¥335</strong></article>
        <article><span>最低成交价</span><strong>¥218</strong></article>
        <article class="up"><span>近30天涨跌</span><strong>+12.4%</strong></article>
      </div>
    </section>

    <section class="chart-panel">
      <div class="section-head">
        <div>
          <p class="eyebrow">价格走势图</p>
          <h2>近90天每日平均成交价</h2>
        </div>
        <span>当前参考价参考线：¥286</span>
      </div>

      <div class="chart-wrap">
        <svg class="line-chart" viewBox="0 0 920 420" role="img" aria-label="玛奇朵亚克力砖近90天价格变化折线图">
          <line class="grid-line" x1="70" y1="60" x2="860" y2="60" />
          <line class="grid-line" x1="70" y1="130" x2="860" y2="130" />
          <line class="grid-line" x1="70" y1="200" x2="860" y2="200" />
          <line class="grid-line" x1="70" y1="270" x2="860" y2="270" />
          <line class="grid-line" x1="70" y1="340" x2="860" y2="340" />
          <text x="20" y="65">¥320</text>
          <text x="20" y="135">¥290</text>
          <text x="20" y="205">¥260</text>
          <text x="20" y="275">¥230</text>
          <text x="20" y="345">¥200</text>
          <line class="axis" x1="70" y1="40" x2="70" y2="340" />
          <line class="axis" x1="70" y1="340" x2="860" y2="340" />
          <line class="reference" x1="70" y1="139" x2="860" y2="139" />
          <text class="reference-text" x="732" y="128">参考价 ¥286</text>
          <polyline class="trend-line" points="70,265 168,235 267,251 366,209 465,181 563,151 662,163 761,126 860,139" />
          <g class="point"><circle cx="70" cy="265" r="6" /><text x="88" y="286">最低 ¥232</text></g>
          <g class="point"><circle cx="168" cy="235" r="5" /><circle cx="267" cy="251" r="5" /><circle cx="366" cy="209" r="5" /><circle cx="465" cy="181" r="5" /><circle cx="563" cy="151" r="5" /><circle cx="662" cy="163" r="5" /></g>
          <g class="point high"><circle cx="761" cy="126" r="6" /><text x="700" y="104">最高 ¥292</text></g>
          <g class="point current"><circle cx="860" cy="139" r="7" /><text x="774" y="170">当前 ¥286</text></g>
          <text class="x-label" x="48" y="382">3月第1周</text>
          <text class="x-label" x="146" y="382">3月第2周</text>
          <text class="x-label" x="245" y="382">3月第3周</text>
          <text class="x-label" x="344" y="382">3月第4周</text>
          <text class="x-label" x="443" y="382">4月第1周</text>
          <text class="x-label" x="541" y="382">4月第2周</text>
          <text class="x-label" x="640" y="382">4月第3周</text>
          <text class="x-label" x="739" y="382">4月第4周</text>
          <text class="x-label" x="838" y="382">5月第1周</text>
        </svg>
      </div>

      <p class="chart-note">玛奇朵亚克力砖近90天价格呈整体上升趋势，3月初价格在较低水平，4月下旬持续上涨，5月初小幅回落但仍然高于前期的均值，说明该谷子有较高的市场热度。</p>
    </section>

    <section class="bottom-layout">
      <section class="table-panel">
        <div class="section-head">
          <div><p class="eyebrow">近期成交参考</p><h2>成交记录</h2></div>
          <span>基于平台数据统计</span>
        </div>
        <div class="table-wrap">
          <table>
            <thead><tr><th>成交时间</th><th>谷子名称</th><th>成交价</th><th>谷子状态</th><th>交易方式</th></tr></thead>
            <tbody>
              <tr><td>2026-05-03</td><td>玛奇朵 亚克力砖</td><td>¥286</td><td>全新未拆</td><td>平台担保</td></tr>
              <tr><td>2026-04-28</td><td>玛奇朵 亚克力砖</td><td>¥292</td><td>全新未拆</td><td>平台担保</td></tr>
              <tr><td>2026-04-21</td><td>玛奇朵 亚克力砖</td><td>¥276</td><td>微瑕疵</td><td>平台担保</td></tr>
              <tr><td>2026-04-12</td><td>玛奇朵 亚克力砖</td><td>¥281</td><td>全新未拆</td><td>平台担保</td></tr>
              <tr><td>2026-03-26</td><td>玛奇朵 亚克力砖</td><td>¥256</td><td>拆封未用</td><td>平台担保</td></tr>
            </tbody>
          </table>
        </div>
      </section>

      <aside class="conclusion-panel">
        <div class="section-head"><div><p class="eyebrow">分析结论</p><h2>价格判断</h2></div></div>
        <ul>
          <li>当前参考价为¥286，较近90日均值略高。</li>
          <li>谷子处于持续上升趋势中，短期存在小幅波动。</li>
          <li>若用户计划购入，需关注近期回调风险。</li>
          <li>若用户计划出售，当前价格水平较适合挂出。</li>
        </ul>
      </aside>
    </section>
  </main>
</template>

<style scoped>
.page { width: min(1240px, calc(100% - 32px)); margin: 0 auto; padding: 28px 0 44px; }
.query-panel, .summary-panel, .chart-panel, .table-panel, .conclusion-panel { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); }
.query-panel {
  display: grid; grid-template-columns: minmax(0, 1fr) minmax(460px, 560px);
  gap: 28px; align-items: center; padding: 30px; color: #fff;
  background: linear-gradient(rgba(10,74,90,0.88), rgba(10,74,90,0.92)),
    url("https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1600&q=80") center/cover;
}
.eyebrow { margin: 0 0 8px; color: var(--gold); font-size: 13px; font-weight: 800; }
h1, h2, p { margin: 0; }
h1 { font-size: 38px; line-height: 1.16; }
.query-panel p:last-child { max-width: 650px; margin-top: 12px; color: rgba(255,255,255,0.84); line-height: 1.8; }
.query-form { display: grid; grid-template-columns: minmax(0, 1fr) 220px 88px; gap: 10px; padding: 12px; border: 1px solid rgba(255,255,255,0.28); border-radius: 10px; background: rgba(255,255,255,0.14); }
input { width: 100%; height: 44px; border: 0; border-radius: 8px; padding: 0 12px; outline: none; font: inherit; }
.range-tabs { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 6px; }
.range-tabs button { border: 1px solid rgba(255,255,255,0.28); border-radius: 8px; color: #fff; background: rgba(255,255,255,0.12); cursor: pointer; font: inherit; }
.range-tabs button.active { color: #172126; background: var(--gold); }
.primary { min-height: 44px; border: 0; border-radius: 8px; color: #fff; background: var(--accent); font-weight: 800; cursor: pointer; font: inherit; }
.primary:hover { background: var(--accent-dark); }
.summary-panel { margin-top: 20px; padding: 24px; }
.product-info { display: flex; justify-content: space-between; gap: 18px; align-items: center; margin-bottom: 18px; }
.summary-panel .eyebrow, .chart-panel .eyebrow, .table-panel .eyebrow, .conclusion-panel .eyebrow { color: var(--accent); }
h2 { font-size: 26px; }
.meta-tags { display: flex; flex-wrap: wrap; gap: 8px; }
.meta-tags span { padding: 7px 10px; border-radius: 7px; color: var(--accent); background: #eaf6f8; font-size: 13px; font-weight: 800; }
.metric-grid { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 14px; }
.metric-grid article { padding: 18px; border-radius: 10px; background: var(--soft); }
.metric-grid span { color: var(--muted); font-size: 14px; }
.metric-grid strong { display: block; margin-top: 10px; font-size: 28px; }
.metric-grid .up strong { color: #1f7a4d; }
.chart-panel { margin-top: 20px; padding: 24px; }
.section-head { display: flex; justify-content: space-between; gap: 16px; align-items: center; margin-bottom: 16px; }
.section-head span { color: var(--muted); font-size: 14px; }
.chart-wrap { overflow-x: auto; border: 1px solid var(--line); border-radius: 10px; background: #fff; }
.line-chart { width: 100%; min-width: 920px; height: auto; display: block; }
.line-chart :deep(text) { fill: var(--muted); font-size: 13px; }
.grid-line { stroke: #e4edf0; stroke-width: 1; }
.axis { stroke: #9dafb6; stroke-width: 1.5; }
.reference { stroke: var(--gold); stroke-width: 2; stroke-dasharray: 8 6; }
.reference-text { fill: #9a5d00; font-weight: 800; }
.trend-line { fill: none; stroke: var(--accent); stroke-width: 4; stroke-linecap: round; stroke-linejoin: round; }
.point :deep(circle) { fill: #fff; stroke: var(--accent); stroke-width: 3; }
.point.high :deep(circle) { stroke: var(--gold); }
.point.current :deep(circle) { fill: var(--accent); stroke: #fff; }
.point :deep(text) { fill: var(--ink); font-weight: 800; }
.x-label { font-size: 12px; }
.chart-note { margin-top: 16px; color: var(--muted); line-height: 1.8; }
.bottom-layout { display: grid; grid-template-columns: minmax(0, 1fr) 320px; gap: 20px; margin-top: 20px; }
.table-panel, .conclusion-panel { padding: 22px; }
.table-wrap { overflow-x: auto; }
table { width: 100%; min-width: 760px; border-collapse: collapse; font-size: 14px; }
th, td { padding: 14px 12px; border-bottom: 1px solid var(--line); text-align: left; }
th { color: var(--muted); background: var(--soft); }
.conclusion-panel ul { margin: 0; padding-left: 20px; color: var(--muted); line-height: 2; }

@media (max-width: 1080px) {
  .query-panel, .bottom-layout { grid-template-columns: 1fr; }
  .metric-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}
@media (max-width: 760px) {
  .product-info, .section-head { align-items: flex-start; flex-direction: column; }
  .query-form, .metric-grid { grid-template-columns: 1fr; }
}
@media (max-width: 560px) {
  .page { width: min(100% - 20px, 1240px); }
  .query-panel, .summary-panel, .chart-panel, .table-panel, .conclusion-panel { padding: 20px; }
  h1 { font-size: 30px; }
}
</style>

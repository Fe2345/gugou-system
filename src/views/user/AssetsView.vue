<script setup lang="ts">
import TopBar from '@/layouts/TopBar.vue'
</script>

<template>
  <TopBar />
  <main class="page">
    <section class="page-head">
      <div>
        <p class="eyebrow">资产管理</p>
        <h1>我的资产</h1>
        <p>集中查看和管理您的谷子资产，了解成本、当前估值和流转状态。</p>
      </div>
      <button class="primary" type="button">添加资产</button>
    </section>

    <section class="overview-grid" aria-label="资产概览">
      <article class="overview-card"><span>资产总数量</span><strong>126 件</strong><p>已录入收藏谷子</p></article>
      <article class="overview-card"><span>资产品类数</span><strong>48 种</strong><p>不同谷子品类分布</p></article>
      <article class="overview-card"><span>累计总成本</span><strong>¥3860</strong><p>用户录入购买成本</p></article>
      <article class="overview-card"><span>当前总估值</span><strong>¥4520</strong><p>按参考价估算</p></article>
      <article class="overview-card gain"><span>估值变化</span><strong>+¥660</strong><p>相对录入成本增长</p></article>
    </section>

    <section class="toolbar" aria-label="筛选与搜索">
      <div class="search-box"><input type="search" placeholder="搜索谷子名称 / IP / 角色"></div>
      <select aria-label="状态筛选">
        <option>全部状态</option><option>持有中</option><option>出售中</option><option>交换中</option><option>已卖出</option>
      </select>
      <select aria-label="排列方式">
        <option>按录入时间</option><option>按当前估值</option><option>按估值变化</option>
      </select>
      <button class="primary" type="button">筛选资产</button>
    </section>

    <section class="table-panel">
      <div class="section-head">
        <div><p class="eyebrow">资产列表</p><h2>资产明细</h2></div>
        <span>共 8 条示例数据</span>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>资产编号</th><th>谷子名称</th><th>IP/角色</th><th>品类</th>
              <th>数量</th><th>成本价</th><th>当前估值</th><th>估值变化</th>
              <th>状态</th><th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>A001</td><td>鸣神 千本樱姬 限定徽章</td><td>哈利波特 / 千本樱姬</td><td>徽章</td>
              <td>2</td><td>¥76</td><td>¥96</td><td class="up">+¥20</td>
              <td><span class="status hold">持有中</span></td>
              <td class="actions">详情 / 编辑 / 出售 / 交换</td>
            </tr>
            <tr>
              <td>A002</td><td>哈利波特 影山飞雄 亚克力立牌</td><td>哈利波特 / 影山飞雄</td><td>亚克力</td>
              <td>1</td><td>¥88</td><td>¥82</td><td class="down">-¥6</td>
              <td><span class="status hold">持有中</span></td>
              <td class="actions">详情 / 编辑 / 出售 / 交换</td>
            </tr>
            <tr>
              <td>A003</td><td>精灵宝可梦 皮卡丘 限定明信片</td><td>精灵宝可梦 / 皮卡丘</td><td>明信片</td>
              <td>3</td><td>¥45</td><td>¥72</td><td class="up">+¥27</td>
              <td><span class="status sale">出售中</span></td>
              <td class="actions">详情 / 编辑</td>
            </tr>
            <tr>
              <td>A004</td><td>原神 风 岩神角色挂件</td><td>原神 / 风</td><td>挂件</td>
              <td>1</td><td>¥58</td><td>¥64</td><td class="up">+¥6</td>
              <td><span class="status trade">交换中</span></td>
              <td class="actions">详情 / 编辑</td>
            </tr>
            <tr>
              <td>A005</td><td>崩坏星穹铁道 刃 色纸</td><td>崩坏星穹铁道 / 刃</td><td>色纸</td>
              <td>1</td><td>¥35</td><td>¥35</td><td>¥0</td>
              <td><span class="status hold">持有中</span></td>
              <td class="actions">详情 / 编辑 / 出售 / 交换</td>
            </tr>
            <tr>
              <td>A006</td><td>圣斗士星矢 瞬 门票</td><td>圣斗士星矢 / 瞬</td><td>票据</td>
              <td>4</td><td>¥40</td><td>¥52</td><td class="up">+¥12</td>
              <td><span class="status hold">持有中</span></td>
              <td class="actions">详情 / 编辑 / 出售 / 交换</td>
            </tr>
            <tr>
              <td>A007</td><td>新世纪福音战士 明日香 限定套装</td><td>新世纪福音战士 / 明日香</td><td>限定套装</td>
              <td>1</td><td>¥120</td><td>¥108</td><td class="down">-¥12</td>
              <td><span class="status sale">出售中</span></td>
              <td class="actions">详情 / 编辑</td>
            </tr>
            <tr>
              <td>A008</td><td>时光代理人 陆光 透卡</td><td>时光代理人 / 陆光</td><td>透卡</td>
              <td>2</td><td>¥30</td><td>¥38</td><td class="up">+¥8</td>
              <td><span class="status done">已卖出</span></td>
              <td class="actions">详情</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </main>
</template>

<style scoped>
.page { width: min(1240px, calc(100% - 32px)); margin: 0 auto; padding: 28px 0 44px; }
.page-head {
  display: flex; justify-content: space-between; gap: 24px; align-items: center; padding: 30px; border-radius: 10px; color: #fff;
  background: linear-gradient(rgba(10,74,90,0.88), rgba(10,74,90,0.92)),
    url("https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1600&q=80") center/cover;
  box-shadow: var(--shadow);
}
.eyebrow { margin: 0 0 8px; color: var(--gold); font-size: 13px; font-weight: 800; }
h1, h2, p { margin: 0; }
h1 { font-size: 40px; line-height: 1.16; }
.page-head p:last-child { max-width: 640px; margin-top: 12px; color: rgba(255,255,255,0.84); line-height: 1.8; }
.primary { min-height: 44px; border: 0; border-radius: 8px; padding: 0 18px; color: #fff; background: var(--accent); font-weight: 800; cursor: pointer; font: inherit; }
.primary:hover { background: var(--accent-dark); }
.overview-grid { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 16px; margin-top: 20px; }
.overview-card, .toolbar, .table-panel { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); }
.overview-card { padding: 20px; }
.overview-card span { color: var(--muted); font-size: 14px; }
.overview-card strong { display: block; margin-top: 10px; font-size: 28px; }
.overview-card p { margin-top: 8px; color: var(--muted); font-size: 14px; }
.overview-card.gain strong { color: #1f7a4d; }
.toolbar { display: grid; grid-template-columns: minmax(280px, 1fr) 180px 180px 120px; gap: 12px; align-items: center; margin-top: 20px; padding: 18px; }
input, select { width: 100%; height: 44px; border: 1px solid var(--line); border-radius: 8px; padding: 0 12px; color: var(--ink); background: #fff; outline: none; font: inherit; }
input:focus, select:focus { border-color: var(--accent); box-shadow: 0 0 0 4px rgba(15,100,120,0.12); }
.table-panel { margin-top: 20px; padding: 22px; }
.section-head { display: flex; justify-content: space-between; gap: 16px; align-items: center; margin-bottom: 16px; }
.section-head .eyebrow { color: var(--accent); }
h2 { font-size: 24px; }
.section-head span { color: var(--muted); font-size: 14px; }
.table-wrap { overflow-x: auto; }
table { width: 100%; min-width: 1120px; border-collapse: collapse; font-size: 14px; }
th, td { padding: 14px 12px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: middle; }
th { color: var(--muted); background: var(--soft); font-weight: 800; }
tbody tr:hover { background: #fbfdfe; }
.up { color: #1f7a4d; font-weight: 800; }
.down { color: #b9352b; font-weight: 800; }
.status { display: inline-flex; align-items: center; min-height: 28px; border-radius: 999px; padding: 0 10px; font-size: 13px; font-weight: 800; }
.status.hold { color: var(--accent); background: #eaf6f8; }
.status.sale { color: #9a5d00; background: #fff3d7; }
.status.trade { color: #6d4bc2; background: #f1ebff; }
.status.done { color: var(--muted); background: #edf1f3; }
.actions { color: var(--accent); font-weight: 700; white-space: nowrap; }

@media (max-width: 1100px) {
  .overview-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .toolbar { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 760px) {
  .page-head { align-items: flex-start; flex-direction: column; }
  .overview-grid, .toolbar { grid-template-columns: 1fr; }
}
@media (max-width: 560px) {
  .page { width: min(100% - 20px, 1240px); }
  .page-head, .table-panel { padding: 20px; }
  h1 { font-size: 30px; }
}
</style>

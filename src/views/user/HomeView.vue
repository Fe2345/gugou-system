<script setup lang="ts">
import TopBar from '@/layouts/TopBar.vue'
</script>

<template>
  <TopBar />
  <main class="page">
    <section class="hero">
      <div class="hero-text">
        <p class="eyebrow">首页概览</p>
        <h1>欢迎来到谷子交易系统</h1>
        <p>集中展示您的关注窗口、市场推荐和个人数据，帮助您从系统功能快速找到所需业务</p>
      </div>
      <form class="search-box" @submit.prevent>
        <input type="search" placeholder="搜索谷子名称、IP或角色产品">
        <button type="button">搜索</button>
      </form>
    </section>

    <section class="data-grid" aria-label="关键数据概览">
      <article class="data-card">
        <span>我的资产总数</span>
        <strong>36</strong>
        <p>已录入收藏谷子</p>
      </article>
      <article class="data-card">
        <span>资产总值</span>
        <strong>¥ 4,280</strong>
        <p>基于近期成交价格估算</p>
      </article>
      <article class="data-card">
        <span>待处理订单</span>
        <strong>2</strong>
        <p>等待用户完成付款</p>
      </article>
      <article class="data-card">
        <span>待收货物</span>
        <strong>5</strong>
        <p>谷子已发货等待确认收货</p>
      </article>
    </section>

    <section class="quick-section">
      <div class="section-head">
        <div>
          <p class="eyebrow">快捷入口</p>
          <h2>常用功能</h2>
        </div>
      </div>
      <div class="quick-grid">
        <button type="button">
          <strong>录入资产</strong>
          <span>登记您拥有的谷子和相关信息</span>
        </button>
        <button type="button">
          <strong>查看行情</strong>
          <span>查看价格趋势和市场热度</span>
        </button>
        <button type="button">
          <strong>发起交易</strong>
          <span>发布您想交易的谷子需求</span>
        </button>
        <button type="button">
          <strong>参与拼团</strong>
          <span>加入拼团并等待用户集合</span>
        </button>
        <button type="button">
          <strong>查看订单</strong>
          <span>查看购买、交易和收货状态</span>
        </button>
      </div>
    </section>

    <section class="recommend-section">
      <div class="section-head">
        <div>
          <p class="eyebrow">推荐展示</p>
          <h2>热点信息</h2>
        </div>
      </div>

      <div class="recommend-grid">
        <article class="panel">
          <div class="panel-title">
            <h3>热门谷子</h3>
            <span>热度榜</span>
          </div>
          <ul>
            <li><strong>玛奇朵限定徽章</strong><span>热度 2.4k</span></li>
            <li><strong>幽兰色限定角色卡</strong><span>收藏 918</span></li>
            <li><strong>维多利亚明信片</strong><span>关注 786</span></li>
          </ul>
        </article>

        <article class="panel">
          <div class="panel-title">
            <h3>近期成交谷子</h3>
            <span>市场动态</span>
          </div>
          <ul>
            <li><strong>春日限定徽章</strong><span>¥ 128 成交</span></li>
            <li><strong>深海明信片套装</strong><span>¥ 96 成交</span></li>
            <li><strong>秋色色纸</strong><span>¥ 58 成交</span></li>
          </ul>
        </article>

        <article class="panel highlight">
          <div class="panel-title">
            <h3>活跃拼团</h3>
            <span>即将成团</span>
          </div>
          <ul>
            <li><strong>限定徽章拼团套装</strong><span>差 3 人</span></li>
            <li><strong>金色限定徽章</strong><span>差 5 人</span></li>
            <li><strong>迷你卡片拼团</strong><span>差 2 人</span></li>
          </ul>
        </article>

        <article class="panel">
          <div class="panel-title">
            <h3>交换需求</h3>
            <span>匹配推荐</span>
          </div>
          <ul>
            <li><strong>维多利亚金色色纸</strong><span>匹配 12 人</span></li>
            <li><strong>精灵宝可梦卡牌</strong><span>匹配 8 人</span></li>
            <li><strong>明信片套装</strong><span>匹配 6 人</span></li>
          </ul>
        </article>
      </div>
    </section>
  </main>
</template>

<style scoped>
.page {
  width: min(1180px, calc(100% - 32px));
  margin: 0 auto;
  padding: 28px 0 44px;
}

.hero {
  min-height: 260px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(360px, 440px);
  align-items: center;
  gap: 28px;
  padding: 38px;
  border-radius: 10px;
  color: #fff;
  background:
    linear-gradient(rgba(10, 74, 90, 0.86), rgba(10, 74, 90, 0.92)),
    url("https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1600&q=80") center/cover;
  box-shadow: var(--shadow);
}

.eyebrow { margin: 0 0 8px; color: var(--gold); font-size: 13px; font-weight: 800; }
h1, h2, h3, p { margin: 0; }
h1 { font-size: 42px; line-height: 1.16; }
.hero-text p:last-child { max-width: 620px; margin-top: 14px; color: rgba(255, 255, 255, 0.84); line-height: 1.8; }

.search-box {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 92px;
  gap: 10px;
  padding: 12px;
  border: 1px solid rgba(255,255,255,0.28);
  border-radius: 10px;
  background: rgba(255,255,255,0.14);
}
.search-box input { width: 100%; height: 48px; border: 0; border-radius: 8px; padding: 0 14px; outline: none; font: inherit; }
.search-box button {
  border: 0; border-radius: 8px; color: #fff; background: var(--accent); font-weight: 800; cursor: pointer; font: inherit;
}
.search-box button:hover { background: var(--accent-dark); }

.data-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; margin-top: 20px; }

.data-card, .quick-section, .recommend-section, .panel {
  border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow);
}
.data-card { padding: 20px; }
.data-card span { color: var(--muted); font-size: 14px; }
.data-card strong { display: block; margin-top: 10px; font-size: 30px; }
.data-card p { margin-top: 8px; color: var(--muted); }

.quick-section, .recommend-section { margin-top: 20px; padding: 24px; }
.section-head { margin-bottom: 18px; }
.section-head .eyebrow { color: var(--accent); }
h2 { font-size: 26px; }

.quick-grid { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 14px; }
.quick-grid button {
  min-height: 118px; padding: 18px; text-align: left; border: 0; border-radius: 8px;
  color: #fff; background: var(--accent); font-weight: 800; cursor: pointer; font: inherit;
}
.quick-grid button:hover { background: var(--accent-dark); }
.quick-grid strong, .quick-grid span { display: block; }
.quick-grid strong { font-size: 18px; }
.quick-grid span { margin-top: 10px; color: rgba(255,255,255,0.78); line-height: 1.5; }

.recommend-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; }
.panel { padding: 18px; box-shadow: none; }
.panel.highlight { border-color: rgba(220, 161, 46, 0.65); background: #fffaf0; }
.panel-title { display: flex; justify-content: space-between; gap: 12px; align-items: center; margin-bottom: 14px; }
.panel-title h3 { font-size: 18px; }
.panel-title span { color: var(--muted); font-size: 13px; }
ul { list-style: none; margin: 0; padding: 0; display: grid; gap: 10px; }
li { display: flex; justify-content: space-between; gap: 12px; padding: 12px; border-radius: 8px; background: var(--soft); }
li strong { font-size: 14px; }
li span { flex: 0 0 auto; color: var(--accent); font-size: 13px; font-weight: 700; }

@media (max-width: 980px) {
  .hero { grid-template-columns: 1fr; }
  .data-grid, .recommend-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .quick-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}
@media (max-width: 620px) {
  .page { width: min(100% - 20px, 1180px); }
  .hero, .quick-section, .recommend-section { padding: 20px; }
  h1 { font-size: 30px; }
  .search-box, .data-grid, .quick-grid, .recommend-grid { grid-template-columns: 1fr; }
}
</style>

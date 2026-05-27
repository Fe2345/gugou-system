<script setup lang="ts">
import TopBar from '@/layouts/TopBar.vue'
</script>

<template>
  <TopBar />
  <main class="page">
    <section class="hero">
      <div class="hero-text">
        <p class="eyebrow">交换交易</p>
        <h1>发布交换需求与浏览交换列表</h1>
        <p>围绕「我提供什么」和「我想换什么」展示交换需求，帮助你快速找到合适的交易伙伴。</p>
      </div>
      <div class="hero-tools">
        <form class="search-box" @submit.prevent>
          <input type="search" placeholder="搜索谷子名称 / IP / 角色">
          <button type="button">搜索</button>
        </form>
        <div class="mode-tabs">
          <button type="button" class="active">交换需求</button>
          <button type="button">我提供的</button>
          <button type="button">最新发布</button>
        </div>
        <div class="hero-actions">
          <button class="primary" type="button">发布交换</button>
          <button class="secondary" type="button">我的交换</button>
        </div>
      </div>
    </section>

    <section class="swap-layout">
      <aside class="filter-panel" aria-label="交换筛选条件">
        <div class="section-head">
          <p class="eyebrow">筛选条件</p><h2>交换筛选</h2>
        </div>
        <label><span>IP 来源</span>
          <select><option>全部 IP</option><option>女神异闻录</option><option>哈利波特</option><option>精灵宝可梦</option><option>原神</option><option>崩坏星穹铁道</option></select>
        </label>
        <label><span>谷子品类</span>
          <select><option>全部品类</option><option>徽章</option><option>色纸</option><option>明信片</option><option>挂件</option><option>亚克力砖</option></select>
        </label>
        <label><span>交换状态</span>
          <select><option>全部状态</option><option>可交易</option><option>匹配中</option><option>待确认</option></select>
        </label>
        <label><span>是否补差价</span>
          <select><option>不限</option><option>不需补差</option><option>可补差价</option><option>可协商</option></select>
        </label>
        <label><span>交易区域</span>
          <select><option>全部区域</option><option>同城交易</option></select>
        </label>
        <label><span>用户等级</span>
          <select><option>全部用户</option><option>优秀用户</option><option>普通用户</option></select>
        </label>
        <button class="primary full" type="button">应用筛选</button>
      </aside>

      <section class="list-panel">
        <div class="section-head list-head">
          <div><p class="eyebrow">交换广场</p><h2>最新交换列表</h2></div>
          <span>4 个交换</span>
        </div>

        <article class="swap-card">
          <div class="card-meta">
            <strong>交换编号 W001</strong>
            <span>发起人：星空收藏家 · 优秀用户 · 2026-05-04</span>
          </div>
          <div class="compare">
            <section><p class="label">我提供</p><h3>鸣神 千本樱姬 限定徽章</h3><ul><li>品类：徽章</li><li>状态：全新未拆</li><li>参考价：¥48</li></ul></section>
            <div class="arrow">→</div>
            <section><p class="label want">我想换</p><h3>玛奇朵 亚克力砖</h3><ul><li>品类：亚克力砖</li><li>期望状态：全新或微瑕疵</li><li>期望价：可协商</li></ul></section>
          </div>
          <div class="card-bottom">
            <span class="status open">可交易</span>
            <div class="card-actions">
              <button class="secondary" type="button">查看详情</button>
              <button class="primary" type="button">发起交换</button>
            </div>
          </div>
        </article>

        <article class="swap-card">
          <div class="card-meta"><strong>交换编号 W002</strong><span>发起人：纸条收藏家 · 普通用户 · 2026-05-03</span></div>
          <div class="compare">
            <section><p class="label">我提供</p><h3>精灵宝可梦 皮卡丘 限定明信片 3枚</h3><ul><li>品类：明信片</li><li>状态：拆封已用</li><li>参考价：¥72</li></ul></section>
            <div class="arrow">→</div>
            <section><p class="label want">我想换</p><h3>原神 风 岩神角色挂件</h3><ul><li>品类：挂件</li><li>期望状态：颜色较好</li><li>期望价：不需补差</li></ul></section>
          </div>
          <div class="card-bottom">
            <span class="status matching">匹配中</span>
            <div class="card-actions single"><button class="secondary" type="button">查看详情</button></div>
          </div>
        </article>

        <article class="swap-card">
          <div class="card-meta"><strong>交换编号 W003</strong><span>发起人：纸片人仓库 · 优秀用户 · 2026-05-02</span></div>
          <div class="compare">
            <section><p class="label">我提供</p><h3>哈利波特 影山飞雄 亚克力立牌</h3><ul><li>品类：亚克力</li><li>状态：全新未拆</li><li>参考价：¥82</li></ul></section>
            <div class="arrow">→</div>
            <section><p class="label want">我想换</p><h3>崩坏星穹铁道 刃 色纸</h3><ul><li>品类：色纸</li><li>期望状态：全新或拆封</li><li>期望价：可补差价20</li></ul></section>
          </div>
          <div class="card-bottom">
            <span class="status open">可交易</span>
            <div class="card-actions">
              <button class="secondary" type="button">查看详情</button>
              <button class="primary" type="button">发起交换</button>
            </div>
          </div>
        </article>

        <article class="swap-card">
          <div class="card-meta"><strong>交换编号 W004</strong><span>发起人：小明同学 · 新人 · 2026-05-01</span></div>
          <div class="compare">
            <section><p class="label">我提供</p><h3>圣斗士星矢 瞬 门票 2张</h3><ul><li>品类：票据</li><li>状态：颜色较好</li><li>参考价：¥52</li></ul></section>
            <div class="arrow">→</div>
            <section><p class="label want">我想换</p><h3>鸣神 千本樱姬 徽章</h3><ul><li>品类：徽章</li><li>期望状态：全新未拆</li><li>期望价：不需补差</li></ul></section>
          </div>
          <div class="card-bottom">
            <span class="status pending">待确认</span>
            <div class="card-actions single"><button class="secondary" type="button">查看详情</button></div>
          </div>
        </article>
      </section>

      <aside class="right-panel" aria-label="我的交换状态">
        <section class="state-card">
          <div class="section-head"><p class="eyebrow">我的交换</p><h2>状态统计</h2></div>
          <div class="state-grid">
            <div><span>我发起的</span><strong>3</strong></div><div><span>收到的</span><strong>2</strong></div>
            <div><span>匹配中</span><strong>2</strong></div><div><span>待确认</span><strong>1</strong></div>
            <div><span>已完成</span><strong>5</strong></div><div><span>已取消</span><strong>1</strong></div>
          </div>
          <button class="primary full" type="button">查看全部交换记录</button>
        </section>
        <section class="state-card">
          <div class="section-head"><p class="eyebrow">待处理提醒</p><h2>需要确认</h2></div>
          <div class="notice"><strong>W006</strong><span>对方已接受交换，请确认谷子状态。</span></div>
          <div class="notice"><strong>W008</strong><span>对方要求补差价 ¥15，请查看详情。</span></div>
        </section>
      </aside>
    </section>
  </main>
</template>

<style scoped>
.page { width: min(1240px, calc(100% - 32px)); margin: 0 auto; padding: 28px 0 44px; }
.hero {
  display: grid; grid-template-columns: minmax(0, 1fr) minmax(420px, 540px);
  gap: 28px; align-items: center; padding: 34px; border-radius: 10px; color: #fff;
  background: linear-gradient(rgba(10,74,90,0.88), rgba(10,74,90,0.92)),
    url("https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1600&q=80") center/cover;
  box-shadow: var(--shadow);
}
.eyebrow { margin: 0 0 8px; color: var(--gold); font-size: 13px; font-weight: 800; }
h1, h2, h3, p { margin: 0; }
h1 { font-size: 40px; line-height: 1.16; }
.hero-text p:last-child { max-width: 660px; margin-top: 14px; color: rgba(255,255,255,0.84); line-height: 1.8; }
.hero-tools { display: grid; gap: 12px; }
.search-box { display: grid; grid-template-columns: minmax(0, 1fr) 92px; gap: 10px; padding: 12px; border: 1px solid rgba(255,255,255,0.28); border-radius: 10px; background: rgba(255,255,255,0.14); }
input, select { width: 100%; height: 44px; border: 1px solid var(--line); border-radius: 8px; padding: 0 12px; color: var(--ink); background: #fff; outline: none; font: inherit; }
.search-box input { border: 0; }
.primary, .secondary, .search-box button, .mode-tabs button { min-height: 44px; border-radius: 8px; font-weight: 800; cursor: pointer; font: inherit; }
.primary, .search-box button { border: 0; color: #fff; background: var(--accent); }
.primary:hover, .search-box button:hover { background: var(--accent-dark); }
.secondary { border: 1px solid var(--line); color: var(--accent); background: #fff; }
.mode-tabs, .hero-actions { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; }
.hero-actions { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.mode-tabs button { border: 1px solid rgba(255,255,255,0.28); color: #fff; background: rgba(255,255,255,0.12); }
.mode-tabs button.active { color: #172126; background: var(--gold); }
.swap-layout { display: grid; grid-template-columns: 250px minmax(0, 1fr) 280px; gap: 20px; margin-top: 20px; }
.filter-panel, .list-panel, .state-card, .swap-card { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); }
.filter-panel { align-self: start; display: grid; gap: 14px; padding: 20px; }
.section-head { margin-bottom: 14px; }
.section-head .eyebrow { color: var(--accent); }
h2 { font-size: 23px; }
label { display: grid; gap: 8px; color: var(--muted); font-size: 14px; }
.full { width: 100%; }
.list-panel { display: grid; gap: 16px; padding: 22px; }
.list-head { display: flex; justify-content: space-between; gap: 16px; align-items: center; }
.list-head span { color: var(--muted); font-size: 14px; }
.swap-card { display: grid; gap: 16px; padding: 18px; box-shadow: none; }
.card-meta { display: flex; justify-content: space-between; gap: 14px; align-items: center; color: var(--muted); }
.card-meta strong { color: var(--ink); font-size: 18px; }
.compare { display: grid; grid-template-columns: minmax(0, 1fr) 54px minmax(0, 1fr); gap: 14px; align-items: stretch; }
.compare section { padding: 16px; border-radius: 10px; background: var(--soft); }
.label { margin-bottom: 8px; color: var(--accent); font-size: 13px; font-weight: 800; }
.label.want { color: #6d4bc2; }
.compare h3 { font-size: 18px; line-height: 1.35; }
.compare ul { margin: 12px 0 0; padding-left: 18px; color: var(--muted); line-height: 1.8; }
.arrow { display: grid; place-items: center; border-radius: 10px; color: #172126; background: var(--gold); font-weight: 900; }
.card-bottom { display: flex; justify-content: space-between; gap: 12px; align-items: center; }
.status { display: inline-flex; align-items: center; min-height: 30px; border-radius: 999px; padding: 0 12px; font-size: 13px; font-weight: 800; }
.status.open { color: #1f7a4d; background: #e8f7ef; }
.status.matching { color: var(--accent); background: #eaf6f8; }
.status.pending { color: #9a5d00; background: #fff3d7; }
.card-actions { display: grid; grid-template-columns: repeat(2, minmax(0, 120px)); gap: 10px; }
.card-actions.single { grid-template-columns: minmax(0, 120px); }
.right-panel { align-self: start; display: grid; gap: 16px; }
.state-card { padding: 18px; }
.state-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; margin-bottom: 14px; }
.state-grid div, .notice { padding: 12px; border-radius: 8px; background: var(--soft); }
.state-grid span, .notice span { display: block; color: var(--muted); font-size: 13px; }
.state-grid strong { display: block; margin-top: 8px; font-size: 22px; }
.notice + .notice { margin-top: 10px; }
.notice strong { display: block; margin-bottom: 8px; }

@media (max-width: 1120px) {
  .swap-layout { grid-template-columns: 240px minmax(0, 1fr); }
  .right-panel { grid-column: 1 / -1; grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 860px) {
  .hero, .swap-layout, .compare, .right-panel { grid-template-columns: 1fr; }
  .arrow { min-height: 42px; }
}
@media (max-width: 620px) {
  .page { width: min(100% - 20px, 1240px); }
  .hero, .list-panel { padding: 20px; }
  h1 { font-size: 30px; }
  .search-box, .mode-tabs, .hero-actions, .card-bottom, .card-actions, .state-grid { grid-template-columns: 1fr; }
  .card-meta { align-items: flex-start; flex-direction: column; }
}
</style>

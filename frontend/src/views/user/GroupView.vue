<script setup lang="ts">
import TopBar from '@/layouts/TopBar.vue'
</script>

<template>
  <TopBar />
  <main class="page">
    <section class="hero">
      <div class="hero-text">
        <p class="eyebrow">拼团项目</p>
        <h1>浏览拼团项目并判断是否值得参与</h1>
        <p>围绕谷子品类、参团人数和截止时间展示拼团状态，帮助您决定是否值得参与。</p>
      </div>
      <div class="hero-tools">
        <form class="search-box" @submit.prevent>
          <input type="search" placeholder="搜索谷子名称 / IP / 角色">
          <button type="button">搜索</button>
        </form>
        <div class="mode-tabs">
          <button type="button" class="active">正在拼团</button>
          <button type="button">最新发布</button>
          <button type="button">即将截止</button>
        </div>
        <div class="hero-actions">
          <button class="primary" type="button">发起拼团</button>
          <button class="secondary" type="button">我的拼团</button>
        </div>
      </div>
    </section>

    <section class="group-layout">
      <aside class="filter-panel" aria-label="拼团筛选条件">
        <div class="section-head"><p class="eyebrow">筛选条件</p><h2>拼团筛选</h2></div>
        <label><span>IP 来源</span>
          <select><option>全部 IP</option><option>女神异闻录</option><option>哈利波特</option><option>精灵宝可梦</option><option>原神</option></select>
        </label>
        <label><span>谷子品类</span>
          <select><option>全部品类</option><option>徽章</option><option>色纸</option><option>明信片</option><option>挂件</option><option>亚克力砖</option></select>
        </label>
        <label><span>拼团状态</span>
          <select><option>全部状态</option><option>拼团中</option><option>即将成团</option><option>已成团</option><option>即将截止</option></select>
        </label>
        <label><span>目标人数</span>
          <select><option>不限人数</option><option>2人团</option><option>3-5人团</option><option>6人及以上</option></select>
        </label>
        <label><span>截止时间</span>
          <select><option>不限时间</option><option>24小时内</option><option>3天内</option><option>7天内</option></select>
        </label>
        <label><span>价格区间</span>
          <select><option>不限价格</option><option>50元以下</option><option>50-100元</option><option>100元以上</option></select>
        </label>
        <button class="primary full" type="button">应用筛选</button>
      </aside>

      <section class="list-panel">
        <div class="section-head list-head">
          <div><p class="eyebrow">拼团项目列表</p><h2>当前拼团</h2></div>
          <span>5 个项目</span>
        </div>

        <article class="group-card">
          <div class="group-main">
            <div>
              <p class="code">拼团项目 P001</p>
              <h3>收到的第51号通关证周边大礼包</h3>
              <div class="tags"><span>游戏通关证周边</span><span>维多利亚手工</span><span>优秀用户</span></div>
            </div>
            <strong class="price">¥25/人</strong>
          </div>
          <div class="progress-block">
            <div class="progress-head"><span>当前人数 7 / 10</span><strong>70%</strong></div>
            <div class="progress-bar"><span style="width: 70%"></span></div>
            <div class="progress-meta"><span>剩余人数：3人</span><span>截止时间：2026-05-08 22:00</span></div>
          </div>
          <div class="card-bottom">
            <span class="status near">即将成团</span>
            <div class="card-actions">
              <button class="secondary" type="button">查看</button>
              <button class="primary" type="button">参与</button>
            </div>
          </div>
        </article>

        <article class="group-card">
          <div class="group-main">
            <div>
              <p class="code">拼团项目 P002</p>
              <h3>哈利波特 MOLLY 系列盲盒限定拼团</h3>
              <div class="tags"><span>盲盒摆件</span><span>盲盒研究所</span><span>普通用户</span></div>
            </div>
            <strong class="price">¥79/人</strong>
          </div>
          <div class="progress-block">
            <div class="progress-head"><span>当前人数 9 / 12</span><strong>75%</strong></div>
            <div class="progress-bar"><span style="width: 75%"></span></div>
            <div class="progress-meta"><span>剩余人数：3人</span><span>截止时间：2026-05-09 18:00</span></div>
          </div>
          <div class="card-bottom">
            <span class="status doing">拼团中</span>
            <div class="card-actions">
              <button class="secondary" type="button">查看</button>
              <button class="primary" type="button">参与</button>
            </div>
          </div>
        </article>

        <article class="group-card">
          <div class="group-main">
            <div>
              <p class="code">拼团项目 P003</p>
              <h3>精灵宝可梦 一本手册拼团</h3>
              <div class="tags"><span>一本手册</span><span>纸片人仓库</span><span>优秀用户</span></div>
            </div>
            <strong class="price">¥65/人</strong>
          </div>
          <div class="progress-block">
            <div class="progress-head"><span>当前人数 16 / 20</span><strong>80%</strong></div>
            <div class="progress-bar warning"><span style="width: 80%"></span></div>
            <div class="progress-meta"><span>剩余人数：4人</span><span>截止时间：2026-05-07 20:00</span></div>
          </div>
          <div class="card-bottom">
            <span class="status deadline">即将截止</span>
            <div class="card-actions">
              <button class="secondary" type="button">查看</button>
              <button class="primary" type="button">参与</button>
            </div>
          </div>
        </article>

        <article class="group-card">
          <div class="group-main">
            <div>
              <p class="code">拼团项目 P004</p>
              <h3>原神 金色角色卡盲盒拼团</h3>
              <div class="tags"><span>盲盒抽卡</span><span>冒险者补给站</span><span>优秀用户</span></div>
            </div>
            <strong class="price">¥45/人</strong>
          </div>
          <div class="progress-block">
            <div class="progress-head"><span>当前人数 5 / 8</span><strong>62.5%</strong></div>
            <div class="progress-bar"><span style="width: 62.5%"></span></div>
            <div class="progress-meta"><span>剩余人数：3人</span><span>截止时间：2026-05-10 21:00</span></div>
          </div>
          <div class="card-bottom">
            <span class="status doing">拼团中</span>
            <div class="card-actions">
              <button class="secondary" type="button">查看</button>
              <button class="primary" type="button">参与</button>
            </div>
          </div>
        </article>

        <article class="group-card">
          <div class="group-main">
            <div>
              <p class="code">拼团项目 P005</p>
              <h3>哈利波特 官方亚克力挂件限定拼团</h3>
              <div class="tags"><span>限定周边</span><span>魔法商店</span><span>优秀用户</span></div>
            </div>
            <strong class="price">¥52/人</strong>
          </div>
          <div class="progress-block">
            <div class="progress-head"><span>当前人数 8 / 8</span><strong>100%</strong></div>
            <div class="progress-bar success"><span style="width: 100%"></span></div>
            <div class="progress-meta"><span>剩余人数：0人</span><span>截止时间：2026-05-06 23:30</span></div>
          </div>
          <div class="card-bottom">
            <span class="status done">已成团</span>
            <div class="card-actions single"><button class="secondary" type="button">查看</button></div>
          </div>
        </article>
      </section>

      <aside class="right-panel" aria-label="我的拼团状态">
        <section class="state-card">
          <div class="section-head"><p class="eyebrow">我的拼团</p><h2>状态统计</h2></div>
          <div class="state-grid">
            <div><span>我发起的</span><strong>2</strong></div>
            <div><span>我参与的</span><strong>4</strong></div>
            <div><span>拼团中</span><strong>3</strong></div>
            <div><span>待确认</span><strong>1</strong></div>
            <div><span>已成团</span><strong>5</strong></div>
            <div><span>已失败</span><strong>1</strong></div>
          </div>
          <button class="primary full" type="button">查看全部拼团记录</button>
        </section>
        <section class="state-card">
          <div class="section-head"><p class="eyebrow">待处理提醒</p><h2>重要提醒</h2></div>
          <div class="notice"><strong>P001</strong><span>仅差 3 人即可成团，请关注进度。</span></div>
          <div class="notice"><strong>P004</strong><span>将在 2026-05-10 21:00 截止。</span></div>
          <div class="notice"><strong>P006</strong><span>已成团，请确认订单。</span></div>
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
.group-layout { display: grid; grid-template-columns: 250px minmax(0, 1fr) 280px; gap: 20px; margin-top: 20px; }
.filter-panel, .list-panel, .state-card, .group-card { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); }
.filter-panel { align-self: start; display: grid; gap: 14px; padding: 20px; }
.section-head { margin-bottom: 14px; }
.section-head .eyebrow { color: var(--accent); }
h2 { font-size: 23px; }
label { display: grid; gap: 8px; color: var(--muted); font-size: 14px; }
.full { width: 100%; }
.list-panel { display: grid; gap: 16px; padding: 22px; }
.list-head { display: flex; justify-content: space-between; gap: 16px; align-items: center; }
.list-head span { color: var(--muted); font-size: 14px; }
.group-card { display: grid; gap: 16px; padding: 18px; box-shadow: none; }
.group-main { display: flex; justify-content: space-between; gap: 18px; align-items: flex-start; }
.code { margin-bottom: 8px; color: var(--accent); font-size: 13px; font-weight: 800; }
.group-main h3 { font-size: 20px; line-height: 1.35; }
.price { flex: 0 0 auto; color: var(--accent); font-size: 24px; }
.tags { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
.tags span { padding: 6px 10px; border-radius: 7px; color: var(--accent); background: #eaf6f8; font-size: 13px; font-weight: 800; }
.progress-block { display: grid; gap: 8px; }
.progress-head, .progress-meta, .card-bottom { display: flex; justify-content: space-between; gap: 12px; align-items: center; }
.progress-head span, .progress-meta span { color: var(--muted); font-size: 14px; }
.progress-head strong { color: var(--accent); }
.progress-bar { height: 12px; border-radius: 999px; background: #e5eef1; overflow: hidden; }
.progress-bar span { display: block; height: 100%; border-radius: inherit; background: var(--accent); }
.progress-bar.warning :deep(span) { background: var(--gold); }
.progress-bar.success :deep(span) { background: #1f7a4d; }
.status { display: inline-flex; align-items: center; min-height: 30px; border-radius: 999px; padding: 0 12px; font-size: 13px; font-weight: 800; }
.status.near { color: #1f7a4d; background: #e8f7ef; }
.status.doing { color: var(--accent); background: #eaf6f8; }
.status.deadline { color: #b86b00; background: #fff3d7; }
.status.done { color: #1f7a4d; background: #e8f7ef; }
.card-actions { display: grid; grid-template-columns: repeat(2, minmax(0, 110px)); gap: 10px; }
.card-actions.single { grid-template-columns: minmax(0, 110px); }
.right-panel { align-self: start; display: grid; gap: 16px; }
.state-card { padding: 18px; }
.state-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; margin-bottom: 14px; }
.state-grid div, .notice { padding: 12px; border-radius: 8px; background: var(--soft); }
.state-grid span, .notice span { display: block; color: var(--muted); font-size: 13px; }
.state-grid strong { display: block; margin-top: 8px; font-size: 22px; }
.notice + .notice { margin-top: 10px; }
.notice strong { display: block; margin-bottom: 8px; }

@media (max-width: 1120px) {
  .group-layout { grid-template-columns: 240px minmax(0, 1fr); }
  .right-panel { grid-column: 1 / -1; grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 860px) {
  .hero, .group-layout, .right-panel { grid-template-columns: 1fr; }
}
@media (max-width: 620px) {
  .page { width: min(100% - 20px, 1240px); }
  .hero, .list-panel { padding: 20px; }
  h1 { font-size: 30px; }
  .search-box, .mode-tabs, .hero-actions, .group-main, .progress-head, .progress-meta, .card-bottom, .card-actions, .state-grid { grid-template-columns: 1fr; }
  .group-main, .progress-head, .progress-meta, .card-bottom { align-items: flex-start; flex-direction: column; }
}
</style>

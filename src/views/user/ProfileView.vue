<script setup lang="ts">
import TopBar from '@/layouts/TopBar.vue'
</script>

<template>
  <TopBar />
  <main class="page">
    <section class="user-hero">
      <div class="avatar">谷</div>
      <div class="user-info">
        <p class="eyebrow">用户中心</p>
        <h1>谷子收藏家001</h1>
        <div class="user-meta">
          <span>账号ID：U202605001</span>
          <span>手机号：138****5260</span>
          <span>信用等级：优秀用户</span>
          <span>账户状态：正常</span>
        </div>
      </div>
      <div class="hero-actions">
        <button class="primary" type="button">编辑资料</button>
        <button class="secondary" type="button">修改密码</button>
        <button class="secondary" type="button">查看交易记录</button>
      </div>
    </section>

    <section class="profile-layout">
      <aside class="side-menu" aria-label="用户中心菜单">
        <button class="active" type="button">基本信息</button>
        <button type="button">地址管理</button>
        <button type="button">安全设置</button>
        <button type="button">信用评价</button>
        <button type="button">消息通知</button>
      </aside>

      <section class="content">
        <section class="panel">
          <div class="section-head">
            <div><p class="eyebrow">基本信息</p><h2>账户基本信息</h2></div>
            <div class="panel-actions">
              <button class="secondary" type="button">编辑资料</button>
              <button class="primary" type="button">提交修改</button>
              <button class="secondary" type="button">取消</button>
            </div>
          </div>
          <div class="profile-grid">
            <div><span>头像</span><strong>当前头像</strong></div>
            <div><span>昵称</span><strong>谷子收藏家001</strong></div>
            <div><span>手机号</span><strong>138****5260</strong></div>
            <div><span>联系方式</span><strong>微信号或站内联系</strong></div>
            <div><span>注册时间</span><strong>2026-03-15</strong></div>
            <div><span>信用等级</span><strong>优秀市场用户</strong></div>
          </div>
        </section>

        <section class="panel">
          <div class="section-head">
            <div><p class="eyebrow">地址管理</p><h2>收货地址</h2></div>
            <button class="primary" type="button">添加新地址</button>
          </div>
          <div class="table-wrap">
            <table>
              <thead><tr><th>收货人</th><th>手机号</th><th>所在地区</th><th>详细地址</th><th>默认地址</th><th>操作</th></tr></thead>
              <tbody>
                <tr>
                  <td>张同学</td><td>138****5260</td><td>北京市朝阳区</td><td>XX大学南门快递点</td>
                  <td><span class="tag ok">是</span></td><td class="link-text">编辑 / 删除</td>
                </tr>
                <tr>
                  <td>张同学</td><td>138****5260</td><td>北京市海淀区</td><td>XX小区3号楼</td>
                  <td><span class="tag">否</span></td><td class="link-text">设为默认 / 编辑</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section class="panel">
          <div class="section-head"><div><p class="eyebrow">安全设置</p><h2>账户安全</h2></div></div>
          <div class="table-wrap">
            <table>
              <thead><tr><th>安全项目</th><th>当前状态</th><th>操作</th></tr></thead>
              <tbody>
                <tr><td>登录密码</td><td>已设置</td><td class="link-text">修改密码</td></tr>
                <tr><td>手机号</td><td>已绑定</td><td class="link-text">更换手机号</td></tr>
                <tr><td>支付验证</td><td>已开启</td><td class="link-text">修改验证方式</td></tr>
                <tr><td>登录记录</td><td>已开启</td><td class="link-text">查看记录</td></tr>
              </tbody>
            </table>
          </div>
        </section>

        <section class="panel">
          <div class="section-head"><div><p class="eyebrow">信用评价</p><h2>信用状态</h2></div></div>
          <div class="credit-grid">
            <div><span>信用分</span><strong>92</strong></div>
            <div><span>信用等级</span><strong>优秀用户</strong></div>
            <div><span>完成交易</span><strong>18 次</strong></div>
            <div><span>完成交换</span><strong>6 次</strong></div>
            <div><span>拼团履约</span><strong>5 次</strong></div>
            <div><span>投诉记录</span><strong>0 次</strong></div>
          </div>
          <div class="table-wrap">
            <table>
              <thead><tr><th>类型</th><th>对方</th><th>评价内容</th><th>时间</th></tr></thead>
              <tbody>
                <tr><td>交易评价</td><td>卖家 星空收藏家</td><td>发货及时，谷子状态准确</td><td>2026-05-01</td></tr>
                <tr><td>交易评价</td><td>用户 纸条收藏家</td><td>沟通顺畅，包装完好</td><td>2026-04-26</td></tr>
                <tr><td>拼团评价</td><td>团长 维多利亚手工</td><td>拼团过程顺利，品质保证</td><td>2026-04-20</td></tr>
              </tbody>
            </table>
          </div>
        </section>

        <section class="panel">
          <div class="section-head">
            <div><p class="eyebrow">消息通知</p><h2>消息列表</h2></div>
            <div class="panel-actions">
              <button class="secondary" type="button">全部标为已读</button>
              <button class="secondary" type="button">查看详情</button>
              <button class="secondary" type="button">删除消息</button>
            </div>
          </div>
          <div class="message-list">
            <article><span class="tag warn">未读</span><div><strong>订单通知</strong><p>您的订单 O20260503001 已发货</p></div></article>
            <article><span class="tag warn">未读</span><div><strong>交换通知</strong><p>用户星空收藏家发起了交换请求</p></div></article>
            <article><span class="tag">已读</span><div><strong>拼团通知</strong><p>收到的第51号通关证拼团已成团</p></div></article>
            <article><span class="tag">已读</span><div><strong>系统通知</strong><p>平台更新了信用评价规则</p></div></article>
          </div>
        </section>
      </section>

      <aside class="right-panel" aria-label="信息与提醒">
        <section class="remind-card">
          <div class="section-head"><p class="eyebrow">待处理提醒</p><h2>当前状态</h2></div>
          <div class="remind-grid">
            <div><span>待确认收货</span><strong>1</strong></div>
            <div><span>待处理交换</span><strong>2</strong></div>
            <div><span>待确认拼团</span><strong>1</strong></div>
            <div><span>未读消息</span><strong>4</strong></div>
          </div>
        </section>
        <section class="remind-card">
          <div class="section-head"><p class="eyebrow">账户状态</p><h2>当前状态</h2></div>
          <ul>
            <li>当前无违规记录</li>
            <li>近30天无投诉记录</li>
            <li>请及时确认收货</li>
          </ul>
        </section>
      </aside>
    </section>
  </main>
</template>

<style scoped>
.page { width: min(1240px, calc(100% - 32px)); margin: 0 auto; padding: 28px 0 44px; }
.user-hero {
  display: grid; grid-template-columns: 86px minmax(0, 1fr) 360px;
  gap: 20px; align-items: center; padding: 30px; border-radius: 10px; color: #fff;
  background: linear-gradient(rgba(10,74,90,0.88), rgba(10,74,90,0.92)),
    url("https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1600&q=80") center/cover;
  box-shadow: var(--shadow);
}
.avatar { width: 86px; height: 86px; display: grid; place-items: center; border-radius: 10px; color: #172126; background: var(--gold); font-size: 34px; font-weight: 900; }
.eyebrow { margin: 0 0 8px; color: var(--gold); font-size: 13px; font-weight: 800; }
h1, h2, p { margin: 0; }
h1 { font-size: 34px; }
.user-meta { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 12px; }
.user-meta span { padding: 7px 10px; border-radius: 7px; background: rgba(255,255,255,0.13); color: rgba(255,255,255,0.86); font-size: 13px; }
.hero-actions, .panel-actions { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; }
.primary, .secondary { min-height: 42px; border-radius: 8px; padding: 0 14px; font-weight: 800; cursor: pointer; font: inherit; }
.primary { border: 0; color: #fff; background: var(--accent); }
.primary:hover { background: var(--accent-dark); }
.secondary { border: 1px solid var(--line); color: var(--accent); background: #fff; }
.profile-layout { display: grid; grid-template-columns: 190px minmax(0, 1fr) 260px; gap: 20px; margin-top: 20px; }
.side-menu, .panel, .remind-card { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); }
.side-menu { align-self: start; display: grid; gap: 8px; padding: 14px; }
.side-menu button { min-height: 42px; border: 0; border-radius: 8px; padding: 0 12px; color: var(--muted); background: transparent; text-align: left; font-weight: 800; cursor: pointer; font: inherit; }
.side-menu button.active, .side-menu button:hover { color: #fff; background: var(--accent); }
.content, .right-panel { display: grid; gap: 20px; }
.right-panel { align-self: start; }
.panel, .remind-card { padding: 22px; }
.section-head { display: flex; justify-content: space-between; gap: 16px; align-items: center; margin-bottom: 16px; }
.section-head .eyebrow { color: var(--accent); }
h2 { font-size: 23px; }
.profile-grid, .credit-grid, .remind-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
.profile-grid div, .credit-grid div, .remind-grid div { padding: 14px; border-radius: 8px; background: var(--soft); }
.profile-grid span, .credit-grid span, .remind-grid span { display: block; color: var(--muted); font-size: 13px; }
.profile-grid strong, .credit-grid strong, .remind-grid strong { display: block; margin-top: 8px; }
.credit-grid { margin-bottom: 16px; }
.credit-grid strong, .remind-grid strong { font-size: 22px; }
.table-wrap { overflow-x: auto; }
table { width: 100%; min-width: 720px; border-collapse: collapse; font-size: 14px; }
th, td { padding: 13px 12px; border-bottom: 1px solid var(--line); text-align: left; }
th { color: var(--muted); background: var(--soft); }
.link-text { color: var(--accent); font-weight: 800; }
.tag { display: inline-flex; min-height: 26px; align-items: center; border-radius: 999px; padding: 0 10px; color: var(--muted); background: #edf1f3; font-size: 13px; font-weight: 800; }
.tag.ok { color: #1f7a4d; background: #e8f7ef; }
.tag.warn { color: #b86b00; background: #fff3d7; }
.message-list { display: grid; gap: 10px; }
.message-list article { display: grid; grid-template-columns: 70px minmax(0, 1fr); gap: 12px; align-items: start; padding: 14px; border-radius: 8px; background: var(--soft); }
.message-list p { margin-top: 6px; color: var(--muted); }
.remind-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.remind-card ul { margin: 0; padding-left: 20px; color: var(--muted); line-height: 2; }

@media (max-width: 1120px) {
  .user-hero, .profile-layout { grid-template-columns: 1fr; }
  .side-menu { grid-template-columns: repeat(5, minmax(0, 1fr)); }
}
@media (max-width: 760px) {
  .section-head { align-items: flex-start; flex-direction: column; }
  .hero-actions, .panel-actions, .side-menu, .profile-grid, .credit-grid, .remind-grid { grid-template-columns: 1fr; }
}
@media (max-width: 560px) {
  .page { width: min(100% - 20px, 1240px); }
  .user-hero, .panel, .remind-card { padding: 20px; }
  h1 { font-size: 28px; }
}
</style>

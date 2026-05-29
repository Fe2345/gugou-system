<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import TopBar from '@/layouts/TopBar.vue'
import { useUserStore } from '@/stores/user'
import { createGroup } from '@/api/group'
import { getGoodsList } from '@/api/goods'
import type { GoodsItem } from '@/types/goods'

const router = useRouter()
const userStore = useUserStore()
const creditScore = computed(() => userStore.userInfo?.creditScore ?? 100)
const canJoinTeam = computed(() => creditScore.value >= 40)
const goodsList = ref<GoodsItem[]>([])
const submitting = ref(false)

const form = ref({
  product_id: '',
  target_count: '',
  team_price: '',
  deadline_hours: '24',
})

async function loadGoods() {
  try {
    const res = await getGoodsList({ page: 1, pageSize: 100 })
    if (res.code === 200) {
      goodsList.value = res.data.list
    }
  } catch (e) {
    console.error('加载商品列表失败', e)
  }
}

async function handleSubmit() {
  if (!form.value.product_id || !form.value.target_count || !form.value.team_price) {
    alert('请填写必填项')
    return
  }
  const targetCount = Number(form.value.target_count)
  if (targetCount < 2 || targetCount > 100) {
    alert('拼团人数需在 2-100 之间')
    return
  }
  submitting.value = true
  try {
    const res = await createGroup({
      product_id: form.value.product_id,
      target_count: targetCount,
      team_price: Number(form.value.team_price),
      deadline_hours: Number(form.value.deadline_hours) || 24,
    })
    if (res.code === 200) {
      alert('拼团已发起')
      router.push('/group/my')
    } else {
      alert(res.message || '发起失败')
    }
  } catch (e: any) {
    alert(e?.response?.data?.message || '发起失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadGoods()
})
</script>

<template>
  <TopBar />
  <main class="page">
    <section class="page-head">
      <div>
        <p class="eyebrow">拼团市场</p>
        <h1>发起拼团</h1>
        <p>选择商品并设置拼团人数、团购价和截止时间</p>
      </div>
      <button class="secondary" type="button" @click="router.push('/group')">返回拼团</button>
    </section>

    <div v-if="!canJoinTeam" class="credit-warning">
      信用分过低（当前 {{ creditScore }} 分），禁止参与拼团。
    </div>

    <section class="form-panel">
        <div class="form-group">
          <label>选择商品 <span class="required">*</span></label>
          <select v-model="form.product_id" required>
            <option value="">请选择商品</option>
            <option v-for="g in goodsList" :key="g.id" :value="g.id">{{ g.name }}</option>
          </select>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>目标人数 <span class="required">*</span></label>
            <input v-model="form.target_count" type="number" min="2" max="100" placeholder="2-100" required>
          </div>
          <div class="form-group">
            <label>团购价 (元/人) <span class="required">*</span></label>
            <input v-model="form.team_price" type="number" min="0.01" step="0.01" placeholder="每人价格" required>
          </div>
        </div>
        <div class="form-group">
          <label>截止时间 (小时)</label>
          <input v-model="form.deadline_hours" type="number" min="1" max="720" placeholder="24">
          <p class="hint">从现在开始计算，默认 24 小时</p>
        </div>
        <div class="form-actions">
          <button class="secondary" type="button" @click="router.push('/group')">取消</button>
          <button class="primary" type="submit" :disabled="submitting || !canJoinTeam">{{ submitting ? '发起中...' : '确认发起' }}</button>
        </div>
      </form>
    </section>
  </main>
</template>

<style scoped>
.page { width: min(900px, calc(100% - 32px)); margin: 0 auto; padding: 28px 0 44px; }
.page-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 18px; margin-bottom: 20px; }
.eyebrow { margin: 0 0 8px; color: var(--gold); font-size: 13px; font-weight: 800; }
h1, h2, h3, p { margin: 0; }
h1 { font-size: 32px; }
.page-head > div > p:last-child { margin-top: 8px; color: var(--muted); }
.form-panel { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); padding: 28px; }
.form-group { margin-bottom: 20px; }
.form-group label { display: block; margin-bottom: 8px; font-weight: 700; font-size: 14px; }
.required { color: #be123c; }
.hint { margin-top: 6px; color: var(--muted); font-size: 13px; }
.form-row { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
input, select { width: 100%; height: 44px; border: 1px solid var(--line); border-radius: 8px; padding: 0 14px; font: inherit; background: var(--soft); box-sizing: border-box; }
.form-actions { display: flex; gap: 10px; justify-content: flex-end; padding-top: 12px; border-top: 1px solid var(--line); }
.primary, .secondary { min-height: 44px; padding: 0 24px; border-radius: 8px; font-weight: 800; cursor: pointer; font: inherit; }
.primary { border: 0; color: #fff; background: var(--accent); }
.primary:hover { background: var(--accent-dark); }
.primary:disabled { opacity: 0.6; cursor: not-allowed; }
.secondary { border: 1px solid var(--line); color: var(--accent); background: #fff; }
.credit-warning { padding: 14px 18px; border-radius: 8px; background: #fdecea; border: 1px solid #f0b8b3; color: #be123c; font-weight: 600; margin-bottom: 16px; }
</style>

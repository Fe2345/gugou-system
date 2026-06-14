<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import TopBar from '@/layouts/TopBar.vue'
import { useUserStore } from '@/stores/user'
import { createGroup } from '@/api/group'
import { getGoodsList } from '@/api/goods'
import { ElMessage, ElSelect, ElOption } from 'element-plus'
import type { GoodsItem } from '@/types/goods'

const router = useRouter()
const userStore = useUserStore()
const creditScore = computed(() => userStore.userInfo?.creditScore ?? 100)
const canJoinTeam = computed(() => creditScore.value >= 40)
const submitting = ref(false)
const products = ref<GoodsItem[]>([])

const form = ref({
  product_name: '',
  team_price: '',
  deadline_hours: '24',
})

// 小商品选项列表（存储选中的 product_id）
const itemProductIds = ref<string[]>([])
const searchQuery = ref('')

onMounted(async () => {
  await loadProducts()
})

async function loadProducts(keyword?: string) {
  try {
    const params: Record<string, any> = { pageSize: 200 }
    if (keyword) params.keyword = keyword
    const res = await getGoodsList(params)
    if (res.code === 200) {
      products.value = res.data.list || []
    }
  } catch {
    // ignore
  }
}

function addItem(productId: string) {
  if (itemProductIds.value.includes(productId)) {
    ElMessage.warning('该小商品已添加')
    return
  }
  itemProductIds.value.push(productId)
  const p = products.value.find(x => x.id === productId)
  if (p) {
    ElMessage.success(`已添加小商品：${p.name}`)
  }
  searchQuery.value = ''
}

function removeItem(index: number) {
  itemProductIds.value.splice(index, 1)
}

const itemProducts = computed(() =>
  itemProductIds.value
    .map(id => products.value.find(p => p.id === id))
    .filter((p): p is GoodsItem => !!p)
)

async function handleSubmit() {
  if (!form.value.product_name.trim()) {
    ElMessage.warning('请填写拼团名称')
    return
  }
  if (!form.value.team_price) {
    ElMessage.warning('请填写团购价')
    return
  }
  if (itemProductIds.value.length < 2) {
    ElMessage.warning('请至少添加 2 个小商品选项')
    return
  }
  submitting.value = true
  try {
    const res = await createGroup({
      product_name: form.value.product_name.trim(),
      team_price: Number(form.value.team_price),
      deadline_hours: Number(form.value.deadline_hours) || 24,
      items: itemProductIds.value,
    })
    if (res.code === 200) {
      ElMessage.success('拼团已发起')
      router.push('/group/my')
    } else {
      ElMessage.error(res.message || '发起失败')
    }
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '发起失败')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <TopBar />
  <main class="page">
    <section class="page-head">
      <div>
        <p class="eyebrow">拼团市场</p>
        <h1>发起拼团</h1>
        <p>填写拼团名称，添加小商品选项，设置团购价和截止时间</p>
      </div>
      <button class="secondary" type="button" @click="router.push('/group')">返回拼团</button>
    </section>

    <div v-if="!canJoinTeam" class="credit-warning">
      信用分过低（当前 {{ creditScore }} 分），禁止参与拼团。
    </div>

    <section class="form-panel">
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label>拼团名称 <span class="required">*</span></label>
          <input v-model="form.product_name" type="text" maxlength="100" placeholder="例如：拉布布盲盒团、初音未来徽章套装" required>
          <p class="hint">填写你想要的拼团展示名称</p>
        </div>

        <div class="form-group">
          <label>小商品选项 <span class="required">* 至少 2 个</span></label>
          <p class="hint" style="margin-bottom: 10px">从商品库中选择该拼团包含的具体商品选项，参与者可从中选择想要的款式</p>

          <div class="items-list">
            <div v-for="(item, index) in itemProducts" :key="item.id" class="item-row">
              <span class="item-tag">{{ item.name }}{{ item.ipName ? '（' + item.ipName + '）' : '' }}</span>
              <button class="icon-btn danger-icon" type="button" @click="removeItem(index)" title="删除">✕</button>
            </div>
          </div>

          <div class="add-item-row">
            <ElSelect
              v-model="searchQuery"
              filterable
              remote
              :remote-method="loadProducts"
              placeholder="搜索并选择小商品"
              style="flex:1"
              no-data-text="无匹配商品"
              @change="(val: string) => { if (val) { addItem(val); searchQuery = ''; } }"
            >
              <ElOption
                v-for="p in products"
                :key="p.id"
                :label="`${p.name}${p.ipName ? '（' + p.ipName + '）' : ''}`"
                :value="p.id"
                :disabled="itemProductIds.includes(p.id)"
              />
            </ElSelect>
          </div>
          <p class="hint">已添加 {{ itemProducts.length }} 个小商品选项</p>
        </div>

        <div class="form-group">
          <label>团购价 (元/人) <span class="required">*</span></label>
          <input v-model="form.team_price" type="number" min="0.01" step="0.01" placeholder="每人价格" required>
          <p class="hint">拼团人数自动等于小商品选项数量（当前 {{ itemProducts.length }} 人）</p>
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

.items-list { display: grid; gap: 8px; margin-bottom: 12px; }
.item-row { display: flex; gap: 8px; align-items: center; }
.item-row input { flex: 1; }
.item-tag { flex: 1; padding: 0 14px; height: 44px; display: flex; align-items: center; border: 1px solid var(--line); border-radius: 8px; background: var(--soft); font-size: 14px; }
.icon-btn { width: 44px; height: 44px; border-radius: 8px; border: 1px solid var(--line); background: #fff; cursor: pointer; font-size: 16px; display: grid; place-items: center; flex-shrink: 0; }
.danger-icon { color: #be123c; border-color: #f0b8b3; }
.danger-icon:hover { background: #fdecea; }
.add-item-row { display: flex; gap: 8px; align-items: center; margin-top: 8px; }
.add-item-row input { flex: 1; }
.add-item-row .secondary { white-space: nowrap; min-height: 44px; }
</style>

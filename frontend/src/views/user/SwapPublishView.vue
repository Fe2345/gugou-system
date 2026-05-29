<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import TopBar from '@/layouts/TopBar.vue'
import { useUserStore } from '@/stores/user'
import { createSwap } from '@/api/swap'
import { getAssetsList } from '@/api/assets'
import type { AssetItem } from '@/types/assets'

const router = useRouter()
const userStore = useUserStore()
const creditScore = computed(() => userStore.userInfo?.creditScore ?? 100)
const canExchange = computed(() => creditScore.value >= 60)
const assetsList = ref<AssetItem[]>([])
const submitting = ref(false)

const form = ref({
  offered_asset_id: '',
  target_condition: '',
  price_difference_note: '',
})

async function loadAssets() {
  try {
    const res = await getAssetsList()
    if (res.code === 200) {
      assetsList.value = res.data.list.filter(a => a.status === 'holding')
    }
  } catch (e) {
    console.error('加载资产列表失败', e)
  }
}

async function handleSubmit() {
  if (!form.value.offered_asset_id) {
    alert('请选择换出资产')
    return
  }
  submitting.value = true
  try {
    const res = await createSwap({
      offered_asset_id: form.value.offered_asset_id,
      target_condition: form.value.target_condition || undefined,
      price_difference_note: form.value.price_difference_note || undefined,
    })
    if (res.code === 200) {
      alert('发布成功')
      router.push('/swap/my')
    } else {
      alert(res.message || '发布失败')
    }
  } catch (e: any) {
    alert(e?.response?.data?.message || '发布失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadAssets()
})
</script>

<template>
  <TopBar />
  <main class="page">
    <section class="page-head">
      <div>
        <p class="eyebrow">换物市场</p>
        <h1>发布换物请求</h1>
        <p>选择换出的资产并设置目标条件，等待其他用户匹配</p>
      </div>
      <button class="secondary" type="button" @click="router.push('/swap')">返回换物</button>
    </section>

    <div v-if="!canExchange" class="credit-warning">
      信用分不足（当前 {{ creditScore }} 分），需要 60 分以上才能发起换物。
      <button class="link-btn" type="button" @click="router.push('/profile')">查看信用详情</button>
    </div>

    <section class="form-panel">
        <div class="form-group">
          <label>换出资产 <span class="required">*</span></label>
          <select v-model="form.offered_asset_id" required>
            <option value="">请选择要换出的资产</option>
            <option v-for="a in assetsList" :key="a.id" :value="a.id">{{ a.productName }} ({{ a.category }})</option>
          </select>
          <p class="hint">仅显示持有状态的资产</p>
        </div>
        <div class="form-group">
          <label>目标条件</label>
          <textarea v-model="form.target_condition" rows="3" placeholder="描述希望换到的谷子条件，如：同系列其他角色、特定IP等"></textarea>
        </div>
        <div class="form-group">
          <label>差价说明</label>
          <textarea v-model="form.price_difference_note" rows="2" placeholder="如有差价补偿需求，在此说明"></textarea>
        </div>
        <div class="form-actions">
          <button class="secondary" type="button" @click="router.push('/swap')">取消</button>
          <button class="primary" type="submit" :disabled="submitting || !canExchange">{{ submitting ? '发布中...' : '确认发布' }}</button>
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
input, select, textarea { width: 100%; border: 1px solid var(--line); border-radius: 8px; padding: 0 14px; font: inherit; background: var(--soft); box-sizing: border-box; }
input, select { height: 44px; }
textarea { height: auto; padding: 12px 14px; resize: vertical; }
.form-actions { display: flex; gap: 10px; justify-content: flex-end; padding-top: 12px; border-top: 1px solid var(--line); }
.primary, .secondary { min-height: 44px; padding: 0 24px; border-radius: 8px; font-weight: 800; cursor: pointer; font: inherit; }
.primary { border: 0; color: #fff; background: var(--accent); }
.primary:hover { background: var(--accent-dark); }
.primary:disabled { opacity: 0.6; cursor: not-allowed; }
.secondary { border: 1px solid var(--line); color: var(--accent); background: #fff; }
.credit-warning { padding: 14px 18px; border-radius: 8px; background: #fdecea; border: 1px solid #f0b8b3; color: #be123c; font-weight: 600; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; }
.link-btn { border: 0; background: transparent; color: var(--accent); font-weight: 800; cursor: pointer; font: inherit; }
.link-btn:hover { text-decoration: underline; }
</style>

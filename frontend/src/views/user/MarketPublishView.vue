<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import TopBar from '@/layouts/TopBar.vue'
import { useUserStore } from '@/stores/user'
import { publishToMarket, uploadMarketImage } from '@/api/market'
import { getGoodsList } from '@/api/goods'
import { getAssetsList } from '@/api/assets'
import type { GoodsItem } from '@/types/goods'
import type { AssetItem } from '@/types/assets'

const router = useRouter()
const userStore = useUserStore()
const creditScore = computed(() => userStore.userInfo?.creditScore ?? 100)
const canPublish = computed(() => creditScore.value >= 60)
const goodsList = ref<GoodsItem[]>([])
const assetsList = ref<AssetItem[]>([])
const submitting = ref(false)
const uploading = ref(false)
const imageList = ref<{ image_url: string; sort_order: number }[]>([])
const fileInputRef = ref<HTMLInputElement | null>(null)

const form = ref({
  product_id: '',
  asset_id: '',
  price: '',
  quantity: '1',
  description: '',
})

const selectableAssets = computed(() => (
  assetsList.value.filter(asset => (
    asset.status === 'holding'
    && (!form.value.product_id || asset.productId === form.value.product_id)
  ))
))

async function loadOptions() {
  try {
    const [goodsRes, assetsRes] = await Promise.all([
      getGoodsList({ page: 1, pageSize: 100 }),
      getAssetsList(),
    ])
    if (goodsRes.code === 200) goodsList.value = goodsRes.data.list
    if (assetsRes.code === 200) assetsList.value = assetsRes.data.list
  } catch (e) {
    console.error('加载选项失败', e)
  }
}

function triggerFileInput() {
  fileInputRef.value?.click()
}

async function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  const files = target.files
  if (!files || files.length === 0) return

  // 限制最多5张图片
  if (imageList.value.length >= 5) {
    alert('最多只能上传5张图片')
    return
  }

  const file = files[0]
  if (!file) return

  // 验证文件类型
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  if (!allowedTypes.includes(file.type)) {
    alert('仅支持 JPG、PNG、GIF、WebP 格式的图片')
    return
  }

  // 验证文件大小 (限制5MB)
  if (file.size > 5 * 1024 * 1024) {
    alert('图片大小不能超过 5MB')
    return
  }

  uploading.value = true
  try {
    const res = await uploadMarketImage(file)
    if (res.code === 200) {
      imageList.value.push({
        image_url: res.data.image_url,
        sort_order: imageList.value.length,
      })
    } else {
      alert(res.message || '图片上传失败')
    }
  } catch (e: any) {
    alert(e?.response?.data?.message || '图片上传失败')
  } finally {
    uploading.value = false
    // 清空input值，允许重新选择同一文件
    target.value = ''
  }
}

function removeImage(index: number) {
  imageList.value.splice(index, 1)
  // 重新排序
  imageList.value.forEach((img, i) => {
    img.sort_order = i
  })
}

async function handleSubmit() {
  if (!form.value.product_id || !form.value.asset_id || !form.value.price) {
    alert('请填写必填项')
    return
  }
  submitting.value = true
  try {
    const res = await publishToMarket({
      product_id: form.value.product_id,
      asset_id: form.value.asset_id,
      price: Number(form.value.price),
      quantity: Number(form.value.quantity) || 1,
      description: form.value.description,
      images: imageList.value.length > 0 ? imageList.value : undefined,
    })
    if (res.code === 200) {
      alert('发布成功')
      router.push('/market/my')
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
  loadOptions()
})

watch(() => form.value.product_id, () => {
  if (!selectableAssets.value.some(asset => asset.id === form.value.asset_id)) {
    form.value.asset_id = ''
  }
})
</script>

<template>
  <TopBar />
  <main class="page">
    <section class="page-head">
      <div>
        <p class="eyebrow">交易市场</p>
        <h1>发布在售谷子</h1>
        <p>填写商品信息和出售价格，将谷子发布到交易市场</p>
      </div>
      <button class="secondary" type="button" @click="router.push('/market')">返回市场</button>
    </section>

    <div v-if="!canPublish" class="credit-warning">
      信用分不足（当前 {{ creditScore }} 分），需要 60 分以上才能发布商品。
      <button class="link-btn" type="button" @click="router.push('/profile')">查看信用详情</button>
    </div>

    <section class="form-panel">
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label>选择商品 <span class="required">*</span></label>
          <select v-model="form.product_id" required>
            <option value="">请选择商品</option>
            <option v-for="g in goodsList" :key="g.id" :value="g.id">{{ g.name }}</option>
          </select>
        </div>
        <div class="form-group">
          <label>选择资产 <span class="required">*</span></label>
          <select v-model="form.asset_id" required>
            <option value="">请选择资产</option>
            <option v-for="a in selectableAssets" :key="a.id" :value="a.id">{{ a.productName }} (数量: {{ a.quantity }})</option>
          </select>
          <p v-if="form.product_id && !selectableAssets.length" class="hint">暂无可出售的匹配资产，请先在“我的资产”中添加该商品。</p>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>售价 (元) <span class="required">*</span></label>
            <input v-model="form.price" type="number" min="0.01" step="0.01" placeholder="输入售价" required>
          </div>
          <div class="form-group">
            <label>数量</label>
            <input v-model="form.quantity" type="number" min="1" placeholder="1">
          </div>
        </div>
        <div class="form-group">
          <label>商品描述</label>
          <textarea v-model="form.description" rows="4" placeholder="描述商品状态、瑕疵等信息"></textarea>
        </div>
        <div class="form-group">
          <label>商品图片 <span class="optional">(最多5张)</span></label>
          <div class="image-upload-area">
            <div v-for="(img, index) in imageList" :key="index" class="image-preview">
              <img :src="img.image_url" :alt="`商品图片 ${index + 1}`">
              <button type="button" class="remove-btn" @click="removeImage(index)">×</button>
            </div>
            <div v-if="imageList.length < 5" class="upload-trigger" @click="triggerFileInput" :class="{ disabled: uploading }">
              <span v-if="uploading">上传中...</span>
              <span v-else>+ 添加图片</span>
            </div>
          </div>
          <input
            ref="fileInputRef"
            type="file"
            accept="image/jpeg,image/png,image/gif,image/webp"
            style="display: none"
            @change="handleFileChange"
          >
          <p class="upload-hint">支持 JPG、PNG、GIF、WebP 格式，单张图片不超过 5MB</p>
        </div>
        <div class="form-actions">
          <button class="secondary" type="button" @click="router.push('/market')">取消</button>
          <button class="primary" type="submit" :disabled="submitting || !canPublish">{{ submitting ? '发布中...' : '确认发布' }}</button>
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
.form-row { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
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
.optional { color: var(--muted); font-weight: normal; font-size: 12px; }
.image-upload-area { display: flex; flex-wrap: wrap; gap: 12px; }
.image-preview { position: relative; width: 120px; height: 120px; border-radius: 8px; overflow: hidden; border: 1px solid var(--line); }
.image-preview img { width: 100%; height: 100%; object-fit: cover; }
.remove-btn { position: absolute; top: 4px; right: 4px; width: 24px; height: 24px; border-radius: 50%; border: none; background: rgba(0,0,0,0.6); color: #fff; font-size: 16px; cursor: pointer; display: flex; align-items: center; justify-content: center; line-height: 1; }
.remove-btn:hover { background: rgba(0,0,0,0.8); }
.upload-trigger { width: 120px; height: 120px; border: 2px dashed var(--line); border-radius: 8px; display: flex; align-items: center; justify-content: center; cursor: pointer; color: var(--muted); font-size: 14px; transition: all 0.2s; }
.upload-trigger:hover:not(.disabled) { border-color: var(--accent); color: var(--accent); }
.upload-trigger.disabled { opacity: 0.6; cursor: not-allowed; }
.upload-hint { margin-top: 8px; color: var(--muted); font-size: 12px; }
</style>

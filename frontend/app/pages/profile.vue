<script setup>
definePageMeta({ layout: false })
const router = useRouter()
onMounted(() => router.replace('/settings'))
</script>

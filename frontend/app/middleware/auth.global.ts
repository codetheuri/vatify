export default defineNuxtRouteMiddleware((to, from) => {
  const { isAuthenticated } = useAuth()

  // Define public routes
  const publicRoutes = ['/login', '/signup', '/forgot-password', '/reset-password', '/verify-mfa', '/verify-account']

  if (!isAuthenticated.value && !publicRoutes.includes(to.path)) {
    return navigateTo('/login')
  }

  if (isAuthenticated.value && publicRoutes.includes(to.path)) {
    return navigateTo('/')
  }
})

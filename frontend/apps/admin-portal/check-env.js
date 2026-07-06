/**
 * Build-time environment variable checker
 * Ensures NEXT_PUBLIC_API_URL is set during build
 */

console.log('=== Environment Variable Check ===')
console.log('NEXT_PUBLIC_API_URL:', process.env.NEXT_PUBLIC_API_URL)
console.log('NODE_ENV:', process.env.NODE_ENV)
console.log('================================')

if (!process.env.NEXT_PUBLIC_API_URL) {
  console.warn('⚠️  WARNING: NEXT_PUBLIC_API_URL is not set!')
  console.warn('The frontend will default to http://localhost:8000')
  console.warn('Make sure to set this environment variable in Render')
} else {
  console.log('✅ NEXT_PUBLIC_API_URL is set correctly')
}

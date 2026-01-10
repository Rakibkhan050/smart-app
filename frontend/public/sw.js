// Placeholder service worker for push subscriptions
self.addEventListener('push', function(event) {
  const data = event.data ? event.data.text() : 'No payload'
  event.waitUntil(self.registration.showNotification('School SaaS', { body: data }))
})

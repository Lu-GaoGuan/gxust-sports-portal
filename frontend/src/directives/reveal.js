const prefersReducedMotion = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches

export default {
  mounted(element) {
    if (prefersReducedMotion() || !('IntersectionObserver' in window)) {
      element.classList.add('is-visible')
      return
    }

    element.classList.add('reveal-on-scroll')
    const observer = new IntersectionObserver(([entry]) => {
      if (!entry.isIntersecting) return
      element.classList.add('is-visible')
      observer.disconnect()
    }, { threshold: 0.14, rootMargin: '0px 0px -5% 0px' })

    observer.observe(element)
    element._revealObserver = observer
  },
  unmounted(element) {
    element._revealObserver?.disconnect()
  },
}

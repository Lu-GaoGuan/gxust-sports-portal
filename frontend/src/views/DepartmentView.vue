<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { departmentGrowth, departmentSemesters } from '../data/departmentContent'

const chapters = [
  { id: 'overview', number: '01', label: '部门概况' },
  { id: 'work', number: '02', label: '工作方面' },
  { id: 'life', number: '03', label: '生活方面' },
  { id: 'learning', number: '04', label: '学习方面' },
  { id: 'ending', number: '05', label: '结语' },
]
const activeChapter = ref('overview')
let chapterObserver
let manualNavigationUntil = 0
function syncChapterAtPageEnd() {
  if (window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 6) {
    activeChapter.value = 'ending'
    return true
  }
  return false
}

function scrollToChapter(id) {
  activeChapter.value = id
  manualNavigationUntil = performance.now() + 900
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  document.querySelector(`[data-department-chapter="${id}"]`)?.scrollIntoView({
    behavior: reducedMotion ? 'auto' : 'smooth',
    block: 'start',
  })
}

onMounted(() => {
  chapterObserver = new IntersectionObserver((entries) => {
    if (performance.now() < manualNavigationUntil) return
    if (syncChapterAtPageEnd()) return
    const visible = entries.filter((entry) => entry.isIntersecting)
      .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0]
    if (visible) activeChapter.value = visible.target.dataset.departmentChapter
  }, { rootMargin: '-22% 0px -58% 0px', threshold: [0, 0.2, 0.5] })
  document.querySelectorAll('[data-department-chapter]').forEach((section) => chapterObserver.observe(section))
  window.addEventListener('scroll', syncChapterAtPageEnd, { passive: true })
})

onBeforeUnmount(() => {
  chapterObserver?.disconnect()
  window.removeEventListener('scroll', syncChapterAtPageEnd)
})
</script>

<template>
  <main class="department-page">
    <section class="department-hero content-section">
      <div class="department-hero-copy">
        <p class="section-kicker">ABOUT SPORTS DEPARTMENT</p>
        <h1>体育部介绍</h1>
        <p>认真办好每一场赛事，也认真珍藏每一次并肩同行。</p>
        <div class="department-tags"><span>服务师生</span><span>赛事组织</span><span>共同成长</span></div>
      </div>
      <figure><img src="/media/sports-tug-of-war.jpeg" alt="校运会拔河比赛现场"><figcaption>赛场有热爱，幕后有担当</figcaption></figure>
    </section>

    <nav class="department-chapter-nav" aria-label="体育部介绍章节导航">
      <button v-for="chapter in chapters" :key="chapter.id" type="button" :class="{ active: activeChapter === chapter.id }" :aria-current="activeChapter === chapter.id ? 'location' : undefined" @click="scrollToChapter(chapter.id)"><span>{{ chapter.number }}</span>{{ chapter.label }}</button>
    </nav>

    <section class="department-overview content-section" data-department-chapter="overview">
      <div><p class="section-kicker">01 / 部门概况</p><h2>用认真与热爱，<br>让活动有声有色</h2></div>
      <div class="department-lead">
        <p>体育部是学院体育活动的策划者与组织者，始终以“服务师生、丰富校园体育文化”为宗旨，用认真与热爱把每一场赛事、每一次活动办得有声有色。</p>
        <p>下面从工作、生活、学习三个方面，带大家认识这个充满活力与温度的部门。</p>
      </div>
    </section>

    <section v-reveal class="department-work content-section" data-department-chapter="work">
      <header class="department-section-head"><div><p class="section-kicker">02 / 工作方面</p><h2>忙而有章，办赛有方</h2></div><p>体育部的工作贯穿两个学期，现已形成较为成熟的活动组织与赛事保障体系。</p></header>
      <div class="semester-list">
        <article v-for="semester in departmentSemesters" :key="semester.term" class="semester-card">
          <div class="semester-media"><img :src="semester.image" :alt="semester.alt"><div><small>{{ semester.term }}</small><h3>{{ semester.theme }}</h3></div></div>
          <ol class="work-flow">
            <li v-for="(item, index) in semester.items" :key="item.title"><span>{{ String(index + 1).padStart(2, '0') }}</span><div><h4>{{ item.title }}</h4><p>{{ item.text }}</p></div></li>
          </ol>
        </article>
      </div>
      <aside class="work-principle"><p class="section-kicker light">OUR WAY OF WORKING</p><h3>分工明确，责任到人；专人对接，协同合作。</h3><p>我们重视赛事细节、物资管理和活动复盘，也注重培养下一届负责人，让成员在实践中成长，让部门工作持续、稳定地传承。</p></aside>
    </section>

    <section v-reveal class="department-life content-section" data-department-chapter="life">
      <header class="department-section-head"><div><p class="section-kicker">03 / 生活方面</p><h2>温暖相伴，凝心聚力</h2></div><p>体育部不只是完成工作的地方，更是一个团结友爱、充满归属感的大家庭。</p></header>
      <div class="life-grid">
        <figure class="life-photo"><img src="/media/birthday-group.jpeg" alt="体育部成员参加部门生日会"><figcaption><b>生日会</b><span>认真工作，也认真庆祝属于集体的温暖时刻。</span></figcaption></figure>
        <div class="life-story"><p>工作之余，我们为成员送上生日祝福，参与志愿服务，一起组队运动，也通过见面会和团建活动拉近彼此的距离。</p><div class="life-tags"><span>生日祝福</span><span>志愿服务</span><span>组队运动</span><span>见面团建</span></div></div>
        <figure class="life-photo"><img src="/media/team-training.jpeg" alt="成员参加团学素质拓展活动"><figcaption><b>并肩协作</b><span>在协作任务与欢声笑语中，伙伴慢慢成为队友。</span></figcaption></figure>
      </div>
      <p class="life-quote">“赛场边忙碌筹备的身影、活动现场细致协调的瞬间、伙伴们开怀大笑的时刻，都是体育部珍贵的共同回忆。”</p>
    </section>

    <section v-reveal class="department-learning content-section" data-department-chapter="learning">
      <header class="department-section-head"><div><p class="section-kicker light">04 / 学习方面</p><h2>共同成长，薪火相传</h2></div><p>在体育部，每个人的成长都看得见。</p></header>
      <div class="growth-grid"><article v-for="item in departmentGrowth" :key="item.number"><span>{{ item.number }}</span><h3>{{ item.title }}</h3><p>{{ item.text }}</p></article></div>
    </section>

    <section class="department-ending content-section" data-department-chapter="ending">
      <p class="section-kicker">05 / 结语</p>
      <h2>热爱不止于赛场，<br>担当始终在路上</h2>
      <p>回顾一路走来的经历，我们在实践中积累经验，在协作中共同成长，顺利完成了一项项工作任务。感谢老师们的指导与信任，也感谢每一位成员的认真付出。</p>
      <p>未来，愿体育部继续保有这份热爱与担当，组织更多精彩的体育活动，为学院体育文化建设贡献青春力量。</p>
      <RouterLink class="button button-blue" to="/activities">查看活动回顾</RouterLink>
    </section>
  </main>
</template>

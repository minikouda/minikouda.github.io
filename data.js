/* =============================================
   ANDY ZHANG — Site Content Data
   data.js  ·  Edit this file to update content
   ============================================= */

// ── SVG ICON STRINGS ──────────────────────────────────────────────────────────
const SVG = {
  github: `<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
    <path d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.865 8.17 6.839 9.49.5.092.682-.217.682-.482
    0-.237-.008-.866-.013-1.7-2.782.603-3.369-1.34-3.369-1.34-.454-1.156-1.11-1.464-1.11-1.464
    -.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.832
    .092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683
    -.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.578 9.578 0 0 1 12 6.836c.85.004
    1.705.114 2.504.336 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.202 2.394.1 2.647.64.699
    1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0
    1.336-.012 2.415-.012 2.741 0 .267.18.578.688.48C19.138 20.167 22 16.418 22 12c0-5.523-4.477-10-10-10z"/>
  </svg>`,
  play: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
    stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="12" cy="12" r="10"/>
    <polygon points="10 8 16 12 10 16 10 8" fill="currentColor" stroke="none"/>
  </svg>`,
  report: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
    <polyline points="14 2 14 8 20 8"/>
    <line x1="16" y1="13" x2="8" y2="13"/>
    <line x1="16" y1="17" x2="8" y2="17"/>
    <polyline points="10 9 9 9 8 9"/>
  </svg>`,
};

// ── EXPERIENCE ────────────────────────────────────────────────────────────────
const EXPERIENCE = [
  {
    role: 'AI Developer',
    company: 'Monolithic Power Systems',
    date: 'May – Aug 2026',
    alt: false,
    bullets: [
      'Built a layout-preserving <strong>translation agent</strong> for PDF/DOCX/PPTX on a self-hosted LLM: <strong>layout detection and OCR</strong> for scanned pages (BabelDOC reflow + DocLayout-YOLO + MinerU OCR), a <strong>retrieval-based memory</strong> (short-term context window, exemplars retrieved from past translations, and records pinning proper nouns document-wide), and <strong>guided-decoding guards</strong> that prevent digit loss in datasheets — FastAPI + Next.js&nbsp;16 with Azure AD SSO.',
      'Shipped a production <strong>SEC&nbsp;EDGAR MCP server</strong> (Model Context Protocol) on <strong>Cloudflare Workers</strong> that lets the finance team query 10-K/10-Q/8-K filings and XBRL financials directly inside <strong>Claude</strong>. Exposed <strong>10 tools + 2 analyst workflows</strong> over a resilient data layer — token-bucket throttling, exponential-backoff retries, edge caching, and a dependency-free multi-MB HTML parser — with guardrails enforcing exact figures and source citations.',
      'Developed a <strong>slide-generation agent</strong> with <strong>schema-constrained action generation</strong> (executed by a python-pptx backend, so hallucinated edits are impossible) and <strong>VLM-guided iterative refinement</strong> that uses rendered-slide feedback to correct layout defects; improved content-quality scores by <strong>20%</strong> on a PPTEval-style rubric. Event-sourced version tree with replay-based undo; Next.js/React UI.',
    ],
    tags: ['LLM/VLM Agents', 'vLLM', 'MCP', 'Guided Decoding', 'RAG', 'FastAPI', 'TypeScript'],
  },
  {
    role: 'Quantitative Researcher',
    company: 'Guotai Haitong Securities',
    date: 'Jun – Aug 2025',
    alt: false,
    bullets: [
      'Designed and maintained <strong>ETL pipelines</strong> to consolidate financial data from multiple sources, reducing data processing time significantly.',
      'Built an <strong>XGBoost</strong> classification model for equity return prediction, supporting analyst coverage decisions.',
      'Produced research reports synthesizing model outputs with fundamental analysis for investment committee review.',
    ],
    tags: ['XGBoost', 'ETL Pipelines', 'Equity Research', 'SQL'],
  },
  {
    role: 'Quantitative Researcher',
    company: 'SDIC Securities',
    date: 'Oct 2023 – Mar 2024',
    alt: false,
    bullets: [
      'Developed <strong>event-driven A-share stock-selection strategies</strong> from trading disclosures and brokerage co-trading patterns.',
      'Engineered trading-flow features and trained a <strong>LightGBM LambdaRank</strong> model with return-quantile relevance labels and cross-validation; the top-quintile portfolio achieved <strong>2.3% monthly excess return</strong> over the market benchmark.',
      'Trained a <strong>Temporal Graph Network (TGN)</strong> on irregular brokerage–stock interactions to learn brokerage embeddings from trading histories, aggregated into a buying-pressure signal for a CSI&nbsp;300–CSI&nbsp;2000 long-short strategy — improving signal precision by <strong>14%</strong> over heuristic benchmarks.',
    ],
    tags: ['Learning to Rank', 'LightGBM', 'Temporal GNN', 'PyTorch', 'Alpha Research'],
  },
  {
    role: 'President',
    company: 'League of Economics School, Zhejiang University',
    date: 'Jun 2023 – Jun 2024',
    alt: true,
    bullets: [
      'Led a student organization of <strong>500+ members</strong>, overseeing academic lectures, career development events, and cross-department collaborations.',
      'Organized 10+ high-profile events including industry talks with alumni from top financial institutions.',
      'Mentored underclassmen on research skills, internship preparation, and academic planning.',
    ],
    tags: ['Leadership', 'Event Management', 'Mentorship'],
  },
];

// ── PROJECTS ──────────────────────────────────────────────────────────────────
// link types: 'github' | 'demo' | 'report'
// demo types: 'gif' | 'video'
// diagram: optional architecture diagram (only for Claude project)
const PROJECTS = [
  {
    featured: true,
    demo: { type: 'gif', src: 'assets/ga_animation.gif', alt: 'Genetic Algorithm evolution animation' },
    icon: '🧬',
    partner: 'UC Berkeley STAT 243',
    title: 'Genetic Algorithm for Variable Selection',
    desc: 'A flexible Python library for feature selection via Genetic Algorithms. Evolves binary feature masks using tournament selection, uniform/single/k-point crossover, and bit-flip/swap mutation with elitism and adaptive mutation. Supports pluggable fitness backends (Linear/Logistic Regression, Random Forest, SVR, Gradient Boosting), parallel cross-validation, and early stopping. The animation shows the population converging toward the true signal features over 15 generations.',
    links: [{ type: 'github', url: 'https://github.com/minikouda/GA' }],
    tags: ['Genetic Algorithm', 'Feature Selection', 'Optimization', 'scikit-learn', 'Python'],
  },
  {
    featured: true,
    demo: { type: 'gif', src: 'assets/pyramyd_demo.gif', alt: 'Pyramyd RAG demo' },
    icon: '🔍',
    partner: 'ML Scientist · Pyramyd AI · Oct – Dec 2025',
    title: 'RAG-Driven Company Search System',
    desc: 'Company-discovery RAG system over <strong>1M+ employee reviews</strong> that matches user preferences to ranked companies. First-stage retrieval uses a BGE-based <strong>multi-aspect bi-encoder</strong> with hierarchical attention pooling, combining reviews across workload, mentorship and compensation — <strong style="color:var(--gold)">+25% company-level NDCG@10</strong> over an off-the-shelf dense retriever. A <strong>cross-encoder reranker</strong> fine-tuned with InfoNCE loss on preference-violating hard negatives jointly scores queries and review evidence, cutting top-5 preference violations by <strong style="color:var(--gold)">20%</strong>. Tuned FAISS HNSW (graph degree, efSearch) against exact and IVF-PQ indexes for real-time serving: <strong style="color:var(--gold)">32× lower p95 latency</strong> at 96% of exact-search quality, with the full retrieve-and-rerank path at 64 ms p95. Answers come with LLM-generated, evidence-cited explanations.',
    links: [{ type: 'github', url: 'https://github.com/minikouda/pyramyd_ml' }],
    tags: ['RAG', 'Bi-Encoder', 'Cross-Encoder Reranking', 'Contrastive Learning', 'FAISS / HNSW', 'Search'],
  },
  {
    featured: true,
    demo: { type: 'video', src: 'assets/claude_computer_use_demo.mp4' },
    icon: '🖥️',
    title: 'Claude Computer Use — Backend API',
    desc: "Anthropic's reference demo only supports a single session and must be manually restarted between runs. This project wraps it in a production-ready backend with multi-session management, persistent state, and real-time streaming.",
    diagram: {
      flow: [
        { label: 'CLIENT',     color: 'blue',   lines: ['REST calls', 'WebSocket'] },
        { label: 'FASTAPI',    color: 'blue',   lines: ['Session CRUD', 'SQLAlchemy DB', 'WS streaming'] },
        { label: 'AGENT LOOP', color: 'gold',   lines: ['Tool dispatch', 'State tracking', 'Error handling'] },
        { label: 'CLAUDE API', color: 'purple', lines: ['claude-opus-4', 'Tool use', 'Vision'] },
      ],
      docker: {
        label: 'DOCKER  ·  Ubuntu 22.04 + X11',
        tools: ['Screenshot', 'Mouse / Keyboard', 'Bash', 'File Edit', 'Firefox', 'LibreOffice'],
      },
    },
    links: [{ type: 'github', url: 'https://github.com/minikouda/msca' }],
    tags: ['FastAPI', 'Claude API', 'Computer Use', 'Docker', 'WebSocket', 'SQLAlchemy', 'Python'],
  },
  {
    featured: true,
    slides: [
      { src: 'assets/refgame_demo.png',     alt: 'How a reference game works: the speaker describes a hidden target, the listener must pick it or ask' },
      { src: 'assets/refgame_decision.png', alt: 'The ask-or-commit rule: commit when confident, ask only when the description is ambiguous' },
      { src: 'assets/refgame_result.png',   alt: 'Key finding: the listener that never over-asks scores highest; more reasoning lowers the score' },
    ],
    slideLabels: false,
    icon: '🎯',
    partner: 'Research Assistant · UC Berkeley · Apr – May 2026',
    title: 'Ask or Commit? Cost-Aware Clarification in Multimodal Reference Games',
    desc: 'A decision-theoretic study of when a language agent should <em>ask a clarifying question</em> versus commit. Grounded in Rational Speech Act theory, the listener asks only when its top posterior falls below a confidence threshold of <strong>1&minus;c</strong> — a training-free expected-utility rule. Built a speaker/listener framework for vision-language agents (Claude, Gemini) and benchmarked 6 posterior-estimation methods and 8 speaker strategies across 600 scenes (<strong style="color:var(--gold)">28,800 evaluations</strong>); a counterintuitive result emerges: <strong>more reasoning hurts</strong>. Chain-of-Thought listeners verbalize visual uncertainty into diffuse posteriors that trigger needless questions and <em>lower</em> cost-penalized accuracy, even when the top guess was already right. The bottleneck is not reasoning capability but <strong style="color:var(--gold)">miscalibrated uncertainty</strong> — <strong>posterior sharpening recovers 76%</strong> of the lost cost-penalized accuracy.',
    links: [
      { type: 'github', url: 'https://github.com/minikouda/ask-or-commit' },
      { type: 'report', url: 'assets/ask-or-commit.pdf' },
    ],
    tags: ['LLMs &amp; VLMs', 'Pragmatic Reasoning (RSA)', 'Uncertainty Calibration', 'Decision Theory', 'Zero-Shot', 'Python'],
  },
  {
    featured: true,
    slides: [
      { src: 'assets/cloud_data_pipeline.png',          alt: 'Data Pipeline' },
      { src: 'assets/cloud_autoencoder_architecture.png', alt: 'Autoencoder Architecture' },
    ],
    icon: '🛰️',
    title: 'Polar Cloud Detection — MISR Satellite Imagery',
    desc: 'Pixel-level cloud classification in Arctic regions using NASA\'s Multi-angle Imaging SpectroRadiometer (MISR). Exploits the physical insight that clouds scatter light differently across viewing angles than ice/snow. Engineered 9 features from 5-angle radiances (including a novel NDAI variant that outperforms the original). Pre-trained a convolutional autoencoder on 164 unlabeled satellite images to extract 32-dim spatial embeddings — concatenated with hand-crafted features for 41 total inputs. Histogram Gradient Boosting achieves <strong style="color:var(--gold)">96.1% accuracy</strong> and <strong style="color:var(--gold)">0.996 AUC</strong>; SD (local radiance variance) is the dominant predictor, with clouds showing ~4.4× higher variance than ice.',
    links: [
      { type: 'github', url: 'https://github.com/minikouda/polar-cloud-detection' },
      { type: 'report', url: 'assets/polar-cloud-detection.pdf' },
    ],
    tags: ['Classification', 'Remote Sensing', 'Transfer Learning', 'Feature Engineering', 'scikit-learn', 'Python'],
  },
  {
    featured: false,
    icon: '📈',
    partner: 'Research Assistant · Zhejiang University · Nov – Dec 2024',
    title: 'Robust Portfolio Optimization of CNE5 Factors',
    desc: 'Framed portfolio allocation as estimating risk from correlated predictors: standardized 100+ style and industry factors and applied <strong>sparse PCA</strong> to extract interpretable structure for high-dimensional covariance estimation. Trained a <strong>GRU-based covariance predictor</strong> with a positive-definite low-rank-plus-diagonal parameterization and Gaussian NLL loss, cutting out-of-sample portfolio-variance forecast RMSE by <strong>21%</strong> vs Ledoit–Wolf shrinkage. Stress-tested with 10,000+ Monte Carlo scenarios and block bootstrap: the statistical risk models improved Sharpe by <strong>11%</strong> and cut max drawdown by <strong>6%</strong>.',
    links: [{ type: 'github', url: 'https://github.com/minikouda/quantinvest' }],
    tags: ['Covariance Estimation', 'GRU', 'Sparse PCA', 'Robust Optimization', 'Quant Finance', 'Python'],
  },
  {
    featured: false,
    icon: '🤖',
    title: 'Berkeley EECS RAG Question-Answering System',
    desc: 'End-to-end Retrieval-Augmented Generation pipeline over Berkeley EECS web content. Built an async web crawler, LLM-powered data cleaner, and semantic chunker. Retrieval uses FAISS dense search (BGE embeddings) fused with BM25 via RRF, augmented by HyDE query expansion and cross-encoder re-ranking. Generation powered by LLaMA-3.1-8B.',
    links: [
      { type: 'demo', url: 'projects/rag-demo/' },
      { type: 'github', url: 'https://github.com/minikouda/cs-288/tree/main/cs288-sp26-a3' },
    ],
    tags: ['RAG', 'FAISS', 'BM25', 'HyDE', 'LLaMA', 'Web Crawling', 'NLP'],
  },
  {
    featured: false,
    icon: '🏥',
    title: 'ciTBI Pediatric Head Trauma — EDA',
    desc: 'Exploratory data analysis of 42,000+ pediatric head trauma cases from the PECARN TBI dataset. Identified GCS as the dominant predictor of clinically important TBI, characterized age-stratified risk profiles, and analyzed CT utilization patterns against actual ciTBI outcomes.',
    links: [
      { type: 'github', url: 'https://github.com/minikouda/citbi-eda' },
      { type: 'report', url: 'assets/ciTBI-EDA.pdf' },
    ],
    tags: ['EDA', 'Clinical Data', 'Python', 'Health Informatics', 'Statistical Analysis'],
  },
  {
    featured: false,
    icon: '🔬',
    title: 'Capital Market, Rational Inattention & Internet Search',
    desc: 'Empirical research examining how investor limited attention — proxied through internet search volume indices — affects asset pricing in capital markets. Constructed panel datasets linking search trends to stock-level return anomalies.',
    links: [],
    tags: ['Econometrics', 'Panel Data', 'Asset Pricing', 'Python', 'Quantitative Investment'],
  },
];

// ── EDUCATION ─────────────────────────────────────────────────────────────────
const EDUCATION = [
  {
    logo: 'UC',
    logoClass: 'edu-logo-berkeley',
    degree: 'M.A. Statistics &amp; Data Science',
    school: 'University of California, Berkeley',
    date: 'Aug 2025 – Dec 2026',
    gpa: '4.0 / 4.0',
    desc: 'Advanced topics in Neural Networks, NLP, Randomness &amp; Computation, Causal Inference, Statistical Learning Theory, and Optimization.',
    honors: [],
    tags: ['Neural Networks', 'NLP', 'Causal Inference', 'Statistical Learning Theory', 'Optimization'],
  },
  {
    logo: 'ZJU',
    logoClass: 'edu-logo-zju',
    degree: 'B.S. Economics (Advanced Class), Minor in Mathematics',
    school: 'Zhejiang University',
    date: 'Aug 2021 – Jun 2025',
    gpa: '3.96 / 4.0',
    desc: 'Advanced Class (selected from top 10%). Coursework in Game Theory, Econometrics, Time Series, and Quantitative Investment; Math minor in Real Analysis, Stochastic Processes, Numerical Analysis, PDE, and Operations Research.',
    honors: [
      'First Prize, National College Mathematics Competition',
      'Certificate of the Chu Kochen Honors Program (Top 1.3%)',
      'Outstanding Graduate',
      'First Prize Scholarships (Multiple)',
    ],
    tags: [],
  },
];

// ── BLOGS ─────────────────────────────────────────────────────────────────────
const BLOGS = [
  {
    date: 'March 4, 2026',
    title: 'Equilibrium Strategies in the Continuous Yankee Swap',
    href: 'blogs/game/game.html',
    desc: 'A rigorous game-theoretic analysis of sequential allocation mechanisms, exploring backward induction and optimal stealing heuristics in a continuous uniform distribution.',
    tag: 'Game Theory',
  },
  {
    date: 'December 18, 2025',
    title: 'STAT 201B: Advanced Statistics Notes',
    href: 'blogs/201B_note/201B_note.html',
    desc: 'A comprehensive set of study notes for STAT 201B at UC Berkeley, covering Bootstrap, MLE, Bayesian inference, and decision theory.',
    tag: 'Mathematics',
  },
];

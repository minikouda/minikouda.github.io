# STAT 201B: Introduction to Statistics at an Advanced Level

<div style="text-align: center; margin-bottom: 40px;">
  <img src="images/page-1.png" alt="Cover Page" style="width: 100%; max-width: 600px; border-radius: 12px; box-shadow: 0 20px 40px rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1);">
</div>

These are my personal study notes for the **STAT 201B** course at UC Berkeley. The notes cover fundamental and advanced statistical concepts, ranging from axiomatic foundations of inference to decision theory and Bayesian statistics.

<div class="glass-card" style="padding: 20px; margin: 30px 0; text-align: center;">
  <p class="mono" style="font-size: 1rem; color: var(--gold); margin-bottom: 15px;">// Resource Archive</p>
  <a href="STAT201B_ShizheZhang.pdf" class="back-btn mono" style="font-size: 1.2rem; text-decoration: none;" download>
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="margin-right: 8px;"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
    Download Full PDF Notes (71 Pages)
  </a>
</div>

## Course Highlights

The notes are structured by lecture and include rigorous mathematical derivations, examples, and computational snippets in Python.

### 1. The Bootstrap Method
The Bootstrap is a powerful non-parametric tool for estimating the sampling distribution of an estimator by resampling with replacement from the original data.

$$ \hat{V}_{boot} = \frac{1}{B} \sum_{j=1}^B (T_{n,j}^* - \bar{T}_n^*)^2 $$

### 2. Maximum Likelihood Estimation (MLE)
Detailed analysis of MLE properties, including consistency, asymptotic normality, and efficiency.

$$ \sqrt{n}(\hat{\theta}_n - \theta) \xrightarrow{D} N(0, 1/I(\theta)) $$

### 3. Bayesian Inference & Decision Theory
Coverage of posterior distributions, conjugate priors, and decision-theoretic frameworks such as Minimax and Bayes rules.

$$ f(\theta|x^n) = \frac{f(x^n|\theta)f(\theta)}{f(x^n)} $$

---

## Example Pages from the Notes

<div class="gallery" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0;">
  <img src="images/page-2.png" alt="Example Page 2" style="width: 100%; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);">
  <img src="images/page-3.png" alt="Example Page 3" style="width: 100%; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);">
</div>

---

## Detailed Lecture List
*   **Lecture 1-2:** Introduction to Inference & Point Estimation
*   **Lecture 3-4:** The Bootstrap & Parametric Inference
*   **Lecture 5-6:** Sufficiency & Minimal Sufficiency
*   **Lecture 7-9:** MLE Properties & Fisher Information
*   **Lecture 11-12:** Hypothesis Testing & Likelihood Ratio Tests
*   **Lecture 13-15:** Bayesian Statistics & Posterior Distribution
*   **Lecture 16-18:** Decision Theory (Minimax, Bayes Risk)

<div class="glass-card" style="padding: 20px; margin: 30px 0;">
  <p class="mono" style="font-size: 0.9rem; color: var(--gold); margin-bottom: 10px;">// Insight</p>
  <p style="margin-bottom: 0;">Statistical inference is essentially the art of "reversing" the generative process—using observed data to uncover the hidden parameters that produced it.</p>
</div>

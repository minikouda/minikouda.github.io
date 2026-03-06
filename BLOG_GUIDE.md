# 🐥 Andy's Blog Publishing Guide

This guide explains how to add new blog posts to your website using the established **Berkeley Blue & Gold** theme and the **MathJax** workflow.

## 📁 Directory Structure
*   `index.html`: The homepage where the "Latest Blogs" cards live.
*   `style.css`: Global styles (colors, fonts, layout).
*   `blogs/`:
    *   `blog-post-template.html`: The empty shell for new posts.
    *   `blog-post-1.html`, etc.: Your actual published posts.

---

## 🛠 Step 1: Convert your Content
Use **Pandoc** to convert your source files into HTML "fragments" that can be pasted into the template.

### From LaTeX (`.tex`)
Run this in your terminal to preserve all math formulas:
```bash
pandoc blogs/your-file.tex -f latex -t html --mathjax -o blogs/fragment.html
```

### From Markdown (`.md`)
```bash
pandoc blogs/your-file.md -f markdown -t html --mathjax -o blogs/fragment.html
```

### From Word (`.docx`)
```bash
pandoc blogs/your-file.docx -f docx -t html --mathjax -o blogs/fragment.html
```

---

## 📝 Step 2: Create the Blog Page
1.  **Duplicate** `blogs/blog-post-template.html` and rename it (e.g., `blogs/my-new-post.html`).
2.  **Open** your new file and update the metadata:
    *   `<title>`: The browser tab title.
    *   `<span class="blog-date">`: The date shown on the page.
    *   `<span class="blog-category">`: The category (e.g., Mathematics, DS).
    *   `<h1 class="blog-post-title">`: The main heading.
3.  **Paste Content:** Open `blogs/fragment.html`, copy everything, and paste it inside the `<article class="blog-content tex2jax_process">` tag.

---

## 🏠 Step 3: Add to Homepage
To make the blog visible on your main site, open `index.html` and find the `<div class="blogs-grid">` section. Add a new card:

```html
<div class="blog-card glass-card fade-in">
  <div class="blog-date mono">March 6, 2026</div>
  <h3 class="blog-title"><a href="blogs/my-new-post.html">Your Title Here</a></h3>
  <p class="blog-desc">A short 1-2 sentence summary of the post.</p>
  <div class="blog-footer">
    <span class="blog-tag p-tag">Category</span>
    <a href="blogs/my-new-post.html" class="blog-more">Read More →</a>
  </div>
</div>
```

---

## 🎨 Styling Tips
### 1. Math Support
The template uses **MathJax**. You can write LaTeX directly in the HTML file:
*   Inline: `$x = 2$`
*   Block: `$$ E = mc^2 $$`

### 2. Theorem & Proof Blocks
If your LaTeX conversion uses `\begin{theorem}` or `\begin{proof}`, the template will automatically style them with a gold border. You can manually wrap content like this:
```html
<div class="theorem">
  <strong>Theorem 1.</strong> <em>Your mathematical statement here.</em>
</div>

<div class="proof">
  <em>Proof.</em> Your derivation here. ◻
</div>
```

### 3. Highlighting Insights
Use the "Glass Card" for key takeaways:
```html
<div class="glass-card" style="padding: 20px; margin: 30px 0;">
  <p class="mono" style="font-size: 0.9rem; color: var(--gold); margin-bottom: 10px;">// Insight</p>
  <p>Your important conclusion here.</p>
</div>
```

---

## ⚠️ Important Checklist
*   **Relative Paths:** Because blogs are in the `blogs/` folder, all links to core assets must start with `../` (e.g., `../style.css`, `../index.html`, `../images/profile.png`).
*   **MathJax Class:** Ensure the `<article>` tag has the `tex2jax_process` class, or MathJax might skip it.
*   **Clean Up:** Delete the temporary `fragment.html` once you are done pasting.

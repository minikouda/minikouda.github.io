# 🐥 Andy's Blog Publishing Guide

This guide explains how to add new blog posts to your website using the established **Berkeley Blue & Gold** theme and the **MathJax** workflow.

## 📁 Directory Structure
*   `index.html`: The homepage where the "Latest Blogs" cards live.
*   `style.css`: Global styles (colors, fonts, layout).
*   `blogs/`:
    *   `blog-post-template.html`: The empty shell for new posts.
    *   `blog-post-1.html`, etc.: Your actual published posts.

---

## 🚀 Automated Workflow (Recommended)
You can now automate the conversion and page creation using the `publish.py` script. This ensures all styling, math support, and section numbering are applied correctly.

### How to use:
Run the script from the `blogs/` directory:
```bash
python3 publish.py source_file target_file --title "Your Title" --category "Category"
```

**Example (LaTeX):**
```bash
python3 publish.py game.tex game.html --title "Equilibrium Strategies" --category "Mathematics"
```

**Example (Markdown):**
```bash
python3 publish.py notes.md notes.html --title "Research Notes" --category "DS"
```

The script will:
1.  **Convert** your content via Pandoc.
2.  **Clean up** LaTeX artifacts (like table "continued" markers).
3.  **Inject** the content into the theme template.
4.  **Update** all metadata (title, date, category).
5.  **Apply** automatic section numbering and professional table styling.

---

## 🛠 Manual Workflow (Legacy)
If you prefer to do it manually:
1.  **Convert:** Use Pandoc to get an HTML fragment:
    ```bash
    pandoc your-file.tex -f latex -t html --mathjax -o fragment.html
    ```
2.  **Duplicate Template:** Copy `blog-post-template.html` to your new filename.
3.  **Update Meta:** Manually edit `<title>`, `<h1 class="blog-post-title">`, etc.
4.  **Paste:** Copy from `fragment.html` into the `<article>` tag.

---

## 🏠 Step 3: Add to Homepage
To make the blog visible on your main site, open `index.html` and find the `<div class="blogs-grid">` section. Add a new card. 

**Note:** If your blog is in a nested folder (like `blogs/game/game.html`), ensure the link includes the folder name.

```html
<div class="blog-card glass-card fade-in">
  <div class="blog-date mono">March 8, 2026</div>
  <!-- Use folder name if nested: blogs/folder/file.html -->
  <h3 class="blog-title"><a href="blogs/game/game.html">Your Title Here</a></h3>
  <p class="blog-desc">A short 1-2 sentence summary of the post.</p>
  <div class="blog-footer">
    <span class="blog-tag p-tag">Category</span>
    <a href="blogs/game/game.html" class="blog-more">Read More →</a>
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

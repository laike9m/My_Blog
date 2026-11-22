import os
import re

import litellm

litellm.suppress_debug_info = True

DEFAULT_SUMMARY_MODEL = "deepseek/deepseek-flash"

_CODE_BLOCK_RE = re.compile(r"```.*?```", re.DOTALL)
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")
_ASCII_ALPHA_RE = re.compile(r"[A-Za-z]")

SYSTEM_PROMPT_EN = (
    "You write concise blog post descriptions for HTML meta tags and social media previews. "
    "Summarize the provided blog post in 1 to 3 concise sentences in English capturing its "
    "core point. Output only the plain-text summary: no markdown, no bullet points, no "
    "labels or prefixes, and no surrounding quotation marks."
)

SYSTEM_PROMPT_ZH = (
    "你负责为博客文章撰写简明扼要的简介，用于 HTML meta description 和社交媒体分享预览。"
    "请用 1 到 3 句简洁流畅的中文概括文章的核心观点。"
    "只输出纯文本简介本身，不要使用 Markdown、项目符号或外层引号，也不要添加“摘要：”“简介：”等前缀。"
)


def _is_chinese_article(body: str) -> bool:
    prose = _CODE_BLOCK_RE.sub("", body)
    cjk_count = len(_CJK_RE.findall(prose))
    latin_count = len(_ASCII_ALPHA_RE.findall(prose))
    return cjk_count > 0 and (cjk_count / max(cjk_count + latin_count, 1)) >= 0.1


def summarize_post(body: str, title: str = "", model: str | None = None) -> str:
    content_body = (body or "").strip()
    if not content_body:
        raise ValueError("Article body is empty.")

    selected_model = model or os.environ.get("SUMMARY_MODEL", DEFAULT_SUMMARY_MODEL)
    if selected_model.startswith("deepseek/") and not os.environ.get("DEEPSEEK_API_KEY"):
        raise ValueError("DEEPSEEK_API_KEY is not configured in .env.")

    is_zh = _is_chinese_article(content_body)
    system_prompt = SYSTEM_PROMPT_ZH if is_zh else SYSTEM_PROMPT_EN

    clean_title = (title or "").strip()
    if is_zh:
        user_prompt = (
            f"标题：{clean_title}\n\n正文：\n{content_body}"
            if clean_title
            else f"正文：\n{content_body}"
        )
    else:
        user_prompt = (
            f"Title: {clean_title}\n\nArticle:\n{content_body}"
            if clean_title
            else f"Article:\n{content_body}"
        )

    response = litellm.completion(
        model=selected_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        reasoning_effort="none",
        drop_params=True,
        timeout=60,
    )

    choices = getattr(response, "choices", None) or []
    if not choices:
        raise RuntimeError("Model returned no choices.")

    summary = (getattr(choices[0].message, "content", None) or "").strip()
    if not summary:
        raise RuntimeError("Model returned an empty summary.")

    return summary

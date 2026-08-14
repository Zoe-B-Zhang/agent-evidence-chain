"""基于字符/词的 token 估算（D2）。"""

from __future__ import annotations


def estimate_tokens(text: str) -> int:
    """粗估 token 数：约 4 字符 ≈ 1 token，且不低于词数。"""
    if not text:
        return 0
    by_chars = max(1, (len(text) + 3) // 4)
    by_words = max(1, len(text.split()))
    return max(by_chars, by_words)


def estimate_prompt_tokens(system: str, user: str) -> int:
    """估算 prompt 总 token。"""
    return estimate_tokens(system) + estimate_tokens(user)

"""
Summarization providers.

Swap the implementation of `summarize_text` later (e.g. OpenAI)
without changing views.
"""

from django.conf import settings


class SummarizationError(Exception):
    """Raised when summarization fails for a user-visible reason."""


def summarize_text(original_text: str) -> str:
    """Return a Japanese summary of original_text via the configured provider."""
    return summarize_with_gemini(original_text)


def summarize_with_gemini(original_text: str) -> str:
    api_key = (getattr(settings, 'GEMINI_API_KEY', None) or '').strip()
    if not api_key:
        raise SummarizationError(
            'GEMINI_API_KEY が設定されていません。.env にキーを追加してください。'
        )

    text = (original_text or '').strip()
    if not text:
        raise SummarizationError('原文が空です。')

    # Soft limit to avoid huge bills / timeouts on MVP
    if len(text) > 50000:
        raise SummarizationError('原文が長すぎます（5万文字以内にしてください）。')

    model_name = getattr(settings, 'GEMINI_MODEL', None) or 'gemini-2.0-flash'
    prompt = (
        '次の文章を日本語で要約してください。\n'
        '・重要な点を逃さない\n'
        '・箇条書きを中心に、短く読みやすくまとめる\n'
        '・前置きや「要約すると」などのメタ説明は書かない\n\n'
        '----\n'
        f'{text}'
    )

    try:
        from google import genai

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )
    except Exception as exc:  # noqa: BLE001 — surface as user message
        raise SummarizationError(
            f'Gemini API の呼び出しに失敗しました: {exc}'
        ) from exc

    summary = (getattr(response, 'text', None) or '').strip()
    if not summary:
        raise SummarizationError('要約結果が空でした。もう一度試してください。')
    return summary

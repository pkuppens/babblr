"""Provide a shared language catalog for STT and TTS.

This module defines a small, explicit list of language/locales supported by Babblr.
It centralizes names, native names, ISO codes, and capability flags so API endpoints
and services can stay consistent.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LanguageVariant:
    """Represent a single locale variant used by the app.

    Args:
        locale (str): IETF BCP 47 locale identifier (e.g., "en-US", "es-ES").
        iso_639_1 (str): ISO-639-1 language code (e.g., "en", "es").
        iso_3166_1 (str | None): Optional ISO-3166-1 country/region code (e.g., "US", "GB").
        name (str): English display name (e.g., "English (United States)").
        native_name (str): Native display name (e.g., "English (United States)").
        stt (bool): Whether this locale is supported for speech-to-text.
        tts (bool): Whether this locale is supported for text-to-speech.
    """

    locale: str
    iso_639_1: str
    iso_3166_1: str | None
    name: str
    native_name: str
    stt: bool
    tts: bool


# Note: Whisper itself supports many languages. This catalog is intentionally scoped
# to languages/locales we explicitly support in Babblr UX and defaults.
LANGUAGE_VARIANTS: list[LanguageVariant] = [
    LanguageVariant(
        locale="en-US",
        iso_639_1="en",
        iso_3166_1="US",
        name="English (United States)",
        native_name="English (United States)",
        stt=True,
        tts=True,
    ),
    LanguageVariant(
        locale="en-GB",
        iso_639_1="en",
        iso_3166_1="GB",
        name="English (United Kingdom)",
        native_name="English (United Kingdom)",
        stt=True,
        tts=True,
    ),
    LanguageVariant(
        locale="es-ES",
        iso_639_1="es",
        iso_3166_1="ES",
        name="Spanish (Spain)",
        native_name="Español (España)",
        stt=True,
        tts=True,
    ),
    LanguageVariant(
        locale="es-MX",
        iso_639_1="es",
        iso_3166_1="MX",
        name="Spanish (Mexico)",
        native_name="Español (México)",
        stt=True,
        tts=True,
    ),
    LanguageVariant(
        locale="fr-FR",
        iso_639_1="fr",
        iso_3166_1="FR",
        name="French (France)",
        native_name="Français (France)",
        stt=True,
        tts=True,
    ),
    LanguageVariant(
        locale="de-DE",
        iso_639_1="de",
        iso_3166_1="DE",
        name="German (Germany)",
        native_name="Deutsch (Deutschland)",
        stt=True,
        tts=True,
    ),
    LanguageVariant(
        locale="it-IT",
        iso_639_1="it",
        iso_3166_1="IT",
        name="Italian (Italy)",
        native_name="Italiano (Italia)",
        stt=True,
        tts=True,
    ),
    LanguageVariant(
        locale="nl-NL",
        iso_639_1="nl",
        iso_3166_1="NL",
        name="Dutch (Netherlands)",
        native_name="Nederlands (Nederland)",
        stt=True,
        tts=True,
    ),
    LanguageVariant(
        locale="pt-BR",
        iso_639_1="pt",
        iso_3166_1="BR",
        name="Portuguese (Brazil)",
        native_name="Português (Brasil)",
        stt=False,
        tts=True,
    ),
    LanguageVariant(
        locale="pt-PT",
        iso_639_1="pt",
        iso_3166_1="PT",
        name="Portuguese (Portugal)",
        native_name="Português (Portugal)",
        stt=False,
        tts=True,
    ),
]


def list_locales(*, stt_only: bool = False, tts_only: bool = False) -> list[str]:
    """List supported locales, optionally filtered by capability.

    Args:
        stt_only (bool): When True, return only locales supported for STT.
        tts_only (bool): When True, return only locales supported for TTS.

    Returns:
        list[str]: List of locale strings, sorted for stable output.

    Raises:
        ValueError: If both `stt_only` and `tts_only` are True.
    """
    if stt_only and tts_only:
        raise ValueError("stt_only and tts_only cannot both be True")

    variants = LANGUAGE_VARIANTS
    if stt_only:
        variants = [v for v in variants if v.stt]
    if tts_only:
        variants = [v for v in variants if v.tts]

    return sorted({v.locale for v in variants})


def find_variant(locale_or_code: str) -> LanguageVariant | None:
    """Find a language variant by locale or ISO-639-1 code.

    Args:
        locale_or_code (str): Locale (e.g., "en-GB") or ISO-639-1 code (e.g., "en").

    Returns:
        LanguageVariant | None: Matching variant, if any.
    """
    value = (locale_or_code or "").strip()
    if not value:
        return None

    value_norm = value.replace("_", "-")
    for variant in LANGUAGE_VARIANTS:
        if variant.locale.lower() == value_norm.lower():
            return variant

    # Fallback: match by ISO-639-1 and return a stable default variant.
    if len(value_norm) == 2:
        for variant in LANGUAGE_VARIANTS:
            if variant.iso_639_1.lower() == value_norm.lower():
                return variant

    return None


def locale_to_iso_639_1(locale_or_code: str | None) -> str | None:
    """Convert a locale (or ISO code) into an ISO-639-1 language code.

    Args:
        locale_or_code (str | None): Locale like "en-US" or ISO code like "en".

    Returns:
        str | None: ISO-639-1 language code (e.g., "en"), or None when input is empty.
    """
    if not locale_or_code:
        return None

    value = locale_or_code.strip().replace("_", "-")
    if not value:
        return None

    variant = find_variant(value)
    if variant is not None:
        return variant.iso_639_1

    # Generic parsing fallback: "en-US" -> "en"
    if "-" in value:
        return value.split("-", 1)[0].lower()

    # Do not attempt to convert arbitrary language names here (e.g., "spanish").
    # Those should be handled by service-specific name mappings.
    if len(value) == 2 and value.isalpha():
        return value.lower()

    return None

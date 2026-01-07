/**
 * Sanitize text for text-to-speech output.
 *
 * This removes Markdown formatting tokens (like `**bold**` and list bullets)
 * that some TTS engines read aloud (for example, "asterisk").
 * It keeps the readable words and normal punctuation.
 */
export function sanitizeTtsText(input: string): string {
  if (typeof input !== 'string') return '';

  let text = input.replace(/\r\n/g, '\n');

  // Remove fenced code blocks entirely (they are usually not useful for TTS).
  text = text.replace(/```[\s\S]*?```/g, ' ');

  // Inline code: keep the content, drop the backticks.
  text = text.replace(/`([^`]+)`/g, '$1');

  // Images: keep alt text.
  text = text.replace(/!\[([^\]]*)\]\([^)]+\)/g, '$1');

  // Links: keep link text.
  text = text.replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');

  // Headings and blockquotes.
  text = text.replace(/^\s{0,3}#{1,6}\s+/gm, '');
  text = text.replace(/^\s{0,3}>\s?/gm, '');

  // Bullet markers at the start of a line.
  text = text.replace(/^\s*([*+-]|•)\s+/gm, '');

  // Common Markdown emphasis / strike tokens.
  text = text.replace(/\*\*/g, '');
  text = text.replace(/__/g, '');
  text = text.replace(/~~/g, '');

  // Remove leftover Markdown punctuation that is commonly read aloud.
  text = text.replace(/[*_`]/g, '');

  // Tables (best-effort): remove pipes used as separators.
  text = text.replace(/\|/g, ' ');

  // Normalize whitespace.
  text = text.replace(/\s+/g, ' ').trim();

  return text;
}



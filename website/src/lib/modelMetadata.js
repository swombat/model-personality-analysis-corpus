const familyLabels = {
  'claude-haiku': 'Claude Haiku',
  'claude-fable': 'Claude Fable',
  'claude-opus': 'Claude Opus',
  'claude-sonnet': 'Claude Sonnet',
  deepseek: 'DeepSeek',
  gemini: 'Gemini',
  gemma: 'Gemma',
  glm: 'GLM',
  gpt: 'GPT',
  grok: 'Grok',
  kimi: 'Kimi',
  llama: 'Llama',
  minimax: 'MiniMax',
  mistral: 'Mistral',
  qwen: 'Qwen',
};

export function familyLabel(family) {
  return familyLabels[family] || family;
}

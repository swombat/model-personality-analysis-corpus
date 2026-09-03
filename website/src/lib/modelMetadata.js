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
  muse: 'Muse',
  minimax: 'MiniMax',
  mistral: 'Mistral',
  'openai-o': 'OpenAI o-series',
  qwen: 'Qwen',
  yi: 'Yi',
};

export function familyLabel(family) {
  return familyLabels[family] || family;
}

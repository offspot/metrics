module.exports = {
  root: true,
  parser: 'vue-eslint-parser',
  parserOptions: {
    sourceType: 'module',
    ecmaVersion: 'latest',
    parser: '@typescript-eslint/parser',
  },
  extends: [
    'eslint:recommended',
    'plugin:vue/vue3-recommended',
    '@vue/eslint-config-typescript/recommended',
    'prettier',
  ],
  rules: {
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    'no-console': 'error',
    'no-debugger': 'error',
    'vue/multi-word-component-names': 'error',
    'vue/no-reserved-component-names': 'error',
    'vue/require-explicit-emits': 'error',
    'vue/attributes-order': 'error',
    'vue/component-definition-name-casing': 'error',
  },
  overrides: [
    {
      files: ['*.cjs'],
      env: { node: true },
    },
  ],
}

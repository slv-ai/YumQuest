import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import { defineConfig, globalIgnores } from 'eslint/config'

export default defineConfig([
  // Never lint build output
  globalIgnores(['dist']),

  {
    files: ['**/*.{js,jsx}'],
    extends: [
      js.configs.recommended, // ESLint's core rules: unused variables, undefined names, ...
      reactHooks.configs.flat.recommended, // rules of hooks + exhaustive dependencies for useEffect
      reactRefresh.configs.vite, // keeps hot reload working: component files should only export components
    ],
    languageOptions: {
      ecmaVersion: 'latest',
      globals: globals.browser, // allows window, document, fetch, ...
      parserOptions: {
        ecmaFeatures: { jsx: true }, // lets ESLint read JSX
        sourceType: 'module',
      },
    },
    rules: {
      // A capitalised name that is only used inside JSX (<Answer />) is not "unused"
      'no-unused-vars': ['error', { varsIgnorePattern: '^[A-Z_]' }],
    },
  },

  {
    // Config files run in Node, not in the browser
    files: ['vite.config.js', 'eslint.config.js'],
    languageOptions: { globals: globals.node },
  },
])

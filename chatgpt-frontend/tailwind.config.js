/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}", // Reactのコンポーネントファイルをスキャン対象に含める
    "./public/index.html",        // HTMLファイルをスキャン対象に含める
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}

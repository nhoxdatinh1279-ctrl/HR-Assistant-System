/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        './pages/**/*.{js,ts,jsx,tsx}',
        './components/**/*.{js,ts,jsx,tsx}',
        './app/**/*.{js,ts,jsx,tsx}',
    ],
    theme: {
        extend: {
            colors: {
                primary: '#3b82f6',
                secondary: '#1e40af',
                accent: '#10b981',
            },
            fontFamily: {
                sans: ['system-ui', 'sans-serif'],
            },
        },
    },
    plugins: [],
}

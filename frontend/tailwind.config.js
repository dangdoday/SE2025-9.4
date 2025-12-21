/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{vue,js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                primary: {
                    DEFAULT: '#F0B90B',
                    50: '#FEF9E7',
                    100: '#FDF3CF',
                    200: '#FBE79F',
                    300: '#F9DB6F',
                    400: '#F7CF3F',
                    500: '#F0B90B',
                    600: '#C99A09',
                    700: '#A27B07',
                    800: '#7B5C05',
                    900: '#543D04'
                },
                dark: {
                    DEFAULT: '#0B0E11',
                    50: '#1E2329',
                    100: '#181B20',
                    200: '#12151A',
                    300: '#0B0E11'
                },
                success: '#0ECB81',
                danger: '#F6465D',
                warning: '#F0B90B'
            }
        }
    },
    plugins: []
}

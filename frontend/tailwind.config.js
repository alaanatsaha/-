/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        cairo: ["Arial", "Tahoma", "sans-serif"],
      },
      colors: {
        pib: {
          greenDark: "#053d70",
          green: "#075b91",
          greenLight: "#eaf3f9",
          gold: "#f4c400",
          goldLight: "#fff6cc",
          ink: "#18324a",
          muted: "#627588",
          line: "#dce5ec",
          paper: "#f7f8f9",
          danger: "#a23b34",
          dangerBg: "#fbeeed",
        },
      },
      borderRadius: {
        xl2: "18px",
      },
    },
  },
  plugins: [],
};

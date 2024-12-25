import js from "@eslint/js";


module.exports = [
    {
        ignores: ["**/*.config.js"],
        rules: {
            semi: "error",
            "prefer-const": "error"
        }
    }
];
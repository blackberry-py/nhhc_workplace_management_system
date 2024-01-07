const { defineConfig } = require('cypress');
const { cypressConfig } = require('@axe-core/watcher');

module.exports = defineConfig(
  cypressConfig({
    axe: {
      apiKey: 'afdbbcdd-a925-4740-b0cb-8ae259c9c893'
    },
  e2e: {
    setupNodeEvents(on, config) {
      // implement node event listeners here
    },
  },
});

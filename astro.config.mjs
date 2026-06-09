// @ts-check
import { defineConfig } from "astro/config";
import vue from "@astrojs/vue";

// GitHub Pages project site: served under /i2dl-exam-qa/.
// Math is rendered at build time (KaTeX renderToString in src/lib/md.ts),
// so there is no client-side KaTeX JS — only the stylesheet is loaded.
export default defineConfig({
  site: "https://c0nsTantin77.github.io",
  base: "/i2dl-exam-qa",
  trailingSlash: "ignore",
  integrations: [vue()],
  build: {
    // emit clean URLs: /chapters/ch01/ instead of /chapters/ch01.html
    format: "directory",
    assets: "_assets",
  },
  devToolbar: { enabled: false },
});

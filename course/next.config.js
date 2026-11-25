const withMarkdoc = require('@markdoc/next.js');

const basePath = process.env.NEXT_PUBLIC_BASE_PATH || '';
const staticExport = process.env.DAGSTER_STATIC_EXPORT === '1';

module.exports = withMarkdoc({schemaPath: './markdoc', mode: 'static'})({
  pageExtensions: ['js', 'jsx', 'ts', 'tsx', 'md', 'mdoc'],
  basePath,
  ...(staticExport ? {output: 'export', trailingSlash: true, images: {unoptimized: true}} : {}),
});

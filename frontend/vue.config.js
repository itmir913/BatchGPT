const { defineConfig } = require('@vue/cli-service');
module.exports = defineConfig({
  transpileDependencies: true,
  outputDir: '../backend/dist', // 빌드 파일 경로를 Django 정적 파일 디렉토리로 지정
  assetsDir: 'static',
  devServer: {
    proxy: 'http://127.0.0.1:8000', // Django 개발 서버와 연동 (필요 시)
  },
});
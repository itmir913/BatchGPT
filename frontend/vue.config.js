const {defineConfig} = require('@vue/cli-service');
module.exports = defineConfig({
    transpileDependencies: true,
    outputDir: '../backend/dist', // 빌드 파일 경로를 Django 정적 파일 디렉토리로 지정
    assetsDir: 'static',
    publicPath: '/',
    devServer: {
        host: '0.0.0.0',  // 모든 네트워크 인터페이스에서 접근 가능하도록 설정
        port: 8080,  // 원하는 포트로 설정
        client: {
            webSocketURL: 'ws://127.0.0.1:8080/ws',  // WebSocket의 상대 경로를 지정
        },
        proxy: {
            '^/ws/': {
                target: 'ws://127.0.0.1:8000',
                ws: true,
                changeOrigin: true,
                pathRewrite: {
                    '^/api/ws/': '/ws/',  // 필요한 경우 경로를 변경할 수 있음
                },
            },
            '^/api/': {
                target: 'http://127.0.0.1:8000',  // API 서버의 주소
                changeOrigin: true,  // 원본 호스트 헤더를 타겟 서버로 변경
                pathRewrite: {
                    '^/': '/',  // 필요한 경우 경로를 변경할 수 있음
                },
            },
        },
    },
});
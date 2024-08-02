# ベースイメージ
FROM node:14-alpine AS build

# 作業ディレクトリの設定
WORKDIR /chatgpt-frontend

# package.jsonとpackage-lock.jsonをコピー
COPY package*.json ./

# 依存関係のインストール
RUN npm install

# アプリケーションのソースをコピー
COPY . .

# ビルド
RUN npm run build

# Nginxを使用してビルドされた静的ファイルを提供
FROM nginx:alpine

# カスタムNginx設定ファイルをコピー
COPY nginx.conf /etc/nginx/conf.d/default.conf

# ビルド成果物をNginxのルートディレクトリにコピー
COPY --from=build /chatgpt-frontend/build /usr/share/nginx/html

# ログディレクトリをホストの特定ディレクトリにマウント
RUN mkdir -p /var/log/nginx

# Nginxが使用するポートを公開
EXPOSE 80

# Nginxを起動
CMD ["nginx", "-g", "daemon off;"]
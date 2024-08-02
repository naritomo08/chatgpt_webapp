# ベースイメージ
FROM node:14-alpine

# 作業ディレクトリの設定
WORKDIR /chatgpt-frontend

# package.jsonとpackage-lock.jsonをコピー
COPY package*.json ./

# 依存関係のインストール
RUN npm install

# アプリケーションのソースをコピー
COPY . .

# 環境変数をビルド時に注入
ARG REACT_APP_API_BASE_URL
ENV REACT_APP_API_BASE_URL=${REACT_APP_API_BASE_URL}

# ビルド
RUN npm run build

# アプリケーションの実行
CMD ["npm", "start"]

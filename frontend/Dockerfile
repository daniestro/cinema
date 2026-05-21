FROM node:22.13.1-alpine3.20 AS base
WORKDIR /app
RUN corepack enable && corepack prepare pnpm@9.15.0 --activate

FROM base AS deps
COPY package.json pnpm-lock.yaml* ./
RUN pnpm install --frozen-lockfile || pnpm install

FROM base AS dev
COPY --from=deps /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
CMD ["pnpm", "dev"]

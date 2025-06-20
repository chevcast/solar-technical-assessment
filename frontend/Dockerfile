# --------------------------
# 1) builder stage (Bun)
# --------------------------
FROM oven/bun:alpine AS builder
WORKDIR /app

COPY ./package.json ./bun.lock   ./

RUN bun install --frozen-lockfile

COPY ./frontend   ./frontend

WORKDIR /app/fontend
RUN bun run build


# --------------------------
# 2) runner stage (Node)
# --------------------------
FROM node:alpine AS runner
WORKDIR /app

COPY --from=builder /app/node_modules   ./node_modules

COPY --from=builder /app/frontend      ./frontend

WORKDIR /app/frontend
ENV NODE_ENV=production
EXPOSE 3000

CMD ["npm", "start"]

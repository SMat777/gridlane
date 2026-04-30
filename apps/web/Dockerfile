FROM node:22-slim

RUN npm install -g pnpm

WORKDIR /app

# Copy workspace config from monorepo root
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./

# Copy package.json for workspace packages (pnpm needs these to resolve)
COPY apps/web/package.json apps/web/
COPY packages/shared/package.json packages/shared/

RUN pnpm install --frozen-lockfile

# Copy shared package source (needed at build time)
COPY packages/shared/ packages/shared/

# Copy web app source
COPY apps/web/ apps/web/

WORKDIR /app/apps/web

EXPOSE 3000
CMD ["pnpm", "dev"]

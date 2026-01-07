FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm ci

# Copy source code
COPY . .

# Build application
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]

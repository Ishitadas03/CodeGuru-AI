FROM node:18-alpine

WORKDIR /app

# Copy dependency configurations
COPY package.json ./

# Install npm packages
RUN npm install

# Copy source code
COPY . .

# Expose NextJS port
EXPOSE 3000
CMD ["npm", "run", "dev"]

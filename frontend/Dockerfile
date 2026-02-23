# Use Node.js LTS version
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm install

# Copy application files
COPY frontend/ .

# Ensure runtime files are owned by non-root user
RUN chown -R node:node /app

# Expose port
EXPOSE 3000

# Start development server as non-root
USER node
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

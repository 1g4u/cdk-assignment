FROM node:lts-alpine

# Set working directory
WORKDIR /app
# Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the application code
COPY . .
# Build TypeScript files
RUN npm run build
# Expose the application port
EXPOSE 3000
# Start the application
CMD ["node", "dist/app/index.js"]

## TODO: to reduce image size, try: https://github.com/Mikhus/ts-docker/blob/master/Dockerfile
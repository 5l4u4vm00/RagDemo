# Use an official Node.js runtime as a parent image
FROM node:22-slim

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json to the working directory
COPY package*.json ./

# Install any needed packages specified in package.json
RUN npm install

# Copy the rest of the application's code
COPY . .

# Make port 5173 available to the world outside this container
EXPOSE 5173

# Run the "dev" script and expose the server to the host
CMD ["npm", "run", "dev", "--", "--host"]

# Use a base image that includes both Python and Node.js
FROM python:3.11-slim-buster

# Install Node.js and npm
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy backend files
COPY facebook_ad_spy_backend /app/facebook_ad_spy_backend

# Copy frontend files
COPY facebook-ad-spy-frontend /app/facebook-ad-spy-frontend

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/facebook_ad_spy_backend/requirements.txt

# Build frontend and copy to backend static folder
RUN cd /app/facebook-ad-spy-frontend && npm install && npm run build && cp -r dist/* /app/facebook_ad_spy_backend/src/static/

# Expose the port Flask runs on
EXPOSE 5001

# Command to run the application
CMD ["python", "/app/facebook_ad_spy_backend/src/main.py"]

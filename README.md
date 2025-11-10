# # Build image
docker build -t gym-api .

# Run container
docker run -d -p 3000:3000 --env-file .env gym-api

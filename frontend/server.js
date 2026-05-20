import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import { createProxyMiddleware } from 'http-proxy-middleware';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 8080;
const API_URL = process.env.API_URL || 'http://localhost:3000';

console.log(`[Frontend Server] Target API URL set to: ${API_URL}`);

// 1. Reverse proxy all /api requests to the Flask backend
app.use('/api', createProxyMiddleware({
  target: API_URL,
  changeOrigin: true,
  logLevel: 'info',
}));

// 2. Serve Vite production static files from /dist
app.use(express.static(path.join(__dirname, 'dist')));

// 3. Fallback for SPA Routing: redirect all unmatched paths to index.html
app.use((req, res) => {
  res.sendFile(path.join(__dirname, 'dist', 'index.html'));
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`[Frontend Server] Listening on port ${PORT}`);
});

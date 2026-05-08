const express = require('express');
const crypto = require('crypto');
const { execSync } = require('child_process');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;
const WEBHOOK_SECRET = process.env.WEBHOOK_SECRET || '';

app.use(express.static(path.join(__dirname)));
app.use(express.json({ verify: (req, _res, buf) => { req.rawBody = buf; } }));

app.post('/webhook', (req, res) => {
  if (WEBHOOK_SECRET) {
    const sig = req.headers['x-hub-signature-256'];
    const expected = 'sha256=' + crypto.createHmac('sha256', WEBHOOK_SECRET).update(req.rawBody).digest('hex');
    if (sig !== expected) return res.status(401).send('Unauthorized');
  }

  const event = req.headers['x-github-event'];
  if (event === 'push') {
    try {
      execSync('git pull origin main', { cwd: __dirname, stdio: 'pipe' });
      console.log('[webhook] git pull OK');
    } catch (err) {
      console.error('[webhook] git pull failed:', err.message);
      return res.status(500).send('Deploy failed');
    }
  }

  res.send('OK');
});

app.listen(PORT, () => console.log(`Server running on port ${PORT}`));

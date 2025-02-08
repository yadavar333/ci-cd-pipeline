const express = require('express');

const app = express();
app.use(express.json());

// In-memory store
const posts = new Map();
let nextId = 1;

app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'service-b' });
});

app.get('/posts', (req, res) => {
  res.json([...posts.values()]);
});

app.get('/posts/:id', (req, res) => {
  const post = posts.get(Number(req.params.id));
  if (!post) return res.status(404).json({ error: 'Post not found' });
  res.json(post);
});

app.post('/posts', (req, res) => {
  const { title, body } = req.body || {};
  if (!title || !body) {
    return res.status(400).json({ error: 'title and body are required' });
  }
  const post = { id: nextId++, title, body };
  posts.set(post.id, post);
  res.status(201).json(post);
});

app.delete('/posts/:id', (req, res) => {
  const id = Number(req.params.id);
  if (!posts.has(id)) return res.status(404).json({ error: 'Post not found' });
  posts.delete(id);
  res.json({ message: 'deleted' });
});

module.exports = { app, posts, resetStore: () => { posts.clear(); nextId = 1; } };

if (require.main === module) {
  const PORT = process.env.PORT || 4000;
  app.listen(PORT, () => console.log(`service-b running on port ${PORT}`));
}

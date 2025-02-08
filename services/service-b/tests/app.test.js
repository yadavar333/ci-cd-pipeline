const request = require('supertest');
const { app, resetStore } = require('../app');

beforeEach(() => resetStore());

test('GET /health returns ok', async () => {
  const res = await request(app).get('/health');
  expect(res.statusCode).toBe(200);
  expect(res.body.status).toBe('ok');
});

test('POST /posts creates a post and returns 201', async () => {
  const res = await request(app)
    .post('/posts')
    .send({ title: 'Hello', body: 'World' });
  expect(res.statusCode).toBe(201);
  expect(res.body.title).toBe('Hello');
  expect(res.body.id).toBeDefined();
});

test('GET /posts returns all created posts', async () => {
  await request(app).post('/posts').send({ title: 'A', body: 'a' });
  await request(app).post('/posts').send({ title: 'B', body: 'b' });
  const res = await request(app).get('/posts');
  expect(res.statusCode).toBe(200);
  expect(res.body).toHaveLength(2);
});

test('GET /posts/:id returns the correct post', async () => {
  const created = await request(app).post('/posts').send({ title: 'Specific', body: 'Content' });
  const res = await request(app).get(`/posts/${created.body.id}`);
  expect(res.statusCode).toBe(200);
  expect(res.body.title).toBe('Specific');
});

test('DELETE /posts/:id removes the post', async () => {
  const created = await request(app).post('/posts').send({ title: 'ToDelete', body: 'Gone' });
  const del = await request(app).delete(`/posts/${created.body.id}`);
  expect(del.statusCode).toBe(200);
  const get = await request(app).get(`/posts/${created.body.id}`);
  expect(get.statusCode).toBe(404);
});

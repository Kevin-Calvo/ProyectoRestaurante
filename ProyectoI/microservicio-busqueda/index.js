require('dotenv').config();
const express = require('express');
const client = require('./elasticsearch');
const reindexDummy = require('./reindex');

const app = express();
const PORT = 4000;

app.use(express.json());

// GET /search/products?q=texto
app.get('/search/products', async (req, res) => {
  const q = req.query.q;
  if (!q) return res.status(400).send({ error: 'Falta el parámetro q' });

  const result = await client.search({
    index: 'products',
    query: {
      multi_match: {
        query: q,
        fields: ['name', 'description']
      }
    }
  });

  res.json(result.hits.hits.map(hit => hit._source));
});

// GET /search/products/category/:categoria
app.get('/search/products/category/:categoria', async (req, res) => {
  const category = req.params.categoria;

  const result = await client.search({
    index: 'products',
    query: {
      term: { category: category }
    }
  });

  res.json(result.hits.hits.map(hit => hit._source));
});

// POST /search/reindex
app.post('/search/reindex', async (req, res) => {
  await reindexDummy(); // Más adelante usamos datos reales
  res.send({ message: 'Reindexación completa' });
});

app.listen(PORT, () => {
  console.log(`🧠 Microservicio de búsqueda corriendo en http://localhost:${PORT}`);
});

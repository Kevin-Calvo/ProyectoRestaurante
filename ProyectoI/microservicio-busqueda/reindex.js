const client = require('./elasticsearch');

async function reindexDummy() {
  // Asegurarse de que el índice exista
  const exists = await client.indices.exists({ index: 'products' });
  if (exists) await client.indices.delete({ index: 'products' });

  await client.indices.create({
    index: 'products',
    mappings: {
      properties: {
        name: { type: 'text' },
        description: { type: 'text' },
        category: { type: 'keyword' },
      },
    },
  });

  // Insertar algunos productos fake
  const products = [
    { name: 'Pizza Margherita', description: 'Deliciosa pizza italiana', category: 'Italiana' },
    { name: 'Sushi Roll', description: '', category: 'Japonesa' },
    { name: 'Hamburguesa', description: null, category: 'Americana' },
  ];

  const body = products.flatMap(doc => [
    { index: { _index: 'products' } },
    {
      name: doc.name,
      description: doc.description || 'Producto sin descripción',
      category: doc.category
    }
  ]);

  await client.bulk({ refresh: true, body });
  console.log('✔ Productos dummy indexados');
}

module.exports = reindexDummy;

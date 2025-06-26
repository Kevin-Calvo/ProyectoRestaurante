const express = require('express');
const connectMongo = require('./config/mongo');

const app = express.Router();
const PORT = 3000;

let isConnected = false;

app.get('/connect', async (req, res) => {
  if (isConnected) {
    return res.status(200).json({ message: 'Ya conectado a MongoDB' });
  }

  try {
    await connectMongo();
    isConnected = true;
    res.status(200).json({ message: 'Conexión a MongoDB exitosa' });
  } catch (error) {
    res.status(500).json({ message: 'Error al conectar a MongoDB', error });
  }
});

app.listen(PORT, () => {
  console.log(`Servidor iniciado en puerto ${PORT}`);
});

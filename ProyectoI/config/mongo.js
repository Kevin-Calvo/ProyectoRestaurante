const mongoose = require('mongoose');

const connectMongo = async () => {
  if (mongoose.connection.readyState === 1) {
    // Ya conectado
    return;
  }
  try {
    await mongoose.connect(process.env.MONGO_URI, {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });
    console.log('🔗 Conectado a MongoDB desde controller');
  } catch (error) {
    console.error('❌ Error al conectar a MongoDB desde controller:', error);
    throw error;
  }
};

module.exports = connectMongo;


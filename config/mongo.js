const mongoose = require('mongoose');

const connectMongo = async () => {
  try {
    await mongoose.connect('mongodb://mongos:27017/mi_base_de_datos', {
      useNewUrlParser: true,
      useUnifiedTopology: true,
      // otras opciones si las necesitas
    });

    console.log('✅ Conectado a MongoDB');
  } catch (error) {
    console.error('❌ Error al conectar a MongoDB:', error);
    process.exit(1); // termina la app si no conecta
  }
};

module.exports = connectMongo;


// index.js COMPLETO y FUNCIONAL con ruta /ping

const express = require('express');
const cors = require('cors');
const sequelize = require('./config/database');
const User = require('./models/User');
const Restaurant = require('./models/Restaurant');
const Menu = require('./models/Menu');
const Reservation = require('./models/Reservation');
const Order = require('./models/Order');

const authRoutes = require('./routes/authRoutes');
const restaurantRoutes = require('./routes/restaurantRoutes');
const menuRoutes = require('./routes/menuRoutes');
const reservationRoutes = require('./routes/reservationRoutes');
const orderRoutes = require('./routes/orderRoutes');

const app = express();
app.use(express.json());
app.use(cors());

// Ruta /ping para testear el balanceador
app.get('/ping', (req, res) => {
  console.log(`🧠 Instancia PID ${process.pid} respondió /ping`);
  res.send(`Hola desde instancia PID: ${process.pid}`);
});

// Relaciones entre modelos
User.hasMany(Restaurant, { foreignKey: 'ownerId' });
Restaurant.belongsTo(User, { foreignKey: 'ownerId' });
Restaurant.hasMany(Menu, { foreignKey: 'restaurantId' });
Menu.belongsTo(Restaurant, { foreignKey: 'restaurantId' });
User.hasMany(Reservation, { foreignKey: 'userId' });
Restaurant.hasMany(Reservation, { foreignKey: 'restaurantId' });
Reservation.belongsTo(User, { foreignKey: 'userId' });
Reservation.belongsTo(Restaurant, { foreignKey: 'restaurantId' });
User.hasMany(Order, { foreignKey: 'userId' });
Restaurant.hasMany(Order, { foreignKey: 'restaurantId' });
Order.belongsTo(User, { foreignKey: 'userId' });
Order.belongsTo(Restaurant, { foreignKey: 'restaurantId' });

// Rutas principales
app.use('/auth', authRoutes);
app.use('/restaurants', restaurantRoutes);
app.use('/menus', menuRoutes);
app.use('/reservations', reservationRoutes);
app.use('/orders', orderRoutes);

const PORT = process.env.PORT || 3000;

console.log(`Buscando desde PID ${process.pid}`);


// Levantar servidor
app.listen(PORT, async () => {
  console.log(`Microservicio principal corriendo en http://localhost:${PORT}`);
  console.log(`PID activo: ${process.pid}`);

  if (process.env.SYNC === 'true') {
    try {
      await sequelize.sync({ force: true });
      console.log('Base de datos sincronizada');
    } catch (error) {
      console.error('Error al sincronizar la base de datos:', error);
    }
  }
});

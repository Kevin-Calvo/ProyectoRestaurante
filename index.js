const express = require('express');
const cors = require('cors');
const sequelize = require('./config/database');
const User = require('./models/User');
const Restaurant = require('./models/Restaurant');
const Menu = require('./models/Menu');
const Reservation = require('./models/Reservation');
const Order = require('./models/Order'); // 📌 Agregado

const authRoutes = require('./routes/authRoutes');
const restaurantRoutes = require('./routes/restaurantRoutes');
const menuRoutes = require('./routes/menuRoutes');
const reservationRoutes = require('./routes/reservationRoutes');
const orderRoutes = require('./routes/orderRoutes');

const app = express();
app.use(express.json());
app.use(cors());

// Definir relaciones entre modelos
User.hasMany(Restaurant, { foreignKey: 'ownerId' });
Restaurant.belongsTo(User, { foreignKey: 'ownerId' });

Restaurant.hasMany(Menu, { foreignKey: 'restaurantId' });
Menu.belongsTo(Restaurant, { foreignKey: 'restaurantId' });

User.hasMany(Reservation, { foreignKey: 'userId' });
Restaurant.hasMany(Reservation, { foreignKey: 'restaurantId' });

Reservation.belongsTo(User, { foreignKey: 'userId' });
Reservation.belongsTo(Restaurant, { foreignKey: 'restaurantId' });

User.hasMany(Order, { foreignKey: 'userId' }); // 📌 Relación con órdenes
Restaurant.hasMany(Order, { foreignKey: 'restaurantId' }); // 📌 Relación con restaurantes

Order.belongsTo(User, { foreignKey: 'userId' }); 
Order.belongsTo(Restaurant, { foreignKey: 'restaurantId' });

// Rutas
app.use('/auth', authRoutes);
app.use('/restaurants', restaurantRoutes);
app.use('/menus', menuRoutes);
app.use('/reservations', reservationRoutes);
app.use('/orders', orderRoutes);

const PORT = process.env.PORT || 3000;

// Iniciar el servidor y sincronizar la base de datos
app.listen(PORT, async () => {
    console.log(`Servidor corriendo en http://localhost:${PORT}`);
    try {
        await sequelize.sync({ force: true }); // 📌 Esto crea la tabla si no existe
        console.log('Base de datos sincronizada');
    } catch (error) {
        console.error('Error al sincronizar la base de datos:', error);
    }
});

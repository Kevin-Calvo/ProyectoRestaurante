const { Sequelize } = require('sequelize');

const sequelize = new Sequelize('reserva_restaurantes', 'postgres', 'postgres', {
    host: 'db',  
    dialect: 'postgres',
    define: {
        underscored: true 
    }
});

module.exports = sequelize;



const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');
const User = require('./User');
const Restaurant = require('./Restaurant');

const Order = sequelize.define('Order', {
    id: {
        type: DataTypes.UUID,
        defaultValue: DataTypes.UUIDV4,
        primaryKey: true
    },
    userId: {
        type: DataTypes.UUID,
        allowNull: false,
        references: {
            model: User,
            key: 'id'
        }
    },
    restaurantId: {
        type: DataTypes.UUID,
        allowNull: false,
        references: {
            model: Restaurant,
            key: 'id'
        }
    },
    status: {
        type: DataTypes.STRING,
        allowNull: false,
        defaultValue: 'pendiente' // Estado inicial del pedido
    }
});

module.exports = Order;

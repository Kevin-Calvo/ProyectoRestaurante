const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');
const Restaurant = require('./Restaurant'); // Relación con restaurantes

const Menu = sequelize.define('Menu', {
    id: {
        type: DataTypes.UUID,
        defaultValue: DataTypes.UUIDV4,
        primaryKey: true
    },
    name: {
        type: DataTypes.STRING(100),
        allowNull: false
    },
    description: {
        type: DataTypes.TEXT,
        allowNull: true
    },
    price: {
        type: DataTypes.DECIMAL(10, 2), // Precio con 2 decimales
        allowNull: false
    },
    restaurantId: {
        type: DataTypes.UUID,
        allowNull: false,
        references: {
            model: Restaurant,
            key: 'id'
        }
    }
}, {
    tableName: 'menus',
    timestamps: true
});

module.exports = Menu;

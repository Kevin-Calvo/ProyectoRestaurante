const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');
const User = require('./User'); // Importamos el modelo de usuario

const Restaurant = sequelize.define('Restaurant', {
    id: {
        type: DataTypes.UUID,
        defaultValue: DataTypes.UUIDV4,
        primaryKey: true
    },
    name: {
        type: DataTypes.STRING(100),
        allowNull: false
    },
    address: {
        type: DataTypes.TEXT,
        allowNull: false
    },
    owner_id: {
        type: DataTypes.UUID,
        allowNull: false,
        references: {
            model: User,
            key: 'id'
        }
    }
}, {
    tableName: 'restaurants',
    timestamps: true
});

module.exports = Restaurant;

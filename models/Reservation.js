const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');
const User = require('./User');
const Restaurant = require('./Restaurant');

const Reservation = sequelize.define('Reservation', {
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
    date: {
        type: DataTypes.DATE,
        allowNull: false
    },
    guests: {
        type: DataTypes.INTEGER,
        allowNull: false
    }
});

module.exports = Reservation;

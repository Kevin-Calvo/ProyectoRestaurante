const Reservation = require('../models/Reservation');
const Restaurant = require('../models/Restaurant');
const { Op } = require('sequelize');

exports.createReservation = async (req, res) => {
    try {
        const { restaurantId, date, guests } = req.body;
        const userId = req.user.id; // El usuario autenticado hace la reserva

        const restaurant = await Restaurant.findByPk(restaurantId);
        if (!restaurant) {
            return res.status(404).json({ message: 'Restaurante no encontrado' });
        }

        const reservation = await Reservation.create({ userId, restaurantId, date, guests });
        res.status(201).json({ message: 'Reserva creada con éxito', reservation });
    } catch (error) {
        res.status(500).json({ message: 'Error al crear la reserva', error });
    }
};

exports.cancelReservation = async (req, res) => {
    try {
        const { id } = req.params;
        const reservation = await Reservation.findByPk(id);

        if (!reservation) {
            return res.status(404).json({ message: 'Reserva no encontrada' });
        }

        await reservation.destroy();
        res.json({ message: 'Reserva cancelada con éxito' });
    } catch (error) {
        res.status(500).json({ message: 'Error al cancelar la reserva', error });
    }
};

exports.checkAvailability = async (req, res) => {
    try {
        const { restaurantId, date } = req.query;

        if (!restaurantId || !date) {
            return res.status(400).json({ message: 'Se requiere restaurantId y date' });
        }

        // Busca si ya hay reservas en ese horario
        const existingReservations = await Reservation.count({
            where: {
                restaurantId,
                date: new Date(date)
            }
        });

        // Define un número máximo de reservas por restaurante
        const MAX_RESERVAS = 10;

        if (existingReservations >= MAX_RESERVAS) {
            return res.status(200).json({ available: false, message: 'No hay mesas disponibles' });
        }

        return res.status(200).json({ available: true, message: 'Hay mesas disponibles' });
    } catch (error) {
        console.error('Error al verificar disponibilidad:', error);
        res.status(500).json({ message: 'Error en el servidor' });
    }
};

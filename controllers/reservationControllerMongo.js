const Reservation = require('../mongoModels/reservation');
const Restaurant = require('../mongoModels/restaurants');
const mongoConnector = require('../config/mongo');

// Crear una nueva reserva
exports.createReservation = async (req, res) => {
    try {
        await mongoConnector();

        const { restaurantId, date, guests } = req.body;
        const userId = req.user.id;

        const restaurant = await Restaurant.findById(restaurantId);
        if (!restaurant) {
            return res.status(404).json({ message: 'Restaurante no encontrado' });
        }

        const reservation = new Reservation({
            userId,
            restaurantId,
            date,
            guests
        });

        await reservation.save();
        res.status(201).json({ message: 'Reserva creada con éxito', reservation });
    } catch (error) {
        res.status(500).json({ message: 'Error al crear la reserva', error });
    }
};

// Cancelar una reserva
exports.cancelReservation = async (req, res) => {
    try {
        await mongoConnector();

        const { id } = req.params;

        const reservation = await Reservation.findById(id);
        if (!reservation) {
            return res.status(404).json({ message: 'Reserva no encontrada' });
        }

        await reservation.deleteOne();
        res.json({ message: 'Reserva cancelada con éxito' });
    } catch (error) {
        res.status(500).json({ message: 'Error al cancelar la reserva', error });
    }
};

// Verificar disponibilidad
exports.checkAvailability = async (req, res) => {
    try {
        await mongoConnector();
        
        const { restaurantId, date } = req.query;

        if (!restaurantId || !date) {
            return res.status(400).json({ message: 'Se requiere restaurantId y date' });
        }

        const reservationDate = new Date(date);

        const existingReservations = await Reservation.countDocuments({
            restaurantId,
            date: reservationDate
        });

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


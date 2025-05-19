const { createReservation } = require('../../../controllers/reservationControllerPostgres');
const Reservation = require('../../../models/Reservation');
const Restaurant = require('../../../models/Restaurant');

jest.mock('../../../models/Reservation');
jest.mock('../../../models/Restaurant');

describe('reservationController - createReservation', () => {
  it('debería crear una reserva si el restaurante existe', async () => {
    const mockRestaurant = { id: 1 };
    const mockReservation = {
      id: 1,
      userId: 5,
      restaurantId: 1,
      date: '2025-06-01',
      guests: 2
    };

    Restaurant.findByPk.mockResolvedValue(mockRestaurant);
    Reservation.create.mockResolvedValue(mockReservation);

    const req = {
      user: { id: 5 },
      body: {
        restaurantId: 1,
        date: '2025-06-01',
        guests: 2
      }
    };
    const res = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };

    await createReservation(req, res);

    expect(res.status).toHaveBeenCalledWith(201);
    expect(res.json).toHaveBeenCalledWith({
      message: 'Reserva creada con éxito',
      reservation: mockReservation
    });
  });

  it('debería retornar 404 si el restaurante no existe', async () => {
    Restaurant.findByPk.mockResolvedValue(null); // simula restaurante no encontrado

    const req = {
      user: { id: 5 },
      body: {
        restaurantId: 99,
        date: '2025-06-01',
        guests: 2
      }
    };
    const res = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };

    await createReservation(req, res);

    expect(res.status).toHaveBeenCalledWith(404);
    expect(res.json).toHaveBeenCalledWith({ message: 'Restaurante no encontrado' });
  });
});

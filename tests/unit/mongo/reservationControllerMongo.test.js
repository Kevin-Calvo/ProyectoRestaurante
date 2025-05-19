const { createReservation } = require('../../../controllers/reservationControllerMongo');
const Reservation = require('../../../mongoModels/reservation');
const Restaurant = require('../../../mongoModels/restaurants');

jest.mock('../../../mongoModels/reservation');
jest.mock('../../../mongoModels/restaurants');
jest.mock('../../../config/mongo', () => jest.fn().mockResolvedValue());

describe('reservationControllerMongo - createReservation', () => {
  it('debería crear una reserva si el restaurante existe', async () => {
    const mockRestaurant = { id: 'r1' };
    const mockReservation = {
      userId: 'u1',
      restaurantId: 'r1',
      date: '2025-05-30',
      guests: 4
    };

    Restaurant.findById.mockResolvedValue(mockRestaurant);
    Reservation.prototype.save = jest.fn().mockResolvedValue(mockReservation);

    const req = {
      user: { id: 'u1' },
      body: {
        restaurantId: 'r1',
        date: '2025-05-30',
        guests: 4
      }
    };

    const res = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };

    await createReservation(req, res);

    expect(res.status).toHaveBeenCalledWith(201);
    expect(res.json).toHaveBeenCalledWith(expect.objectContaining({
      message: 'Reserva creada con éxito'
    }));
  });

  it('debería devolver 404 si el restaurante no existe', async () => {
    Restaurant.findById.mockResolvedValue(null); // Restaurante no encontrado

    const req = {
      user: { id: 'u1' },
      body: {
        restaurantId: 'noExiste',
        date: '2025-05-30',
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

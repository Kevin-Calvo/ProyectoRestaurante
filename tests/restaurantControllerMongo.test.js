const { createRestaurant } = require('../controllers/restaurantControllerMongo');
const Restaurant = require('../mongoModels/restaurants');

jest.mock('../mongoModels/restaurants');
jest.mock('../config/mongo', () => jest.fn().mockResolvedValue());

describe('restaurantControllerMongo - createRestaurant', () => {
  it('debería registrar un restaurante si el usuario es admin', async () => {
    const mockRestaurant = {
      name: 'Soda La U',
      address: 'Cartago',
      owner_id: 'admin123'
    };

    Restaurant.prototype.save = jest.fn().mockResolvedValue(mockRestaurant);

    const req = {
      user: { id: 'admin123', role: 'admin' },
      body: {
        name: 'Soda La U',
        address: 'Cartago'
      }
    };

    const res = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };

    await createRestaurant(req, res);

    expect(res.status).toHaveBeenCalledWith(201);
    expect(res.json).toHaveBeenCalledWith(expect.objectContaining({
      message: 'Restaurante registrado con éxito'
    }));
  });

  it('debería retornar 403 si el usuario no es admin', async () => {
    const req = {
      user: { id: 'client1', role: 'client' },
      body: {
        name: 'Soda Tiquicia',
        address: 'San José'
      }
    };

    const res = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };

    await createRestaurant(req, res);

    expect(res.status).toHaveBeenCalledWith(403);
    expect(res.json).toHaveBeenCalledWith({ message: 'No autorizado' });
  });
});

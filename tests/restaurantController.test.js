const { getRestaurants } = require('../controllers/restaurantControllerPostgres');
const Restaurant = require('../models/Restaurant');

jest.mock('../models/Restaurant');

describe('getRestaurants', () => {
  it('debería retornar una lista de restaurantes', async () => {
    const mockData = [
      { id: 1, name: 'La Soda', address: 'San José' },
      { id: 2, name: 'El Buen Comer', address: 'Cartago' }
    ];

    Restaurant.findAll.mockResolvedValue(mockData);

    const req = {};
    const res = {
      json: jest.fn(),
      status: jest.fn().mockReturnThis()
    };

    await getRestaurants(req, res);

    expect(res.json).toHaveBeenCalledWith(mockData);
  });

  it('debería retornar status 500 si ocurre un error', async () => {
    Restaurant.findAll.mockRejectedValue(new Error('Error de base de datos'));

    const req = {};
    const res = {
      json: jest.fn(),
      status: jest.fn().mockReturnThis()
    };

    await getRestaurants(req, res);

    expect(res.status).toHaveBeenCalledWith(500);
    expect(res.json).toHaveBeenCalledWith(expect.objectContaining({
  message: 'Error al obtener los restaurantes'}));
  });
});

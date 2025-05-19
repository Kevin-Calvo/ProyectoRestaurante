
const authController = require('../controllers/authControllerPostgres');
const User = require('../models/User');

jest.mock('../models/User');

describe('authController - login', () => {
  it('debería devolver error 404 si el usuario no existe', async () => {
    User.findOne.mockResolvedValue(null);

    const req = { body: { email: 'noexiste@example.com', password: '1234' } };
    const res = {
      json: jest.fn(),
      status: jest.fn().mockReturnThis()
    };

    await authController.login(req, res);

    expect(res.status).toHaveBeenCalledWith(404);
    expect(res.json).toHaveBeenCalledWith({ message: 'Usuario no encontrado' }); // ajustá al mensaje real de tu controlador
  });

  it('debería devolver error 401 si la contraseña es incorrecta', async () => {
    User.findOne.mockResolvedValue({
      id: 1,
      email: 'test@example.com',
      password: '$2a$10$invalidpass', // hash incorrecto
      role: 'client'
    });

    const req = { body: { email: 'test@example.com', password: 'wrong' } };
    const res = {
      json: jest.fn(),
      status: jest.fn().mockReturnThis()
    };

    await authController.login(req, res);

    expect(res.status).toHaveBeenCalledWith(401);
    expect(res.json).toHaveBeenCalledWith({ message: 'Contraseña incorrecta' }); // ajustá al mensaje real
  });
});


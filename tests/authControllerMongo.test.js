const { register, login } = require('../controllers/authControllerMongo');
const User = require('../mongoModels/users');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

jest.mock('../mongoModels/users');
jest.mock('bcryptjs');
jest.mock('jsonwebtoken');

describe('authControllerMongo - register', () => {
  it('debería registrar un usuario correctamente', async () => {
    User.findOne.mockResolvedValue(null); // no existe
    bcrypt.hash.mockResolvedValue('hashed_pass');
    User.prototype.save = jest.fn().mockResolvedValue();

    const req = {
      body: {
        name: 'Test',
        email: 'test@example.com',
        password: '123456',
        role: 'client'
      }
    };

    const res = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };

    await register(req, res);

    expect(res.status).toHaveBeenCalledWith(201);
    expect(res.json).toHaveBeenCalledWith(expect.objectContaining({
      message: 'Usuario registrado con éxito'
    }));
  });

  it('debería rechazar si el correo ya existe', async () => {
    User.findOne.mockResolvedValue({ email: 'test@example.com' }); // ya existe

    const req = {
      body: {
        name: 'Test',
        email: 'test@example.com',
        password: '123456',
        role: 'client'
      }
    };

    const res = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };

    await register(req, res);

    expect(res.status).toHaveBeenCalledWith(400);
    expect(res.json).toHaveBeenCalledWith({ message: 'El usuario ya existe' });
  });
});

describe('authControllerMongo - login', () => {
  it('debería loguear con éxito', async () => {
    const mockUser = {
      _id: 'abc123',
      role: 'client',
      password: 'hashed',
    };

    User.findOne.mockResolvedValue(mockUser);
    bcrypt.compare.mockResolvedValue(true);
    jwt.sign.mockReturnValue('fake_token');

    const req = {
      body: {
        email: 'test@example.com',
        password: '123456'
      }
    };

    const res = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };

    await login(req, res);

    expect(res.json).toHaveBeenCalledWith({ token: 'fake_token' });
  });

  it('debería rechazar login con contraseña incorrecta', async () => {
    User.findOne.mockResolvedValue({ password: 'hashed' });
    bcrypt.compare.mockResolvedValue(false);

    const req = {
      body: {
        email: 'test@example.com',
        password: 'wrongpassword'
      }
    };

    const res = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };

    await login(req, res);

    expect(res.status).toHaveBeenCalledWith(401);
    expect(res.json).toHaveBeenCalledWith({ message: 'Contraseña incorrecta' });
  });
});

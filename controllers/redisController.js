const redis = require('../config/redis');

class RedisController {
  async guardarDato(req, res) {
    const { key, value } = req.body;
    try {
      await redis.set(key, value);
      res.status(200).json({ message: 'Dato guardado en Redis' });
    } catch (error) {
      res.status(500).json({ error: 'Error guardando en Redis' });
    }
  }

  async obtenerDato(req, res) {
    const { key } = req.params;
    try {
      const value = await redis.get(key);
      if (value) {
        res.status(200).json({ value });
      } else {
        res.status(404).json({ message: 'Dato no encontrado' });
      }
    } catch (error) {
      res.status(500).json({ error: 'Error consultando Redis' });
    }
  }
}

module.exports = new RedisController();

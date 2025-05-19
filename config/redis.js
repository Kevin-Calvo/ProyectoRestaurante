const Redis = require('ioredis');

class RedisConnector {
  constructor() {
    this.redis = new Redis({
      host: process.env.REDIS_HOST || 'redis',  // nombre del servicio en docker
      port: process.env.REDIS_PORT || 6379,
    });

    this.redis.on('connect', () => {
      console.log('Conectado a Redis');
    });

    this.redis.on('error', (err) => {
      console.error('Error en Redis:', err);
    });
  }

  async set(key, value, expireInSeconds = 3600) {
    await this.redis.set(key, value, 'EX', expireInSeconds);
  }

  async get(key) {
    return await this.redis.get(key);
  }

  async del(key) {
    return await this.redis.del(key);
  }
}

module.exports = new RedisConnector();


const crypto = require('crypto');

const generarClave = (categoria, id) => {
    return crypto.createHash('sha256').update(`${categoria}:${id}`).digest('hex');
};

module.exports = { generarClave };
const mysql = require('mysql2');

const db = mysql.createConnection({
  host: 'localhost',
  user: 'root',       // your MySQL username
  password: '',       // your MySQL password
  database: 'auth_db'
});

db.connect(err => {
  if (err) throw err;
  console.log('MySQL Connected...');
});

module.exports = db;

const express = require("express");
const path = require("path");
const bcrypt = require("bcrypt");
const db = require("./db");
const session = require("express-session");

const app = express();
const PORT = 3000;

// Middleware
app.use(express.urlencoded({ extended: true }));
app.use(express.static("public"));
app.set("view engine", "ejs");

app.use(session({
  secret: "your_secret_key", // change this in production
  resave: false,
  saveUninitialized: false
}));

// Middleware to protect routes
function isAuthenticated(req, res, next) {
  if (req.session.userId) {
    return next();
  }
  res.redirect("/login");
}

// Routes
app.get("/", (req, res) => {
  res.redirect("/login");
});

app.get("/register", (req, res) => {
  res.render("register", { message: "" });
});

app.post("/register", async (req, res) => {
  const { name, email, password } = req.body;
  const hashedPassword = await bcrypt.hash(password, 10);

  db.query("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", 
    [name, email, hashedPassword], 
    (err, result) => {
      if (err) {
        if (err.code === "ER_DUP_ENTRY") {
          return res.render("register", { message: "Email already exists!" });
        }
        return res.send("Database error");
      }
      res.redirect("/login");
    });
});

app.get("/login", (req, res) => {
  res.render("login", { message: "", username: null });
});

app.post("/login", (req, res) => {
  const { email, password } = req.body;

  db.query("SELECT * FROM users WHERE email = ?", [email], async (err, results) => {
    if (err) return res.send("DB error");
    if (results.length === 0) return res.render("login", { message: "User not found", username: null });

    const match = await bcrypt.compare(password, results[0].password);
    if (!match) return res.render("login", { message: "Incorrect password", username: null });

    // Save user info to session
    req.session.userId = results[0].id;
    req.session.username = results[0].name;

    res.redirect("/dashboard");
  });
});

app.get("/dashboard", isAuthenticated, (req, res) => {
  res.render("dashboard", { username: req.session.username });
});

app.get("/logout", (req, res) => {
  req.session.destroy(() => {
    res.redirect("/login");
  });
});

app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});
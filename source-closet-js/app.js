const express = require('express');
const nunjucks = require('nunjucks');
const path = require('path');
const os = require('os');

const app = express();
const port = 3000;

const tursoAuthToken = process.env.TURSO_AUTH_TOKEN || '';
const tursoDBURL = process.env.TURSO_DATABASE_URL || '';

// Configure Nunjucks
nunjucks.configure(path.resolve(__dirname, 'views'), {
    express: app,
    autoescape: true, // Recommended for security
    watch: true // Reload templates automatically during development
});

// Set Nunjucks as the view engine for files with .html or .njk extensions
app.set('view engine', 'njk'); // or 'njk'

// Define a route
app.get('/', (req, res) => {
    // Renders the 'index.html' template from the 'views' folder, passing data
    res.render('index.njk', { myname: 'John Doe' });
});

// Start the server
app.listen(port, () => {
    console.log(`Express server running on http://localhost:${port}`);
});
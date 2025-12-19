const express = require('express');
const nunjucks = require('nunjucks');
const path = require('path');
const os = require('os');
const createClient = require('@libsql/client').createClient;
const session = require('express-session');
const readFile = require('fs');

const app = express();
const port = 3000;

app.use('/static', express.static(path.join(__dirname, 'static')));
app.use(express.urlencoded({ extended: false }));
app.use(express.json());
app.use(session({
    secret: '@SinghasanKhaliKaro101', // Replace with a strong secret in production
    resave: false,
    saveUninitialized: true,
    cookie: { secure: false } // Set to true if using HTTPS
}));

const tursoAuthToken = process.env.TURSO_AUTH_TOKEN || '';
const tursoDBURL = process.env.TURSO_DATABASE_URL || '';

const client = createClient({
  url: process.env.TURSO_DATABASE_URL,
  authToken: process.env.TURSO_AUTH_TOKEN
});

var max_id = 0;

let maxIdResult = client.execute("SELECT MAX(ID) AS MAX_ID FROM SOURCES").then(result => {
    const v = result.rows && result.rows[0] && result.rows[0].MAX_ID;
    const n = Number(v);
    if (Number.isFinite(n)) {
        max_id = n;
    } else {
        max_id = 0;
    }
    return result;
}).catch(error => {
    console.error('Error fetching max ID:', error);
});

// Configure Nunjucks
nunjucks.configure(path.resolve(__dirname, 'views'), {
    express: app,
    autoescape: true, // Recommended for security
    watch: true // Reload templates automatically during development
});

// Set Nunjucks as the view engine for files with .html or .njk extensions
app.set('view engine', 'njk'); // or 'njk'

app.get('/', async (req, res) => {
    try {
        // Use a deterministic query to fetch the latest 5 sources directly.
        // This avoids relying on the module-level `max_id` which may still be 0
        // if the initial MAX(ID) query hasn't completed at request time.
        const result = await client.execute("SELECT ID,DESCRIPTION,YEAR,MONTH,DATE,AUTHOR,TITLE FROM SOURCES ORDER BY ID DESC LIMIT 5");

        // Fetch tags for each source in parallel and attach them
        await Promise.all(result.rows.map(async (item) => {
            const tagResult = await client.execute(
                "SELECT TAG FROM TAGS WHERE ID IN (SELECT TAG_ID FROM SRC_TAGS WHERE SRC_ID=?)",
                [item.ID]
            );
            item.TAGS = tagResult.rows.map(r => r.TAG).join(', ');
        }));

        // Query returns newest-first due to ORDER BY DESC, keep that order
        res.render('index.njk', { sources: result.rows, length: result.rows.length, login: req.session.user ? true : false });
    } catch (error) {
        console.error('Database query error:', error);
        res.status(500).send('Internal Server Error');
    }
});

app.get('/source/:id', async (req, res) => {
    const sourceId = req.params.id;
    try {
        const result = await client.execute(
            "SELECT * FROM SOURCES WHERE ID = ?",
            [sourceId]
        );

        if (result.rows.length === 0) {
            return res.status(404).send('Source not found');
        }

        const source = result.rows[0];

        const tagResult = await client.execute(
            "SELECT ID, TAG FROM TAGS WHERE ID IN (SELECT TAG_ID FROM SRC_TAGS WHERE SRC_ID=?)",
             [sourceId]
         );
         source.TAGS = tagResult.rows.map(r => r.TAG).join(', ');
 
         const counResult = await client.execute(
             "SELECT NAME FROM COUNTRIES WHERE ID IN (SELECT COUN_ID FROM SRC_COUNS WHERE SRC_ID=?)",
             [sourceId]
         );
         source.COUNTRIES = counResult.rows.map(r => r.NAME).join(', ');
 
        source.FURTHER_READING = [];
        await Promise.all(tagResult.rows.map(async (element) => {
            const furtherResult = await client.execute(
                "SELECT NAME, URL FROM FURTHER WHERE ID IN (SELECT FURT_ID FROM TAGS_FURTHER WHERE TAG_ID=?)",
                [element.ID]
            );
            source.FURTHER_READING.push(...furtherResult.rows);
        }));


        res.render('source.njk', { source: source, prot: source.ID == 1, max_id: max_id, login: req.session.user ? true : false });
    } catch (error) {
        console.error('Database query error:', error);
        res.status(500).send('Internal Server Error');
    }
});

app.get('/search', async (req, res) => {
    try {
        const queryKeys = Object.keys(req.query || {});
        const hasFilters = queryKeys.some(k =>
            k === 'id_' || k === 'keywds_' || k === 'start_yr' || k === 'end_yr' || k.startsWith('tag_') || k.startsWith('country_')
        );

        if (!hasFilters) {
            const tagsRes = await client.execute("SELECT TAG FROM TAGS ORDER BY TAG");
            const countriesRes = await client.execute("SELECT NAME FROM COUNTRIES ORDER BY NAME");
            const tags = tagsRes.rows.map(r => r.TAG);
            const countries = countriesRes.rows.map(r => r.NAME);
            return res.render('search.njk', { tags, countries });
        }

        // Read form inputs
        const id = req.query.id_ || '';
        const keywds = req.query.keywds_ || '';
        const year_from = req.query.start_yr || '';
        const year_to = req.query.end_yr || '';

        const selectedTags = queryKeys.filter(k => k.startsWith('tag_') && req.query[k]).map(k => k.slice('tag_'.length));
        const selectedCountries = queryKeys.filter(k => k.startsWith('country_') && req.query[k]).map(k => k.slice('country_'.length));

        // Build parameterized query
        const params = [];
        const where = [];

        if (id) {
            where.push("S.ID = ?");
            params.push(id);
        }
        if (keywds) {
            where.push("(S.TITLE LIKE ? OR S.DESCRIPTION LIKE ? OR S.AUTHOR LIKE ?)");
            const kw = `%${keywds}%`;
            params.push(kw, kw, kw);
        }
        if (year_from) {
            const y = parseInt(year_from, 10);
            if (!Number.isNaN(y)) {
                where.push("S.YEAR >= ?");
                params.push(y);
            }
        }
        if (year_to) {
            const y = parseInt(year_to, 10);
            if (!Number.isNaN(y)) {
                where.push("S.YEAR <= ?");
                params.push(y);
            }
        }
        if (selectedTags.length) {
            const ph = selectedTags.map(() => '?').join(',');
            where.push(`T.TAG IN (${ph})`);
            params.push(...selectedTags);
        }
        if (selectedCountries.length) {
            const ph = selectedCountries.map(() => '?').join(',');
            where.push(`C.NAME IN (${ph})`);
            params.push(...selectedCountries);
        }

        let sql = `
            SELECT DISTINCT S.ID, S.DESCRIPTION, S.YEAR, S.MONTH, S.DATE, S.AUTHOR, S.TITLE
            FROM SOURCES S
            LEFT JOIN SRC_TAGS ST ON ST.SRC_ID = S.ID
            LEFT JOIN TAGS T ON T.ID = ST.TAG_ID
            LEFT JOIN SRC_COUNS SC ON SC.SRC_ID = S.ID
            LEFT JOIN COUNTRIES C ON C.ID = SC.COUN_ID
        `;
        if (where.length) sql += ' WHERE ' + where.join(' AND ');
        sql += ' ORDER BY S.ID DESC LIMIT 200';

        const result = await client.execute(sql, params);

        // Attach TAGS to each source (optional; keeps consistent with other pages)
        await Promise.all(result.rows.map(async (item) => {
            const tagResult = await client.execute(
                "SELECT TAG FROM TAGS WHERE ID IN (SELECT TAG_ID FROM SRC_TAGS WHERE SRC_ID=?)",
                [item.ID]
            );
            item.TAGS = tagResult.rows.map(r => r.TAG).join(', ');
        }));

        res.render('search_result.njk', { sources: result.rows, query: req.query.keywds_ || '', login: req.session.user ? true : false });
    } catch (error) {
        console.error('Search error:', error);
        res.status(500).send('Internal Server Error');
    }
});

app.get('/login', (req, res) => {
    if (req.session.user) return res.redirect('/');
    res.render('login.njk');
});

// Fixed POST /login: only process token when not already logged in
app.post('/login', async (req, res) => {
    if (req.session.user) {
        return res.redirect('/');
    }

    const token = req.body?.token_ || '';
    if (!token) {
        return res.render('login.njk', { error: 'Token required' });
    }

    try {
        const result = await client.execute("SELECT * FROM USERS WHERE TOKEN=?", [token]);
        if (result.rows.length > 0) {
            req.session.user = result.rows[0];
            res.redirect('/');
        } else {
            res.render('login.njk', { error: 'Invalid token' });
        }
    } catch (err) {
        console.error('Login error:', err);
        res.status(500).send('Internal Server Error');
    }
});

app.get('/logout', (req, res) => {
    req.session.destroy(err => {
        if (err) {
            console.error('Logout error:', err);
            return res.status(500).send('Internal Server Error');
        }
        res.redirect('/');
    });
});

app.get('/save_source/:id', async (req, res) => {
    if (!req.session.user) {
        return res.status(401).send('Unauthorized');
    }
    const sourceId = req.params.id;
    const userId = req.session.user.ID;

    await client.execute("INSERT OR IGNORE INTO USERS_SRCS (UID, SRC_ID) VALUES (?, ?)", [userId, sourceId]);
    return res.redirect(`/source/${sourceId}`);
});

app.get('/profile', async (req, res) => {
    if (!req.session.user) {
        return res.status(401).send('Unauthorized');
    }
    const userId = req.session.user.ID;
    
    const result = await client.execute("SELECT ID, DESCRIPTION, YEAR, MONTH, DATE, AUTHOR, TITLE FROM SOURCES WHERE ID IN (SELECT SRC_ID FROM USERS_SRCS WHERE UID=?)", [userId]);

    res.render('profile.njk', { sources: result.rows, login: true });
});

app.get('/delete_source/:id', async (req, res) => {
    if (!req.session.user) {
        return res.status(401).send('Unauthorized');
    }
    const sourceId = req.params.id;
    const userId = req.session.user.ID;

    await client.execute("DELETE FROM USERS_SRCS WHERE UID=? AND SRC_ID=?", [userId, sourceId]);
    return res.redirect('/profile');
});

app.get('/about', (req, res) => {
    res.render('about.njk', { login: req.session.user ? true : false });
});

app.get('/browse', async (req, res) => {
    const result = await client.execute("SELECT ID, DESCRIPTION, YEAR, MONTH, DATE, AUTHOR, TITLE FROM SOURCES ORDER BY ID DESC");
    await Promise.all(result.rows.map(async (item) => {
            const tagResult = await client.execute(
                "SELECT TAG FROM TAGS WHERE ID IN (SELECT TAG_ID FROM SRC_TAGS WHERE SRC_ID=?)",
                [item.ID]
            );
            item.TAGS = tagResult.rows.map(r => r.TAG).join(', ');
            console.log(item);
        }));
    res.render('browse.njk', { sources: result.rows, login: req.session.user ? true : false });
});

app.get('/signup', (req, res) => {
    if (req.session.user) return res.redirect('/');
    res.render('signup.njk', { login: req.session.user ? true : false, post: false });
});

app.post('/signup', async (req, res) => {
    if (req.session.user) {
        return res.redirect('/');
    }
    let token = '';
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    for (let i = 0; i < 30; i++) {
        const randomInd = Math.floor(Math.random() * characters.length);
        token += characters.charAt(randomInd);
    }

    client.execute("INSERT INTO USERS (TOKEN, DATE_CREATED) VALUES (?, ?)", [token, new Date().toISOString().split("T")[0]]).then(() => {
        res.render('signup.njk', { token: token, login: req.session.user ? true : false, post: true });
    }).catch(error => {
        console.error('Signup error:', error);
        res.status(500).send('Internal Server Error');
    });
});

app.get('/sources_abbr', (req, res) => {
    res.render('Sources.njk', { login: req.session.user ? true : false });
});

app.get('/further_reading', async (req, res) => {
    furt_client = createClient({
      url: "file://" + path.join(__dirname, 'further.db'),
    });
    const result = await furt_client.execute("SELECT Title, Author, Date, CoverPath, TimePeriod_start, TimePeriod_end, TopicsList FROM Further_Sources ORDER BY TimePeriod_start ASC");
    result.rows.forEach(r => {
        r.CoverPath = r.CoverPath || '';
        if (r.CoverPath) {
            r.previewId = r.CoverPath.replace('covers/', '').replace('.jpeg', '');
        } else {
            r.previewId = '';
        }
    });
    console.log(result.rows);
    res.render('further_reading.njk', { login: req.session.user ? true : false, further_reading: result.rows });
});

app.get('/further_source/:id', async (req, res) => {
    const sourceId = req.params.id;
    furt_client = createClient({
      url: "file://" + path.join(__dirname, 'further.db'),
    });
    const result = await furt_client.execute("SELECT * FROM Further_Sources WHERE CoverPath LIKE ?", [`%${sourceId}.%`]);
    if (result.rows.length === 0) {
        return res.status(404).send('Source not found');
    }
    const source = result.rows[0];
    source.CoverPath = source.CoverPath || '';
    res.render('further_source.njk', { login: req.session.user ? true : false, source: source });
});

app.get('/stats', async (req, res) => {
    const result = await client.execute("SELECT LENGTH FROM SOURCES");
    const numSources = max_id;
    let numPages = 0;
    result.rows.map(r => r.LENGTH).forEach((length, index) => {
        numPages += length;
    });
    res.send(`${numSources} sources hosted on Source Closet, totalling ${numPages} pages of documentation.`);
});

app.get('/robots.txt', (req, res) => {
    const robots = readFile.readFileSync(path.join(__dirname, 'static/assets/robots.txt'), 'utf8');
    res.type('text/plain');
    res.send(robots);
});

app.get('/sitemap.txt', (req, res) => {
    const sitemap = readFile.readFileSync(path.join(__dirname, 'static/assets/sitemap.txt'), 'utf8');
    res.type('text/plain');
    res.send(sitemap);
});

app.get('/.well-known/discord', (req, res) => {
    res.type('text/plain');
    res.send('dh=b423c40a76035ddef43e4d16052440ac71a9be4d');
});

// Start the server
app.listen(port, () => {
    console.log(`Express server running on http://localhost:${port}`);
});
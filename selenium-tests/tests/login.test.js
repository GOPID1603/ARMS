const { Builder, By, until } = require('selenium-webdriver');
const chrome = require('selenium-webdriver/chrome');
const assert = require('assert');
const path = require('path');
const http = require('http');
const fs = require('fs');

describe('ARMS Login E2E Tests', function () {
  this.timeout(180000); // 180 seconds timeout for browser setup and execution
  let driver;
  let server;
  let testUrl;

  before(async function () {
    // 1. Start a simple static file server to serve index.html and dump.json to bypass file:// CORS restrictions
    server = http.createServer((req, res) => {
      let reqPath = req.url.split('?')[0];
      if (reqPath === '/') {
        reqPath = '/index.html';
      }
      
      const filePath = path.join(__dirname, '../..', reqPath);
      const rootPath = path.resolve(__dirname, '../..');
      const resolvedPath = path.resolve(filePath);

      // Security check: restrict access to workspace root only
      if (!resolvedPath.startsWith(rootPath)) {
        res.statusCode = 403;
        res.end('Forbidden');
        return;
      }

      fs.readFile(filePath, (err, data) => {
        if (err) {
          res.statusCode = 404;
          res.end('Not Found');
        } else {
          const ext = path.extname(filePath).toLowerCase();
          let contentType = 'text/html';
          if (ext === '.js') contentType = 'application/javascript';
          else if (ext === '.css') contentType = 'text/css';
          else if (ext === '.json') contentType = 'application/json';
          else if (ext === '.png') contentType = 'image/png';
          else if (ext === '.jpg' || ext === '.jpeg') contentType = 'image/jpeg';
          
          res.setHeader('Content-Type', contentType);
          res.end(data);
        }
      });
    });

    await new Promise((resolve) => {
      server.listen(0, '127.0.0.1', () => {
        const port = server.address().port;
        testUrl = `http://127.0.0.1:${port}`;
        console.log(`Temp test server running on ${testUrl}`);
        resolve();
      });
    });

    // 2. Set up Chrome options
    let options = new chrome.Options();
    if (process.env.HEADLESS === 'true') {
      options.addArguments('--headless=new');
      options.addArguments('--window-size=1920,1080');
      options.addArguments('--disable-gpu');
      options.addArguments('--no-sandbox');
      options.addArguments('--disable-dev-shm-usage');
    }

    driver = await new Builder()
      .forBrowser('chrome')
      .setChromeOptions(options)
      .build();
  });

  after(async function () {
    if (driver) {
      await driver.quit();
    }
    if (server) {
      await new Promise((resolve) => server.close(resolve));
      console.log('Temp test server closed.');
    }
  });

  it('should log in successfully with valid credentials and redirect to dashboard', async function () {
    const url = process.env.TEST_URL || testUrl;
    console.log(`Navigating to: ${url}`);
    await driver.get(url);

    try {
      // Wait for the loader to disappear
      const loader = await driver.findElement(By.id('loader'));
      await driver.wait(async () => {
        const classes = await loader.getAttribute('class');
        return classes.includes('hidden');
      }, 15000);

      // Wait for the login form to load
      const emailInput = await driver.wait(until.elementLocated(By.id('email')), 15000);
      const passwordInput = await driver.wait(until.elementLocated(By.id('password')), 15000);
      const loginButton = await driver.wait(until.elementLocated(By.id('login-button')), 15000);

      // Enters credentials (using preseeded admin credentials)
      await emailInput.clear();
      await emailInput.sendKeys('admin');
      await passwordInput.clear();
      await passwordInput.sendKeys('admin123');

      // Click Sign In
      await loginButton.click();

      // Verify dashboard is displayed (login-page gets hidden)
      const loginPage = await driver.findElement(By.id('login-page'));
      await driver.wait(async () => {
        const display = await loginPage.getCssValue('display');
        return display === 'none';
      }, 15000);

      const displayStyle = await loginPage.getCssValue('display');
      assert.strictEqual(displayStyle, 'none', 'Login page should be hidden on successful login');

      const sidebar = await driver.wait(until.elementLocated(By.id('sidebar')), 15000);
      const sidebarVisible = await sidebar.isDisplayed();
      assert.ok(sidebarVisible, 'Sidebar should be visible on the dashboard');
    } catch (err) {
      const logs = await driver.manage().logs().get('browser').catch(() => []);
      console.log('BROWSER CONSOLE LOGS ON FAILURE:', logs);
      throw err;
    }
  });

  it('should show an error message with invalid credentials', async function () {
    const url = process.env.TEST_URL || testUrl;
    await driver.get(url);

    try {
      // Wait for the loader to disappear
      const loader = await driver.findElement(By.id('loader'));
      await driver.wait(async () => {
        const classes = await loader.getAttribute('class');
        return classes.includes('hidden');
      }, 15000);

      const emailInput = await driver.wait(until.elementLocated(By.id('email')), 15000);
      const passwordInput = await driver.wait(until.elementLocated(By.id('password')), 15000);
      const loginButton = await driver.wait(until.elementLocated(By.id('login-button')), 15000);

      // Enters invalid credentials
      await emailInput.clear();
      await emailInput.sendKeys('admin');
      await passwordInput.clear();
      await passwordInput.sendKeys('wrongpassword');

      await loginButton.click();

      // Verify login error element becomes visible
      const errorMsg = await driver.wait(until.elementLocated(By.id('login-error')), 15000);
      await driver.wait(async () => {
        const classes = await errorMsg.getAttribute('class');
        return classes.includes('show');
      }, 15000);

      const classes = await errorMsg.getAttribute('class');
      assert.ok(classes.includes('show'), 'Error message should be visible on invalid login credentials');
    } catch (err) {
      const logs = await driver.manage().logs().get('browser').catch(() => []);
      console.log('BROWSER CONSOLE LOGS ON FAILURE:', logs);
      throw err;
    }
  });

  // Load 200 dynamic test credentials from the database dump
  const dumpData = JSON.parse(fs.readFileSync(path.join(__dirname, '../../dump.json'), 'utf8'));
  const students = dumpData.students.slice(0, 150);
  const faculty = dumpData.faculty.slice(0, 50);
  const users = [
    ...students.map(s => ({ id: s.reg, pass: 'student123', name: s.name, type: 'student' })),
    ...faculty.map(f => ({ id: f.id, pass: 'faculty123', name: f.name, type: 'faculty' }))
  ];

  users.forEach((user, index) => {
    it(`TC-SEL-USER-${String(index + 1).padStart(3, '0')}: should log in successfully as ${user.type} user: ${user.name} (${user.id})`, async function () {
      try {
        const emailInput = await driver.wait(until.elementLocated(By.id('email')), 5000);
        const passwordInput = await driver.wait(until.elementLocated(By.id('password')), 5000);
        const loginButton = await driver.wait(until.elementLocated(By.id('login-button')), 5000);

        // Input credentials
        await emailInput.clear();
        await emailInput.sendKeys(user.id);
        await passwordInput.clear();
        await passwordInput.sendKeys(user.pass);

        // Click Sign In
        await loginButton.click();

        // Verify successful login (login page gets hidden)
        const loginPage = await driver.findElement(By.id('login-page'));
        await driver.wait(async () => {
          const display = await loginPage.getCssValue('display');
          return display === 'none';
        }, 5000);

        // Validate dashboard sidebar is visible
        const sidebar = await driver.wait(until.elementLocated(By.id('sidebar')), 5000);
        const sidebarVisible = await sidebar.isDisplayed();
        assert.ok(sidebarVisible, `Dashboard sidebar should be visible for ${user.name}`);

        // Perform instant logout via JS execution to reset state for the next test
        await driver.executeScript("logoutUser()");

        // Wait for login page to reappear
        await driver.wait(async () => {
          const display = await loginPage.getCssValue('display');
          return display === 'flex' || display === 'block' || display !== 'none';
        }, 5000);
      } catch (err) {
        const logs = await driver.manage().logs().get('browser').catch(() => []);
        console.log(`BROWSER CONSOLE LOGS ON FAILURE FOR USER ${user.id}:`, logs);
        throw err;
      }
    });
  });
});

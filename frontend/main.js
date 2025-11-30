/**
 * Main process script for the Electron application.
 * This script creates the main application window and configures its properties.
 */

const { app, BrowserWindow } = require('electron');
const path = require('node:path');
const dotenv = require('dotenv');

// Load environment variables from .env file in project root
dotenv.config({ path: path.join(__dirname, '..', '.env') });

let mainWindow;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 500,
        height: 700,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            contextIsolation: true,
            nodeIntegration: false,
            webSecurity: true
        },
        resizable: false,
        titleBarStyle: 'hiddenInset'
    });

    mainWindow.loadFile('renderer/index.html');
    mainWindow.setMenuBarVisibility(false);
    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

await app.whenReady();
createWindow();

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});

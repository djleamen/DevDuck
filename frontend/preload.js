/**
 * DevDuck Electron Preload Script
 * 
 * Provides secure communication between renderer and main process.
 */

const { contextBridge, ipcRenderer } = require('electron');

// TODO: Define secure API for renderer communication

const devDuckAPI = {
    toggleListening: async () => {
        // TODO: Implement listening toggle
        return await ipcRenderer.invoke('toggle-listening');
    },

    getConversationHistory: async () => {
        // TODO: Implement history retrieval
        return await ipcRenderer.invoke('get-conversation-history');
    },

    sendMessage: async (message) => {
        // TODO: Implement message sending
        return await ipcRenderer.invoke('send-message', message);
    },

    clearHistory: async () => {
        // TODO: Implement history clearing
        return await ipcRenderer.invoke('clear-history');
    },

    getAppState: async () => {
        // TODO: Implement state retrieval
        return await ipcRenderer.invoke('get-app-state');
    },

    onConversationUpdate: (callback) => {
        // TODO: Implement conversation update listener
        ipcRenderer.on('conversation-update', (event, data) => {
            callback(data);
        });
    },

    onSentimentUpdate: (callback) => {
        // TODO: Implement sentiment update listener
        ipcRenderer.on('sentiment-update', (event, data) => {
            callback(data);
        });
    },

    onListeningStateChange: (callback) => {
        // TODO: Implement listening state change listener
        ipcRenderer.on('listening-state-change', (event, data) => {
            callback(data);
        });
    },

    onDuckAction: (callback) => {
        // TODO: Implement duck action listener
        ipcRenderer.on('duck-action', (event, data) => {
            callback(data);
        });
    },

    removeAllListeners: () => {
        // TODO: Implement listener cleanup
        ipcRenderer.removeAllListeners('conversation-update');
        ipcRenderer.removeAllListeners('sentiment-update');
        ipcRenderer.removeAllListeners('listening-state-change');
        ipcRenderer.removeAllListeners('duck-action');
    }
};

// TODO: Expose API to renderer process securely
contextBridge.exposeInMainWorld('devDuckAPI', devDuckAPI);

// TODO: Add additional security measuresssss
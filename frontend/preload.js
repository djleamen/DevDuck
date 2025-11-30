/**
 * Preload script for Electron renderer process
 * Securely exposes environment variables to the renderer
 */

const { contextBridge } = require('electron');

// Expose protected methods that allow the renderer process to use
// environment variables without exposing the entire process object
contextBridge.exposeInMainWorld('electronAPI', {
    vapiPublicKey: process.env.VAPI_PUBLIC_KEY || '',
    vapiAssistantId: process.env.VAPI_ASSISTANT_ID || '',
    vapiWebhookUrl: process.env.VAPI_WEBHOOK_URL || ''
});

#!/usr/bin/env python3
"""
Servidor HTTP simple para el contador de tickets
Guarda los datos en tickets-data.json
"""

import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import webbrowser

DATA_FILE = 'tickets-data.json'
PORT = 8888

class TicketHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Maneja peticiones GET"""
        if self.path == '/' or self.path == '/index.html':
            self.send_file('index.html', 'text/html')
        elif self.path == '/styles.css':
            self.send_file('styles.css', 'text/css')
        elif self.path == '/script.js':
            self.send_file('script.js', 'application/javascript')
        elif self.path == '/api/data':
            self.send_json_data()
        else:
            self.send_error(404, "File not found")
    
    def do_POST(self):
        """Maneja peticiones POST para guardar datos"""
        if self.path == '/api/save':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                self.save_data(data)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True}).encode())
            except Exception as e:
                self.send_error(500, f"Error saving data: {str(e)}")
        else:
            self.send_error(404, "Not found")
    
    def send_file(self, filename, content_type):
        """Envía un archivo estático"""
        try:
            with open(filename, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404, f"File {filename} not found")
    
    def send_json_data(self):
        """Envía los datos del archivo JSON"""
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {
                    "pendingTickets": 0,
                    "totalTickets": 0,
                    "resolvedTickets": 0
                }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
        except Exception as e:
            self.send_error(500, f"Error reading data: {str(e)}")
    
    def save_data(self, data):
        """Guarda los datos en el archivo JSON"""
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def log_message(self, format, *args):
        """Suprime los mensajes de log del servidor"""
        pass

def start_server():
    """Inicia el servidor HTTP"""
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, TicketHandler)
    
    url = f'http://localhost:{PORT}'
    print(f'\n✓ Servidor iniciado en {url}')
    print(f'✓ Los datos se guardan en: {os.path.abspath(DATA_FILE)}')
    print(f'\nPresiona Ctrl+C para detener el servidor\n')
    
    # Abrir el navegador automáticamente solo si no estamos en modo servicio
    if os.getenv('SERVICE_MODE') != '1':
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\n\n✓ Servidor detenido')
        httpd.server_close()

if __name__ == '__main__':
    start_server()

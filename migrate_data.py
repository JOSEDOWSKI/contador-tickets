#!/usr/bin/env python3
"""
Script para migrar datos del formato antiguo al nuevo formato mensual
"""

import json
import os
from datetime import datetime
from pathlib import Path

def migrate():
    old_file = Path('tickets-data.json')
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    
    if not old_file.exists():
        print("No se encontró tickets-data.json para migrar")
        return
    
    print("Migrando datos...")
    
    # Leer datos antiguos
    with open(old_file, 'r', encoding='utf-8') as f:
        old_data = json.load(f)
    
    # Crear archivo del mes actual
    month = datetime.now().strftime('%Y-%m')
    month_file = data_dir / f'tickets-{month}.json'
    
    # Crear estructura nueva
    new_data = {
        "pendingTickets": old_data.get('pendingTickets', 0),
        "totalTickets": old_data.get('totalTickets', 0),
        "resolvedTickets": old_data.get('resolvedTickets', 0),
        "month": month,
        "history": [{
            "timestamp": datetime.now().isoformat(),
            "action": "migrated_from_old_format",
            "pendingTickets": old_data.get('pendingTickets', 0),
            "totalTickets": old_data.get('totalTickets', 0),
            "resolvedTickets": old_data.get('resolvedTickets', 0)
        }]
    }
    
    # Si el archivo del mes ya existe, preservar su historial
    if month_file.exists():
        with open(month_file, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
            if 'history' in existing_data:
                new_data['history'] = existing_data['history'] + new_data['history']
    
    # Guardar nuevo formato
    with open(month_file, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)
    
    # Hacer backup del archivo antiguo
    backup_file = Path('tickets-data.json.backup')
    if backup_file.exists():
        backup_file.unlink()
    old_file.rename(backup_file)
    
    print(f"✓ Datos migrados exitosamente a data/tickets-{month}.json")
    print(f"✓ Archivo antiguo renombrado a tickets-data.json.backup")

if __name__ == '__main__':
    migrate()

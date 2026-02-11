#!/usr/bin/env python3
"""
Network Scanner Application
Une application moderne de scanning réseau avec interface web
"""

import asyncio
import json
import subprocess
import ipaddress
import socket
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

# Import du gestionnaire de base de données
from database import db_manager

app = FastAPI(title="Network Scanner", description="Scanner réseau moderne avec interface GNOME")

# Models
class ScanRequest(BaseModel):
    target: str
    scan_type: str = "quick"  # quick, full, stealth
    ports: Optional[str] = None

class ScanResult(BaseModel):
    host: str
    status: str
    ports: List[Dict]
    os_info: Optional[str] = None
    scan_time: str

class NetworkInfo(BaseModel):
    interface: str
    ip_address: str
    netmask: str
    network: str

class BookmarkCreate(BaseModel):
    name: str
    target: str
    description: str = ""
    scan_type: str = "quick"
    ports: str = ""

class BookmarkUpdate(BaseModel):
    name: str
    target: str
    description: str = ""
    scan_type: str = "quick"
    ports: str = ""

# Store active connections and scan state
active_connections: List[WebSocket] = []
scan_should_stop = False

async def broadcast_message(message: dict):
    """Diffuser un message à toutes les connexions WebSocket actives"""
    for connection in active_connections:
        try:
            await connection.send_text(json.dumps(message))
        except:
            active_connections.remove(connection)

def get_network_interfaces():
    """Obtenir les interfaces réseau disponibles"""
    try:
        result = subprocess.run(['ip', 'addr', 'show'], capture_output=True, text=True)
        interfaces = []
        
        current_interface = None
        for line in result.stdout.split('\n'):
            if ': ' in line and 'lo:' not in line:
                parts = line.split(': ')
                if len(parts) >= 2:
                    current_interface = parts[1].split('@')[0]
            elif 'inet ' in line and current_interface:
                inet_part = line.strip().split('inet ')[1].split(' ')[0]
                ip, prefix = inet_part.split('/')
                
                # Calculer le réseau
                network = ipaddress.IPv4Network(f"{ip}/{prefix}", strict=False)
                
                interfaces.append({
                    'interface': current_interface,
                    'ip_address': ip,
                    'netmask': str(network.netmask),
                    'network': str(network.network_address) + '/' + prefix
                })
                current_interface = None
        
        return interfaces
    except Exception as e:
        return [{'interface': 'eth0', 'ip_address': '192.168.1.100', 'netmask': '255.255.255.0', 'network': '192.168.1.0/24'}]

async def scan_host(host: str, ports: str = "auto", scan_type: str = "quick") -> Dict:
    """Scanner un hôte spécifique avec méthodes améliorées"""
    result = {
        'host': host,
        'status': 'down',
        'ports': [],
        'os_info': None,
        'scan_time': datetime.now().isoformat()
    }
    
    try:
        # Test de ping simple
        ping_result = subprocess.run(['ping', '-c', '1', '-W', '1', host], 
                                   capture_output=True, text=True)
        
        if ping_result.returncode == 0:
            result['status'] = 'up'
            
            # Définir les ports selon le type de scan
            if ports == "auto" or not ports:
                # Détection automatique intelligente
                if scan_type == "quick":
                    # Scan rapide : ports les plus courants (1-1024)
                    port_list = ",".join(str(p) for p in range(1, 1025))
                elif scan_type == "full":
                    # Scan complet : tous les ports TCP (1-65535)
                    port_list = ",".join(str(p) for p in range(1, 65536))
                elif scan_type == "range":
                    # Scan par plage personnalisée (1-10000)
                    port_list = ",".join(str(p) for p in range(1, 10001))
                else:
                    # Par défaut : scan intelligent adaptatif
                    port_list = ",".join(str(p) for p in range(1, 1025))
            else:
                # Ports spécifiés manuellement
                port_list = ports
            
            # Scanner les ports avec timeout adaptatif et parallélisme
            if scan_type == "full":
                timeout = 0.3  # Très rapide pour scan complet
                max_concurrent = 100  # Plus de connexions simultanées
            elif scan_type == "range":
                timeout = 0.5
                max_concurrent = 50
            else:
                timeout = 0.8  # Équilibre vitesse/précision
                max_concurrent = 30
            
            # Scanner les ports en parallèle avec limitation de concurrence
            ports_to_scan = [int(p.strip()) for p in port_list.split(',') if p.strip().isdigit()]
            
            # Diviser en chunks pour éviter la surcharge
            chunk_size = max_concurrent
            open_ports = []
            
            for i in range(0, len(ports_to_scan), chunk_size):
                chunk = ports_to_scan[i:i + chunk_size]
                
                # Vérifier si le scan doit être arrêté
                if scan_should_stop:
                    break
                
                # Scanner ce chunk de ports
                semaphore = asyncio.Semaphore(max_concurrent)
                tasks = [scan_single_port_with_semaphore(semaphore, host, port, timeout) for port in chunk]
                
                chunk_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Collecter les ports ouverts
                for port_result in chunk_results:
                    if isinstance(port_result, dict) and port_result.get('status') == 'open':
                        open_ports.append(port_result)
                
                # Envoyer une mise à jour intermédiaire si beaucoup de ports
                if len(ports_to_scan) > 1000 and i % (chunk_size * 5) == 0:
                    await broadcast_message({
                        'type': 'port_progress',
                        'host': host,
                        'scanned': i + len(chunk),
                        'total': len(ports_to_scan),
                        'found': len(open_ports)
                    })
            
            result['ports'] = open_ports
                        
    except Exception as e:
        result['status'] = 'error'
        result['error'] = str(e)
    
    return result

async def scan_single_port_with_semaphore(semaphore: asyncio.Semaphore, host: str, port: int, timeout: float = 0.8) -> Dict:
    """Scanner un port avec limitation de concurrence"""
    async with semaphore:
        return await scan_single_port(host, port, timeout)

async def scan_single_port(host: str, port: int, timeout: float = 0.8) -> Dict:
    """Scanner un port spécifique de manière asynchrone"""
    try:
        # Créer une connexion socket asynchrone
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        
        try:
            # Essayer de se connecter avec timeout
            await asyncio.wait_for(
                asyncio.get_event_loop().sock_connect(sock, (host, port)),
                timeout=timeout
            )
            
            # Connexion réussie - port ouvert
            try:
                service = socket.getservbyport(port)
            except:
                # Services personnalisés courants
                service_map = {
                    8080: "http-proxy",
                    8443: "https-alt", 
                    3306: "mysql",
                    5432: "postgresql",
                    1433: "mssql",
                    3389: "rdp",
                    5900: "vnc",
                    6379: "redis",
                    27017: "mongodb",
                    9200: "elasticsearch"
                }
                service = service_map.get(port, "unknown")
            
            return {
                'port': port,
                'status': 'open',
                'service': service
            }
            
        except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
            # Port fermé ou filtré
            return {'port': port, 'status': 'closed'}
            
        finally:
            sock.close()
            
    except Exception as e:
        return {'port': port, 'status': 'error', 'error': str(e)}

async def scan_network(target: str, scan_type: str = "quick", ports: str = "22,80,443,8080"):
    """Scanner un réseau ou une plage d'adresses avec sauvegarde en base"""
    global scan_should_stop
    scan_should_stop = False
    
    # Créer une session de scan en base de données
    session_id = await db_manager.create_scan_session(target, scan_type, ports)
    
    try:
        # Déterminer les hôtes à scanner
        if '/' in target:
            # CIDR notation
            network = ipaddress.IPv4Network(target, strict=False)
            hosts = [str(ip) for ip in network.hosts()]
        elif '-' in target:
            # Range notation (ex: 192.168.1.1-254)
            start_ip, end_range = target.split('-')
            base_ip = '.'.join(start_ip.split('.')[:-1])
            start_num = int(start_ip.split('.')[-1])
            end_num = int(end_range)
            hosts = [f"{base_ip}.{i}" for i in range(start_num, end_num + 1)]
        else:
            # Single host
            hosts = [target]
        
        # Limiter le nombre d'hôtes pour éviter la surcharge
        if len(hosts) > 254:
            hosts = hosts[:254]
        
        await broadcast_message({
            'type': 'scan_started',
            'total_hosts': len(hosts),
            'target': target,
            'session_id': session_id
        })
        
        # Scanner les hôtes par petits groupes
        batch_size = 10
        scanned = 0
        hosts_up = 0
        
        for i in range(0, len(hosts), batch_size):
            # Vérifier si le scan doit être arrêté
            if scan_should_stop:
                await db_manager.update_scan_session(session_id, 'stopped', len(hosts), hosts_up)
                await broadcast_message({
                    'type': 'scan_stopped',
                    'message': 'Scan arrêté par l\'utilisateur',
                    'scanned': scanned,
                    'session_id': session_id
                })
                return
            
            batch = hosts[i:i + batch_size]
            tasks = [scan_host(host, ports, scan_type) for host in batch]
            results = await asyncio.gather(*tasks)
            
            for result in results:
                # Vérifier à nouveau si le scan doit être arrêté
                if scan_should_stop:
                    await db_manager.update_scan_session(session_id, 'stopped', len(hosts), hosts_up)
                    await broadcast_message({
                        'type': 'scan_stopped',
                        'message': 'Scan arrêté par l\'utilisateur',
                        'scanned': scanned,
                        'session_id': session_id
                    })
                    return
                
                # Sauvegarder le résultat en base de données
                await db_manager.save_scan_result(session_id, result)
                
                if result['status'] == 'up':
                    hosts_up += 1
                
                scanned += 1
                await broadcast_message({
                    'type': 'host_result',
                    'result': result,
                    'progress': (scanned / len(hosts)) * 100,
                    'session_id': session_id
                })
        
        # Mettre à jour la session comme terminée
        await db_manager.update_scan_session(session_id, 'completed', len(hosts), hosts_up)
        
        await broadcast_message({
            'type': 'scan_completed',
            'total_scanned': scanned,
            'hosts_up': hosts_up,
            'session_id': session_id
        })
        
    except Exception as e:
        await db_manager.update_scan_session(session_id, 'error', 0, 0)
        await broadcast_message({
            'type': 'scan_error',
            'error': str(e),
            'session_id': session_id
        })

# Routes API
@app.get("/api/interfaces")
async def get_interfaces():
    """Obtenir les interfaces réseau"""
    return get_network_interfaces()

@app.post("/api/scan")
async def start_scan(scan_request: ScanRequest):
    """Démarrer un scan réseau"""
    # Détection automatique par défaut
    ports = scan_request.ports or "auto"
    
    # Lancer le scan en arrière-plan
    asyncio.create_task(scan_network(
        scan_request.target,
        scan_request.scan_type,
        ports
    ))
    
    return {"status": "scan_started", "target": scan_request.target}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket pour les mises à jour en temps réel"""
    global scan_should_stop
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            # Recevoir les messages du client
            message = await websocket.receive_text()
            try:
                data = json.loads(message)
                if data.get('type') == 'stop_scan':
                    scan_should_stop = True
                    await broadcast_message({
                        'type': 'scan_stop_acknowledged',
                        'message': 'Arrêt du scan demandé'
                    })
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        if websocket in active_connections:
            active_connections.remove(websocket)

# Nouveaux endpoints pour la gestion de la base de données

@app.get("/api/history")
async def get_scan_history(limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0)):
    """Récupérer l'historique des scans"""
    sessions = await db_manager.get_scan_sessions(limit, offset)
    return {"sessions": sessions}

@app.get("/api/history/{session_id}")
async def get_scan_session_details(session_id: int):
    """Récupérer les détails d'une session de scan"""
    session = await db_manager.get_scan_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session non trouvée")
    
    results = await db_manager.get_scan_results(session_id)
    return {"session": session, "results": results}

@app.delete("/api/history/{session_id}")
async def delete_scan_session(session_id: int):
    """Supprimer une session de scan"""
    success = await db_manager.delete_scan_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session non trouvée")
    return {"message": "Session supprimée avec succès"}

@app.get("/api/search")
async def search_hosts(q: str = Query(..., min_length=1), limit: int = Query(20, ge=1, le=50)):
    """Rechercher des hôtes dans l'historique"""
    results = await db_manager.search_hosts(q, limit)
    return {"results": results}

@app.get("/api/statistics")
async def get_statistics():
    """Obtenir des statistiques sur les scans"""
    stats = await db_manager.get_statistics()
    return stats

# Endpoints pour les analytics et la carte réseau
@app.get("/api/analytics")
async def get_analytics():
    """Obtenir les données analytics"""
    try:
        stats = await db_manager.get_statistics()
        return stats
    except Exception as e:
        return {"error": str(e), "general": {"total_sessions": 0, "total_hosts_scanned": 0}, "top_ports": [], "recent_activity": []}

@app.get("/api/network-map")
async def get_network_map():
    """Obtenir les données pour la carte réseau"""
    try:
        # Récupérer les sessions récentes terminées
        sessions = await db_manager.get_scan_sessions(limit=5)
        completed_sessions = [s for s in sessions if s['status'] == 'completed']
        
        if not completed_sessions:
            return {"hosts": [], "networks": [], "session_info": None}
        
        # Prendre la session la plus récente
        latest_session = completed_sessions[0]
        results = await db_manager.get_scan_results(latest_session['id'])
        
        # Analyser les réseaux
        networks = {}
        for result in results:
            network_base = '.'.join(result['host'].split('.')[:-1])
            if network_base not in networks:
                networks[network_base] = {
                    'network': network_base + '.0/24',
                    'hosts': 0,
                    'active_hosts': 0
                }
            networks[network_base]['hosts'] += 1
            if result['status'] == 'up':
                networks[network_base]['active_hosts'] += 1
        
        return {
            "hosts": results,
            "networks": list(networks.values()),
            "session_info": latest_session
        }
    except Exception as e:
        return {"hosts": [], "networks": [], "session_info": None, "error": str(e)}

# Endpoints pour les bookmarks
@app.get("/api/bookmarks")
async def get_bookmarks():
    """Récupérer tous les bookmarks"""
    bookmarks = await db_manager.get_bookmarks()
    return {"bookmarks": bookmarks}

@app.post("/api/bookmarks")
async def create_bookmark(bookmark: BookmarkCreate):
    """Créer un nouveau bookmark"""
    bookmark_id = await db_manager.create_bookmark(
        bookmark.name, bookmark.target, bookmark.description, 
        bookmark.scan_type, bookmark.ports
    )
    return {"id": bookmark_id, "message": "Bookmark créé avec succès"}

@app.put("/api/bookmarks/{bookmark_id}")
async def update_bookmark(bookmark_id: int, bookmark: BookmarkUpdate):
    """Mettre à jour un bookmark"""
    success = await db_manager.update_bookmark(
        bookmark_id, bookmark.name, bookmark.target, bookmark.description,
        bookmark.scan_type, bookmark.ports
    )
    if not success:
        raise HTTPException(status_code=404, detail="Bookmark non trouvé")
    return {"message": "Bookmark mis à jour avec succès"}

@app.delete("/api/bookmarks/{bookmark_id}")
async def delete_bookmark(bookmark_id: int):
    """Supprimer un bookmark"""
    success = await db_manager.delete_bookmark(bookmark_id)
    if not success:
        raise HTTPException(status_code=404, detail="Bookmark non trouvé")
    return {"message": "Bookmark supprimé avec succès"}

# Servir les fichiers statiques
app.mount("/", StaticFiles(directory="static", html=True), name="static")

@app.on_event("startup")
async def startup_event():
    """Initialiser la base de données au démarrage"""
    await db_manager.init_database()
    print("Base de données SQLite initialisée")

if __name__ == "__main__":
    # Créer le dossier static s'il n'existe pas
    Path("static").mkdir(exist_ok=True)
    
    print(" Démarrage du Network Scanner...")
    print(" Interface web disponible sur: http://localhost:5000")
    print(" Base de données SQLite: network_scanner.db")
    
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info")

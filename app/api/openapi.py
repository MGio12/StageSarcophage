"""Spécification OpenAPI de l'API v1."""

OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "Modes Degrades API",
        "description": "API REST pour l'integration avec les outils internes.",
        "version": "1.0.0",
        "contact": {"name": "CLCC", "email": "support@clcc.local"},
    },
    "servers": [{"url": "/api/v1", "description": "API v1"}],
    "security": [{"bearerAuth": []}],
    "components": {
        "securitySchemes": {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "description": "Token API genere depuis l'interface d'administration",
            }
        },
        "schemas": {
            "Source": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "nom": {"type": "string"},
                    "protocole": {"type": "string", "enum": ["sftp", "smb", "local"]},
                    "actif": {"type": "boolean"},
                    "frequence_sync_minutes": {"type": "integer"},
                },
            },
            "Document": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "nom_fichier": {"type": "string"},
                    "source_id": {"type": "integer"},
                    "statut": {
                        "type": "string",
                        "enum": ["ok", "avertissement", "critique", "purge"],
                    },
                    "taille_octets": {"type": "integer"},
                },
            },
            "Job": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "operation": {"type": "string"},
                    "status": {
                        "type": "string",
                        "enum": ["queued", "running", "succeeded", "failed"],
                    },
                    "status_url": {"type": "string"},
                    "result": {"type": "object", "nullable": True},
                    "error": {"type": "string", "nullable": True},
                },
            },
            "Error": {
                "type": "object",
                "properties": {"error": {"type": "string"}},
            },
        },
    },
    "paths": {
        "/health": {
            "get": {
                "summary": "Etat de sante de l'API",
                "tags": ["Monitoring"],
                "security": [],
                "responses": {"200": {"description": "API fonctionnelle"}},
            }
        },
        "/stats": {
            "get": {
                "summary": "Statistiques globales",
                "tags": ["Monitoring"],
                "responses": {"200": {"description": "Statistiques"}},
            }
        },
        "/sources": {
            "get": {
                "summary": "Liste des sources",
                "tags": ["Sources"],
                "responses": {"200": {"description": "Liste des sources"}},
            }
        },
        "/sources/{id}": {
            "get": {
                "summary": "Detail d'une source",
                "tags": ["Sources"],
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}
                ],
                "responses": {
                    "200": {"description": "Source trouvee"},
                    "404": {"description": "Source non trouvee"},
                },
            }
        },
        "/sources/{id}/sync": {
            "post": {
                "summary": "Declencher la synchronisation asynchrone d'une source",
                "tags": ["Sources", "Jobs"],
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}
                ],
                "responses": {
                    "202": {
                        "description": "Job cree",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {"job": {"$ref": "#/components/schemas/Job"}},
                                }
                            }
                        },
                    },
                    "400": {"description": "Source inactive"},
                    "404": {"description": "Source non trouvee"},
                },
            }
        },
        "/jobs/{id}": {
            "get": {
                "summary": "Statut d'un job",
                "tags": ["Jobs"],
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}
                ],
                "responses": {
                    "200": {"description": "Statut du job"},
                    "403": {"description": "Permission insuffisante"},
                    "404": {"description": "Job non trouve"},
                },
            }
        },
        "/sources/{id}/status": {
            "get": {
                "summary": "Etat d'une source",
                "tags": ["Sources"],
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}
                ],
                "responses": {"200": {"description": "Etat de la source"}},
            }
        },
        "/documents": {
            "get": {
                "summary": "Liste des documents paginee",
                "tags": ["Documents"],
                "responses": {"200": {"description": "Liste paginee de documents"}},
            }
        },
        "/documents/{id}": {
            "get": {
                "summary": "Detail d'un document",
                "tags": ["Documents"],
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}
                ],
                "responses": {"200": {"description": "Document trouve"}},
            }
        },
        "/documents/{id}/download": {
            "get": {
                "summary": "Telecharger un document",
                "tags": ["Documents"],
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}
                ],
                "responses": {"200": {"description": "Fichier PDF"}},
            }
        },
    },
}

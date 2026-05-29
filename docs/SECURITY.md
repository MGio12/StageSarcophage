# Securite

## Lecteur cible

Ce document s'adresse a un mainteneur, exploitant ou auditeur qui doit verifier
ou modifier les controles de securite. Apres lecture, il doit pouvoir proteger
les secrets, verifier les headers HTTP, executer les audits et faire une
rotation de cle sans perdre les identifiants de sources.

## Checklist Rapide

Avant de considerer un deploiement pret:

```bash
make check
make permissions
git log --all -- .env
```

Attendus:

- `make check` passe les tests, le lint, Bandit, pip-audit, le scan de secrets
  suivis et le controle de permissions.
- `.env` n'apparait pas dans l'historique Git local.
- `.env` est en `0600` ou plus restrictif.
- Les secrets de production viennent de l'environnement, pas du code.

## Secrets Et Configuration

Secrets requis en production:

- `SECRET_KEY`: signe les sessions et protections Flask.
- `ENCRYPTION_KEY`: cle Fernet pour les identifiants de sources.

En developpement, une cle Flask temporaire est generee si `SECRET_KEY` est
absente. En production, l'application refuse de demarrer si `SECRET_KEY` ou
`ENCRYPTION_KEY` manque. `ENCRYPTION_KEY` doit etre une cle Fernet valide.

Les fichiers exemples peuvent contenir des placeholders, jamais de valeur
utilisable. Le fichier d'environnement reel reste ignore par Git.

## Rotation Fernet

Les champs login et mot de passe des sources sont stockes chiffres. Changer
`ENCRYPTION_KEY` sans rotation rend ces valeurs illisibles.

Procedure:

1. Generer une nouvelle cle Fernet.
2. Exporter l'ancienne cle dans `OLD_ENCRYPTION_KEY`.
3. Exporter la nouvelle cle dans `NEW_ENCRYPTION_KEY`.
4. Executer la commande de rotation.
5. Remplacer `ENCRYPTION_KEY` dans l'environnement seulement apres succes.
6. Redemarrer l'application et tester la lecture des sources configurees.

Commande:

```bash
OLD_ENCRYPTION_KEY=... NEW_ENCRYPTION_KEY=... .venv/bin/flask --app run.py rotate-encryption-key
```

La commande utilise une transaction: en cas d'erreur, les changements sont
annules. Elle ne journalise pas les secrets ni les valeurs dechiffrees.

## Permissions Locales

Le fichier `.env` doit etre lisible uniquement par son proprietaire:

```bash
chmod 600 .env
make permissions
```

Les scripts appeles directement peuvent etre rendus executables en `750`.

## Headers HTTP Et CSP

L'application ajoute ses headers de securite en interne:

- Content Security Policy avec nonce sur `script-src`.
- `object-src 'none'`.
- `base-uri 'self'`.
- `form-action 'self'`.
- `X-Content-Type-Options: nosniff`.
- `X-Frame-Options: SAMEORIGIN`.
- `Referrer-Policy: strict-origin-when-cross-origin`.
- `Permissions-Policy` refusant geolocalisation, micro et camera.

`script-src` ne doit pas contenir `'unsafe-inline'`. Les scripts inline
necessaires dans les templates doivent porter le nonce fourni par l'application.

## Transport, Sessions Et Proxy

En production:

- `SESSION_COOKIE_SECURE` est active par defaut.
- `LDAP_REQUIRE_TLS` est active par defaut.
- `FORCE_HTTPS` peut forcer les redirections HTTPS.
- `TRUST_PROXY` ne doit etre active que derriere un proxy de confiance qui
  nettoie les en-tetes Forwarded.

Si TLS est termine par un reverse proxy, aligner `FORCE_HTTPS`,
`SESSION_COOKIE_SECURE` et `TRUST_PROXY` avec le mode de terminaison choisi.

## Migrations SQLite

Les migrations idempotentes ajoutent seulement des colonnes connues par une
allowlist interne. Les identifiants de table et colonne sont valides puis
quotes avant construction SQL. Le DDL de colonne est egalement valide.

Ne jamais brancher une entree utilisateur, un nom fourni par API ou un fichier
de configuration externe dans cette allowlist.

## Dependances Et Audits

Le controle standard est:

```bash
make check
```

Pour isoler les audits:

```bash
.venv/bin/python -m pip_audit -r requirements.txt -r requirements-dev.txt
.venv/bin/python -m bandit -r app config.py run.py -q
```

Les montes de version doivent rester ciblees et verifiees par la suite de tests.
Ne pas remplacer une dependance par une autre qui ne couvre pas le meme role.

## Donnees Et Stockage

Les chemins de documents, corbeille, exports et telechargements doivent rester
sous le stockage controle. Les noms exposes en ZIP, CSV, XLSX ou email sont
normalises, neutralises ou echappes selon le format.

Les sources locales doivent appartenir a une racine explicitement autorisee.
Eviter les racines larges comme `/` ou un dossier personnel complet.

## Incident Secret

Si un secret local a pu etre lu par un tiers:

1. Traiter la valeur comme compromise.
2. Generer une nouvelle valeur.
3. Pour `ENCRYPTION_KEY`, executer la rotation Fernet avant remplacement.
4. Verifier que `.env` n'est pas suivi par Git et que ses permissions sont
   restrictives.
5. Relancer `make check`.
6. Verifier si un depot distant ou une archive externe contient le secret avant
   de planifier une reecriture d'historique.

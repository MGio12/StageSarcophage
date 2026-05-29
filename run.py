from app import create_app

app = create_app()

if __name__ == "__main__":
    # Serveur de développement uniquement; la production passe par Gunicorn.
    app.run(debug=True, host="0.0.0.0", port=5000)  # nosec B104

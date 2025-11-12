from app import create_app

app = create_app()

if __name__ == '__main__':
    # Při nasazení na produkci nastavit debug=False!
    app.run(debug=True)
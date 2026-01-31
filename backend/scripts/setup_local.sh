#!/bin/bash
# Local dev setup: install deps + Playwright browser
cd "$(dirname "$0")/.." || exit

echo "Creating venv if needed..."
python3 -m venv venv 2>/dev/null || true
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -r requirements.txt -q

echo "Installing Playwright Chromium (required for scraping)..."
playwright install chromium

echo "Done. To see the map/browser when scraping locally, add to backend/.env:"
echo "  HEADLESS=False"
echo ""
echo "Start backend: source venv/bin/activate && python app.py"
echo "Start frontend: cd frontend && npm run dev"

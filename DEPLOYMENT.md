# OLX Vehicle Monitor - Deployment Guide

## ✅ Project Status: COMPLETE & TESTED

### Test Results Summary

**Scraping Methods Tested:**
- ❌ requests-html: Failed (403 Forbidden)
- ❌ Selenium: Loaded page but couldn't extract listings
- ✅ **Playwright: SUCCESS** - 57 listings extracted in 6.24s

**Component Testing:**
- ✅ Scraper: Working (50 listings)
- ✅ Storage: Working (JSON persistence)
- ✅ Deduplication: Working (47 new / 50 total)
- ✅ Notifier: Working (test sent to ntfy.sh/carros-mg-olx)

### Quick Start

#### 1. Create GitHub Repository
```bash
# Go to https://github.com/new
# Repository name: olx-vehicle-monitor
# Visibility: Public
# Do NOT initialize with README
```

#### 2. Push to GitHub
```bash
cd /Users/renato/projetos/olx-vehicle-monitor

# Add your GitHub remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/olx-vehicle-monitor.git

# Update config files with your username
# Edit config.yaml: change url to your GitHub repo
# Edit repository.yaml: change url to your GitHub repo

# Commit changes
git add config.yaml repository.yaml
git commit -m "Update repository URLs"

# Push to GitHub
git push -u origin main
```

#### 3. Install in Home Assistant

1. Open Home Assistant
2. Go to **Settings** → **Add-ons** → **Add-on Store**
3. Click ⋮ (top right) → **Repositories**
4. Add your repository URL:
   ```
   https://github.com/YOUR_USERNAME/olx-vehicle-monitor
   ```
5. Click **Add**
6. Refresh the page
7. Find "OLX Vehicle Monitor" in the add-on list
8. Click **Install**
9. After installation, click **Start**
10. Enable "Start on boot" (optional)

#### 4. Subscribe to Notifications

**On Mobile:**
1. Install ntfy.sh app:
   - Android: https://play.google.com/store/apps/details?id=io.heckel.ntfy
   - iOS: https://apps.apple.com/app/ntfy/id1625396347
2. Open the app
3. Tap "Subscribe to topic"
4. Enter: `carros-mg-olx`
5. Done! You'll receive notifications when new vehicles are found

**On Web:**
- Visit: https://ntfy.sh/carros-mg-olx

### Configuration

All configuration is **hardcoded** as per requirements:

- **OLX URL**: MG vehicles, R$ 19.000 - R$ 26.000
- **Filters**: Flex/Gas, Manual/Auto, Inspected vehicles
- **ntfy.sh Topic**: `carros-mg-olx`
- **Check Interval**: 10 minutes
- **Storage**: `/data/seen_listings.json` (persistent)

To change these, edit `app/monitor.py`:
```python
OLX_URL = "https://www.olx.com.br/..."  # Line 14
NTFY_TOPIC = "carros-mg-olx"            # Line 15
CHECK_INTERVAL = 600                     # Line 16 (in seconds)
```

### Monitoring

**View Logs:**
1. Open the add-on in Home Assistant
2. Click on the "Logs" tab
3. You'll see:
   - Check timestamps
   - Number of listings found
   - New listings detected
   - Notification status
   - Any errors

**Expected Log Output:**
```
--- Check started at 2026-04-04 10:00:00 ---
Fetching listings from OLX...
Fetched 57 total listings
Previously seen: 54 listings
Found 3 NEW listings!
  1. [1491406879] Chevrolet Kadett GLS 2.0 MPFI 1998... - R$ 19.500
  2. [1481607403] Renault Logan Expression Hi-flex 1.6 16V... - R$ 25.000
  3. [1425689084] Citroën Xsara Picasso 2.0 Exclusive... - R$ 25.000
Notification sent successfully
Saved 3 new IDs to storage
Check completed. Sleeping for 600 seconds...
```

### Troubleshooting

**Add-on won't start:**
- Check logs for errors
- Verify Docker has enough resources
- Try rebuilding: Settings → Add-on → Rebuild

**No notifications received:**
- Verify you're subscribed to `carros-mg-olx` topic
- Test manually: `curl -d "Test" ntfy.sh/carros-mg-olx`
- Check add-on logs for notification errors

**Duplicate notifications:**
- Check if `/data/seen_listings.json` exists
- Stop add-on, delete the file, restart

**OLX structure changed:**
- The scraper extracts from `__NEXT_DATA__` JSON
- If OLX changes their page structure, the scraper may break
- Open an issue on GitHub for updates

### File Structure

```
olx-vehicle-monitor/
├── config.yaml          # HAOS addon metadata
├── Dockerfile          # Container definition
├── repository.yaml     # Custom repository config
├── requirements.txt    # Python dependencies
├── run.sh             # Startup script
├── README.md          # Full documentation
├── test_monitor.py    # Local testing script
└── app/
    ├── monitor.py     # Main loop (entry point)
    ├── scraper.py     # OLX scraping logic
    ├── storage.py     # JSON persistence
    └── notifier.py    # ntfy.sh integration
```

### Technical Details

**Dependencies:**
- Python 3.9+
- Playwright 1.47.0 (browser automation)
- Requests 2.31.0 (HTTP client)
- Chromium (headless browser)

**Docker Image:**
- Base: Home Assistant base image (Alpine Linux)
- Size: ~300-400MB (includes Chromium)
- Architectures: amd64, armv7, aarch64

**Data Persistence:**
- Storage location: `/data/seen_listings.json`
- Mapped to HAOS persistent volume
- Survives container restarts
- Format: JSON with sorted listing IDs

### Notification Format

As notificações usam Markdown com hyperlinks clicáveis:

```
Novos Anuncios OLX - 3 veiculos

1. [Fiat Uno Vivace 1.0 2015](https://mg.olx.com.br/...)
   R$ 25.000
   Belo Horizonte, Centro - DDD 31

2. [VW Gol 1.6 Total Flex 2018](https://mg.olx.com.br/...)
   R$ 22.500
   Contagem - DDD 31

3. [Chevrolet Onix 1.0 2020](https://mg.olx.com.br/...)
   R$ 24.800
   Betim - DDD 31
```

**Features:**
- Títulos são links clicáveis (Markdown)
- Texto sem acentos
- Clique no título para abrir o anúncio

### Testing Locally (Optional)

```bash
cd /Users/renato/projetos/olx-vehicle-monitor

# Install dependencies
pip3 install -r requirements.txt
playwright install chromium

# Run test
python3 test_monitor.py

# Expected output:
# ✓ Scraper works! Found X listings
# ✓ Storage works!
# ✓ Deduplication works!
# ✓ Notifier works!
# ✅ ALL TESTS PASSED!
```

---

## Support

For issues or questions:
1. Check the logs in HAOS
2. Review this guide
3. Open an issue on GitHub

## License

This project is provided as-is without warranties.
Use at your own risk. Web scraping may violate OLX's Terms of Service.

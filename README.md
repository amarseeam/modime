# 🛢️ Modular Oil Disaster Interactive Modeling Environment: 

A full-stack web application to simulate oil spills in the Indian Ocean using NOAA's GNOME modeling engine. Designed originally to simulate the MV Wakashio disaster near Mauritius, this platform supports:

- 🌍 **Interactive map** with Leaflet.js for selecting spill locations
- 🌬️ **Live wind forecast** integration via [Open-Meteo API](https://open-meteo.com)
- 🐚 High-resolution coastline via `.bna` files
- 🛢️ ADIOS-compatible oil types for realistic modeling
- 📈 Output formats: NetCDF (`.nc`), KMZ (`.kmz`), and animated `.gif`
- ⚙️ Flask backend with Conda-managed GNOME environment



## 📦 Features

| Feature                  | Description |
|--------------------------|-------------|
| **Click-to-Spill**       | Choose coordinates on the map to simulate an oil spill |
| **Wind Forecast**        | Automatically fetches 7-day forecast based on clicked location |
| **Custom Spill Logic**   | Configurable release duration, oil volume, and model duration (in progress) |
| **GNOME Integration**    | Uses `gnome.scripting` to define oceanographic movers and weatherers |
| **Simulation Outputs**   | NetCDF, KMZ, and image sequence/GIF available for download or display |
| **Modular Python Design**| Separate scripts for Wakashio using fixed data, custom, and forecasted simulations |

---
## 📦 Simulation Assets

This project uses two key files to support accurate oil spill modeling:

### `mauritius.bna`
A **Boundary Node Attribute (BNA)** file that defines the **coastline and land-water boundaries** around Mauritius.  
It enables GNOME to simulate how oil interacts with the island’s geography.

### `vlsfo-im-5-imaros_AD02592.json`
A **NOAA ADIOS oil properties file** for **Very Low Sulphur Fuel Oil (VLSFO)** — the type spilled by the Wakashio.  
It provides detailed chemical and physical properties for simulating oil weathering, evaporation, and dispersion.

---

## 📦 Future Work

Defining safe perimeter, real-time extraction of potential ship hazards nearby, and integration with other software

## 🧪 Requirements

- Python 3.8+
- Conda environment with GNOME (`gnome`, `pygnome`)
- Flask
- `requests`, `datetime`, `netCDF4`, `matplotlib` (if plotting)
- Access to:
  - `mauritius.bna`
  - `vlsfo-im-5-imaros_AD02592.json`

---
## 🗺️ Demo Interface

![GUI](gui.png)

## 🚀 Quick Start

```bash
# 1. Activate GNOME environment
conda activate gnome

# 2. Run Flask backend
python app.py

# 3. Open browser at:
http://localhost:5000

from flask import Flask, request, render_template, jsonify
import subprocess

app = Flask(__name__)

@app.route("/")
def map_page():
    return render_template("map2.html")

@app.route("/run_sim", methods=["POST"])
def run_sim():
    data = request.get_json()
    lat = data.get("lat")
    lon = data.get("lon")
    mode = data.get("mode", "wakashio")  # Default to wakashio if not provided

    if lat is None or lon is None:
        return jsonify({"output": "❌ Missing coordinates in request."})

    # Determine which script to run
    script_map = {
        "wakashio": "run_wakashio_sim.py",
        "wind_now": "run_wind.py",
        "custom": "run_wakashio_sim.py"
    }

    script = script_map.get(mode)
    if script is None:
        return jsonify({"output": f"❌ Invalid simulation mode '{mode}'."})

    try:
        result = subprocess.run(
            ["conda", "run", "-n", "gnome", "python", script, str(lat), str(lon)],
            capture_output=True,
            text=True,
            timeout=900  # 15 minutes
        )

        output = result.stdout + "\n" + result.stderr
        return jsonify({"output": output})

    except subprocess.TimeoutExpired:
        return jsonify({"output": "❌ Simulation timed out after 15 minutes."})
    except Exception as e:
        return jsonify({"output": f"❌ Error running simulation: {str(e)}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

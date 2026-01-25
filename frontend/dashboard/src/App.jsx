import { useEffect, useState } from "react";
import WateringPanel from "./components/WateringPanel";
import SensorCard from "./components/SensorCard";
import Header from "./components/Header";
import PlantStatus from "./components/PlantStatus";
import { getPlantInfo, waterPlant } from "./api/plantApi";

export default function App() {
  const [plant, setPlant] = useState(null);
  const [error, setError] = useState("");
  const [lastUpdated, setLastUpdated] = useState(null);

  async function load() {
    try {
      setError("");
      const data = await getPlantInfo();
      setPlant(data.plant_info);
      setLastUpdated(
        data.last_updated ? new Date(data.last_updated) : new Date(), // last_updated trenutno nije dostupan pa se koristi trenutno vrijeme
      );
    } catch (e) {
      setPlant(null);
      setError(
        e?.message ||
          "Oops! Something went wrong while loading plant data. Please try again.",
      );
    } 
  }

  useEffect(() => {
    load();
    const id = setInterval(load, 30000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center px-4">
      <div className="w-full max-w-4xl rounded-3xl border border-white/10 bg-white/5 backdrop-blur p-6 md:p-8 shadow-2xl">
        <Header lastUpdated={lastUpdated} onRefresh={load} />

        {error ? (
          <div className="mb-4 rounded-2xl border border-red-500/30 bg-red-500/10 p-4 text-red-200">
            {error}
          </div>
        ) : null}

        <PlantStatus plant={plant} />

        {!plant ? (
          <div className="rounded-2xl border border-white/10 bg-white/5 p-6 text-center text-white/70">
            Loading plant data…
          </div>
        ) : (
          <div className="grid gap-6 lg:grid-cols-2">
            <div className="lg:sticky lg:top-6">
              <WateringPanel onWater={waterPlant} />
            </div>

            <div className="grid gap-4 ">
              <SensorCard
                label="Temperature"
                value={plant.air.temperature}
                status={plant.air.status}
              />

              <SensorCard
                label="Air humidity"
                value={plant.air.humidity}
                status={plant.air.status}
              />

              <SensorCard
                label="Soil humidity"
                value={plant.ground.humidity}
                status={plant.ground.status}
              />
            </div>
          </div>
        )}

        <div className="mt-6 text-center text-xs text-white/40">
          Auto-refresh every 30s
        </div>
      </div>
    </div>
  );
}
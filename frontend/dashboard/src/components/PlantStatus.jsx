const unknown_state = {
  health: "unknown",
  title: "—",
  description: "Waiting for sensor data…",
};

function evaluatePlantHealth(plant) {
  if (!plant) return unknown_state;

  const air = plant.air?.status;
  const ground = plant.ground?.status;

  if (!air || !ground) return unknown_state;

  if (air === "optimal" && ground === "optimal") {
    return {
      health: "ok",
      title: "Everything looks good 𑣲",
      description: "All parameters are within the target range.",
    };
  }

  if (air === "bad") {
    if (ground === "dry") {
      return {
        health: "critical",
        title: "Critical environment conditions",
        description:
          "Air conditions are outside safe limits and soil moisture is low. Immediate action is required to protect the plant.",
      };
    }
    return {
      health: "critical",
      title: "Air conditions are outside safe limits",
      description:
        "Air temperature or humidity is far outside the recommended range. Please adjust room conditions or relocate the plant.",
    };
  }

  if (ground === "dry") {
    if (air === "moderate") {
      return {
        health: "warning",
        title: "Current conditions need adjustment",
        description:
          "Both air conditions and soil moisture are outside the optimal range. Consider adjusting the environment and watering the plant.",
      };
    }
    return {
      health: "warning",
      title: "Soil moisture is low",
      description:
        "Soil humidity is below the target range. Watering is recommended.",
    };
  }

  if (air === "moderate") {
    return {
      health: "warning",
      title: "Air conditions are slightly off",
      description:
        "Temperature or air humidity is outside the optimal range but still acceptable.",
    };
  }

  return unknown_state;
}

export default function PlantStatus({ plant }) {
  const state = evaluatePlantHealth(plant);

  const titleColor = {
    ok: "text-emerald-100",
    warning: "text-orange-200",
    critical: "text-red-400",
    unknown: "text-white/40",
  };

  return (
    <div className="mb-4 py-2">
      <div className="flex flex-col gap-2">
        <div className={`text-2xl font-semibold ${titleColor[state.health]}`}>
          {state.title}
        </div>

        <div className="text-sm md:text-base text-white/60">
          {state.description}
        </div>
      </div>
    </div>
  );
}
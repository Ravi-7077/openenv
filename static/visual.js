function setState(data) {
    document.getElementById('timestep').textContent = `Timestep: ${data.timestep}`;
    const phaseEl = document.getElementById('phase');
    phaseEl.textContent = `Phase: ${data.current_phase}`;
    phaseEl.className = `phase ${data.current_phase}`;

    const lanesEl = document.getElementById('lanes');
    lanesEl.innerHTML = data.lanes.map(lane => `
        <div class="lane">
            <strong>${lane.lane_id}</strong>: ${lane.vehicle_count} vehicles, avg wait ${lane.avg_wait_time.toFixed(1)}s
        </div>
    `).join('');
}

setInterval(async () => {
  const res = await fetch("/state");
  const data = await res.json();
  setState(data);
}, 500);
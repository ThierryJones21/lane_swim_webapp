<script>
    import { onMount } from 'svelte';
    import axios from 'axios';
    import MultiSelect from 'svelte-multiselect';
    import { Map, Marker, controls } from '@beyonk/svelte-mapbox';

    const mapboxApiKey = process.env.VITE_PUBLIC_MAPBOX_API_KEY;
    const { GeolocateControl, NavigationControl, ScaleControl } = controls

    let schedules = [];
    let poolFilter = [];
    let dayFilter = '';
    let timeFilter = '';
    let isStartTimeSortedAsc = true;
    let pools = [];
    let poolsDict = {};
    let scriptLog = {};
    let mapComponent;
    let brandColour = "rgb(255, 0, 0)";

    const fetchLastRunTime = async () => {
        try {
            const response = await axios.get("http://127.0.0.1:5000/script-log");
            scriptLog = response.data;
        } catch (error) {
            console.error('Error fetching pools:', error);
        }
    };

    const geocodeAddress = async (address) => {
        try {
            console.log(address);
            const geocodeResponse = await axios.get(`https://api.mapbox.com/search/geocode/v6/forward?q=${encodeURIComponent(address)}.json&proximity=-75.695000,45.4201&access_token=${mapboxApiKey}`);
            console.log(geocodeResponse.data.features);
            const features = geocodeResponse.data.features;
            if (features.length > 0) {
                const [lng, lat] = features[0].geometry.coordinates;
                return { lat, lng };
            }
        } catch (error) {
            console.error('Error geocoding address:', error);
        }
        return null;
    };

    // Fetching pools from the backend
    const fetchPools = async () => {
        try {
            const response = await axios.get('http://127.0.0.1:5000/pools');
            pools = response.data;
            
        } catch (error) {
            console.error('Error fetching pools:', error);
        }
    };

    const fetchSchedules = async () => {
        try {
            const response = await axios.get('http://127.0.0.1:5000/schedules', {
                params: { 'pool[]': poolFilter, day: dayFilter, time: timeFilter }
            });
            schedules = response.data;
            for (const schedule of schedules) {
                const { lat, lng } = await geocodeAddress(schedule.address);
                poolsDict[schedule.pool] = { "name" : schedule.pool, "lat": lat, "lng": lng  }; // Add lat/lng to the pool
            }
        } catch (error) {
            console.error('Error fetching schedules:', error);
        }
    };

    const sortSchedulesByStartTime = () => {
        schedules = schedules.slice().sort((a, b) => {
            const timeA = new Date(`1970-01-01T${a.start_time}`);
            const timeB = new Date(`1970-01-01T${b.start_time}`);
            return isStartTimeSortedAsc ? timeA - timeB : timeB - timeA;
        });
        isStartTimeSortedAsc = !isStartTimeSortedAsc;
    };

    onMount(() => {
        fetchPools(); // Fetch pools when the component mounts
        fetchSchedules(); // Fetch schedules initially
        fetchLastRunTime();
        if (mapComponent){
            mapComponent.setCenter([ '-75.695000','45.4201'], 4)
        }
    });

    function handleRecentre(e) {
        console.log('Map recentered:', e.detail.center);
    }
</script>

<h1>Ottawa Lane Swim Schedules</h1>

<div class="script-log">
    <p><strong>Last Updated:</strong> {scriptLog.last_run_time ? `${scriptLog.last_run_time} (Script: ${scriptLog.script_name})` : "Fetching..."}</p>
</div>

<div class="filters">
    <div class="filter-container">
        <div class="filter-item">
            <label for="pool-select"><strong>Filter by Pool:</strong></label>
            <MultiSelect
                id="pool-select"
                options={pools}
                placeholder="Select pools"
                bind:selected={poolFilter}
                on:change={fetchSchedules}
                allowUserOptions="append"
                ulSelectedClass="selected-pools"  />
        </div>

        <div class="filter-item">
            <label for="day-select"><strong>Filter by Day:</strong></label>
            <select id="day-select" bind:value={dayFilter} on:change={fetchSchedules}>
                <option value="">All Days</option>
                {#each ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"] as day}
                    <option value={day}>{day}</option>
                {/each}
            </select>
        </div>

        <div class="filter-item">
            <label for="time-select"><strong>Filter by Time:</strong></label>
            <select id="time-select" bind:value={timeFilter} on:change={fetchSchedules}>
                <option value="">All Times</option>
                {#each ["06:00-09:00", "09:00-12:00", "12:00-15:00", "15:00-18:00", "18:00-21:00", "21:00-23:00"] as time}
                    <option value={time}>{time}</option>
                {/each}
            </select>
        </div>
    </div>
</div>

<div style="display: flex; justify-content: center; align-items: center; height: 60vh;">
    <div style="height: 60vh; width: 75%;">
        <Map
        accessToken={mapboxApiKey}
        bind:this={mapComponent}
        on:recentre={handleRecentre}
        options={{ scrollZoom: true }}
        >
        <NavigationControl />
        <GeolocateControl options={{ some: 'control-option' }}  />
        <ScaleControl />
        {#each Object.values(poolsDict) as pool}
            {#if pool.lat && pool.lng}
            <Marker
                lat={pool.lat}
                lng={pool.lng}
                label={pool.name}
                color={brandColour}
            />
            {console.log("Marker added for:", pool.name, pool.lat, pool.lng)}
            {/if}
        {/each}

        </Map>
    </div>
</div>

<table>
    <thead>
        <tr>
            <th>Pool</th>
            <th>Swim Type</th>
            <th>Day</th>
            <th on:click={sortSchedulesByStartTime} style="cursor: pointer;">
                Start Time {isStartTimeSortedAsc ? '▲' : '▼'}
            </th>
            <th>End Time</th>
        </tr>
    </thead>
    <tbody>
        {#each schedules as schedule}
            <tr>
                <td><a href="https://www.google.com/maps/search/?api=1&query={schedule.address}" target="_blank">{schedule.pool}</a></td>
                <td>{schedule.swim_type}</td>
                <td>{schedule.day}</td>
                <td>{schedule.start_time}</td>
                <td>{schedule.end_time}</td>
            </tr>
        {/each}
    </tbody>
</table>

<style>
    /* Basic styling */
    table { width: 100%; border-collapse: collapse; }
    th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
    th { cursor: pointer; }
    div { margin-bottom: 1rem; }
    
    /* Centering the filters */
    .filters {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-bottom: 1rem;
    }

    .filter-container {
        display: flex;
        align-items: center;
        gap: 1rem;
        justify-content: center; /* Centers the filter items horizontally */
        flex-wrap: wrap; /* Allows wrapping for responsiveness */
        position: sticky; /* Keeps filters locked in place */
        top: 0; /* Position from the top */
        background-color: white; /* Background to ensure visibility */
        z-index: 100; /* Higher z-index to overlay on content */
        padding: 1rem; /* Padding for aesthetics */
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* Subtle shadow for depth */
    }

    .filter-item {
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    :global(.mapboxgl-marker){
      cursor: pointer;
    } 
    :global(.mapboxgl-map) {
        height: 100vh;  /* Make the map take full height */
        width: 100%;    /* Make the map take full width */
    }
</style>
